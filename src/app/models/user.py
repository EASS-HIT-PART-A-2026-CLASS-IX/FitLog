"""User database models."""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """User account model stored in database."""
    __tablename__ = "users"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(max_length=100, unique=True, index=True)
    hashed_password: str
    name: str = Field(max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    fitness_profiles: list["FitnessProfile"] = Relationship(back_populates="owner")
    exercises: list["Exercise"] = Relationship(back_populates="owner")
    workout_logs: list["WorkoutLog"] = Relationship(back_populates="owner")
    macro_entries: list["MacroEntry"] = Relationship(back_populates="owner")


class FitnessProfileBase(SQLModel):
    """Base fields for fitness profiles (per-user training goals)."""
    name: str = Field(max_length=100, index=True)
    weight_kg: float = Field(gt=0, le=500)
    height_cm: float = Field(gt=0, le=300)
    age: int = Field(ge=10, le=120)
    gender: str = Field(max_length=20)  # "male", "female", "other"
    goal: str = Field(max_length=50)  # "fit", "muscle"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FitnessProfile(FitnessProfileBase, table=True):
    """Fitness profile model - user's training goal and metrics."""
    __tablename__ = "fitness_profiles"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    
    # Relationships
    owner: User = Relationship(back_populates="fitness_profiles")


# Keep UserProfile as an alias for backward compatibility
UserProfile = User
