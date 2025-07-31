import pytest
from datetime import datetime
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/analytics_service/app'))

from schemas import HealthResponse, ErrorResponse

class TestHealthResponse:
    """Test HealthResponse schema validation"""
    
    def test_valid_health_response(self):
        """Test valid health response creation"""
        data = {
            "status": "healthy",
            "service": "analytics_service",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        response = HealthResponse(**data)
        
        assert response.status == "healthy"
        assert response.service == "analytics_service"
        assert response.timestamp == "2025-01-01T12:00:00Z"
    
    def test_health_response_defaults(self):
        """Test health response with default status"""
        data = {
            "service": "analytics_service",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        response = HealthResponse(**data)
        
        assert response.status == "healthy"  # Default value
        assert response.service == "analytics_service"

class TestErrorResponse:
    """Test ErrorResponse schema validation"""
    
    def test_valid_error_response(self):
        """Test valid error response creation"""
        error = ErrorResponse(detail="Internal server error")
        
        assert error.detail == "Internal server error"
    
    def test_error_response_custom_message(self):
        """Test error response with custom message"""
        custom_message = "MongoDB connection failed"
        error = ErrorResponse(detail=custom_message)
        
        assert error.detail == custom_message