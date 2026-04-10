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
from datetime import datetime, timedelta, timezone
from typing import Optional

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


def get_idempotency_key(profile_id: str) -> str:
    """Generate idempotency key for a profile."""
    return f"refresh:idempotency:{profile_id}"


def is_refresh_in_progress(profile_id: str) -> bool:
    """Check if refresh is already in progress for this profile."""
    return redis_client.exists(get_idempotency_key(profile_id)) > 0


def mark_refresh_in_progress(profile_id: str) -> None:
    """Mark refresh as in progress with TTL."""
    redis_client.setex(
        get_idempotency_key(profile_id),
        IDEMPOTENCY_TTL,
        "in_progress"
    )

                    return {
                        "status": "success",
                        "profile_id": profile_id,
                        "summary": summary,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                elif response.status_code == 404:
                    return {
                        "status": "not_found",
                        "profile_id": profile_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                else:
                    raise Exception(f"API error: {response.status_code}")

    except Exception as e:
        if retry_count < max_retries:
            wait_time = 2**retry_count
            print(
                f"⚠️  Retry {retry_count + 1}/{max_retries} for profile {profile_id} in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)
            return await refresh_user_cache(profile_id, retry_count + 1, max_retries)
        else:
            return {
                "status": "error",
                "profile_id": profile_id,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
    successful = sum(
        1 for r in results if isinstance(r, dict) and r.get("status") == "success"
    )
    failed = sum(
        1 for r in results if isinstance(r, dict) and r.get("status") == "error"
    )
    skipped = sum(
        1 for r in results if isinstance(r, dict) and r.get("status") == "skipped"
    )

    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print("=" * 60)


async def refresh_single_profile(profile_id: str) -> None:
    """Refresh cache for a single profile."""
    print(f"🔄 Refreshing cache for profile {profile_id}...")
    result = await refresh_user_cache(profile_id)

    print("\nResult:")
    print(json.dumps(result, indent=2))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Refresh FitLog profile caches with bounded concurrency & idempotency"
    )
    parser.add_argument(
        "--profile-id", type=str, help="Refresh cache for a specific profile ID"
    )
    parser.add_argument(
        "--all", action="store_true", help="Refresh cache for all profiles"
    )

    args = parser.parse_args()

    if args.profile_id:
        asyncio.run(refresh_single_profile(args.profile_id))
    elif args.all:
        asyncio.run(refresh_all_users())
    else:
        print("Usage:")
        print("  uv run python scripts/refresh.py --profile-id <UUID>")
        print("  uv run python scripts/refresh.py --all")
        parser.print_help()


if __name__ == "__main__":
    main()
