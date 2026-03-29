"""Macro entry database models."""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


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
    owner: "User" = Relationship(back_populates="macro_entries")
