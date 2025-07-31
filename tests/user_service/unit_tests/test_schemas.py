import pytest
from pydantic import ValidationError
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/user_service/app'))

from schemas import (
    UserCreate, UserLogin, UserCreateResponse, TokenResponse, 
    UserListOut, CurrentUserResponse
)

class TestUserCreate:
    """Test user creation schema"""
    
    def test_valid_user_create(self):
        """Test: valid data should pass validation"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "age": 25,
            "city": "New York"
        }
        
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.age == 25
    
    def test_username_validation(self):
        """Test: username must be 3-50 characters"""
        base_data = {
            "email": "test@example.com",
            "password": "password123", 
            "age": 25,
            "city": "New York"
        }
        
        # Too short
        with pytest.raises(ValidationError):
            UserCreate(username="ab", **base_data)
        
        # Too long
        with pytest.raises(ValidationError):
            UserCreate(username="a" * 51, **base_data)
    
    def test_email_validation(self):
        """Test: email must be valid format"""
        base_data = {
            "username": "testuser",
            "password": "password123",
            "age": 25, 
            "city": "New York"
        }
        
        # Invalid emails (including edge case!)
        invalid_emails = ["@domain.com", "user@", "invalid-email"]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                UserCreate(email=email, **base_data)
    
    def test_age_validation(self):
        """Test: age must be between 13-120 years"""
        base_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "city": "New York"
        }
        
        # Invalid ages
        with pytest.raises(ValidationError):
            UserCreate(age=12, **base_data)  # Too young
        
        with pytest.raises(ValidationError):
            UserCreate(age=121, **base_data)  # Too old

class TestUserLogin:
    """Test login schema"""
    
    def test_valid_login(self):
        """Test: valid login data"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        login = UserLogin(**login_data)
        assert login.email == "test@example.com"
        assert login.password == "password123"

class TestUserCreateResponse:
    """Test user creation response schema"""
    
    def test_valid_response(self):
        """Test: valid user creation response"""
        response = UserCreateResponse(
            message="User created successfully",
            user_name="testuser"
        )
        
        assert response.message == "User created successfully"
        assert response.user_name == "testuser"

class TestTokenResponse:
    """Test JWT token response schema"""
    
    def test_valid_token_response(self):
        """Test: valid token response with default type"""
        response = TokenResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        )
        
        assert response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert response.token_type == "bearer"  # default value

class TestUserListOut:
    """Test user list output schema"""
    
    def test_valid_user_list(self):
        """Test: valid user list item"""
        user = UserListOut(
            username="testuser",
            age=25,
            city="New York"
        )
        
        assert user.username == "testuser"
        assert user.age == 25
        assert user.city == "New York"

class TestCurrentUserResponse:
    """Test current user response schema"""
    
    def test_valid_current_user(self):
        """Test: valid current user response"""
        response = CurrentUserResponse(
            id="fdf3b126-8bec-4ce3-9192-c8a944dee98b",
            username="testuser",
            age=25
        )
        
        assert response.id == "fdf3b126-8bec-4ce3-9192-c8a944dee98b"
        assert response.username == "testuser"
        assert response.age == 25