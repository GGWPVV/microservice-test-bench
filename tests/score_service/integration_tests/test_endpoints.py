import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime

def test_roll_endpoint_success(mock_dependencies):
    """Test /roll endpoint with valid token"""
    with patch('main.get_user') as mock_get_user, \
         patch('main.RedisCache.exists', new_callable=AsyncMock) as mock_exists, \
         patch('main.RedisCache.set', new_callable=AsyncMock), \
         patch('main.random.randint') as mock_randint, \
         patch('main.get_db') as mock_get_db:
        
        from main import app
        client = TestClient(app)
        
        # Setup mocks
        mock_get_user.return_value = {"id": str(uuid.uuid4()), "username": "testuser"}
        mock_exists.return_value = False
        mock_randint.return_value = 750000
        
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        response = client.post("/roll", headers={"Authorization": "Bearer valid_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["score"] == 750000

def test_roll_endpoint_already_rolled(mock_dependencies):
    """Test /roll endpoint when user already rolled"""
    with patch('main.get_user') as mock_get_user, \
         patch('main.RedisCache.exists', new_callable=AsyncMock) as mock_exists:
        
        from main import app
        client = TestClient(app)
        
        mock_get_user.return_value = {"id": str(uuid.uuid4()), "username": "testuser"}
        mock_exists.return_value = True
        
        response = client.post("/roll", headers={"Authorization": "Bearer valid_token"})
        
        assert response.status_code == 400
        assert response.json()["detail"] == "You have already rolled."

def test_roll_endpoint_invalid_token(mock_dependencies):
    """Test /roll endpoint with invalid token"""
    with patch('main.get_user') as mock_get_user:
        
        from main import app
        client = TestClient(app)
        
        mock_get_user.return_value = None
        
        response = client.post("/roll", headers={"Authorization": "Bearer invalid_token"})
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid token"

def test_leaderboard_endpoint_cache_hit(mock_dependencies):
    """Test /leaderboard endpoint with cache hit"""
    with patch('main.get_redis', new_callable=AsyncMock) as mock_redis:
        
        from main import app
        client = TestClient(app)
        
        cached_data = '[{"username": "player1", "score": 950000, "play_date": "2025-01-01T12:00:00"}]'
        mock_redis_instance = MagicMock()
        mock_redis_instance.get = AsyncMock(return_value=cached_data)
        mock_redis.return_value = mock_redis_instance
        
        response = client.get("/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["username"] == "player1"

def test_leaderboard_endpoint_cache_miss(mock_dependencies):
    """Test /leaderboard endpoint with cache miss"""
    with patch('main.get_redis', new_callable=AsyncMock) as mock_redis, \
         patch('main.get_db') as mock_get_db:
        
        from main import app
        client = TestClient(app)
        
        mock_redis_instance = MagicMock()
        mock_redis_instance.get = AsyncMock(return_value=None)
        mock_redis_instance.set = AsyncMock()
        mock_redis.return_value = mock_redis_instance
        
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_scores = [
            MagicMock(username="player1", score=950000, created_at=datetime.now()),
            MagicMock(username="player2", score=850000, created_at=datetime.now())
        ]
        mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = mock_scores
        
        response = client.get("/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

def test_clear_cache_endpoint(mock_dependencies):
    """Test /leaderboard/cache DELETE endpoint"""
    with patch('main.get_redis', new_callable=AsyncMock) as mock_redis:
        
        from main import app
        client = TestClient(app)
        
        mock_redis_instance = MagicMock()
        mock_redis_instance.delete = AsyncMock()
        mock_redis.return_value = mock_redis_instance
        
        response = client.delete("/leaderboard/cache")
        
        assert response.status_code == 200
        assert response.json()["detail"] == "Leaderboard cache cleared"

def test_health_endpoint(mock_dependencies):
    """Test /health endpoint"""
    from main import app
    client = TestClient(app)
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "score_service"
    assert "timestamp" in data