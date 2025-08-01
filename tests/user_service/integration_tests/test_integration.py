import pytest
import requests
import time
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class TestUserServiceIntegration:
    """Full integration tests for user service"""
    
    def setup_method(self):
        """Setup for each test"""
        self.test_user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com", 
            "password": "password123",
            "city": "Test City",
            "age": 25
        }
        self.access_token = None
    
    def test_full_user_flow(self):
        """Test complete user registration -> login -> get profile flow"""
        
        # 1. Create user
        response = requests.post(f"{BASE_URL}/users", json=self.test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user_name"] == self.test_user_data["username"]
        
        # 2. Login user
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        self.access_token = data["access_token"]
        
        # 3. Get current user profile
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/user/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == self.test_user_data["username"]
        assert data["age"] == self.test_user_data["age"]
        assert "id" in data
        
        # 4. Get all users
        response = requests.get(f"{BASE_URL}/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
        
        # Verify our user is in the list
        usernames = [user["username"] for user in users]
        assert self.test_user_data["username"] in usernames
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/login", json=invalid_login)
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid credentials"
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        response = requests.get(f"{BASE_URL}/user/me")
        assert response.status_code == 401
    
    def test_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{BASE_URL}/user/me", headers=headers)
        assert response.status_code == 401
    
    def test_user_validation_errors(self):
        """Test user creation with validation errors"""
        
        # Test missing required fields
        invalid_user = {"username": "test"}
        response = requests.post(f"{BASE_URL}/users", json=invalid_user)
        assert response.status_code == 422
        
        # Test invalid email
        invalid_user = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123",
            "city": "Test City", 
            "age": 25
        }
        response = requests.post(f"{BASE_URL}/users", json=invalid_user)
        assert response.status_code == 422
        
        # Test password too short
        invalid_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",  # Too short
            "city": "Test City",
            "age": 25
        }
        response = requests.post(f"{BASE_URL}/users", json=invalid_user)
        assert response.status_code == 422
        
        # Test age too young
        invalid_user = {
            "username": "testuser", 
            "email": "test@example.com",
            "password": "password123",
            "city": "Test City",
            "age": 12  # Too young
        }
        response = requests.post(f"{BASE_URL}/users", json=invalid_user)
        assert response.status_code == 422
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "user_service"
        assert "timestamp" in data
    
    def test_duplicate_user_creation(self):
        """Test creating user with duplicate email"""
        # Create first user
        response = requests.post(f"{BASE_URL}/users", json=self.test_user_data)
        assert response.status_code == 201
        
        # Try to create user with same email
        duplicate_user = self.test_user_data.copy()
        duplicate_user["username"] = "different_username"
        response = requests.post(f"{BASE_URL}/users", json=duplicate_user)
        # Should fail due to unique email constraint
        assert response.status_code == 409

if __name__ == "__main__":
    pytest.main([__file__, "-v"])