"""Tests for /macros nutrition CRUD endpoints."""


def test_list_macros_empty(client):
    resp = client.get("/macros/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_macro(client):
    resp = client.post("/macros/", json={
        "entry_date": "2026-03-25",
        "calories": 2400.0,
        "protein_g": 180.0,
        "carbs_g": 260.0,
        "fat_g": 75.0,
        "notes": "High training day",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["calories"] == 2400.0
    assert data["protein_g"] == 180.0


def test_update_macro(client):
    create = client.post("/macros/", json={
        "entry_date": "2026-03-25",
        "calories": 2000.0,
        "protein_g": 150.0,
        "carbs_g": 200.0,
        "fat_g": 60.0,
    })
    entry_id = create.json()["id"]
    resp = client.put(f"/macros/{entry_id}", json={"protein_g": 170.0})
    assert resp.status_code == 200
    assert resp.json()["protein_g"] == 170.0


def test_delete_macro(client):
    create = client.post("/macros/", json={
        "entry_date": "2026-03-25",
        "calories": 2000.0,
        "protein_g": 150.0,
        "carbs_g": 200.0,
        "fat_g": 60.0,
    })
    entry_id = create.json()["id"]
    resp = client.delete(f"/macros/{entry_id}")
    assert resp.status_code == 204

    resp = client.get(f"/macros/{entry_id}")
    assert resp.status_code == 404
