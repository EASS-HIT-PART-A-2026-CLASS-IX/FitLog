"""
FitLog – Pydantic models for all domain resources.
"""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


# ─────────────────────────────────────────────
#  Authentication & User Management
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
#  Exercise
# ─────────────────────────────────────────────

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Barbell Squat"])
    category: str = Field(..., examples=["strength", "cardio", "flexibility"])
    muscle_group: str = Field(..., examples=["legs", "chest", "back", "shoulders", "arms", "core", "full-body"])
    description: Optional[str] = Field(None, max_length=500)


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    muscle_group: Optional[str] = None
    description: Optional[str] = None


class ExerciseOut(ExerciseBase):
    id: UUID


# ─────────────────────────────────────────────
#  Workout Log
# ─────────────────────────────────────────────

class WorkoutLogBase(BaseModel):
    exercise_id: UUID
    log_date: date = Field(..., examples=["2026-03-25"])
    sets: int = Field(..., ge=1, le=100)
    reps: int = Field(..., ge=1, le=1000)
    weight_kg: float = Field(..., ge=0, le=1000, examples=[80.0])
    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    notes: Optional[str] = Field(None, max_length=500)


class WorkoutLogCreate(WorkoutLogBase):
    pass


class WorkoutLogUpdate(BaseModel):
    exercise_id: Optional[UUID] = None
    log_date: Optional[date] = None
    sets: Optional[int] = Field(None, ge=1, le=100)
    reps: Optional[int] = Field(None, ge=1, le=1000)
    weight_kg: Optional[float] = Field(None, ge=0, le=1000)
    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    notes: Optional[str] = None


class WorkoutLogOut(WorkoutLogBase):
    id: UUID


# ─────────────────────────────────────────────
#  Macro Entry (daily nutrition)
# ─────────────────────────────────────────────

class MacroEntryBase(BaseModel):
    entry_date: date = Field(..., examples=["2026-03-25"])
    calories: float = Field(..., ge=0, le=20000, examples=[2200.0])
    protein_g: float = Field(..., ge=0, le=1000, examples=[180.0])
    carbs_g: float = Field(..., ge=0, le=2000, examples=[250.0])
    fat_g: float = Field(..., ge=0, le=1000, examples=[70.0])
    notes: Optional[str] = Field(None, max_length=500)


class MacroEntryCreate(MacroEntryBase):
    pass


class MacroEntryUpdate(BaseModel):
    entry_date: Optional[date] = None
    calories: Optional[float] = Field(None, ge=0, le=20000)
    protein_g: Optional[float] = Field(None, ge=0, le=1000)
    carbs_g: Optional[float] = Field(None, ge=0, le=2000)
    fat_g: Optional[float] = Field(None, ge=0, le=1000)
    notes: Optional[str] = None


class MacroEntryOut(MacroEntryBase):
    id: UUID


# ─────────────────────────────────────────────
#  User Profile
# ─────────────────────────────────────────────

class UserProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Alex"])
    weight_kg: float = Field(..., gt=0, le=500, examples=[80.0])
    height_cm: float = Field(..., gt=0, le=300, examples=[175.0])
    age: int = Field(..., ge=10, le=120, examples=[28])
    gender: Literal["male", "female", "other"] = Field(..., examples=["male"])
    goal: Literal["fit", "muscle"] = Field(..., examples=["muscle"])


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[Literal["male", "female", "other"]] = None
    goal: Optional[Literal["fit", "muscle"]] = None


class UserProfileOut(UserProfileBase):
    id: UUID


# ─────────────────────────────────────────────
#  Protein Target response
# ─────────────────────────────────────────────

class ProteinTargetOut(BaseModel):
    user_id: UUID
    name: str
    weight_kg: float
    goal: Literal["fit", "muscle"]
    protein_g: float
    multiplier_g_per_kg: float
    recommendation: str


# ─────────────────────────────────────────────
#  AI Assistant
# ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: UUID
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str


# ─────────────────────────────────────────────
#  Workout Summary & Analytics (EX3 Enhancement)
# ─────────────────────────────────────────────

class WorkoutSummaryOut(BaseModel):
    user_id: UUID
    name: str
    total_workouts: int
    total_volume_kg: float
    most_worked_muscle_group: str
    workouts_per_week: int
    recommendation: str

