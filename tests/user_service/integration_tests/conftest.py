import pytest
import asyncio
import httpx
import time
from typing import Dict, Any
import os

# Test environment configuration
BASE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
TIMEOUT = 30.0

@pytest.fixture(scope="session")
def event_loop():
    """Creates event loop for entire test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def http_client() -> httpx.AsyncClient:
    """HTTP client for tests"""
    return httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=TIMEOUT,
        follow_redirects=True
    )

@pytest.fixture(scope="session")
def wait_for_service(http_client: httpx.AsyncClient):
    """Waits for service readiness before tests"""
    import requests
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    pytest.fail("Service is not ready for testing")

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data"""
    import random
    timestamp = int(time.time())
    random_id = random.randint(1000, 9999)
    return {
        "username": f"testuser_{timestamp}_{random_id}",
        "email": f"test_{timestamp}_{random_id}@example.com",
        "password": "testpass123",
        "age": 25,
        "city": "TestCity"
    }

@pytest.fixture
def created_user(http_client: httpx.AsyncClient, test_user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates test user and returns user data"""
    import requests
    response = requests.post(f"{BASE_URL}/users", json=test_user_data)
    assert response.status_code == 201
    return test_user_data

@pytest.fixture
def auth_token(http_client: httpx.AsyncClient, created_user: Dict[str, Any]) -> str:
    """Gets authorization token for test user"""
    import requests
    login_data = {
        "email": created_user["email"],
        "password": created_user["password"]
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token: str) -> Dict[str, str]:
    """Authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def multiple_users_data() -> list[Dict[str, Any]]:
    """Data for creating multiple users"""
    timestamp = int(time.time())
    return [
        {
            "username": f"user1_{timestamp}",
            "email": f"user1_{timestamp}@example.com",
            "password": "password123",
            "age": 20,
            "city": "City1"
        },
        {
            "username": f"user2_{timestamp}",
            "email": f"user2_{timestamp}@example.com",
            "password": "password456",
            "age": 30,
            "city": "City2"
        },
        {
            "username": f"user3_{timestamp}",
            "email": f"user3_{timestamp}@example.com",
            "password": "password789",
            "age": 40,
            "city": "City3"
        }
    ]

@pytest.fixture
def kafka_consumer():
    """Creates Kafka consumer for tests"""
    from aiokafka import AIOKafkaConsumer
    import json
    
    async def _create_consumer():
        # Создаем уникальную группу для каждого теста
        group_id = f"test_group_{int(time.time() * 1000000)}"
        
        consumer = AIOKafkaConsumer(
            "user.registered",
            "user.logged_in", 
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094"),
            group_id=group_id,
            auto_offset_reset="latest",
            enable_auto_commit=True,
            consumer_timeout_ms=5000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None
        )
        
        try:
            await consumer.start()
            # Ждем немного чтобы consumer подключился
            await asyncio.sleep(0.5)
            return consumer
        except Exception as e:
            await consumer.stop()
            raise e
    
    return _create_consumer()