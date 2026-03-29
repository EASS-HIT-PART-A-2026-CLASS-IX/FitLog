"""Workout log database models."""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


class WorkoutLogBase(SQLModel):
    """Base fields for workout logs."""
    exercise_id: str = Field(foreign_key="exercises.id")
    log_date: str  # ISO format date
    sets: int = Field(ge=1, le=100)
    reps: int = Field(ge=1, le=1000)
    weight_kg: float = Field(ge=0, le=1000)
    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkoutLog(WorkoutLogBase, table=True):
    """Workout log model stored in database."""
    __tablename__ = "workout_logs"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    owner_id: str = Field(foreign_key="users.id")
    
    # Relationships
    owner: "User" = Relationship(back_populates="workout_logs")
    exercise: Optional["Exercise"] = Relationship(back_populates="workout_logs")
