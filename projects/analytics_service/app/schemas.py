from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", example="healthy")
    service: str = Field(..., example="analytics_service")
    timestamp: str = Field(..., example="2025-01-01T12:00:00Z")

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Internal server error")