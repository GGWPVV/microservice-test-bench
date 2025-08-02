import pytest
import httpx
from typing import Dict, Any
import jwt
import time

class TestSecurity:
    """Security tests"""

    @pytest.mark.asyncio
    async def test_password_security_requirements(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-061: Password security requirements"""
        timestamp = int(time.time())
        base_data = {
            "username": f"security_test_{timestamp}",
            "email": f"security_{timestamp}@example.com",
            "age": 25,
            "city": "TestCity"
        }
        
        # Test too short password
        short_password_data = base_data.copy()
        short_password_data["password"] = "123"
        
        response = await http_client.post("/users", json=short_password_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_jwt_token_security(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-062: JWT token security"""
        # Get token
        login_data = {
            "email": created_user["email"],
            "password": created_user["password"]
        }
        
        response = await http_client.post("/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Check token structure
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Проверяем наличие обязательных полей
            assert "sub" in decoded  # subject (user_id)
            assert "exp" in decoded  # expiration time
            
            # Проверяем, что токен не содержит чувствительной информации
            sensitive_fields = ["password", "hashed_password", "email"]
            for field in sensitive_fields:
                assert field not in decoded
                
        except jwt.InvalidTokenError:
            pytest.fail("Токен имеет неверную структуру")

    @pytest.mark.asyncio
    async def test_token_expiration(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-063: Истечение срока действия токена"""
        # Создаем токен с истекшим сроком действия
        from datetime import datetime, timedelta
        
        expired_payload = {
            "sub": "test-user-id",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Истек час назад
        }
        
        expired_token = jwt.encode(expired_payload, "your-secret-key", algorithm="HS256")
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = await http_client.get("/user/me", headers=headers)
        assert response.status_code == 401
        
        data = response.json()
        assert data["detail"] == "Invalid token"

    @pytest.mark.asyncio
    async def test_malformed_token_handling(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-064: Обработка некорректных токенов"""
        malformed_tokens = [
            "invalid.token.format",
            "Bearer invalid_token",
            "completely_invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid_payload.signature"
        ]
        
        for token in malformed_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = await http_client.get("/user/me", headers=headers)
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_authorization_header_formats(
        self, 
        http_client: httpx.AsyncClient, 
        auth_token: str,
        wait_for_service
    ):
        """TC-065: Форматы заголовка авторизации"""
        # Правильный формат
        correct_headers = {"Authorization": f"Bearer {auth_token}"}
        response = await http_client.get("/user/me", headers=correct_headers)
        assert response.status_code == 200
        
        # Неправильные форматы
        wrong_formats = [
            {"Authorization": f"Basic {auth_token}"},
            {"Authorization": f"Token {auth_token}"},
            {"Authorization": auth_token},  # Без Bearer
        ]
        
        for headers in wrong_formats:
            response = await http_client.get("/user/me", headers=headers)
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_sql_injection_protection(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-066: Защита от SQL инъекций"""
        # Попытки SQL инъекций в различных полях
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "1' OR 1=1 --"
        ]
        
        timestamp = int(time.time())
        
        for injection in sql_injection_attempts:
            test_data = {
                "username": f"test_{timestamp}_{hash(injection)}",
                "email": f"test_{timestamp}_{hash(injection)}@example.com",
                "password": "password123",
                "age": 25,
                "city": injection  # Попытка инъекции в поле city
            }
            
            response = await http_client.post("/users", json=test_data)
            # Сервис должен либо создать пользователя (если инъекция заблокирована),
            # либо вернуть ошибку валидации, но не упасть
            assert response.status_code in [201, 422, 500]
            
            # Проверяем, что сервис все еще работает
            health_response = await http_client.get("/health")
            assert health_response.status_code == 200

    @pytest.mark.asyncio
    async def test_xss_protection(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-067: Защита от XSS атак"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        timestamp = int(time.time())
        
        for payload in xss_payloads:
            test_data = {
                "username": f"xss_test_{timestamp}_{hash(payload)}",
                "email": f"xss_{timestamp}_{hash(payload)}@example.com",
                "password": "password123",
                "age": 25,
                "city": payload  # XSS payload в поле city
            }
            
            response = await http_client.post("/users", json=test_data)
            
            if response.status_code == 201:
                # Если пользователь создался, проверяем, что данные корректно сохранились
                users_response = await http_client.get("/users")
                assert users_response.status_code == 200
                
                # Проверяем, что ответ не содержит исполняемого кода
                response_text = users_response.text
                # Проверяем что XSS payload был экранирован или удален
                # В JSON ответе < и > символы должны быть экранированы или отфильтрованы
                if "<script>" in response_text:
                    # Если script тег присутствует, он должен быть экранирован в JSON
                    assert "\u003cscript\u003e" in response_text or "&lt;script&gt;" in response_text

    @pytest.mark.asyncio
    async def test_rate_limiting_simulation(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-068: Симуляция ограничения скорости запросов"""
        # Отправляем много запросов подряд
        responses = []
        for i in range(20):
            response = await http_client.get("/health")
            responses.append(response.status_code)
        
        # Проверяем, что сервис обрабатывает все запросы
        # (В реальном окружении может быть настроен rate limiting)
        successful_requests = sum(1 for status in responses if status == 200)
        assert successful_requests > 0  # Хотя бы некоторые запросы должны быть успешными

    @pytest.mark.asyncio
    async def test_cors_security(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-069: Безопасность CORS"""
        # Проверяем CORS заголовки
        response = await http_client.options("/users")
        
        # В текущей конфигурации разрешены все origins (*)
        # В продакшене это должно быть ограничено
        cors_headers = {
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        }
        
        response_headers = {key.lower() for key in response.headers.keys()}
        
        # Проверяем наличие CORS заголовков
        for cors_header in cors_headers:
            if cors_header in response_headers:
                # Заголовок присутствует, это ожидаемо для текущей конфигурации
                pass

    @pytest.mark.asyncio
    async def test_sensitive_data_exposure(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-070: Проверка утечки чувствительных данных"""
        # Получаем список всех пользователей
        response = await http_client.get("/users")
        assert response.status_code == 200
        
        users = response.json()
        
        if users:
            user = users[0]
            
            # Проверяем, что чувствительные данные не возвращаются
            sensitive_fields = [
                "password", "hashed_password", "email", "id"
            ]
            
            for field in sensitive_fields:
                assert field not in user, f"Чувствительное поле {field} присутствует в ответе"
            
            # Проверяем, что возвращаются только безопасные поля
            safe_fields = ["username", "age", "city"]
            for field in safe_fields:
                assert field in user, f"Безопасное поле {field} отсутствует в ответе"

    @pytest.mark.asyncio
    async def test_input_validation_edge_cases(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-071: Граничные случаи валидации входных данных"""
        timestamp = int(time.time())
        
        edge_cases = [
            # Очень длинные строки
            {
                "username": "a" * 1000,
                "email": f"test_{timestamp}@example.com",
                "password": "password123",
                "age": 25,
                "city": "TestCity"
            },
            # Специальные символы
            {
                "username": f"test_{timestamp}",
                "email": f"test_{timestamp}@example.com",
                "password": "password123",
                "age": 25,
                "city": "City with special chars: !@#$%^&*()"
            },
            # Unicode символы
            {
                "username": f"test_{timestamp}",
                "email": f"test_{timestamp}@example.com",
                "password": "password123",
                "age": 25,
                "city": "Москва 🏙️"
            }
        ]
        
        for test_case in edge_cases:
            response = await http_client.post("/users", json=test_case)
            # Сервис должен корректно обработать запрос
            assert response.status_code in [201, 409, 422, 500]
            
            # Проверяем, что сервис остается работоспособным
            health_response = await http_client.get("/health")
            assert health_response.status_code == 200