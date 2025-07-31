import pytest
from datetime import datetime
from pydantic import ValidationError
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/score_service/app'))

from schemas import (
    RollResponse, LeaderboardEntry, ErrorResponse, 
    AlreadyRolledError, InternalErrorResponse, HealthResponse, CacheResponse
)

class TestRollResponse:
    """Test RollResponse schema validation"""
    
    def test_valid_roll_response(self):
        """Test valid roll response creation"""
        data = {
            "username": "testuser",
            "score": 750000,
            "timestamp": datetime.now()
        }
        response = RollResponse(**data)
        
        assert response.username == "testuser"
        assert response.score == 750000
        assert isinstance(response.timestamp, datetime)
    
    def test_score_validation_bounds(self):
        """Test score must be between 1 and 1,000,000"""
        valid_data = {
            "username": "testuser",
            "timestamp": datetime.now()
        }
        
        # Valid scores
        for score in [1, 500000, 1000000]:
            response = RollResponse(score=score, **valid_data)
            assert response.score == score
        
        # Invalid scores should raise ValidationError
        with pytest.raises(ValidationError):
            RollResponse(score=0, **valid_data)
        
        with pytest.raises(ValidationError):
            RollResponse(score=1000001, **valid_data)

class TestLeaderboardEntry:
    """Test LeaderboardEntry schema validation"""
    
    def test_valid_leaderboard_entry(self):
        """Test valid leaderboard entry creation"""
        data = {
            "username": "player1",
            "score": 950000,
            "play_date": "2025-01-01T12:00:00Z"
        }
        entry = LeaderboardEntry(**data)
        
        assert entry.username == "player1"
        assert entry.score == 950000
        assert entry.play_date == "2025-01-01T12:00:00Z"

class TestErrorResponses:
    """Test error response schemas"""
    
    def test_error_response(self):
        """Test ErrorResponse schema"""
        error = ErrorResponse(detail="Invalid token")
        assert error.detail == "Invalid token"
    
    def test_already_rolled_error(self):
        """Test AlreadyRolledError schema"""
        error = AlreadyRolledError(detail="You have already rolled.")
        assert error.detail == "You have already rolled."
    
    def test_internal_error_response(self):
        """Test InternalErrorResponse schema"""
        error = InternalErrorResponse(detail="Internal server error")
        assert error.detail == "Internal server error"

class TestHealthResponse:
    """Test HealthResponse schema validation"""
    
    def test_valid_health_response(self):
        """Test valid health response creation"""
        data = {
            "status": "healthy",
            "service": "score_service",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        response = HealthResponse(**data)
        
        assert response.status == "healthy"
        assert response.service == "score_service"
        assert response.timestamp == "2025-01-01T12:00:00Z"

class TestCacheResponse:
    """Test CacheResponse schema validation"""
    
    def test_valid_cache_response(self):
        """Test valid cache response creation"""
        response = CacheResponse(detail="Leaderboard cache cleared")
        assert response.detail == "Leaderboard cache cleared"