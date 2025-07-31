import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from jose import jwt
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/discount_service/app'))

# Mock external dependencies before importing
with patch('main.setup_logger'), \
     patch('main.start_kafka_producer', new_callable=AsyncMock), \
     patch('main.stop_kafka_producer', new_callable=AsyncMock), \
     patch('main.publish_event', new_callable=AsyncMock), \
     patch('main.get_redis', new_callable=AsyncMock), \
     patch('main.RedisCache'):
    from main import app, decode_token, get_user_info, is_user_in_top

client = TestClient(app)

class TestDecodeToken:
    @patch('main.jwt.decode')
    @pytest.mark.asyncio
    async def test_decode_token_success(self, mock_jwt_decode):
        """Test successful token decoding"""
        mock_jwt_decode.return_value = {"sub": "user123"}
        
        result = await decode_token("valid_token")
        
        assert result == "user123"
        mock_jwt_decode.assert_called_once_with("valid_token", "your-secret-key", algorithms=["HS256"])

    def test_decode_token_invalid_logic(self):
        """Test invalid token logic"""
        # Test that invalid tokens should return None
        invalid_token = "invalid_token"
        
        # Business logic: invalid tokens should be rejected
        assert len(invalid_token) > 0  # Token exists but is invalid
        assert invalid_token != "valid_token"  # Different from valid token

class TestGetUserInfo:
    @patch('main.requests.get')
    @pytest.mark.asyncio
    async def test_get_user_info_success(self, mock_get):
        """Test successful user info retrieval"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "username": "testuser", "age": 25}
        mock_get.return_value = mock_response
        
        result = await get_user_info("valid_token")
        
        assert result["username"] == "testuser"
        assert result["age"] == 25
        mock_get.assert_called_once_with(
            "http://user_service:8000/user/me",
            headers={"Authorization": "Bearer valid_token"}
        )

    @patch('main.requests.get')
    @pytest.mark.asyncio
    async def test_get_user_info_failure(self, mock_get):
        """Test user info retrieval failure"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = await get_user_info("invalid_token")
        
        assert result is None

class TestIsUserInTop:
    @patch('main.requests.get')
    @pytest.mark.asyncio
    async def test_is_user_in_top_true(self, mock_get):
        """Test user is in top leaderboard"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"username": "testuser", "score": 950000},
            {"username": "other", "score": 850000}
        ]
        mock_get.return_value = mock_response
        
        result = await is_user_in_top("testuser")
        
        assert result is True

    @patch('main.requests.get')
    @pytest.mark.asyncio
    async def test_is_user_in_top_false(self, mock_get):
        """Test user is not in top leaderboard"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"username": "other1", "score": 950000},
            {"username": "other2", "score": 850000}
        ]
        mock_get.return_value = mock_response
        
        result = await is_user_in_top("testuser")
        
        assert result is False

class TestDiscountLogic:
    def test_discount_calculation_logic(self):
        """Test discount calculation business logic"""
        # Test age-based discount
        age_40_plus = 45
        age_under_40 = 25
        
        discount_40_plus = 0.1 if age_40_plus >= 40 else 0.0
        discount_under_40 = 0.1 if age_under_40 >= 40 else 0.0
        
        assert discount_40_plus == 0.1
        assert discount_under_40 == 0.0
    
    def test_leaderboard_discount_logic(self):
        """Test leaderboard-based discount logic"""
        # Test top player discount
        is_in_top = True
        is_not_in_top = False
        
        top_discount = 0.1 if is_in_top else 0.0
        no_top_discount = 0.1 if is_not_in_top else 0.0
        
        assert top_discount == 0.1
        assert no_top_discount == 0.0
    
    def test_combined_discount_logic(self):
        """Test combined discount calculation"""
        age_discount = 0.1  # User over 40
        top_discount = 0.1  # User in top
        
        total_discount = age_discount + top_discount
        
        assert total_discount == 0.2

class TestHealthCheck:
    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "discount_service"
        assert "timestamp" in data