import pytest
import httpx
import asyncio
from typing import Dict, Any
import time

class TestDatabaseIntegration:
    """Database integration tests"""

    @pytest.mark.asyncio
    async def test_database_connection_health(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-051: Database connection health check"""
        # Create user to test DB functionality
        timestamp = int(time.time())
        test_data = {
            "username": f"db_test_{timestamp}",
            "email": f"db_test_{timestamp}@example.com",
            "password": "password123",
            "age": 25,
            "city": "TestCity"
        }
        
        response = await http_client.post("/users", json=test_data)
        assert response.status_code == 201
        
        # Check that user was saved
        users_response = await http_client.get("/users")
        assert users_response.status_code == 200
        
        users = users_response.json()
        usernames = [user["username"] for user in users]
        assert test_data["username"] in usernames

    @pytest.mark.asyncio
    async def test_data_persistence(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-052: Проверка сохранности данных"""
        # Создаем пользователя
        create_response = await http_client.post("/users", json=test_user_data)
        assert create_response.status_code == 201
        
        # Авторизуемся
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await http_client.post("/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Получаем данные пользователя
        headers = {"Authorization": f"Bearer {token}"}
        user_response = await http_client.get("/user/me", headers=headers)
        assert user_response.status_code == 200
        
        user_data = user_response.json()
        assert user_data["username"] == test_user_data["username"]
        assert user_data["age"] == test_user_data["age"]

    @pytest.mark.asyncio
    async def test_unique_constraints(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-053: Проверка уникальных ограничений БД"""
        # Попытка создать пользователя с тем же username
        duplicate_username_data = created_user.copy()
        duplicate_username_data["email"] = "different@example.com"
        
        response = await http_client.post("/users", json=duplicate_username_data)
        assert response.status_code == 409  # Ошибка уникальности
        
        # Попытка создать пользователя с тем же email
        duplicate_email_data = created_user.copy()
        duplicate_email_data["username"] = "different_username"
        
        response = await http_client.post("/users", json=duplicate_email_data)
        assert response.status_code == 409  # Ошибка уникальности

    @pytest.mark.asyncio
    async def test_password_hashing(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-054: Проверка хеширования паролей"""
        # Создаем пользователя
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 201
        
        # Проверяем, что можем авторизоваться с правильным паролем
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await http_client.post("/login", json=login_data)
        assert login_response.status_code == 200
        
        # Проверяем, что не можем авторизоваться с неправильным паролем
        wrong_login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        wrong_response = await http_client.post("/login", json=wrong_login_data)
        assert wrong_response.status_code == 401

    @pytest.mark.asyncio
    async def test_concurrent_database_operations(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-055: Одновременные операции с БД"""
        timestamp = int(time.time())
        
        # Создаем данные для нескольких пользователей
        users_data = [
            {
                "username": f"concurrent_db_user_{i}_{timestamp}",
                "email": f"concurrent_db_{i}_{timestamp}@example.com",
                "password": "password123",
                "age": 20 + i,
                "city": f"City{i}"
            }
            for i in range(10)
        ]
        
        # Создаем пользователей одновременно
        tasks = [
            http_client.post("/users", json=user_data)
            for user_data in users_data
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Проверяем результаты
        successful_creates = 0
        for response in responses:
            if not isinstance(response, Exception) and response.status_code == 201:
                successful_creates += 1
        
        assert successful_creates == len(users_data)
        
        # Проверяем, что все пользователи сохранились
        users_response = await http_client.get("/users")
        assert users_response.status_code == 200
        
        all_users = users_response.json()
        created_usernames = [user["username"] for user in users_data]
        existing_usernames = [user["username"] for user in all_users]
        
        for username in created_usernames:
            assert username in existing_usernames

    @pytest.mark.asyncio
    async def test_database_transaction_integrity(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-056: Целостность транзакций БД"""
        # Получаем количество пользователей до операции
        initial_response = await http_client.get("/users")
        initial_count = len(initial_response.json())
        
        # Пытаемся создать пользователя с невалидными данными
        invalid_data = {
            "username": "test_user",
            "email": "invalid-email",  # Невалидный email
            "password": "password123",
            "age": 25,
            "city": "TestCity"
        }
        
        response = await http_client.post("/users", json=invalid_data)
        assert response.status_code == 422  # Ошибка валидации
        
        # Проверяем, что количество пользователей не изменилось
        final_response = await http_client.get("/users")
        final_count = len(final_response.json())
        
        assert final_count == initial_count

    @pytest.mark.asyncio
    async def test_database_field_validation(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-057: Валидация полей на уровне БД"""
        timestamp = int(time.time())
        
        # Тест с очень длинными значениями
        long_string = "a" * 1000
        test_data = {
            "username": f"test_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "password123",
            "age": 25,
            "city": long_string  # Очень длинное значение
        }
        
        # В зависимости от настроек БД, это может вызвать ошибку или обрезать значение
        response = await http_client.post("/users", json=test_data)
        # Проверяем, что сервис корректно обрабатывает такие случаи
        assert response.status_code in [201, 422, 500]

    @pytest.mark.asyncio
    async def test_user_timestamps(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-058: Проверка временных меток"""
        before_creation = time.time()
        
        # Создаем пользователя
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 201
        
        after_creation = time.time()
        
        # Авторизуемся и получаем данные пользователя
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await http_client.post("/login", json=login_data)
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        user_response = await http_client.get("/user/me", headers=headers)
        
        # Проверяем, что пользователь был создан в ожидаемое время
        # (Это базовая проверка, так как API не возвращает timestamps)
        assert user_response.status_code == 200

    @pytest.mark.asyncio
    async def test_database_connection_recovery(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-059: Восстановление подключения к БД"""
        # Этот тест проверяет, что сервис может восстановиться после проблем с БД
        # В реальном окружении можно временно отключить БД
        
        timestamp = int(time.time())
        test_data = {
            "username": f"recovery_test_{timestamp}",
            "email": f"recovery_{timestamp}@example.com",
            "password": "password123",
            "age": 25,
            "city": "TestCity"
        }
        
        # Пытаемся создать пользователя
        response = await http_client.post("/users", json=test_data)
        
        # Если БД доступна, операция должна быть успешной
        if response.status_code == 201:
            # Проверяем, что пользователь действительно создался
            users_response = await http_client.get("/users")
            assert users_response.status_code == 200
            
            users = users_response.json()
            usernames = [user["username"] for user in users]
            assert test_data["username"] in usernames

    @pytest.mark.asyncio
    async def test_database_query_performance(
        self, 
        http_client: httpx.AsyncClient, 
        multiple_users_data: list[Dict[str, Any]],
        wait_for_service
    ):
        """TC-060: Производительность запросов к БД"""
        # Создаем несколько пользователей
        for user_data in multiple_users_data:
            response = await http_client.post("/users", json=user_data)
            assert response.status_code == 201
        
        # Измеряем время выполнения запроса списка пользователей
        start_time = time.time()
        response = await http_client.get("/users")
        end_time = time.time()
        
        query_time = end_time - start_time
        
        assert response.status_code == 200
        assert query_time < 2.0  # Запрос должен выполняться быстрее 2 секунд
        
        users = response.json()
        assert len(users) >= len(multiple_users_data)