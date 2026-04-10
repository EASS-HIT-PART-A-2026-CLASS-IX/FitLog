"""
Centralized application configuration using pydantic-settings.

All environment variables are loaded here exactly once. Missing required
values fail fast at import time with a clear error message.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required secrets
    secret_key: str = Field(..., min_length=32, description="JWT signing key")
    groq_api_key: str = Field(..., min_length=1, description="Groq API key")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./fitlog.db",
        description="SQLAlchemy async database URL",
    )

    # Redis / Celery
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # JWT
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=1440, ge=1)

    # Environment
    app_env: str = Field(default="development")

    # CORS — comma-separated string in env, list in code
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:8501", "http://127.0.0.1:8501"],
    )

    # Cache TTLs (seconds)
    cache_ttl_analytics: int = Field(default=300, ge=0)
    cache_ttl_food_analysis: int = Field(default=86400, ge=0)

    # AI
    groq_model: str = Field(default="llama-3.3-70b-versatile")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor. Use as a FastAPI dependency."""
    return Settings()


# Module-level singleton for non-DI usage (security.py, database.py)
settings = get_settings()
