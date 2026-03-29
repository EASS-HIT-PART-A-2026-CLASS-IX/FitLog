"""
AI Fitness Assistant router.
POST /ai/chat — sends a context-enriched prompt to Groq AI
and returns a personalised fitness/nutrition reply.
Uses the Groq API (OpenAI-compatible interface).
Groq provides faster inference and much higher free tier quotas than Gemini.
"""
from __future__ import annotations

import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Depends
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.schemas import ChatRequest, ChatResponse
from src.app.db.session import get_session
from src.app.models import FitnessProfile, WorkoutLog, MacroEntry

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# Groq Production Models: https://console.groq.com/docs/models
# llama-3.3-70b-versatile: 280 T/sec, balanced capability and speed
_GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_client() -> OpenAI:
    """Get Groq client configured to use Groq API endpoint."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY not configured. Set it in your .env file.",
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


async def _build_context(profile_id: str, session: AsyncSession) -> str:
    """Build a rich context string from the user's stored data."""
    # Get the profile
    stmt = select(FitnessProfile).where(FitnessProfile.id == profile_id)
    result = await session.execute(stmt)
    profile = result.scalars().first()
    
    if not profile:
        return "No fitness profile found."

    # Get recent workout logs for this user
    stmt = select(WorkoutLog).where(WorkoutLog.owner_id == profile.user_id).order_by(WorkoutLog.created_at.desc()).limit(5)
    result = await session.execute(stmt)
    recent_logs = result.scalars().all()

    # Get recent macro entries for this user
    stmt = select(MacroEntry).where(MacroEntry.owner_id == profile.user_id).order_by(MacroEntry.created_at.desc()).limit(3)
    result = await session.execute(stmt)
    recent_macros = result.scalars().all()

    ctx_lines: list[str] = [
        "=== USER FITNESS PROFILE ===",
        f"Name: {profile.name}",
        f"Age: {profile.age} | Gender: {profile.gender}",
        f"Weight: {profile.weight_kg} kg | Height: {profile.height_cm} cm",
        f"Goal: {profile.goal.upper()} "
        f"({'Maintenance/Recomposition' if profile.goal == 'fit' else 'Hypertrophy/Muscle Building'})",
    ]

    if recent_logs:
        ctx_lines.append("\n=== RECENT WORKOUT LOGS (last 5) ===")
        for log in recent_logs:
            ctx_lines.append(
                f"- {log.log_date}: {log.sets}×{log.reps} @ {log.weight_kg} kg"
                + (f" | {log.notes}" if log.notes else "")
            )

    if recent_macros:
        ctx_lines.append("\n=== RECENT NUTRITION (last 3 days) ===")
        for m in recent_macros:
            ctx_lines.append(
                f"- {m.entry_date}: {m.calories} kcal | "
                f"P:{m.protein_g}g C:{m.carbs_g}g F:{m.fat_g}g"
            )

    return "\n".join(ctx_lines)


_SYSTEM_INSTRUCTION = """You are FitLog AI, a knowledgeable and encouraging senior fitness advisor.
You have access to the user's fitness profile, recent workout logs, and nutrition data.
Provide personalised, evidence-based advice. Be concise, warm, and motivating.
When discussing protein, reference ISSN/ACSM guidelines.
Never recommend unsafe practices. Always remind users to consult a doctor for medical concerns."""


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with your AI Fitness Assistant",
    description=(
        "Send a message to FitLog AI. The assistant has full context of your profile, "
        "recent workouts, and nutrition history to give personalised advice."
    ),
)
async def chat(
    body: ChatRequest,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    # Check if profile exists
    stmt = select(FitnessProfile).where(FitnessProfile.id == body.profile_id)
    result = await session.execute(stmt)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fitness profile not found. Create a profile first at POST /profile.",
        )

    context = await _build_context(body.profile_id, session)
    full_message = f"{context}\n\n=== USER QUESTION ===\n{body.message}"

    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": _SYSTEM_INSTRUCTION
                },
                {
                    "role": "user",
                    "content": full_message
                }
            ],
            temperature=0.7,
            max_tokens=500,
        )
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq API error: {exc}",
        ) from exc
