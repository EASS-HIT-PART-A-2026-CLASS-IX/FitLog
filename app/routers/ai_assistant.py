"""
AI Fitness Assistant router.
POST /ai/chat — sends a context-enriched prompt to Google Gemini 2.0 Flash
and returns a personalised fitness/nutrition reply.
Uses the official google-genai SDK (google.genai).
"""
from __future__ import annotations

import os
from uuid import UUID

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from google import genai
from google.genai import types

from app.models import ChatRequest, ChatResponse
from app.repository import macros_repo, profiles_repo, workout_logs_repo

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

_GEMINI_MODEL = "gemini-2.0-flash"


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY not configured. Set it in your .env file.",
        )
    return genai.Client(api_key=api_key)


def _build_context(user_id: UUID) -> str:
    """Build a rich context string from the user's stored data."""
    profile = profiles_repo.get(user_id)
    if not profile:
        return "No user profile found."

    logs = workout_logs_repo.list()
    recent_logs = logs[-5:]  # last 5 logs

    macros = macros_repo.list()
    recent_macros = macros[-3:]  # last 3 days

    ctx_lines: list[str] = [
        "=== USER FITNESS PROFILE ===",
        f"Name: {profile['name']}",
        f"Age: {profile['age']} | Gender: {profile['gender']}",
        f"Weight: {profile['weight_kg']} kg | Height: {profile['height_cm']} cm",
        f"Goal: {profile['goal'].upper()} "
        f"({'Maintenance/Recomposition' if profile['goal'] == 'fit' else 'Hypertrophy/Muscle Building'})",
    ]

    if recent_logs:
        ctx_lines.append("\n=== RECENT WORKOUT LOGS (last 5) ===")
        for log in recent_logs:
            ctx_lines.append(
                f"- {log['log_date']}: {log['sets']}×{log['reps']} @ {log['weight_kg']} kg"
                + (f" | {log['notes']}" if log.get("notes") else "")
            )

    if recent_macros:
        ctx_lines.append("\n=== RECENT NUTRITION (last 3 days) ===")
        for m in recent_macros:
            ctx_lines.append(
                f"- {m['entry_date']}: {m['calories']} kcal | "
                f"P:{m['protein_g']}g C:{m['carbs_g']}g F:{m['fat_g']}g"
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
def chat(body: ChatRequest) -> ChatResponse:
    profile = profiles_repo.get(body.user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Create a profile first at POST /profile.",
        )

    context = _build_context(body.user_id)
    full_message = f"{context}\n\n=== USER QUESTION ===\n{body.message}"

    client = _get_client()
    try:
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=full_message,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        return ChatResponse(reply=response.text)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API error: {exc}",
        ) from exc
