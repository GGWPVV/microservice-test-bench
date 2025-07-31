import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

def test_discount_endpoint_success(mock_dependencies):
    """Test /discount endpoint with valid user"""
    with patch('main.decode_token') as mock_decode, \
         patch('main.get_user_info') as mock_user_info, \
         patch('main.is_user_in_top') as mock_is_top, \
         patch('main.RedisCache.get', new_callable=AsyncMock) as mock_redis_get, \
         patch('main.RedisCache.set', new_callable=AsyncMock):
        
        from main import app
        client = TestClient(app)
        
        # Setup mocks
        mock_decode.return_value = "user123"
        mock_user_info.return_value = {"id": "user123", "username": "testuser", "age": 45}
        mock_is_top.return_value = True
        mock_redis_get.return_value = None  # No cache
        
        response = client.post("/discount", headers={"Authorization": "Bearer valid_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["discount"] == 0.2  # 0.1 for age + 0.1 for top

def test_discount_endpoint_cached(mock_dependencies):
    """Test /discount endpoint with cached result"""
    with patch('main.decode_token') as mock_decode, \
         patch('main.get_user_info') as mock_user_info, \
         patch('main.RedisCache.get', new_callable=AsyncMock) as mock_redis_get:
        
        from main import app
        client = TestClient(app)
        
        mock_decode.return_value = "user123"
        mock_user_info.return_value = {"id": "user123", "username": "testuser", "age": 25}
        mock_redis_get.return_value = "0.1"  # Cached discount
        
        response = client.post("/discount", headers={"Authorization": "Bearer valid_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["discount"] == 0.1

def test_discount_endpoint_invalid_token(mock_dependencies):
    """Test /discount endpoint with invalid token"""
    with patch('main.decode_token') as mock_decode:
        
        from main import app
        client = TestClient(app)
        
        mock_decode.return_value = None
        
        response = client.post("/discount", headers={"Authorization": "Bearer invalid_token"})
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

def test_discount_endpoint_invalid_user_data(mock_dependencies):
    """Test /discount endpoint with invalid user data"""
    with patch('main.decode_token') as mock_decode, \
         patch('main.get_user_info') as mock_user_info:
        
        from main import app
        client = TestClient(app)
        
        mock_decode.return_value = "user123"
        mock_user_info.return_value = {"id": "user123", "username": "testuser"}  # Missing age
        
        response = client.post("/discount", headers={"Authorization": "Bearer valid_token"})
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid user data"

def test_discount_endpoint_young_user_not_in_top(mock_dependencies):
    """Test /discount endpoint for young user not in top"""
    with patch('main.decode_token') as mock_decode, \
         patch('main.get_user_info') as mock_user_info, \
         patch('main.is_user_in_top') as mock_is_top, \
         patch('main.RedisCache.get', new_callable=AsyncMock) as mock_redis_get, \
         patch('main.RedisCache.set', new_callable=AsyncMock):
        
        from main import app
        client = TestClient(app)
        
        mock_decode.return_value = "user123"
        mock_user_info.return_value = {"id": "user123", "username": "testuser", "age": 25}
        mock_is_top.return_value = False
        mock_redis_get.return_value = None
        
        response = client.post("/discount", headers={"Authorization": "Bearer valid_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["discount"] == 0.0  # No discount

def test_health_endpoint(mock_dependencies):
    """Test /health endpoint"""
    from main import app
    client = TestClient(app)
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "discount_service"
    assert "timestamp" in data