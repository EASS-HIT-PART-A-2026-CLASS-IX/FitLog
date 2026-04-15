"""Security tests (EX3 — Session 11 requirement).

Verifies that protected endpoints reject:
- Missing Authorization header
- Expired tokens
- Malformed / tampered tokens
"""
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security import create_access_token


@pytest.fixture
def unauth_client() -> TestClient:
    """TestClient with no Authorization header."""
    return TestClient(app, raise_server_exceptions=True)


# ── Missing token ──────────────────────────────────────────────────────────────

def test_exercises_no_token(unauth_client: TestClient):
    resp = unauth_client.get("/exercises/")
    assert resp.status_code == 401


def test_profile_no_token(unauth_client: TestClient):
    resp = unauth_client.get("/profile/")
    assert resp.status_code == 401


def test_analytics_summary_no_token(unauth_client: TestClient):
    resp = unauth_client.get("/analytics/summary")
    assert resp.status_code == 401


# ── Expired token ──────────────────────────────────────────────────────────────

def test_expired_token_rejected(unauth_client: TestClient):
    """A token whose exp is in the past must be rejected with 401."""
    expired = create_access_token(
        {"user_id": "fake-id", "email": "x@x.com"},
        expires_delta=timedelta(seconds=-1),
    )
    resp = unauth_client.get(
        "/exercises/",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert resp.status_code == 401


def test_expired_token_on_profile(unauth_client: TestClient):
    """Expired token also rejected on profile routes."""
    expired = create_access_token(
        {"user_id": "fake-id", "email": "x@x.com"},
        expires_delta=timedelta(seconds=-60),
    )
    resp = unauth_client.get(
        "/profile/",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert resp.status_code == 401


# ── Malformed / tampered token ─────────────────────────────────────────────────

def test_malformed_token_rejected(unauth_client: TestClient):
    resp = unauth_client.get(
        "/exercises/",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert resp.status_code == 401


def test_wrong_scheme_rejected(unauth_client: TestClient):
    """Basic auth scheme (not Bearer) is rejected."""
    resp = unauth_client.get(
        "/exercises/",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert resp.status_code == 401


def test_token_with_nonexistent_user(unauth_client: TestClient):
    """A valid JWT whose user_id does not exist in the DB returns 401/404."""
    fake_token = create_access_token({"user_id": "00000000-0000-0000-0000-000000000000"})
    resp = unauth_client.get(
        "/exercises/",
        headers={"Authorization": f"Bearer {fake_token}"},
    )
    # App may return 401 or 404 depending on implementation — both are acceptable
    assert resp.status_code in (401, 404)


# ── Valid token flow ───────────────────────────────────────────────────────────

def test_valid_token_accepted(client: TestClient):
    """A freshly issued token allows access to protected endpoints."""
    resp = client.get("/exercises/")
    assert resp.status_code == 200
