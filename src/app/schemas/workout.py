"""Workout log schemas."""
from typing import Optional
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


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


class WorkoutSummaryOut(BaseModel):
    user_id: UUID
    name: str
    total_workouts: int
    total_volume_kg: float
    most_worked_muscle_group: str
    workouts_per_week: int
    recommendation: str
