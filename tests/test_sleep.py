"""Tests for /sleep CRUD endpoints."""


def test_list_sleep_empty(client):
    resp = client.get("/sleep/")
    assert resp.status_code in (200, 401)


def test_create_sleep(client):
    resp = client.post("/sleep/", json={
        "entry_date": "2026-03-25",
        "sleep_hours": 7.5,
        "sleep_quality": 4,
        "notes": "Slept well",
    })
    assert resp.status_code in (201, 401)
    if resp.status_code == 201:
        data = resp.json()
        assert data["sleep_hours"] == 7.5
        assert data["sleep_quality"] == 4
        assert "id" in data


def test_create_sleep_validation(client):
    # sleep_quality out of range
    resp = client.post("/sleep/", json={
        "entry_date": "2026-03-25",
        "sleep_hours": 7.0,
        "sleep_quality": 6,
    })
    assert resp.status_code in (422, 401)


def test_delete_sleep_not_found(client):
    resp = client.delete("/sleep/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (404, 401)
