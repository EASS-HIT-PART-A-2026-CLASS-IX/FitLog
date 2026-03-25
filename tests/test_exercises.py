"""Tests for /exercises CRUD endpoints."""


def test_list_exercises_empty(client):
    resp = client.get("/exercises/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_exercise(client):
    resp = client.post("/exercises/", json={
        "name": "Pull-up",
        "category": "strength",
        "muscle_group": "back",
        "description": "Bodyweight upper body pull",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Pull-up"
    assert "id" in data


def test_list_exercises_after_create(client, sample_exercise):
    resp = client.get("/exercises/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_exercise(client, sample_exercise):
    resp = client.get(f"/exercises/{sample_exercise['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == sample_exercise["name"]


def test_get_exercise_not_found(client):
    resp = client.get("/exercises/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_update_exercise(client, sample_exercise):
    resp = client.put(
        f"/exercises/{sample_exercise['id']}",
        json={"description": "Updated description"},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated description"


def test_delete_exercise(client, sample_exercise):
    resp = client.delete(f"/exercises/{sample_exercise['id']}")
    assert resp.status_code == 204

    # Confirm it's gone
    resp = client.get(f"/exercises/{sample_exercise['id']}")
    assert resp.status_code == 404


def test_delete_exercise_not_found(client):
    resp = client.delete("/exercises/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
