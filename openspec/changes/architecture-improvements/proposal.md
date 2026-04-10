# Architecture Improvements — Proposal

## Why

FitLog has grown into a multi-domain app covering workouts, nutrition, AI chat,
wellness, and analytics. The foundational patterns that served the prototype are
now leaking across boundaries: routers read environment variables directly,
embed raw SQL queries, raise `HTTPException` with free-form strings, and
duplicate upstream client construction.

This change introduces the architectural primitives the app needs to scale past
the prototype stage without a rewrite.

## What Changes

- **Configuration**: `app/config.py` with `pydantic-settings` as the single
  source of truth. Fail fast on missing required secrets.
- **Error handling**: `app/exceptions.py` with a `FitLogError` hierarchy and
  global handlers emitting a consistent JSON error envelope.
- **Repository pattern**: `app/repositories/` decoupling persistence from routers.
- **Database migrations**: Adopt Alembic. Replace hand-rolled `_migrate_add_profile_id`.
- **Caching layer**: `app/cache.py` wrapping Redis with graceful degradation.
- **CORS hardening**: Explicit origins from settings, no wildcard.
- **Structured logging**: Replace `print()` with `logging` module throughout.

## Already Implemented (this session)

- [x] `app/config.py` — pydantic-settings Settings singleton
- [x] `app/exceptions.py` — FitLogError hierarchy + handlers
- [x] `app/security.py` — uses `settings.secret_key`, no random fallback
- [x] `app/main.py` — registers handlers, explicit CORS, structured logging
- [x] `app/tasks.py` — logging module, `datetime.now(timezone.utc)`
- [x] `app/routers/auth.py` — rate limiting on login
- [x] `app/routers/ai_assistant.py` — uses settings, no exception detail leakage
- [x] `app/routers/analytics.py` — 6 new analytics endpoints

## Impact

- `app/config.py` (new)
- `app/exceptions.py` (new)
- `app/security.py` (updated)
- `app/main.py` (updated)
- `app/tasks.py` (updated)
- `app/routers/auth.py` (updated)
- `app/routers/ai_assistant.py` (updated)
- `app/routers/analytics.py` (updated — 6 new endpoints)
