"""
Redis-backed cache with in-process fallback.

Usage:
    from app.cache import cache

    value = await cache.get("key")
    await cache.set("key", value, ttl=300)
    await cache.delete("key")
    await cache.clear_prefix("analytics:")
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Lazy Redis import (optional dependency) ───────────────────────────────────

try:
    import redis.asyncio as aioredis  # type: ignore[import]
    _HAS_REDIS = True
except ImportError:  # pragma: no cover
    _HAS_REDIS = False


class _InMemoryCache:
    """Simple in-process dict cache used when Redis is unavailable."""

    def __init__(self) -> None:
        import time
        self._store: dict[str, tuple[Any, float | None]] = {}
        self._time = time

    async def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and self._time.monotonic() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        import time
        expires_at = time.monotonic() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def clear_prefix(self, prefix: str) -> None:
        keys = [k for k in self._store if k.startswith(prefix)]
        for k in keys:
            self._store.pop(k, None)

    async def close(self) -> None:
        pass


class RedisCache:
    """Redis-backed cache. Values are JSON-serialised."""

    def __init__(self, redis_url: str) -> None:
        self._url = redis_url
        self._client: Optional[Any] = None

    async def _get_client(self) -> Any:
        if self._client is None:
            self._client = aioredis.from_url(self._url, decode_responses=True)
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            raw = await client.get(key)
            return json.loads(raw) if raw is not None else None
        except Exception:
            logger.warning("Redis GET failed for key=%s", key, exc_info=True)
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        try:
            client = await self._get_client()
            serialised = json.dumps(value)
            if ttl:
                await client.setex(key, ttl, serialised)
            else:
                await client.set(key, serialised)
        except Exception:
            logger.warning("Redis SET failed for key=%s", key, exc_info=True)

    async def delete(self, key: str) -> None:
        try:
            client = await self._get_client()
            await client.delete(key)
        except Exception:
            logger.warning("Redis DELETE failed for key=%s", key, exc_info=True)

    async def clear_prefix(self, prefix: str) -> None:
        try:
            client = await self._get_client()
            keys = await client.keys(f"{prefix}*")
            if keys:
                await client.delete(*keys)
        except Exception:
            logger.warning("Redis CLEAR PREFIX failed for prefix=%s", prefix, exc_info=True)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


# ── Factory ───────────────────────────────────────────────────────────────────

def _build_cache() -> RedisCache | _InMemoryCache:
    """Build the best available cache backend."""
    from app.config import settings

    if _HAS_REDIS and settings.redis_url:
        logger.info("Cache: using Redis at %s", settings.redis_url)
        return RedisCache(settings.redis_url)

    logger.warning("Cache: Redis unavailable, falling back to in-process cache")
    return _InMemoryCache()


# ── Module-level singleton (created at first import) ─────────────────────────

cache: RedisCache | _InMemoryCache = _build_cache()


# ── Convenience helpers ───────────────────────────────────────────────────────

def analytics_key(owner_id: str, endpoint: str, **params: Any) -> str:
    """Build a namespaced cache key for analytics endpoints."""
    parts = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"analytics:{owner_id}:{endpoint}:{parts}"


def food_key(description: str) -> str:
    """Build a namespaced cache key for food analysis results."""
    import hashlib
    digest = hashlib.sha256(description.encode()).hexdigest()[:16]
    return f"food:{digest}"
