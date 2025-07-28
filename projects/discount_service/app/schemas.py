from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DiscountResponse(BaseModel):
    username: str
    discount: float = Field(..., ge=0.0, le=1.0, description="Discount percentage (0.0 to 1.0)")
    age_discount: bool = Field(description="Applied age discount (40+)")
    leaderboard_discount: bool = Field(description="Applied leaderboard discount")

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str
    timestamp: datetime