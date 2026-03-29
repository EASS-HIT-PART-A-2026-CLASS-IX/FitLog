"""
FitLog FastAPI application entry point.
Run with: uv run uvicorn src.app.main:app --reload
Docs at:  http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.v1 import (
    routes_ai_assistant,
    routes_exercises,
    routes_macros,
    routes_profile,
    routes_workout_logs,
    routes_auth,
)
from src.app.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    await create_db_and_tables()
    yield


app = FastAPI(
    title="FitLog API",
    description=(
        "🏋️ **FitLog** – Your personal fitness & nutrition tracking backend.\n\n"
        "Track exercises, log workouts, manage daily macros, calculate protein targets, "
        "and get AI-powered fitness advice from Groq."
    ),
    version="0.1.0",
    contact={"name": "FitLog", "email": "fitlog@example.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# Allow frontend (Streamlit) to call this API from localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*", "http://192.168.68.100:*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(routes_auth.router)  # Auth must be first (no token required)
app.include_router(routes_exercises.router)
app.include_router(routes_workout_logs.router)
app.include_router(routes_macros.router)
app.include_router(routes_profile.router)
app.include_router(routes_ai_assistant.router)


@app.get("/", tags=["Health"])
def health_check():
    """API health check – confirms the service is running."""
    return {
        "status": "ok",
        "service": "FitLog API",
        "version": "0.1.0",
        "docs": "/docs",
    }
