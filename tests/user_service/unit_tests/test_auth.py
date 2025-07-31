import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/user_service/app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared'))

# Mock dependencies before importing
with patch('sys.modules', {'kafka_client': MagicMock(), 'logger_config': MagicMock()}):
    from auth import create_jwt, SECRET_KEY, ALGORITHM


class TestAuth:
    """Test JWT authentication functionality"""
    
    def test_create_jwt_success(self):
        """Test successful JWT token creation"""
        user_id = "test-user-id"
        
        token = create_jwt(user_id)
        
        # Verify token is created
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token content
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == user_id
        assert "exp" in payload
    
    def test_create_jwt_with_uuid(self):
        """Test JWT creation with UUID user_id"""
        import uuid
        user_id = uuid.uuid4()
        
        token = create_jwt(user_id)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload["sub"] == str(user_id)
    
    def test_create_jwt_expiration(self):
        """Test JWT token expiration time"""
        user_id = "test-user-id"
        
        token = create_jwt(user_id)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Token should expire in approximately 60 minutes
        time_diff = exp_time - now
        assert 59 <= time_diff.total_seconds() / 60 <= 61
    
    @patch('auth.jwt.encode')
    def test_create_jwt_encoding_error(self, mock_encode):
        """Test JWT creation with encoding error"""
        mock_encode.side_effect = Exception("Encoding failed")
        
        with pytest.raises(Exception, match="Encoding failed"):
            create_jwt("test-user-id")
    
    def test_create_jwt_none_user_id(self):
        """Test JWT creation with None user_id"""
        token = create_jwt(None)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload["sub"] == "None"