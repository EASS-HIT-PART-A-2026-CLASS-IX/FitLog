"""Tests for /analytics endpoints (EX3 enhancement feature)."""
from fastapi.testclient import TestClient


def test_workout_summary_empty(client: TestClient, sample_profile: dict):
    """With no workout logs the summary returns zeros and a recommendation."""
    pid = sample_profile["id"]
    resp = client.get(f"/analytics/{pid}/workout-summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_workouts"] == 0
    assert data["total_volume_kg"] == 0.0
    assert data["most_worked_muscle_group"] == "N/A"
    assert isinstance(data["recommendation"], str)
    assert len(data["recommendation"]) > 0


def test_workout_summary_not_found(client: TestClient):
    """Unknown profile returns 404."""
    resp = client.get("/analytics/00000000-0000-0000-0000-000000000000/workout-summary")
    assert resp.status_code == 404


def test_workout_summary_volume_calculation(
    client: TestClient, sample_profile: dict, sample_exercise: dict
):
    """Total volume = sets × reps × weight_kg across all logged sets."""
    pid = sample_profile["id"]
    # 3 sets × 10 reps × 50 kg = 1500 kg
    resp = client.post(
        "/logs/",
        json={
            "exercise_id": sample_exercise["id"],
            "log_date": "2026-04-01",
            "sets": 3,
            "reps": 10,
            "weight_kg": 50.0,
            "notes": "Test set",
        },
    )
    assert resp.status_code == 201
    resp = client.get(f"/analytics/{pid}/workout-summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_workouts"] == 1
    assert data["total_volume_kg"] == pytest.approx(1500.0)


def test_workout_summary_most_worked_muscle(
    client: TestClient, sample_profile: dict, sample_exercise: dict
):
    """Most worked muscle group is derived from logged exercises."""
    pid = sample_profile["id"]
    for i in range(3):
        client.post(
            "/logs/",
            json={
                "exercise_id": sample_exercise["id"],
                "log_date": f"2026-04-0{i + 1}",
                "sets": 3,
                "reps": 8,
                "weight_kg": 80.0,
            },
        )
    resp = client.get(f"/analytics/{pid}/workout-summary")
    assert resp.status_code == 200
    assert resp.json()["most_worked_muscle_group"] == "legs"


def test_workout_summary_requires_auth(client: TestClient, sample_profile: dict):
    """Request without token returns 401."""
    pid = sample_profile["id"]
    from fastapi.testclient import TestClient as TC
    from app.main import app

    unauth = TC(app)
    resp = unauth.get(f"/analytics/{pid}/workout-summary")
    assert resp.status_code == 401


def test_analytics_summary_endpoint(client: TestClient):
    """Dashboard summary endpoint returns the expected schema."""
    resp = client.get("/analytics/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "workouts_this_week" in data
    assert "avg_calories_7d" in data
    assert "current_streak_days" in data


def test_workout_volume_endpoint(client: TestClient):
    """Weekly volume endpoint returns a list."""
    resp = client.get("/analytics/workout-volume")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_nutrition_trend_endpoint(client: TestClient):
    """Nutrition trend endpoint returns a list."""
    resp = client.get("/analytics/nutrition-trend")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


import pytest
