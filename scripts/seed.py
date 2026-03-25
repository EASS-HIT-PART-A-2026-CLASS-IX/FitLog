"""
FitLog seed script – populates the running API with sample data.
Usage: uv run python scripts/seed.py
Make sure the API is running first: uv run uvicorn app.main:app --reload
"""
import httpx

BASE = "http://127.0.0.1:8000"


def seed():
    print("🌱 Seeding FitLog API...\n")

    # 1. Create user profile
    profile = httpx.post(f"{BASE}/profile/", json={
        "name": "Alex Fitness",
        "weight_kg": 80.0,
        "height_cm": 178.0,
        "age": 28,
        "gender": "male",
        "goal": "muscle",
    }).json()
    print(f"✅ Profile created: {profile['name']} | Goal: {profile['goal']}")
    print(f"   ID: {profile['id']}")

    # 2. Get protein target
    target = httpx.get(f"{BASE}/profile/{profile['id']}/protein-target").json()
    print(f"\n🥩 Protein target: {target['protein_g']} g/day ({target['multiplier_g_per_kg']} g/kg)")
    print(f"   {target['recommendation'][:100]}...")

    # 3. Create exercises
    exercises_data = [
        {"name": "Barbell Squat", "category": "strength", "muscle_group": "legs",
         "description": "King of compound movements. Develops legs, glutes, and core."},
        {"name": "Bench Press", "category": "strength", "muscle_group": "chest",
         "description": "Horizontal push. Primary chest builder."},
        {"name": "Deadlift", "category": "strength", "muscle_group": "back",
         "description": "Full-body compound. Builds posterior chain strength."},
        {"name": "Pull-up", "category": "strength", "muscle_group": "back",
         "description": "Bodyweight vertical pull. Excellent for lat width."},
        {"name": "Overhead Press", "category": "strength", "muscle_group": "shoulders",
         "description": "Vertical push. Builds shoulder mass and triceps."},
        {"name": "30-min Run", "category": "cardio", "muscle_group": "full-body",
         "description": "Steady-state cardio for cardiovascular health."},
    ]
    created_exercises = []
    print("\n🏋️  Creating exercises...")
    for ex in exercises_data:
        resp = httpx.post(f"{BASE}/exercises/", json=ex).json()
        created_exercises.append(resp)
        print(f"   ✅ {resp['name']} [{resp['category']}]")

    # 4. Log some workouts
    squat = created_exercises[0]
    bench = created_exercises[1]
    deadlift = created_exercises[2]

    logs = [
        {"exercise_id": squat["id"], "log_date": "2026-03-23",
         "sets": 4, "reps": 6, "weight_kg": 120.0, "notes": "Heavy day, felt great"},
        {"exercise_id": bench["id"], "log_date": "2026-03-23",
         "sets": 3, "reps": 8, "weight_kg": 90.0},
        {"exercise_id": deadlift["id"], "log_date": "2026-03-24",
         "sets": 3, "reps": 5, "weight_kg": 150.0, "notes": "New PR!"},
        {"exercise_id": squat["id"], "log_date": "2026-03-25",
         "sets": 4, "reps": 8, "weight_kg": 110.0},
    ]
    print("\n📝 Logging workouts...")
    for log in logs:
        resp = httpx.post(f"{BASE}/logs/", json=log).json()
        print(f"   ✅ {log['log_date']}: {log['sets']}×{log['reps']} @ {log['weight_kg']} kg")

    # 5. Log daily macros
    macro_days = [
        {"entry_date": "2026-03-23", "calories": 3000, "protein_g": 180,
         "carbs_g": 350, "fat_g": 80, "notes": "Training day – high carb"},
        {"entry_date": "2026-03-24", "calories": 2800, "protein_g": 175,
         "carbs_g": 300, "fat_g": 85, "notes": "Training day"},
        {"entry_date": "2026-03-25", "calories": 2200, "protein_g": 170,
         "carbs_g": 200, "fat_g": 75, "notes": "Rest day – lower carb"},
    ]
    print("\n🥗 Logging macros...")
    for macro in macro_days:
        httpx.post(f"{BASE}/macros/", json=macro)
        print(f"   ✅ {macro['entry_date']}: {macro['calories']} kcal | P:{macro['protein_g']}g")

    print("\n🎉 Seed complete! Visit http://127.0.0.1:8000/docs to explore the API.")
    print(f"   💬 Try the AI assistant: POST /ai/chat with user_id={profile['id']}")


if __name__ == "__main__":
    seed()
