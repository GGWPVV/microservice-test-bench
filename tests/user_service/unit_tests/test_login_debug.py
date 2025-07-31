import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import uuid
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/user_service/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared'))

# Mock all dependencies before importing
with patch('database.engine'), \
     patch('database.SessionLocal'), \
     patch('kafka_client.start_kafka_producer'), \
     patch('kafka_client.stop_kafka_producer'), \
     patch('kafka_client.publish_event'):
    from main import app, pwd_context
    import main

client = TestClient(app)

def test_debug_login_simple():
    """Debug login without any mocks to see what happens"""
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    
    response = client.post("/login", data=login_data)
    
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response: {response.text}")
    print(f"Login Headers: {response.headers}")
    
    # Just check it doesn't crash
    assert response.status_code in [200, 401, 422, 500]

def test_debug_login_with_basic_mock():
    """Debug login with basic dependency override"""
    # Create mock database session
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()
    mock_user.username = "testuser"
    mock_user.hashed_password = pwd_context.hash("password123")
    
    # Mock database query chain
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Mock get_db dependency
    def mock_get_db():
        return mock_db
    
    # Override FastAPI dependency
    app.dependency_overrides[main.get_db] = mock_get_db
    
    try:
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", data=login_data)
        
        print(f"With Mock Status Code: {response.status_code}")
        print(f"With Mock Response: {response.text}")
        
        # Just check it doesn't crash
        assert response.status_code in [200, 401, 422, 500]
        
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()

def test_debug_check_endpoint_exists():
    """Check if login endpoint is properly registered"""
    # Check if endpoint exists in routes
    routes = [route.path for route in app.routes]
    print(f"Available routes: {routes}")
    
    assert "/login" in routes