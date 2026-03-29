"""Exercise schemas."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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
