from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters", example="john_doe")
    email: EmailStr = Field(..., description="Valid email address", example="john@example.com")
    password: str = Field(..., min_length=6,max_length=50, description="Password must be 6-50 characters", example="password123")
    age: int = Field(..., ge=13, le=120, description="Age must be between 13 and 120", example=25)
    city: str = Field(..., min_length=1, max_length=100, description="City name", example="New York")

class UserCreateResponse(BaseModel):
    message: str = Field(..., example="User created successfully")
    user_name: str = Field(..., example="john_doe")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email", example="john@example.com")
    password: str = Field(..., min_length=6, description="Password", example="password123")

class TokenResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", example="bearer")

class UserListOut(BaseModel):
    username: str = Field(..., example="john_doe")
    email: EmailStr = Field(..., example="john@example.com")
    age: int = Field(..., example=25)
    city: str = Field(..., example="New York")

    class Config:
        from_attributes = True

class CurrentUserResponse(BaseModel):
    id: str = Field(..., example="fdf3b126-8bec-4ce3-9192-c8a944dee98b")
    username: str = Field(..., example="john_doe")
    age: int = Field(..., example=25)

class ValidationErrorDetail(BaseModel):
    loc: List[Any] = Field(..., example=["body", "email"])
    msg: str = Field(..., example="field required")
    type: str = Field(..., example="value_error.missing")

class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorDetail]

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Invalid credentials")

class InternalErrorResponse(BaseModel):
    detail: str = Field(..., example="Internal server error")

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", example="healthy")
    service: str = Field(..., example="user_service")
    timestamp: str = Field(..., example="2025-01-01T00:00:00Z")