import pytest
import httpx
from typing import Dict, Any
import jwt
import time

class TestAuthentication:
    """User authentication tests"""

    @pytest.mark.asyncio
    async def test_successful_login(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-012: Successful login"""
        login_data = {
            "email": created_user["email"],
            "password": created_user["password"]
        }
        
        response = await http_client.post("/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_invalid_email(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-013: Login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await http_client.post("/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_login_invalid_password(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-014: Login with wrong password"""
        login_data = {
            "email": created_user["email"],
            "password": "wrongpassword"
        }
        
        response = await http_client.post("/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_login_missing_email(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-015: Login without email"""
        login_data = {"password": "password123"}
        
        response = await http_client.post("/login", json=login_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_password(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-016: Login without password"""
        login_data = {"email": "test@example.com"}
        
        response = await http_client.post("/login", json=login_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-017: Login with invalid email format"""
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = await http_client.post("/login", json=login_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_jwt_token_structure(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-018: JWT token structure validation"""
        login_data = {
            "email": created_user["email"],
            "password": created_user["password"]
        }
        
        response = await http_client.post("/login", json=login_data)
        assert response.status_code == 200
        
        token = response.json()["access_token"]
        
        # Check that token can be decoded (without signature verification)
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            assert "sub" in decoded  # user_id
            assert "exp" in decoded  # expiration time
        except jwt.InvalidTokenError:
            pytest.fail("Token has invalid structure")

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(
        self, 
        http_client: httpx.AsyncClient, 
        auth_headers: Dict[str, str],
        wait_for_service
    ):
        """TC-019: Get current user with valid token"""
        response = await http_client.get("/user/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "age" in data

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-020: Get current user without token"""
        response = await http_client.get("/user/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-021: Get current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await http_client.get("/user/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid token"

    @pytest.mark.asyncio
    async def test_get_current_user_with_malformed_header(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-022: Get current user with malformed header"""
        headers = {"Authorization": "InvalidFormat token"}
        response = await http_client.get("/user/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_expiration_handling(
        self, 
        http_client: httpx.AsyncClient, 
        created_user: Dict[str, Any],
        wait_for_service
    ):
        """TC-023: Expired token handling (simulation)"""
        # Create token with short lifetime
        import jwt
        from datetime import datetime, timedelta
        
        payload = {
            "sub": "test-user-id",
            "exp": datetime.utcnow() - timedelta(seconds=1)  # Already expired
        }
        expired_token = jwt.encode(payload, "your-secret-key", algorithm="HS256")
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await http_client.get("/user/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid token"