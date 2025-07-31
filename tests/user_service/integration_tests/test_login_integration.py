import pytest
import uuid
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from passlib.context import CryptContext

# Mock external dependencies before importing
with patch('main.setup_logger'), \
     patch('main.start_kafka_producer', new_callable=AsyncMock), \
     patch('main.stop_kafka_producer', new_callable=AsyncMock), \
     patch('main.publish_event', new_callable=AsyncMock):
    from main import app

client = TestClient(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TestLoginIntegration:
    """Integration tests for login functionality"""
    
    @patch('main.publish_event', new_callable=AsyncMock)
    @patch('main.create_jwt', return_value="fake_jwt_token")
    @patch('main.SessionLocal')
    def test_login_success_integration(self, mock_session_local, mock_create_jwt, mock_publish):
        """Integration test for successful login"""
        # Setup mock database with real-like behavior
        mock_db = mock_session_local.return_value.__enter__.return_value
        
        # Create mock user with hashed password
        mock_user = type('User', (), {})()
        mock_user.id = uuid.uuid4()
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.hashed_password = pwd_context.hash("password123")
        
        # Mock database query chain
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Test login request
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", data=login_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "fake_jwt_token"
        assert data["token_type"] == "bearer"
        
        # Verify business logic was called
        mock_create_jwt.assert_called_once_with(mock_user.id)
        mock_publish.assert_called_once()
    
    @patch('main.SessionLocal')
    def test_login_user_not_found_integration(self, mock_session_local):
        """Integration test for login with non-existent user"""
        # Setup mock database
        mock_db = mock_session_local.return_value.__enter__.return_value
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", data=login_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    
    @patch('main.SessionLocal')
    def test_login_wrong_password_integration(self, mock_session_local):
        """Integration test for login with wrong password"""
        # Setup mock database
        mock_db = mock_session_local.return_value.__enter__.return_value
        
        # Create mock user with different password
        mock_user = type('User', (), {})()
        mock_user.id = uuid.uuid4()
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.hashed_password = pwd_context.hash("correctpassword")
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/login", data=login_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

class TestCurrentUserIntegration:
    """Integration tests for current user endpoint"""
    
    @patch('main.SessionLocal')
    def test_get_current_user_integration(self, mock_session_local):
        """Integration test for get current user with real JWT"""
        # Setup mock database
        mock_db = mock_session_local.return_value.__enter__.return_value
        
        # Create mock user
        user_id = str(uuid.uuid4())
        mock_user = type('User', (), {})()
        mock_user.id = user_id
        mock_user.username = "testuser"
        mock_user.age = 25
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Create real JWT token
        from main import create_jwt
        real_token = create_jwt(user_id)
        
        headers = {"Authorization": f"Bearer {real_token}"}
        response = client.get("/user/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"
        assert data["age"] == 25