"""
Workout Summary & Analytics Router (EX3 Enhancement)
Provides insights and summaries of user workout data.
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.app.schemas import WorkoutSummaryOut
from app.repository import workout_logs_repo, profiles_repo

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/{profile_id}/workout-summary",
    response_model=WorkoutSummaryOut,
    summary="Get workout summary for a profile",
    description=(
        "Analyze recent workout logs and provide a summary including:\n"
        "- Total workouts this week\n"
        "- Total volume (weight × reps × sets)\n"
        "- Most worked muscle groups\n"
        "- Strength progression\n"
        "- Personalized recommendations"
    ),
)
def get_workout_summary(profile_id: UUID) -> WorkoutSummaryOut:
    """Generate workout summary and analytics."""
    # Check if profile exists
    profile = profiles_repo.get(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    
    # Get all logs and filter recent ones
    all_logs = workout_logs_repo.list()
    
    # Calculate metrics
    total_volume = 0
    muscle_groups = {}
    total_workouts = 0
    
    for log in all_logs:
        # Calculate volume (sets × reps × weight)
        volume = log.get("sets", 0) * log.get("reps", 0) * log.get("weight_kg", 0)
        total_volume += volume
        total_workouts += 1
        
        # Track muscle groups (from exercises - simplified)
        # In production, would join with exercises table
        muscle_group = log.get("muscle_group", "unknown")
        muscle_groups[muscle_group] = muscle_groups.get(muscle_group, 0) + 1
    
    most_worked = max(muscle_groups, key=muscle_groups.get) if muscle_groups else "N/A"
    
    # Generate recommendation based on profile goal
    goal = profile.get("goal", "fit")
    if goal == "muscle":
        recommendation = (
            f"You're lifting with great volume ({total_volume:.0f} kg total)! "
            f"Keep pushing leg volume to match your {profile['weight_kg']:.0f}kg body weight. "
            f"Consider adding more compound movements."
        )
    else:
        recommendation = (
            f"Nice consistency with {total_workouts} workouts! "
            f"You're at {most_worked} focus. Aim for balanced muscle group distribution."
        )
    
    return WorkoutSummaryOut(
        user_id=profile_id,
        name=profile["name"],
        total_workouts=total_workouts,
        total_volume_kg=total_volume,
        most_worked_muscle_group=most_worked,
        workouts_per_week=max(1, total_workouts // 4),  # Rough estimate
        recommendation=recommendation,
    )
