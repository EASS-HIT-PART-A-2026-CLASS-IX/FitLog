"""Shared pytest fixtures for FitLog tests."""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app

_TEST_PASSWORD = "TestPass1!"


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio for all pytest.mark.anyio tests in this suite."""
    return "asyncio"


@pytest.fixture
def client() -> TestClient:
    """TestClient with a freshly registered user pre-authenticated.

    Each fixture call registers a unique test user so tests are isolated
    even when run against the same SQLite DB file.
    """
    test_client = TestClient(app, raise_server_exceptions=True)
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    resp = test_client.post(
        "/auth/register",
        json={"email": email, "password": _TEST_PASSWORD, "name": "Test User"},
    )
    assert resp.status_code == 201, f"Test user registration failed: {resp.text}"
    token = resp.json()["access_token"]
    test_client.headers.update({"Authorization": f"Bearer {token}"})
    return test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Return the Authorization headers used by the `client` fixture."""
    return {"Authorization": client.headers["Authorization"]}


@pytest.fixture
def sample_exercise(client: TestClient) -> dict:
    resp = client.post(
        "/exercises/",
        json={
            "name": "Barbell Squat",
            "category": "strength",
            "muscle_group": "legs",
            "description": "King of compound movements",
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def sample_profile(client: TestClient) -> dict:
    resp = client.post(
        "/profile/",
        json={
            "name": "Alex",
            "weight_kg": 80.0,
            "height_cm": 175.0,
            "age": 28,
            "gender": "male",
            "goal": "muscle",
        },
    )
    assert resp.status_code == 201
    return resp.json()
