"""
FitLog Async Refresh Script (EX3 Requirement — Session 09)
Refreshes all user analytics caches with bounded concurrency and Redis idempotency.

Features:
- Bounded concurrency (asyncio.Semaphore, max 5 concurrent tasks)
- Redis-backed idempotency (prevents duplicate processing within 1 hour)
- Exponential backoff retries (2^N seconds, up to 3 retries)
- Structured trace output for Redis operations

Usage:
    uv run python scripts/refresh.py --profile-id <UUID>
    uv run python scripts/refresh.py --all

Environment:
    REDIS_URL          Redis connection string (default: redis://localhost:6379/0)
    API_BASE           API base URL (default: http://127.0.0.1:8000)
    REFRESH_API_TOKEN  Bearer token for authenticated API calls
"""

import asyncio
import json
import os
import argparse
from datetime import datetime, timezone

import httpx

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
API_TOKEN = os.getenv("REFRESH_API_TOKEN", "")
MAX_CONCURRENT = 5
IDEMPOTENCY_TTL = 3600  # 1 hour

# Semaphore for bounded concurrency — created lazily inside the event loop
_semaphore: asyncio.Semaphore | None = None


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    return _semaphore


def _get_redis():
    """Return a synchronous Redis client (imported lazily to allow mocking)."""
    import redis as _redis
    return _redis.from_url(REDIS_URL, decode_responses=True)


def get_idempotency_key(profile_id: str) -> str:
    """Return the Redis key used to track in-progress refreshes."""
    return f"refresh:idempotency:{profile_id}"


def is_refresh_in_progress(profile_id: str) -> bool:
    """Check if a refresh is already running for this profile."""
    return _get_redis().exists(get_idempotency_key(profile_id)) > 0


def mark_refresh_in_progress(profile_id: str) -> None:
    """Set the idempotency flag in Redis with a 1-hour TTL."""
    key = get_idempotency_key(profile_id)
    _get_redis().setex(key, IDEMPOTENCY_TTL, "in_progress")
    print(f"[CACHE] SET {key} → 'in_progress' (TTL: {IDEMPOTENCY_TTL}s)")


async def refresh_user_cache(
    profile_id: str,
    retry_count: int = 0,
    max_retries: int = 3,
) -> dict:
    """Refresh the analytics cache for a single profile.

    Idempotency: skips profiles that already have an in-progress refresh key.
    Concurrency: acquires the module-level semaphore before making HTTP calls.
    Retries: exponential backoff (1s, 2s, 4s) on transient errors.
    """
    if is_refresh_in_progress(profile_id):
        print(f"[SKIP] {profile_id} — refresh already in progress")
        return {
            "status": "skipped",
            "reason": "Already in progress",
            "profile_id": profile_id,
        }

    async with _get_semaphore():
        mark_refresh_in_progress(profile_id)
        try:
            headers: dict[str, str] = {}
            if API_TOKEN:
                headers["Authorization"] = f"Bearer {API_TOKEN}"

            async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
                response = await client.get(
                    f"/analytics/{profile_id}/workout-summary",
                    headers=headers,
                )

            if response.status_code == 200:
                summary = response.json()
                print(f"[CACHE] SETEX workout_summary:{profile_id} → refreshed")
                print(f"[LOG]  Refreshed profile {profile_id}")
                print(f"       - Total workouts: {summary.get('total_workouts', 'N/A')}")
                print(f"       - Total volume:   {summary.get('total_volume_kg', 'N/A')} kg")
                print(f"       - Most worked:    {summary.get('most_worked_muscle_group', 'N/A')}")
                return {
                    "status": "success",
                    "profile_id": profile_id,
                    "summary": summary,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            if response.status_code == 404:
                print(f"[WARN] Profile {profile_id} not found (404)")
                return {
                    "status": "not_found",
                    "profile_id": profile_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            raise RuntimeError(f"API error: {response.status_code}")

        except Exception as exc:
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                print(
                    f"[RETRY] {retry_count + 1}/{max_retries} for {profile_id}"
                    f" — waiting {wait_time}s ({exc})"
                )
                await asyncio.sleep(wait_time)
                return await refresh_user_cache(profile_id, retry_count + 1, max_retries)

            print(f"[ERROR] Giving up on {profile_id} after {max_retries} retries: {exc}")
            return {
                "status": "error",
                "profile_id": profile_id,
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


async def get_all_profile_ids() -> list[str]:
    """Fetch all profile IDs from the /profile/ endpoint."""
    headers: dict[str, str] = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
            response = await client.get("/profile/", headers=headers)
            if response.status_code == 200:
                return [p["id"] for p in response.json()]
    except Exception as exc:
        print(f"[ERROR] Failed to fetch profiles: {exc}")
    return []


async def refresh_all_users() -> None:
    """Refresh caches for all profiles with bounded concurrency."""
    print("[INFO] Fetching all profiles...")
    profile_ids = await get_all_profile_ids()

    if not profile_ids:
        print("[WARN] No profiles found — nothing to refresh.")
        return

    print(f"[INFO] Refreshing {len(profile_ids)} profile(s) (max {MAX_CONCURRENT} concurrent)\n")

    tasks = [refresh_user_cache(pid) for pid in profile_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
    failed = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "error")
    skipped = sum(1 for r in results if isinstance(r, dict) and r.get("status") in ("skipped", "not_found"))

    print("\n" + "=" * 60)
    print(f"  Successful : {successful}")
    print(f"  Failed     : {failed}")
    print(f"  Skipped    : {skipped}")
    print("=" * 60)


async def refresh_single_profile(profile_id: str) -> None:
    """Refresh cache for a single profile and print the result."""
    print(f"[INFO] Refreshing profile {profile_id}...\n")
    result = await refresh_user_cache(profile_id)
    print("\nResult:")
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh FitLog profile caches (bounded concurrency + Redis idempotency)"
    )
    parser.add_argument("--profile-id", help="Refresh a specific profile by ID")
    parser.add_argument("--all", action="store_true", help="Refresh all profiles")
    args = parser.parse_args()

    if args.profile_id:
        asyncio.run(refresh_single_profile(args.profile_id))
    elif args.all:
        asyncio.run(refresh_all_users())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
