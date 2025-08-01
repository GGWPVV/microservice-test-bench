import pytest
import httpx
from typing import Dict, Any, List

class TestUserManagement:
    """User management tests"""

    @pytest.mark.asyncio
    async def test_get_all_users_empty_list(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-024: Get all users (may be empty)"""
        response = await http_client.get("/users")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_all_users_with_data(
        self, 
        http_client: httpx.AsyncClient, 
        multiple_users_data: List[Dict[str, Any]],
        wait_for_service
    ):
        """TC-025: Get all users with data"""
        # Create multiple users
        created_usernames = []
        for user_data in multiple_users_data:
            response = await http_client.post("/users", json=user_data)
            assert response.status_code == 201
            created_usernames.append(user_data["username"])
        
        # Get all users list
        response = await http_client.get("/users")
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= len(multiple_users_data)
        
        # Check that created users are present in the list
        usernames_in_response = [user["username"] for user in users]
        for username in created_usernames:
            assert username in usernames_in_response

    @pytest.mark.asyncio
    async def test_user_list_response_structure(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-026: User list response structure validation"""
        response = await http_client.get("/users")
        assert response.status_code == 200
        
        users = response.json()
        if users:  # If users exist
            user = users[0]
            required_fields = ["username", "age", "city"]
            for field in required_fields:
                assert field in user
            
            # Check that sensitive data is not returned
            sensitive_fields = ["password", "hashed_password", "email"]
            for field in sensitive_fields:
                assert field not in user

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, 
        http_client: httpx.AsyncClient, 
        auth_headers: Dict[str, str],
        wait_for_service
    ):
        """TC-027: Get user by ID (via /user/me)"""
        response = await http_client.get("/user/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "age" in data

    @pytest.mark.asyncio
    async def test_user_data_consistency(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-028: User data consistency check"""
        # Create user
        create_response = await http_client.post("/users", json=test_user_data)
        assert create_response.status_code == 201
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await http_client.post("/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get user data
        headers = {"Authorization": f"Bearer {token}"}
        user_response = await http_client.get("/user/me", headers=headers)
        assert user_response.status_code == 200
        
        user_data = user_response.json()
        assert user_data["username"] == test_user_data["username"]
        assert user_data["age"] == test_user_data["age"]

    @pytest.mark.asyncio
    async def test_concurrent_user_creation(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-029: Concurrent user creation"""
        import asyncio
        import time
        
        timestamp = int(time.time())
        users_data = [
            {
                "username": f"concurrent_user_{i}_{timestamp}",
                "email": f"concurrent_{i}_{timestamp}@example.com",
                "password": "password123",
                "age": 20 + i,
                "city": f"City{i}"
            }
            for i in range(5)
        ]
        
        # Create users concurrently
        tasks = [
            http_client.post("/users", json=user_data)
            for user_data in users_data
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that all requests are successful
        successful_responses = 0
        for response in responses:
            if not isinstance(response, Exception) and response.status_code == 201:
                successful_responses += 1
        
        assert successful_responses == len(users_data)

    @pytest.mark.asyncio
    async def test_user_list_pagination_behavior(
        self, 
        http_client: httpx.AsyncClient, 
        multiple_users_data: List[Dict[str, Any]],
        wait_for_service
    ):
        """TC-030: User list behavior with large data sets"""
        # Create users
        for user_data in multiple_users_data:
            response = await http_client.post("/users", json=user_data)
            assert response.status_code == 201
        
        # Get list
        response = await http_client.get("/users")
        assert response.status_code == 200
        
        users = response.json()
        assert len(users) >= len(multiple_users_data)
        
        # Check that response is not too large (basic performance check)
        import sys
        response_size = sys.getsizeof(response.content)
        assert response_size < 1024 * 1024  # Less than 1MB

    @pytest.mark.asyncio
    async def test_user_creation_with_special_characters(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-031: User creation with special characters"""
        import time
        timestamp = int(time.time())
        
        special_user_data = {
            "username": f"user_with_underscore_{timestamp}",
            "email": f"test.email+tag_{timestamp}@example.com",
            "password": "password!@#123",
            "age": 25,
            "city": "New York"
        }
        
        response = await http_client.post("/users", json=special_user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["user_name"] == special_user_data["username"]