import pytest
import httpx
from typing import Dict, Any

class TestUserRegistration:
    """User registration tests"""

    @pytest.mark.asyncio
    async def test_successful_user_registration(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-001: Successful user registration"""
        response = await http_client.post("/users", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user_name"] == test_user_data["username"]

    @pytest.mark.asyncio
    async def test_duplicate_username_registration(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-002: Registration with duplicate username"""
        duplicate_user = created_user.copy()
        duplicate_user["email"] = "different@example.com"
        
        response = await http_client.post("/users", json=duplicate_user)
        assert response.status_code == 409
        
        error_data = response.json()
        assert error_data["detail"] == "Username already exists"

    @pytest.mark.asyncio
    async def test_duplicate_email_registration(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-003: Registration with duplicate email"""
        import time
        duplicate_user = created_user.copy()
        duplicate_user["username"] = f"different_username_{int(time.time())}"
        
        response = await http_client.post("/users", json=duplicate_user)
        assert response.status_code == 409
        
        error_data = response.json()
        assert error_data["detail"] in ["Email already exists", "Username already exists"]

    @pytest.mark.asyncio
    async def test_invalid_email_format(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-004: Registration with invalid email"""
        test_user_data["email"] = "invalid-email"
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        assert any("email" in str(error["loc"]) for error in error_data["detail"])

    @pytest.mark.asyncio
    async def test_short_password(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-005: Registration with short password"""
        test_user_data["password"] = "123"
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_invalid_age_too_young(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-006: Registration with age less than 13"""
        test_user_data["age"] = 12
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_age_too_old(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-007: Registration with age greater than 120"""
        test_user_data["age"] = 121
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_fields(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-008: Registration without required fields"""
        incomplete_data = {"username": "testuser"}
        
        response = await http_client.post("/users", json=incomplete_data)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        required_fields = ["email", "password", "age", "city"]
        error_fields = [error["loc"][-1] for error in error_data["detail"]]
        
        for field in required_fields:
            assert field in error_fields

    @pytest.mark.asyncio
    async def test_empty_username(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-009: Registration with empty username"""
        test_user_data["username"] = ""
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_long_username(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-010: Registration with very long username"""
        test_user_data["username"] = "a" * 51  # More than 50 character limit
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_boundary_age_values(
        self, 
        http_client: httpx.AsyncClient, 
        test_user_data: Dict[str, Any],
        wait_for_service
    ):
        """TC-011: Boundary age values"""
        # Minimum age
        test_user_data["age"] = 13
        test_user_data["username"] = f"{test_user_data['username']}_min"
        test_user_data["email"] = f"min_{test_user_data['email']}"
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 201
        
        # Maximum age
        test_user_data["age"] = 120
        test_user_data["username"] = f"{test_user_data['username']}_max"
        test_user_data["email"] = f"max_{test_user_data['email']}"
        
        response = await http_client.post("/users", json=test_user_data)
        assert response.status_code == 201