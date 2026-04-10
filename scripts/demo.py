"""
FitLog EX3 Demo Script
Demonstrates the complete flow of the FitLog system:
1. Create a user profile
2. Add exercises
3. Log workouts
4. Track macros
5. View workout summary
6. Show AI recommendations

Usage: uv run python scripts/demo.py
"""

import httpx
import json
from datetime import date

BASE = "http://127.0.0.1:8000"
client = httpx.Client(base_url=BASE, timeout=10.0)


def demo():
    """Run the interactive demo."""
    print("=" * 70)
    print("🏋️  FitLog EX3 – Full-Stack Fitness Tracking Demo")
    print("=" * 70)
    print()

    # 1. Create User Profile
    print("📝 Step 1: Creating User Profile...")
    profile_data = {
        "name": "Alex Fitness",
        "weight_kg": 80.0,
        "height_cm": 178.0,
        "age": 28,
        "gender": "male",
        "goal": "muscle",
    }
    profile = client.post("/profile/", json=profile_data).json()
    profile_id = profile["id"]
    print(f"   ✅ Profile created: {profile['name']} ({profile['goal']} goal)")
    print(f"   📊 ID: {profile_id}")
    print()

    # 2. Get Protein Target
    print("🥩 Step 2: Calculate Protein Target...")
    protein_target = client.get(f"/profile/{profile_id}/protein-target").json()
    print(f"   💪 Daily protein target: {protein_target['protein_g']} g")
    print(f"   📈 {protein_target['multiplier_g_per_kg']} g per kg of body weight")
    print(f"   💡 {protein_target['recommendation'][:80]}...")
    print()

    # 3. Create Exercises
    print("🏋️  Step 3: Adding Exercises...")
    exercises_data = [
        {"name": "Barbell Squat", "category": "strength", "muscle_group": "legs"},
        {"name": "Bench Press", "category": "strength", "muscle_group": "chest"},
        {"name": "Deadlift", "category": "strength", "muscle_group": "back"},
        {"name": "Overhead Press", "category": "strength", "muscle_group": "shoulders"},
    ]
    exercises = []
    for ex in exercises_data:
        created = client.post("/exercises/", json=ex).json()
        exercises.append(created)
        print(f"   ✅ {created['name']} [{created['muscle_group']}]")
    print()

    # 4. Log Workouts
    print("📝 Step 4: Logging Workouts...")
    workouts = [
        {
            "exercise": exercises[0],
            "date": "2026-03-23",
            "sets": 4,
            "reps": 6,
            "weight": 120.0,
        },
        {
            "exercise": exercises[1],
            "date": "2026-03-23",
            "sets": 3,
            "reps": 8,
            "weight": 90.0,
        },
        {
            "exercise": exercises[2],
            "date": "2026-03-24",
            "sets": 3,
            "reps": 5,
            "weight": 150.0,
        },
        {
            "exercise": exercises[3],
            "date": "2026-03-25",
            "sets": 3,
            "reps": 8,
            "weight": 70.0,
        },
    ]

    for w in workouts:
        log = client.post(
            "/logs/",
            json={
                "exercise_id": w["exercise"]["id"],
                "log_date": w["date"],
                "sets": w["sets"],
                "reps": w["reps"],
                "weight_kg": w["weight"],
                "notes": "Training session",
            },
        ).json()
        print(
            f"   ✅ {w['date']}: {w['sets']}×{w['reps']} @ {w['weight']} kg ({w['exercise']['name']})"
        )
    print()

    # 5. Log Macros
    print("🥗 Step 5: Logging Daily Nutrition...")
    macros = [
        {
            "date": "2026-03-23",
            "calories": 3000,
            "protein": 180,
            "carbs": 350,
            "fat": 80,
        },
        {
            "date": "2026-03-24",
            "calories": 2800,
            "protein": 175,
            "carbs": 300,
            "fat": 85,
        },
        {
            "date": "2026-03-25",
            "calories": 2300,
            "protein": 170,
            "carbs": 250,
            "fat": 70,
        },
    ]

    for m in macros:
        macro = client.post(
            "/macros/",
            json={
                "entry_date": m["date"],
                "calories": m["calories"],
                "protein_g": m["protein"],
                "carbs_g": m["carbs"],
                "fat_g": m["fat"],
                "notes": "Daily log",
            },
        ).json()
        print(
            f"   ✅ {m['date']}: {m['calories']} kcal | P:{m['protein']}g C:{m['carbs']}g F:{m['fat']}g"
        )
    print()

    # 6. Get Workout Summary (EX3 Enhancement)
    print("📊 Step 6: Viewing Workout Summary (EX3 Enhancement)...")
    summary = client.get(f"/analytics/{profile_id}/workout-summary").json()
    print(f"   📈 Total workouts: {summary['total_workouts']}")
    print(f"   💥 Total volume: {summary['total_volume_kg']:.0f} kg")
    print(f"   💪 Most worked: {summary['most_worked_muscle_group']}")
    print(f"   🎯 Workouts per week: ~{summary['workouts_per_week']}")
    print(f"   💡 Recommendation: {summary['recommendation'][:70]}...")
    print()

    # 7. Chat with AI (if configured)
    print("🤖 Step 7: Get AI Fitness Advice...")
    try:
        ai_response = client.post(
            "/ai/chat",
            json={
                "profile_id": profile_id,
                "message": "Based on my profile, what should I focus on next week?",
            },
        ).json()
        print(f"   🤖 AI: {ai_response['reply'][:100]}...")
    except Exception as e:
        print(f"   ⚠️  AI not available: {e}")
    print()

    # Summary
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("🌐 Access the Dashboard:")
    print("   - API Docs:  http://127.0.0.1:8000/docs")
    print("   - Frontend:  http://127.0.0.1:8501")
    print()
    print("📚 Next Steps:")
    print("   1. Visit http://127.0.0.1:8501 for the Streamlit dashboard")
    print("   2. Log more workouts and nutrition data")
    print("   3. View workout summaries and get AI recommendations")
    print("   4. Check the API docs for more endpoints")
    print()


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  Make sure the API is running:")
        print("   uv run uvicorn app.main:app --reload")
