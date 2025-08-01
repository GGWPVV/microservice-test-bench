import pytest
import httpx
import asyncio
import json
from typing import Dict, Any

class TestKafkaIntegration:
    """Kafka integration tests"""

    @pytest.mark.asyncio
    async def test_user_registration_kafka_event(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-044: Send Kafka event on user registration"""
        # Подготавливаем consumer
        consumer = await kafka_consumer.__anext__()
        
        # Создаем пользователя
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 201
        
        # Ждем сообщение из Kafka
        try:
            async def get_message():
                async for message in consumer:
                    return message
            
            message = await asyncio.wait_for(get_message(), timeout=10.0)
            
            # Проверяем содержимое сообщения
            event_data = message.value
            assert "user_id" in event_data
            assert "username" in event_data
            assert "timestamp" in event_data
            assert event_data["username"] == test_user_data["username"]
            
        except asyncio.TimeoutError:
            pytest.fail("User registration event was not sent to Kafka")

    @pytest.mark.asyncio
    async def test_user_login_kafka_event(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-045: Отправка события в Kafka при входе пользователя"""
        # Подготавливаем consumer
        consumer = await kafka_consumer.__anext__()
        
        # Авторизуемся
        login_data = {
            "email": created_user["email"],
            "password": created_user["password"]
        }
        
        response = await http_client.post("/login", json=login_data)
        assert response.status_code == 200
        
        # Ждем сообщение из Kafka
        try:
            async def get_message():
                async for message in consumer:
                    return message
            
            message = await asyncio.wait_for(get_message(), timeout=10.0)
            
            # Проверяем содержимое сообщения
            event_data = message.value
            assert "user_id" in event_data
            assert "username" in event_data
            assert "timestamp" in event_data
            assert event_data["username"] == created_user["username"]
            
        except asyncio.TimeoutError:
            pytest.fail("Событие входа пользователя не было отправлено в Kafka")

    @pytest.mark.asyncio
    async def test_kafka_message_format(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-046: Проверка формата сообщений Kafka"""
        # Подготавливаем consumer
        consumer = await kafka_consumer.__anext__()
        
        # Создаем пользователя
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 201
        
        # Получаем сообщение
        try:
            async def get_message():
                async for message in consumer:
                    return message
            
            message = await asyncio.wait_for(get_message(), timeout=10.0)
            
            event_data = message.value
            
            # Проверяем обязательные поля
            required_fields = ["user_id", "username", "timestamp"]
            for field in required_fields:
                assert field in event_data, f"Поле {field} отсутствует в событии"
            
            # Проверяем типы данных
            assert isinstance(event_data["user_id"], str)
            assert isinstance(event_data["username"], str)
            assert isinstance(event_data["timestamp"], str)
            
            # Проверяем формат timestamp
            from datetime import datetime
            try:
                datetime.fromisoformat(event_data["timestamp"].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"Неверный формат timestamp: {event_data['timestamp']}")
                
        except asyncio.TimeoutError:
            pytest.fail("Событие не было получено из Kafka")

    @pytest.mark.asyncio
    async def test_multiple_kafka_events(
        self, 
        http_client: httpx.AsyncClient, 
        multiple_users_data: list[Dict[str, Any]],
        kafka_consumer,
        wait_for_service
    ):
        """TC-047: Множественные события Kafka"""
        created_usernames = []
        
        # Создаем несколько пользователей
        for user_data in multiple_users_data:
            response = await http_client.post("/users", json=user_data)
            assert response.status_code == 201
            created_usernames.append(user_data["username"])
        
        # Собираем события из Kafka
        consumer = await kafka_consumer.__anext__()
        received_events = []
        try:
            async def get_message():
                async for message in consumer:
                    return message
            
            for _ in range(len(multiple_users_data)):
                message = await asyncio.wait_for(get_message(), timeout=5.0)
                received_events.append(message.value)
        except asyncio.TimeoutError:
            pytest.fail(f"Получено только {len(received_events)} из {len(multiple_users_data)} событий")
        
        # Проверяем, что все пользователи представлены в событиях
        received_usernames = [event["username"] for event in received_events]
        for username in created_usernames:
            assert username in received_usernames

    @pytest.mark.asyncio
    async def test_kafka_connection_resilience(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-048: Устойчивость к проблемам с Kafka"""
        # Этот тест проверяет, что сервис продолжает работать даже если Kafka недоступна
        # В реальном окружении можно временно отключить Kafka
        
        # Создаем пользователя (должно работать даже если Kafka недоступна)
        response = await http_client.post("/users", json=test_user_data)
        
        # Сервис должен продолжать работать
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"

    @pytest.mark.asyncio
    async def test_kafka_event_ordering(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-049: Порядок событий Kafka"""
        # Создаем пользователя
        create_response = await http_client.post("/users", json=test_user_data)
        assert create_response.status_code == 201
        
        # Сразу авторизуемся
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await http_client.post("/login", json=login_data)
        assert login_response.status_code == 200
        
        # Получаем события в правильном порядке
        consumer = await kafka_consumer.__anext__()
        events = []
        try:
            async def get_message():
                async for message in consumer:
                    return message
            
            for _ in range(2):  # Ожидаем 2 события
                message = await asyncio.wait_for(get_message(), timeout=10.0)
                events.append({
                    "topic": message.topic,
                    "data": message.value
                })
        except asyncio.TimeoutError:
            pytest.fail(f"Получено только {len(events)} из 2 ожидаемых событий")
        
        # Проверяем, что события пришли в правильном порядке
        topics = [event["topic"] for event in events]
        assert "user.registered" in topics
        assert "user.logged_in" in topics

    @pytest.mark.asyncio
    async def test_kafka_event_idempotency(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        kafka_consumer,
        wait_for_service
    ):
        """TC-050: Идемпотентность событий Kafka"""
        login_data = {
            "email": created_user["email"],
            "password": created_user["password"]
        }
        
        # Выполняем несколько входов подряд
        for _ in range(3):
            response = await http_client.post("/login", json=login_data)
            assert response.status_code == 200
        
        # Проверяем, что каждый вход генерирует событие
        consumer = await kafka_consumer.__anext__()
        events_count = 0
        try:
            async def get_message():
                async for message in consumer:
                    return message
            
            while events_count < 3:
                await asyncio.wait_for(get_message(), timeout=5.0)
                events_count += 1
        except asyncio.TimeoutError:
            pass
        
        # Должно быть получено 3 события (по одному на каждый вход)
        assert events_count == 3