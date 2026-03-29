"""User authentication and management schemas."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=100, examples=["SecurePass123!"])
    name: str = Field(..., min_length=1, max_length=100, examples=["Alex"])


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["SecurePass123!"])


class TokenResponse(BaseModel):
    """JWT token response after login."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    expires_in: int = 86400  # 24 hours


class UserResponse(BaseModel):
    """User profile response (without password)."""
    id: UUID
    email: str
    name: str
