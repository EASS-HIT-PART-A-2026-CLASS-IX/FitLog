"""AI chat and messaging schemas."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    profile_id: str  # Profile ID (not user ID) - FitnessProfile.id
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
