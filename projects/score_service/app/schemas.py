from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RollResponse(BaseModel):
    username: str
    score: int = Field(..., ge=1, le=1000000, description="Score between 1 and 1,000,000")
    timestamp: datetime

class LeaderboardEntry(BaseModel):
    username: str
    score: int
    play_date: str

class LeaderboardResponse(BaseModel):
    leaderboard: list[LeaderboardEntry]
    total_players: int

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str
    timestamp: datetime

class CacheResponse(BaseModel):
    detail: str = "Leaderboard cache cleared"