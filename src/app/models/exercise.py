"""Exercise database models."""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


class ExerciseBase(SQLModel):
    """Base fields for exercises."""
    name: str = Field(max_length=100, index=True)
    category: str = Field(max_length=50)  # "strength", "cardio", "flexibility"
    muscle_group: str = Field(max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Exercise(ExerciseBase, table=True):
    """Exercise model stored in database."""
    __tablename__ = "exercises"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    owner_id: str = Field(foreign_key="users.id")
    
    # Relationships
    owner: "User" = Relationship(back_populates="exercises")
    workout_logs: list["WorkoutLog"] = Relationship(back_populates="exercise")
