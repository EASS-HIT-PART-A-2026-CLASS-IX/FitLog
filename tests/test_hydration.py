"""Tests for /hydration CRUD endpoints."""


def test_list_hydration_empty(client):
    resp = client.get("/hydration/")
    assert resp.status_code in (200, 401)


def test_create_hydration(client):
    resp = client.post("/hydration/", json={
        "entry_date": "2026-03-25",
        "water_ml": 500.0,
        "notes": "Morning glass",
    })
    assert resp.status_code in (201, 401)
    if resp.status_code == 201:
        data = resp.json()
        assert data["water_ml"] == 500.0
        assert "id" in data


def test_create_hydration_validation(client):
    # water_ml out of range (negative)
    resp = client.post("/hydration/", json={
        "entry_date": "2026-03-25",
        "water_ml": -100,
    })
    assert resp.status_code in (422, 401)


def test_delete_hydration_not_found(client):
    resp = client.delete("/hydration/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (404, 401)
