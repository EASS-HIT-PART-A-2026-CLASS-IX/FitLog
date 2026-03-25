"""Tests for /logs workout CRUD endpoints."""


def test_list_logs_empty(client):
    resp = client.get("/logs/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_log(client, sample_exercise):
    resp = client.post("/logs/", json={
        "exercise_id": sample_exercise["id"],
        "log_date": "2026-03-25",
        "sets": 4,
        "reps": 8,
        "weight_kg": 100.0,
        "notes": "Felt strong today",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["sets"] == 4
    assert data["weight_kg"] == 100.0


def test_list_logs_after_create(client, sample_exercise):
    client.post("/logs/", json={
        "exercise_id": sample_exercise["id"],
        "log_date": "2026-03-25",
        "sets": 3,
        "reps": 10,
        "weight_kg": 80.0,
    })
    resp = client.get("/logs/")
    assert len(resp.json()) == 1


def test_update_log(client, sample_exercise):
    create = client.post("/logs/", json={
        "exercise_id": sample_exercise["id"],
        "log_date": "2026-03-25",
        "sets": 3,
        "reps": 10,
        "weight_kg": 80.0,
    })
    log_id = create.json()["id"]
    resp = client.put(f"/logs/{log_id}", json={"weight_kg": 85.0})
    assert resp.status_code == 200
    assert resp.json()["weight_kg"] == 85.0


def test_delete_log(client, sample_exercise):
    create = client.post("/logs/", json={
        "exercise_id": sample_exercise["id"],
        "log_date": "2026-03-25",
        "sets": 3,
        "reps": 10,
        "weight_kg": 80.0,
    })
    log_id = create.json()["id"]
    resp = client.delete(f"/logs/{log_id}")
    assert resp.status_code == 204

    resp = client.get(f"/logs/{log_id}")
    assert resp.status_code == 404
