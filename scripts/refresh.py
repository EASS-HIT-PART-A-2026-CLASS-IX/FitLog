"""
FitLog Async Refresh Script (EX3 Requirement)
Refreshes all user caches with bounded concurrency and Redis idempotency.

Usage:
    uv run python scripts/refresh.py [--user-id UUID]
    uv run python scripts/refresh.py --all

Features:
- Bounded concurrency (max 5 concurrent tasks)
- Redis-backed idempotency (prevents duplicate processing)
- Exponential backoff retries
- Comprehensive logging
"""
import asyncio
import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

import redis
import httpx

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
MAX_CONCURRENT = 5
IDEMPOTENCY_TTL = 3600  # 1 hour

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Semaphore for bounded concurrency
semaphore = asyncio.Semaphore(MAX_CONCURRENT)


def get_idempotency_key(user_id: str) -> str:
    """Generate idempotency key for a user."""
    return f"refresh:idempotency:{user_id}"


def is_refresh_in_progress(user_id: str) -> bool:
    """Check if refresh is already in progress for this user."""
    return redis_client.exists(get_idempotency_key(user_id)) > 0


def mark_refresh_in_progress(user_id: str) -> None:
    """Mark refresh as in progress with TTL."""
    redis_client.setex(
        get_idempotency_key(user_id),
        IDEMPOTENCY_TTL,
        "in_progress"
    )


async def refresh_user_cache(user_id: str, retry_count: int = 0, max_retries: int = 3) -> dict:
    """
    Refresh cache for a single user with exponential backoff retry.
    
    Args:
        user_id: User ID to refresh
        retry_count: Current retry attempt
        max_retries: Maximum retry attempts
    
    Returns:
        Result dict with status and details
    """
    # Check idempotency
    if is_refresh_in_progress(user_id):
        return {
            "status": "skipped",
            "user_id": user_id,
            "reason": "Refresh already in progress",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    # Mark as in progress
    mark_refresh_in_progress(user_id)
    
    try:
        async with semaphore:
            async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
                # Fetch workout summary (triggers cache update)
                response = await client.get(f"/analytics/{user_id}/workout-summary")
                
                if response.status_code == 200:
                    summary = response.json()
                    print(f"✅ Refreshed cache for user {user_id}")
                    print(f"   - Total workouts: {summary.get('total_workouts')}")
                    print(f"   - Total volume: {summary.get('total_volume_kg'):.0f} kg")
                    print(f"   - Most worked: {summary.get('most_worked_muscle_group')}")
                    
                    return {
                        "status": "success",
                        "user_id": user_id,
                        "summary": summary,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                elif response.status_code == 404:
                    return {
                        "status": "not_found",
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                else:
                    raise Exception(f"API error: {response.status_code}")
    
    except Exception as e:
        if retry_count < max_retries:
            # Exponential backoff: 2^retry_count seconds
            wait_time = 2 ** retry_count
            print(f"⚠️  Retry {retry_count + 1}/{max_retries} for user {user_id} in {wait_time}s...")
            await asyncio.sleep(wait_time)
            return await refresh_user_cache(user_id, retry_count + 1, max_retries)
        else:
            return {
                "status": "error",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


async def get_all_user_ids() -> list[str]:
    """Fetch all user IDs from the API."""
    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
            response = await client.get("/profile/")
            if response.status_code == 200:
                profiles = response.json()
                return [p["id"] for p in profiles]
    except Exception as e:
        print(f"❌ Failed to fetch profiles: {e}")
    
    return []


async def refresh_all_users() -> None:
    """Refresh cache for all users with bounded concurrency."""
    print("🔄 Fetching all users...")
    user_ids = await get_all_user_ids()
    
    if not user_ids:
        print("⚠️  No users found.")
        return
    
    print(f"📊 Refreshing cache for {len(user_ids)} user(s)...\n")
    
    # Create tasks for all users
    tasks = [refresh_user_cache(user_id) for user_id in user_ids]
    
    # Execute with bounded concurrency
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Summary
    print("\n" + "=" * 60)
    successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
    failed = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "error")
    skipped = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "skipped")
    
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print("=" * 60)


async def refresh_single_user(user_id: str) -> None:
    """Refresh cache for a single user."""
    print(f"🔄 Refreshing cache for user {user_id}...")
    result = await refresh_user_cache(user_id)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Refresh FitLog user caches with bounded concurrency & idempotency"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        help="Refresh cache for a specific user ID"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Refresh cache for all users"
    )
    
    args = parser.parse_args()
    
    if args.user_id:
        asyncio.run(refresh_single_user(args.user_id))
    elif args.all:
        asyncio.run(refresh_all_users())
    else:
        print("Usage:")
        print("  uv run python scripts/refresh.py --user-id <UUID>")
        print("  uv run python scripts/refresh.py --all")
        parser.print_help()


if __name__ == "__main__":
    main()
