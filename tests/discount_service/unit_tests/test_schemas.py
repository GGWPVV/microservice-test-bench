import pytest
from pydantic import ValidationError
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../projects/discount_service/app'))

from schemas import (
    DiscountResponse, ErrorResponse, InvalidUserDataError,
    InternalErrorResponse, HealthResponse
)

class TestDiscountResponse:
    """Test DiscountResponse schema validation"""
    
    def test_valid_discount_response(self):
        """Test valid discount response creation"""
        data = {
            "username": "testuser",
            "discount": 0.2
        }
        response = DiscountResponse(**data)
        
        assert response.username == "testuser"
        assert response.discount == 0.2

    def test_discount_validation_bounds(self):
        """Test discount must be between 0.0 and 1.0"""
        valid_data = {"username": "testuser"}
        
        # Valid discounts
        for discount in [0.0, 0.5, 1.0]:
            response = DiscountResponse(discount=discount, **valid_data)
            assert response.discount == discount
        
        # Invalid discounts should raise ValidationError
        with pytest.raises(ValidationError):
            DiscountResponse(discount=-0.1, **valid_data)
        
        with pytest.raises(ValidationError):
            DiscountResponse(discount=1.1, **valid_data)

class TestErrorResponses:
    """Test error response schemas"""
    
    def test_error_response(self):
        """Test ErrorResponse schema"""
        error = ErrorResponse(detail="Invalid token")
        assert error.detail == "Invalid token"
    
    def test_invalid_user_data_error(self):
        """Test InvalidUserDataError schema"""
        error = InvalidUserDataError(detail="Invalid user data")
        assert error.detail == "Invalid user data"
    
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
            "service": "discount_service",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        response = HealthResponse(**data)
        
        assert response.status == "healthy"
        assert response.service == "discount_service"
        assert response.timestamp == "2025-01-01T12:00:00Z"
    
    def test_health_response_defaults(self):
        """Test health response with default status"""
        data = {
            "service": "discount_service",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        response = HealthResponse(**data)
        
        assert response.status == "healthy"  # Default value