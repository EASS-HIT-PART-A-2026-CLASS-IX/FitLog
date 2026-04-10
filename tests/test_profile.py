"""Tests for /profile CRUD + protein-target calculator."""


def test_create_profile(client):
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
    data = resp.json()
    assert data["name"] == "Alex"
    assert data["goal"] == "muscle"


def test_protein_target_muscle_goal(client, sample_profile):
    """muscle goal → 2.2 g/kg"""
    pid = sample_profile["id"]
    resp = client.get(f"/profile/{pid}/protein-target")
    assert resp.status_code == 200
    data = resp.json()
    assert data["multiplier_g_per_kg"] == 2.2
    # 80 kg × 2.2 = 176.0
    assert data["protein_g"] == 176.0
    assert "recommendation" in data


def test_protein_target_fit_goal(client):
    """fit goal → 1.8 g/kg"""
    create = client.post(
        "/profile/",
        json={
            "name": "Sam",
            "weight_kg": 70.0,
            "height_cm": 168.0,
            "age": 25,
            "gender": "female",
            "goal": "fit",
        },
    )
    pid = create.json()["id"]
    resp = client.get(f"/profile/{pid}/protein-target")
    assert resp.status_code == 200
    data = resp.json()
    assert data["multiplier_g_per_kg"] == 1.8
    # 70 kg × 1.8 = 126.0
    assert data["protein_g"] == 126.0


def test_protein_target_not_found(client):
    resp = client.get("/profile/00000000-0000-0000-0000-000000000000/protein-target")
    assert resp.status_code == 404


def test_create_profile_new_goals(client):
    """New expanded goal values should be accepted."""
    for goal in ["weight_loss", "maintenance", "general_health", "endurance",
                 "flexibility", "hypertrophy", "strength", "athletic_performance"]:
        resp = client.post("/profile/", json={
            "name": f"Test {goal}",
            "weight_kg": 75.0,
            "height_cm": 170.0,
            "age": 30,
            "gender": "male",
            "goal": goal,
        })
        assert resp.status_code in (201, 401), f"Goal '{goal}' rejected: {resp.text}"


def test_create_profile_invalid_goal(client):
    """Invalid goal should be rejected."""
    resp = client.post("/profile/", json={
        "name": "Bad Goal",
        "weight_kg": 75.0,
        "height_cm": 170.0,
        "age": 30,
        "gender": "male",
        "goal": "invalid_goal_xyz",
    })
    assert resp.status_code in (422, 401)


def test_update_profile(client, sample_profile):
    pid = sample_profile["id"]
    resp = client.put(f"/profile/{pid}", json={"weight_kg": 82.5})
    assert resp.status_code == 200
    assert resp.json()["weight_kg"] == 82.5


def test_delete_profile(client, sample_profile):
    pid = sample_profile["id"]
    resp = client.delete(f"/profile/{pid}")
    assert resp.status_code == 204

    resp = client.get(f"/profile/{pid}")
    assert resp.status_code == 404
