"""
Authentication router for FitLog.
Handles user registration, login, and JWT token management.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import UserRegister, UserLogin, TokenResponse, UserResponse
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from app.database import get_session
from app.db import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
)
async def register(body: UserRegister, session: AsyncSession = Depends(get_session)):
    """Register a new user."""
    # Check if user already exists
    stmt = select(User).where(User.email == body.email)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please login instead.",
        )
    
    # Hash password
    hashed_password = hash_password(body.password)
    
    # Create new user
    new_user = User(
        email=body.email,
        name=body.name,
        hashed_password=hashed_password,
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    # Create JWT token
    token = create_access_token({"user_id": str(new_user.id), "email": new_user.email})
    
    return TokenResponse(
        access_token=token,
        user_id=str(new_user.id),
        name=new_user.name,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user with email and password, returns JWT token",
)
async def login(body: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login user and return JWT token."""
    # Find user by email
    stmt = select(User).where(User.email == body.email)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Create JWT token
    token = create_access_token({"user_id": str(user.id), "email": user.email})
    
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        name=user.name,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the profile of the logged-in user",
)
async def get_current_user(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_session),
):
    """Get current logged-in user."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    # Extract token from "Bearer <token>"
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("user_id")
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
    )


@router.post("/logout", summary="Logout user")
async def logout():
    """Logout user (client should discard token)."""
    return {"message": "Logged out successfully. Please discard your token."}


# ─────────────────────────────────────────────
# Dependency: Get current authenticated user
# ─────────────────────────────────────────────

async def get_current_user_from_header(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Extract and verify user from JWT token in Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("user_id")
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user
