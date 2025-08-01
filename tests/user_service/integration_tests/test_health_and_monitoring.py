import pytest
import httpx
from typing import Dict, Any
import time
import asyncio

class TestHealthAndMonitoring:
    """Service health and monitoring tests"""

    @pytest.mark.asyncio
    async def test_health_check_endpoint(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-032: Service health endpoint check"""
        response = await http_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["status", "service", "timestamp"]
        for field in required_fields:
            assert field in data
        
        assert data["status"] == "healthy"
        assert data["service"] == "user_service"
        assert len(data["timestamp"]) > 0

    @pytest.mark.asyncio
    async def test_health_check_response_time(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-033: Health check response time"""
        start_time = time.time()
        response = await http_client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond faster than 1 second

    @pytest.mark.asyncio
    async def test_multiple_health_checks(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-034: Multiple health checks"""
        for _ in range(5):
            response = await http_client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_service_availability_under_load(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-035: Service availability under load"""
        import asyncio
        
        # Create multiple concurrent requests
        tasks = [
            http_client.get("/health")
            for _ in range(10)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_responses = 0
        for response in responses:
            if not isinstance(response, Exception) and response.status_code == 200:
                successful_responses += 1
        
        # All requests should be successful
        assert successful_responses == len(tasks)

    @pytest.mark.asyncio
    async def test_cors_headers(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-036: CORS headers check"""
        response = await http_client.get("/health")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"

    @pytest.mark.asyncio
    async def test_api_documentation_availability(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-037: API documentation availability"""
        # Check Swagger UI
        docs_response = await http_client.get("/docs")
        assert docs_response.status_code == 200
        
        # Check ReDoc
        redoc_response = await http_client.get("/redoc")
        assert redoc_response.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_schema(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-038: OpenAPI schema validation"""
        response = await http_client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Check basic OpenAPI schema fields
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            assert field in schema
        
        # Check service information
        assert schema["info"]["title"] == "User Service API"
        assert schema["info"]["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_error_handling_consistency(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-039: Error handling consistency"""
        # Test non-existent endpoint
        response = await http_client.get("/nonexistent")
        assert response.status_code == 404
        
        # Check error response structure
        error_data = response.json()
        assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_service_metadata(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-040: Service metadata"""
        response = await http_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check timestamp format
        timestamp = data["timestamp"]
        try:
            from datetime import datetime
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")

    @pytest.mark.asyncio
    async def test_http_methods_support(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-041: HTTP methods support"""
        # GET should work
        get_response = await http_client.get("/health")
        assert get_response.status_code == 200
        
        # POST should not be supported for health
        post_response = await http_client.post("/health")
        assert post_response.status_code == 405  # Method Not Allowed

    @pytest.mark.asyncio
    async def test_content_type_headers(
        self, 
        http_client: httpx.AsyncClient,
        wait_for_service
    ):
        """TC-042: Content-Type headers check"""
        response = await http_client.get("/health")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_service_startup_readiness(
        self, 
        http_client: httpx.AsyncClient
    ):
        """TC-043: Service startup readiness"""
        # This test checks that service is ready to work
        # wait_for_service fixture already checked this, but add explicit check
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = await http_client.get("/health")
                if response.status_code == 200:
                    data = response.json()
                    assert data["status"] == "healthy"
                    return
            except Exception:
                if attempt == max_attempts - 1:
                    pytest.fail("Service is not ready to work")
                await asyncio.sleep(1)