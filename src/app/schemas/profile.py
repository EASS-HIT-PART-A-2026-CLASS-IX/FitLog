"""User profile schemas."""
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


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


class ProteinTargetOut(BaseModel):
    user_id: UUID
    name: str
    weight_kg: float
    goal: Literal["fit", "muscle"]
    protein_g: float
    multiplier_g_per_kg: float
    recommendation: str
