from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DiscountResponse(BaseModel):
    username: str = Field(..., example="john_doe")
    discount: float = Field(..., ge=0.0, le=1.0, description="Discount percentage (0.0 to 1.0)", example=0.2)

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Invalid token")

class InvalidUserDataError(BaseModel):
    detail: str = Field(..., example="Invalid user data")

class InternalErrorResponse(BaseModel):
    detail: str = Field(..., example="Internal server error")

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", example="healthy")
    service: str = Field(..., example="discount_service")
    timestamp: str = Field(..., example="2025-01-01T12:00:00Z")