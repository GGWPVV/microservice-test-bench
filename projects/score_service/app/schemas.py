from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RollResponse(BaseModel):
    username: str = Field(..., example="john_doe")
    score: int = Field(..., ge=1, le=1000000, description="Score between 1 and 1,000,000", example=750000)
    timestamp: datetime = Field(..., example="2025-01-01T12:00:00Z")

class LeaderboardEntry(BaseModel):
    username: str = Field(..., example="john_doe")
    score: int = Field(..., example=750000)
    play_date: str = Field(..., example="2025-01-01T12:00:00Z")

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Invalid token")

class AlreadyRolledError(BaseModel):
    detail: str = Field(..., example="You have already rolled.")

class InternalErrorResponse(BaseModel):
    detail: str = Field(..., example="Internal server error")

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", example="healthy")
    service: str = Field(..., example="score_service")
    timestamp: str = Field(..., example="2025-01-01T12:00:00Z")

class CacheResponse(BaseModel):
    detail: str = Field(default="Leaderboard cache cleared", example="Leaderboard cache cleared")