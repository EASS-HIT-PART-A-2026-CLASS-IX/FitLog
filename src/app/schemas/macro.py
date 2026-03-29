"""Macro entry and nutrition schemas."""
from typing import Optional
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


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


class FoodAnalysisRequest(BaseModel):
    """Request to analyze food description and calculate nutrition."""
    food_description: str = Field(..., min_length=3, max_length=500, examples=["2 eggs, bacon, and toast with butter"])


class NutritionAnalysisResponse(BaseModel):
    """Response with calculated nutrition from AI analysis."""
    food_description: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    analysis: str
