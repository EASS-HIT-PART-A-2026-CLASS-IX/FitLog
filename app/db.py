"""
SQLModel definitions for FitLog database persistence.
This replaces the in-memory repository with SQLite/PostgreSQL backed storage.
"""
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
    owner: User = Relationship(back_populates="exercises")
    workout_logs: list["WorkoutLog"] = Relationship(back_populates="exercise")


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
    owner: User = Relationship(back_populates="workout_logs")
    exercise: Optional[Exercise] = Relationship(back_populates="workout_logs")


class MacroEntryBase(SQLModel):
    """Base fields for macro entries."""
    entry_date: str  # ISO format date
    calories: float = Field(ge=0, le=20000)
    protein_g: float = Field(ge=0, le=1000)
    carbs_g: float = Field(ge=0, le=2000)
    fat_g: float = Field(ge=0, le=1000)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MacroEntry(MacroEntryBase, table=True):
    """Macro entry model stored in database."""
    __tablename__ = "macro_entries"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    owner_id: str = Field(foreign_key="users.id")
    
    # Relationships
    owner: User = Relationship(back_populates="macro_entries")
