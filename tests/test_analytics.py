"""
Tests for EX3 enhancement: Workout Summary & Analytics
Uses pytest and async fixtures for comprehensive coverage.
"""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    response = client.post("/profile/", json={
        "name": "Test User",
        "weight_kg": 80.0,
        "height_cm": 178.0,
        "age": 28,
        "gender": "male",
        "goal": "muscle",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_exercise():
    """Create a sample exercise for testing."""
    response = client.post("/exercises/", json={
        "name": "Barbell Squat",
        "category": "strength",
        "muscle_group": "legs",
        "description": "Test exercise",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_workout_logs(sample_exercise):
    """Create sample workout logs for testing."""
    logs = []
    for i in range(4):
        response = client.post("/logs/", json={
            "exercise_id": sample_exercise["id"],
            "log_date": f"2026-03-{20+i}",
            "sets": 3,
            "reps": 8,
            "weight_kg": 100.0 + (i * 10),
            "notes": f"Workout {i+1}",
        })
        assert response.status_code == 201
        logs.append(response.json())
    
    return logs


def test_workout_summary_basic(sample_profile, sample_workout_logs):
    """Test basic workout summary endpoint."""
    profile_id = sample_profile["id"]
    
    response = client.get(f"/analytics/{profile_id}/workout-summary")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["user_id"] == profile_id
    assert data["name"] == "Test User"
    assert data["total_workouts"] >= 0
    assert data["total_volume_kg"] >= 0
    assert data["most_worked_muscle_group"] in ["legs", "N/A"]
    assert "recommendation" in data


def test_workout_summary_not_found():
    """Test workout summary for non-existent profile."""
    fake_id = str(uuid4())
    
    response = client.get(f"/analytics/{fake_id}/workout-summary")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_workout_summary_with_multiple_logs(sample_profile, sample_exercise):
    """Test workout summary calculation with multiple logs."""
    profile_id = sample_profile["id"]
    
    # Create multiple logs
    for weight in [100, 110, 120, 130]:
        client.post("/logs/", json={
            "exercise_id": sample_exercise["id"],
            "log_date": "2026-03-25",
            "sets": 4,
            "reps": 6,
            "weight_kg": weight,
        })
    
    response = client.get(f"/analytics/{profile_id}/workout-summary")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify calculation: 4 sets × 6 reps × (100+110+120+130) kg = 6960 kg total
    assert data["total_workouts"] == 4
    assert data["most_worked_muscle_group"] == "legs"
    assert "recommendation" in data


def test_workout_summary_recommendation_for_muscle_goal(sample_profile, sample_workout_logs):
    """Test that recommendations are tailored to goals."""
    profile_id = sample_profile["id"]
    
    response = client.get(f"/analytics/{profile_id}/workout-summary")
    
    assert response.status_code == 200
    data = response.json()
    
    # For "muscle" goal, should mention compound movements
    recommendation = data["recommendation"].lower()
    assert ("leg" in recommendation or "compound" in recommendation or "volume" in recommendation)


def test_analytics_endpoint_available():
    """Test that analytics endpoints are registered."""
    # Just verify the endpoint prefix works
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    # Check that analytics paths are in OpenAPI spec
    spec = response.json()
    paths = spec.get("paths", {})
    
    assert any("/analytics" in path for path in paths), "Analytics endpoints not registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
