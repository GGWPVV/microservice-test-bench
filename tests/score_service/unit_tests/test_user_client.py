import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/score_service/app'))

with patch('user_client.setup_logger'):
    from user_client import get_user

class TestUserClient:
    """Test user_client functionality"""
    
    @patch('user_client.requests.get')
    def test_get_user_success(self, mock_get):
        """Test successful user retrieval"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "testuser"
        }
        mock_get.return_value = mock_response
        
        result = get_user("Bearer valid_token")
        
        assert result is not None
        assert result["username"] == "testuser"
        assert result["id"] == "123e4567-e89b-12d3-a456-426614174000"
        mock_get.assert_called_once_with(
            "http://user_service:8000/user/me",
            headers={"Authorization": "Bearer valid_token"}
        )
    
    @patch('user_client.requests.get')
    def test_get_user_invalid_token(self, mock_get):
        """Test user retrieval with invalid token"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        result = get_user("Bearer invalid_token")
        
        assert result is None
    
    @patch('user_client.requests.get')
    def test_get_user_network_error(self, mock_get):
        """Test user retrieval with network error"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        result = get_user("Bearer valid_token")
        
        assert result is None
    
    def test_get_user_token_formatting(self):
        """Test token formatting (adds Bearer prefix if missing)"""
        with patch('user_client.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "123", "username": "test"}
            mock_get.return_value = mock_response
            
            # Test with token without Bearer prefix
            get_user("raw_token")
            
            mock_get.assert_called_once_with(
                "http://user_service:8000/user/me",
                headers={"Authorization": "Bearer raw_token"}
            )