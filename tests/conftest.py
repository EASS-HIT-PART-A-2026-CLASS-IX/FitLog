"""Shared pytest fixtures for FitLog tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


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
