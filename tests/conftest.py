"""Shared pytest fixtures for FitLog tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import exercises_repo, macros_repo, profiles_repo, workout_logs_repo


@pytest.fixture(autouse=True)
def clear_repos():
    """Reset all in-memory repos before each test for isolation."""
    exercises_repo._store.clear()
    workout_logs_repo._store.clear()
    macros_repo._store.clear()
    profiles_repo._store.clear()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_exercise(client: TestClient) -> dict:
    resp = client.post("/exercises/", json={
        "name": "Barbell Squat",
        "category": "strength",
        "muscle_group": "legs",
        "description": "King of compound movements",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def sample_profile(client: TestClient) -> dict:
    resp = client.post("/profile/", json={
        "name": "Alex",
        "weight_kg": 80.0,
        "height_cm": 175.0,
        "age": 28,
        "gender": "male",
        "goal": "muscle",
    })
    assert resp.status_code == 201
    return resp.json()
