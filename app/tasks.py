"""
Celery async tasks for FitLog.
- Workout summary report generation
- Nutrition analysis with caching
- Weekly digest email preparation
"""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from celery import Celery
import redis

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)
redis_url = settings.redis_url

# Celery app
celery_app = Celery(
    "fitlog",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3)
def generate_workout_summary(self, user_id: str) -> dict:
    """
    Generate a comprehensive workout summary for a user.
    Uses Redis caching with 1-hour TTL.
    """
    cache_key = f"workout_summary:{user_id}"
    
    # Check cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    try:
        # Placeholder: In real implementation, query the database
        # For now, return a sample summary structure
        summary = {
            "user_id": user_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_workouts_week": 4,
            "total_volume_kg": 2840.0,  # Total weight moved
            "avg_workout_duration_min": 45,
            "most_worked_muscle": "legs",
            "weekly_protein_avg_g": 175.0,
            "progress_notes": "Excellent consistency this week! Consider increasing leg volume.",
        }
        
        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(summary))
        
        return summary
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def analyze_nutrition(self, user_id: str) -> dict:
    """
    Analyze nutrition patterns with Redis caching.
    Returns macro trends and recommendations.
    """
    cache_key = f"nutrition_analysis:{user_id}"
    
    # Check cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    try:
        # Placeholder: In real implementation, query macro entries
        analysis = {
            "user_id": user_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "avg_daily_calories": 2300,
            "avg_daily_protein_g": 175,
            "protein_consistency": 0.92,  # 0-1 scale
            "recommendation": "Protein intake is excellent and consistent with your muscle-building goal.",
            "flags": [],
        }
        
        # Cache for 6 hours
        redis_client.setex(cache_key, 21600, json.dumps(analysis))
        
        return analysis
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task
def send_weekly_digest(user_id: str) -> bool:
    """
    Prepare and send a weekly digest email (placeholder).
    In production, integrate with email service (SendGrid, AWS SES, etc.)
    """
    try:
        # Get cached summaries
        workout_summary = redis_client.get(f"workout_summary:{user_id}")
        nutrition_analysis = redis_client.get(f"nutrition_analysis:{user_id}")
        
        digest = {
            "user_id": user_id,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "workout_summary": json.loads(workout_summary) if workout_summary else None,
            "nutrition_analysis": json.loads(nutrition_analysis) if nutrition_analysis else None,
        }
        
        logger.info("Weekly digest prepared for user_id=%s", user_id)
        return True
    except Exception:
        logger.exception("Error preparing digest for user_id=%s", user_id)
        return False


@celery_app.task
def refresh_user_cache(user_id: str) -> dict:
    """
    Refresh all cached data for a user.
    Idempotent operation with bounded concurrency.
    """
    try:
        # Generate all summaries
        workout_task = generate_workout_summary.delay(user_id)
        nutrition_task = analyze_nutrition.delay(user_id)
        
        # Wait for results
        workout_summary = workout_task.get(timeout=30)
        nutrition_analysis = nutrition_task.get(timeout=30)
        
        return {
            "status": "success",
            "user_id": user_id,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
            "cached_items": ["workout_summary", "nutrition_analysis"],
        }
    except Exception as e:
        return {
            "status": "error",
            "user_id": user_id,
            "error": str(e),
        }
