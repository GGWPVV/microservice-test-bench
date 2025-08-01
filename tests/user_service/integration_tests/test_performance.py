import pytest
import httpx
import asyncio
import time
from typing import Dict, Any, List
import statistics

class TestPerformance:
    """Performance tests"""

    @pytest.mark.asyncio
    async def test_response_time_health_check(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-072: Health check response time"""
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = await http_client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Health check should respond quickly
        assert avg_response_time < 0.5  # Average response less than 500ms
        assert max_response_time < 1.0   # Maximum response less than 1s

    @pytest.mark.asyncio
    async def test_user_creation_performance(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-073: Производительность создания пользователей"""
        response_times = []
        timestamp = int(time.time())
        
        for i in range(5):
            test_data = {
                "username": f"perf_user_{i}_{timestamp}",
                "email": f"perf_{i}_{timestamp}@example.com",
                "password": "password123",
                "age": 25,
                "city": "TestCity"
            }
            
            start_time = time.time()
            response = await http_client.post("/users", json=test_data)
            end_time = time.time()
            
            assert response.status_code == 201
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        
        # Создание пользователя должно быть достаточно быстрым
        assert avg_response_time < 2.0  # Средний ответ меньше 2с

    @pytest.mark.asyncio
    async def test_login_performance(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-074: Производительность авторизации"""
        login_data = {
            "email": created_user["email"],
            "password": created_user["password"]
        }
        
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = await http_client.post("/login", json=login_data)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        
        # Авторизация должна быть быстрой
        assert avg_response_time < 1.0  # Средний ответ меньше 1с

    @pytest.mark.asyncio
    async def test_user_list_performance(
        self, 
        http_client: httpx.AsyncClient, 
        multiple_users_data: List[Dict[str, Any]],
        wait_for_service
    ):
        """TC-075: Производительность получения списка пользователей"""
        # Создаем пользователей для тестирования
        for user_data in multiple_users_data:
            response = await http_client.post("/users", json=user_data)
            assert response.status_code == 201
        
        response_times = []
        
        for _ in range(5):
            start_time = time.time()
            response = await http_client.get("/users")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        
        # Получение списка должно быть быстрым
        assert avg_response_time < 1.0  # Средний ответ меньше 1с

    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-076: Производительность при одновременных запросах"""
        concurrent_requests = 20
        
        start_time = time.time()
        
        # Создаем одновременные запросы к health check
        tasks = [
            http_client.get("/health")
            for _ in range(concurrent_requests)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Проверяем, что все запросы успешны
        successful_responses = 0
        for response in responses:
            if not isinstance(response, Exception) and response.status_code == 200:
                successful_responses += 1
        
        assert successful_responses == concurrent_requests
        
        # Время обработки всех запросов должно быть разумным
        assert total_time < 5.0  # Все запросы за 5 секунд
        
        # Средняя пропускная способность
        throughput = concurrent_requests / total_time
        assert throughput > 5  # Минимум 5 запросов в секунду

    @pytest.mark.asyncio
    async def test_memory_usage_simulation(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-077: Симуляция использования памяти"""
        # Создаем много пользователей подряд для проверки утечек памяти
        timestamp = int(time.time())
        
        for i in range(50):
            test_data = {
                "username": f"memory_test_{i}_{timestamp}",
                "email": f"memory_{i}_{timestamp}@example.com",
                "password": "password123",
                "age": 25,
                "city": "TestCity"
            }
            
            response = await http_client.post("/users", json=test_data)
            assert response.status_code == 201
            
            # Периодически проверяем, что сервис остается отзывчивым
            if i % 10 == 0:
                health_response = await http_client.get("/health")
                assert health_response.status_code == 200

    @pytest.mark.asyncio
    async def test_database_query_performance(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-078: Производительность запросов к БД"""
        # Создаем несколько пользователей
        timestamp = int(time.time())
        for i in range(10):
            test_data = {
                "username": f"db_perf_{i}_{timestamp}",
                "email": f"db_perf_{i}_{timestamp}@example.com",
                "password": "password123",
                "age": 25,
                "city": "TestCity"
            }
            
            response = await http_client.post("/users", json=test_data)
            assert response.status_code == 201
        
        # Измеряем время выполнения запросов к БД
        query_times = []
        
        for _ in range(5):
            start_time = time.time()
            response = await http_client.get("/users")
            end_time = time.time()
            
            assert response.status_code == 200
            query_times.append(end_time - start_time)
        
        avg_query_time = statistics.mean(query_times)
        
        # Запросы к БД должны быть быстрыми
        assert avg_query_time < 1.0  # Средний запрос меньше 1с

    @pytest.mark.asyncio
    async def test_jwt_token_generation_performance(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-079: Производительность генерации JWT токенов"""
        login_data = {
            "email": created_user["email"],
            "password": created_user["password"]
        }
        
        generation_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = await http_client.post("/login", json=login_data)
            end_time = time.time()
            
            assert response.status_code == 200
            assert "access_token" in response.json()
            
            generation_times.append(end_time - start_time)
        
        avg_generation_time = statistics.mean(generation_times)
        
        # Генерация токенов должна быть быстрой
        assert avg_generation_time < 0.5  # Средняя генерация меньше 500мс

    @pytest.mark.asyncio
    async def test_password_hashing_performance(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-080: Производительность хеширования паролей"""
        timestamp = int(time.time())
        hashing_times = []
        
        for i in range(5):
            test_data = {
                "username": f"hash_perf_{i}_{timestamp}",
                "email": f"hash_perf_{i}_{timestamp}@example.com",
                "password": "password123",
                "age": 25,
                "city": "TestCity"
            }
            
            start_time = time.time()
            response = await http_client.post("/users", json=test_data)
            end_time = time.time()
            
            assert response.status_code == 201
            hashing_times.append(end_time - start_time)
        
        avg_hashing_time = statistics.mean(hashing_times)
        
        # Хеширование паролей может занимать время (это нормально для безопасности)
        # но не должно быть слишком медленным
        assert avg_hashing_time < 3.0  # Средний ответ меньше 3с

    @pytest.mark.asyncio
    async def test_api_documentation_performance(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-081: Производительность загрузки документации API"""
        endpoints = ["/docs", "/redoc", "/openapi.json"]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = await http_client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 2.0  # Документация должна загружаться быстро

    @pytest.mark.asyncio
    async def test_error_handling_performance(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-082: Производительность обработки ошибок"""
        error_response_times = []
        
        # Тестируем производительность обработки ошибок валидации
        for i in range(10):
            invalid_data = {
                "username": "test",
                "email": "invalid-email",  # Невалидный email
                "password": "123",  # Слишком короткий пароль
                "age": 12,  # Слишком молодой
                "city": ""  # Пустой город
            }
            
            start_time = time.time()
            response = await http_client.post("/users", json=invalid_data)
            end_time = time.time()
            
            assert response.status_code == 422
            error_response_times.append(end_time - start_time)
        
        avg_error_time = statistics.mean(error_response_times)
        
        # Обработка ошибок должна быть быстрой
        assert avg_error_time < 1.0  # Средний ответ меньше 1с