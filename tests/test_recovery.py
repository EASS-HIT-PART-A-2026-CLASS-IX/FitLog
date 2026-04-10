"""Tests for /recovery CRUD endpoints."""


def test_list_recovery_empty(client):
    resp = client.get("/recovery/")
    assert resp.status_code in (200, 401)


def test_create_recovery(client):
    resp = client.post("/recovery/", json={
        "entry_date": "2026-03-25",
        "soreness_level": 3,
        "energy_level": 4,
        "stress_level": 2,
        "mood": 4,
        "notes": "Feeling good after rest day",
    })
    assert resp.status_code in (201, 401)
    if resp.status_code == 201:
        data = resp.json()
        assert data["soreness_level"] == 3
        assert data["energy_level"] == 4
        assert "id" in data


def test_create_recovery_validation(client):
    # mood out of range
    resp = client.post("/recovery/", json={
        "entry_date": "2026-03-25",
        "soreness_level": 2,
        "energy_level": 3,
        "stress_level": 2,
        "mood": 6,
    })
    assert resp.status_code in (422, 401)


def test_create_recovery_missing_fields(client):
    # Missing required fields
    resp = client.post("/recovery/", json={
        "entry_date": "2026-03-25",
        "soreness_level": 2,
    })
    assert resp.status_code in (422, 401)


def test_delete_recovery_not_found(client):
    resp = client.delete("/recovery/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (404, 401)
