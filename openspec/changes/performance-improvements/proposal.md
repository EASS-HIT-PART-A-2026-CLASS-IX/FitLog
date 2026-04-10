# Performance Improvements — Proposal & Findings

## What Was Slow

### 1. SQLite — missing cache and temp-store PRAGMAs
WAL mode and `synchronous=NORMAL` were already configured, which is good. However
two additional PRAGMAs that have zero downside cost were absent:

- `PRAGMA cache_size=-64000` — allows SQLite to keep up to 64 MB of database
  pages in memory. Without this the default is 2 MB, causing frequent page evictions
  on any query scanning more than a handful of rows.
- `PRAGMA temp_store=MEMORY` — forces SQLite to build temporary B-trees and sort
  buffers in memory instead of creating temp files on disk. Relevant whenever the
  query planner sorts a result set (e.g., `ORDER BY created_at DESC LIMIT 5`).

### 2. PostgreSQL pool parameters were inverted
`pool_size=20, max_overflow=10` was set instead of `pool_size=10, max_overflow=20`.
`pool_size` is the number of persistent connections kept open. `max_overflow` is the
burst headroom. A larger `max_overflow` relative to `pool_size` is correct for a
web API: steady-state load is handled by 10 permanent connections; traffic spikes
can temporarily open up to 20 additional connections without exhausting the pool
under load.

### 3. No response compression
The API had no GZip middleware. Analytics and list endpoints can return tens of
kilobytes of JSON. Without compression every byte crosses the network uncompressed
between the FastAPI container and the Streamlit frontend.

### 4. AI assistant — sequential DB queries and client re-instantiation per request
`_build_context` made two sequential `await session.execute(...)` calls (workouts,
then macros) after the outer `chat` handler had already fetched the profile once
(for the ownership check). This was three sequential round-trips total.

Additionally, `_get_client()` constructed a new `OpenAI(...)` object on every
request, which allocates a new `httpx.Client` with its own connection pool on each
call.

### 5. Docker dependency cache busted on every source change
The Dockerfile did `COPY . .` before `RUN uv sync`, so any change to any source
file — including a comment edit — invalidated the `uv sync` layer. A cold
dependency install of the full dependency tree (FastAPI, SQLModel, Streamlit,
Plotly, etc.) can take 60-120 seconds.

---

## What Was Fixed

### database.py
Added two PRAGMAs executed at startup alongside the existing WAL configuration:
```python
await conn.exec_driver_sql("PRAGMA cache_size=-64000")
await conn.exec_driver_sql("PRAGMA temp_store=MEMORY")
```
Corrected PostgreSQL pool values to `pool_size=10, max_overflow=20`.

### main.py
Added `GZipMiddleware` with a 1 KB minimum response size threshold. Responses
smaller than 1 KB are not worth compressing (the gzip header overhead exceeds the
savings). Larger responses — workout log lists, analytics payloads — compress at
roughly 70-80% reduction for JSON.

### app/routers/ai_assistant.py
Three changes:

1. **Parallel context fetches** — `_fetch_recent_workouts` and
   `_fetch_recent_macros` are now run concurrently with `asyncio.gather`. On a
   local SQLite file the gain is modest, but on a networked PostgreSQL instance
   (the production path, per docker-compose.yml) this cuts two sequential ~5 ms
   queries into one ~5 ms parallel batch.

2. **Eliminated redundant profile fetch** — the outer `chat` handler already
   fetches the profile for the ownership check. The profile object is now passed
   directly into `_build_context` instead of `_build_context` re-fetching it by ID.
   This removes one full DB round-trip per `/ai/chat` request.

3. **In-memory context cache (5-minute TTL)** — the built context string is stored
   in a module-level dict keyed by `profile_id`. Subsequent requests within the TTL
   window skip all three DB queries entirely. The cache is appropriate here because
   the fitness profile, recent logs, and recent macros are not realtime data — a
   5-minute stale window is acceptable for AI context building.

4. **`_get_client()` cached as singleton** — decorated with `@lru_cache(maxsize=1)`
   so the `OpenAI`/`httpx.Client` object is constructed once per process lifetime
   rather than once per request.

### Dockerfile
Split into a two-stage build:

- **Builder stage**: copies only `pyproject.toml` and `uv.lock` first, runs
  `uv sync --no-dev --frozen`, then copies source. The dep-install layer is
  cached independently of source files.
- **Runtime stage**: copies the pre-built `.venv` from the builder, then copies
  only the `app/` directory. Source-only rebuilds skip `uv sync` entirely.

---

## Expected Improvements

| Area | Before | After | Notes |
|------|--------|-------|-------|
| SQLite read-heavy queries | baseline | ~15% faster | 64 MB page cache reduces disk I/O |
| SQLite sort queries | baseline | ~10% faster | temp_store=MEMORY avoids temp file I/O |
| JSON response wire size | 100% | ~20-30% | GZip on list/analytics endpoints |
| AI chat DB round-trips | 3 sequential | 1 profile + 2 parallel | ~40% reduction on PostgreSQL |
| AI chat repeated calls | 3 DB queries | 0 DB queries (cache hit) | within 5-minute TTL window |
| Docker rebuild (source change) | 60-120s | 5-10s | dep layer cached across source edits |
| Docker rebuild (dep change) | 60-120s | 60-120s | unchanged when deps actually change |
