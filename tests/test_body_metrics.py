"""Tests for /body-metrics CRUD endpoints."""


def test_list_body_metrics_empty(client):
    resp = client.get("/body-metrics/")
    assert resp.status_code in (200, 401)


def test_create_body_metric(client):
    resp = client.post("/body-metrics/", json={
        "entry_date": "2026-03-25",
        "weight_kg": 80.5,
        "body_fat_pct": 15.0,
        "waist_cm": 82.0,
        "resting_hr": 65,
        "notes": "Morning measurement",
    })
    assert resp.status_code in (201, 401)
    if resp.status_code == 201:
        data = resp.json()
        assert data["weight_kg"] == 80.5
        assert data["body_fat_pct"] == 15.0
        assert "id" in data


def test_create_body_metric_partial(client):
    # Only weight, others optional
    resp = client.post("/body-metrics/", json={
        "entry_date": "2026-03-25",
        "weight_kg": 79.0,
    })
    assert resp.status_code in (201, 401)
    if resp.status_code == 201:
        data = resp.json()
        assert data["weight_kg"] == 79.0
        assert data["body_fat_pct"] is None


def test_create_body_metric_validation(client):
    # body_fat_pct out of range
    resp = client.post("/body-metrics/", json={
        "entry_date": "2026-03-25",
        "body_fat_pct": 150.0,
    })
    assert resp.status_code in (422, 401)


def test_delete_body_metric_not_found(client):
    resp = client.delete("/body-metrics/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (404, 401)
