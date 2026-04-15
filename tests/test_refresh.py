"""Async tests for the refresh script and analytics endpoints (EX3 — Session 09).

Uses pytest.mark.anyio for async execution via the anyio test runner.
"""
import uuid

import httpx
import pytest

from app.main import app

pytestmark = pytest.mark.anyio


async def test_health_check_async():
    """Health endpoint is reachable via async ASGI transport."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/")
    assert resp.status_code == 200


async def test_async_register_and_login():
    """Register + login flow works end-to-end with an async client."""
    email = f"anyio_{uuid.uuid4().hex[:8]}@example.com"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register
        resp = await client.post(
            "/auth/register",
            json={"email": email, "password": "AnyioPass1!", "name": "AnyIO User"},
        )
        assert resp.status_code == 201
        token = resp.json()["access_token"]

        # Protected endpoint with valid token → 200
        resp = await client.get(
            "/exercises/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

        # Protected endpoint without token → 401
        resp = await client.get("/exercises/")
        assert resp.status_code == 401


async def test_async_analytics_summary():
    """Analytics summary is accessible with a valid async token."""
    email = f"anyio_{uuid.uuid4().hex[:8]}@example.com"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/auth/register",
            json={"email": email, "password": "AnyioPass1!", "name": "AnyIO User2"},
        )
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/analytics/summary", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "workouts_this_week" in data
        assert "current_streak_days" in data


async def test_refresh_idempotency_skip():
    """refresh_user_cache skips profiles already marked as in-progress in Redis.

    Redis is mocked so no live Redis connection is required.
    """
    from unittest.mock import patch
    from scripts.refresh import refresh_user_cache

    with patch("scripts.refresh.is_refresh_in_progress", return_value=True):
        result = await refresh_user_cache("test-profile-id")

    assert result["status"] == "skipped"
    assert result["profile_id"] == "test-profile-id"


async def test_refresh_returns_error_after_max_retries():
    """refresh_user_cache returns an error dict after exhausting retries."""
    from unittest.mock import patch, AsyncMock
    from scripts.refresh import refresh_user_cache

    # Simulate: not in progress, mark succeeds, but HTTP call always fails
    with (
        patch("scripts.refresh.is_refresh_in_progress", return_value=False),
        patch("scripts.refresh.mark_refresh_in_progress"),
        patch("httpx.AsyncClient.get", new_callable=AsyncMock, side_effect=RuntimeError("connection refused")),
    ):
        result = await refresh_user_cache("test-profile-id", max_retries=0)

    assert result["status"] == "error"
    assert "test-profile-id" == result["profile_id"]
