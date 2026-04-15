"""
FitLog EX3 Demo Script
Walks through the complete FitLog flow end-to-end.

Usage:
    uv run python scripts/demo.py

The script registers a fresh demo user each run so it is safe to re-run.
Requires the API to be running on http://127.0.0.1:8000.
"""

import uuid
import httpx
from datetime import date

BASE = "http://127.0.0.1:8000"


def _check_api(client: httpx.Client) -> None:
    try:
        resp = client.get("/")
        resp.raise_for_status()
    except Exception:
        print("ERROR: API is not running.")
        print("  Start it with:  uv run uvicorn app.main:app --reload")
        raise SystemExit(1)


def demo() -> None:
    client = httpx.Client(base_url=BASE, timeout=15.0)

    print("=" * 70)
    print("FitLog EX3 - Full-Stack Fitness Tracking Demo")
    print("=" * 70)
    print()

    _check_api(client)

    # ── Step 1: Register a demo user ──────────────────────────────────────────
    print("Step 1: Registering demo user...")
    email = f"demo_{uuid.uuid4().hex[:8]}@fitlog.demo"
    resp = client.post(
        "/auth/register",
        json={"email": email, "password": "DemoPass1!", "name": "Demo Athlete"},
    )
    if resp.status_code != 201:
        print(f"  ERROR: {resp.text}")
        raise SystemExit(1)
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    print(f"  Registered: {email}")
    print(f"  Token:      {token[:40]}...")
    print()

    # ── Step 2: Create a fitness profile ──────────────────────────────────────
    print("Step 2: Creating fitness profile...")
    resp = client.post(
        "/profile/",
        json={
            "name": "Demo Athlete",
            "weight_kg": 80.0,
            "height_cm": 178.0,
            "age": 28,
            "gender": "male",
            "goal": "muscle",
        },
    )
    assert resp.status_code == 201, resp.text
    profile = resp.json()
    profile_id = profile["id"]
    print(f"  Profile created: {profile['name']} (goal: {profile['goal']})")
    print(f"  Profile ID: {profile_id}")
    print()

    # ── Step 3: Protein target ────────────────────────────────────────────────
    print("Step 3: Calculating protein target...")
    resp = client.get(f"/profile/{profile_id}/protein-target")
    if resp.status_code == 200:
        pt = resp.json()
        print(f"  Daily protein target: {pt['protein_g']} g")
        print(f"  Multiplier: {pt['multiplier_g_per_kg']} g/kg")
    print()

    # ── Step 4: Add exercises ─────────────────────────────────────────────────
    print("Step 4: Adding exercises to library...")
    exercises_data = [
        {"name": "Barbell Squat",  "category": "strength", "muscle_group": "legs"},
        {"name": "Bench Press",    "category": "strength", "muscle_group": "chest"},
        {"name": "Deadlift",       "category": "strength", "muscle_group": "back"},
        {"name": "Overhead Press", "category": "strength", "muscle_group": "shoulders"},
    ]
    exercises = []
    for ex in exercises_data:
        created = client.post("/exercises/", json=ex).json()
        exercises.append(created)
        print(f"  + {created['name']} [{created['muscle_group']}]")
    print()

    # ── Step 5: Log workouts ──────────────────────────────────────────────────
    print("Step 5: Logging workouts...")
    today = date.today().isoformat()
    workouts = [
        {"exercise": exercises[0], "sets": 4, "reps": 6,  "weight": 120.0},
        {"exercise": exercises[1], "sets": 3, "reps": 8,  "weight": 90.0},
        {"exercise": exercises[2], "sets": 3, "reps": 5,  "weight": 150.0},
        {"exercise": exercises[3], "sets": 3, "reps": 8,  "weight": 70.0},
    ]
    for w in workouts:
        client.post(
            "/logs/",
            json={
                "exercise_id": w["exercise"]["id"],
                "profile_id": profile_id,
                "log_date": today,
                "sets": w["sets"],
                "reps": w["reps"],
                "weight_kg": w["weight"],
                "notes": "Demo session",
            },
        )
        vol = w["sets"] * w["reps"] * w["weight"]
        print(
            f"  {w['sets']}x{w['reps']} @ {w['weight']} kg"
            f"  ({w['exercise']['name']})  vol={vol:.0f} kg"
        )
    print()

    # ── Step 6: Log macros ────────────────────────────────────────────────────
    print("Step 6: Logging nutrition...")
    client.post(
        "/macros/",
        json={
            "entry_date": today,
            "calories": 3000,
            "protein_g": 180,
            "carbs_g": 350,
            "fat_g": 80,
            "notes": "Demo day",
        },
    )
    print("  3000 kcal | P:180g C:350g F:80g")
    print()

    # ── Step 7: Workout summary (EX3 enhancement) ─────────────────────────────
    print("Step 7: Viewing workout summary (EX3 enhancement feature)...")
    resp = client.get(f"/analytics/{profile_id}/workout-summary")
    if resp.status_code == 200:
        s = resp.json()
        print(f"  Total workouts:    {s['total_workouts']}")
        print(f"  Total volume:      {s['total_volume_kg']:.0f} kg")
        print(f"  Most worked group: {s['most_worked_muscle_group']}")
        print(f"  Workouts this wk:  {s['workouts_per_week']}")
        print(f"  Recommendation:    {s['recommendation'][:80]}...")
    print()

    # ── Step 8: AI chat (optional) ────────────────────────────────────────────
    print("Step 8: AI fitness advisor (Groq)...")
    try:
        resp = client.post(
            "/ai/chat",
            json={
                "profile_id": profile_id,
                "message": "Based on my workout today, what should I focus on tomorrow?",
            },
        )
        if resp.status_code == 200:
            print(f"  AI: {resp.json()['reply'][:100]}...")
        else:
            print(f"  Skipped (status {resp.status_code})")
    except Exception as exc:
        print(f"  Skipped: {exc}")
    print()

    # ── Done ──────────────────────────────────────────────────────────────────
    print("=" * 70)
    print("Demo complete!")
    print()
    print("Access points:")
    print("  API docs:  http://127.0.0.1:8000/docs")
    print("  Frontend:  http://127.0.0.1:8501  (uv run streamlit run frontend/app.py)")
    print("=" * 70)


if __name__ == "__main__":
    demo()
