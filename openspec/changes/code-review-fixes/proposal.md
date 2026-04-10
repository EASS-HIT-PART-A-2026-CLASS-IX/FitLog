## Why

A code review identified several bugs and gaps in the codebase: wellness routers (sleep, hydration, body_metrics, recovery) are missing GET-by-id and PUT endpoints that the older routers have; test fixtures don't authenticate, making them useless for auth-protected endpoints; and a missing `SECRET_KEY` silently generates a random key at startup, logging out all users on every restart.

## What Changes

- Add `GET /{id}` (fetch single entry) and `PUT /{id}` (update entry) endpoints to all 4 wellness routers, matching the pattern already established in `workout_logs.py`
- Add `registered_user` and `auth_headers` fixtures to `tests/conftest.py` so test helpers can make authenticated requests
- Replace the silent random-key fallback in `app/security.py` with a hard startup failure when `SECRET_KEY` is not set in production environments

## Capabilities

### New Capabilities

- `wellness-router-crud`: Full CRUD on wellness routers — adds the missing GET/{id} and PUT/{id} endpoints to sleep, hydration, body_metrics, and recovery routers
- `test-auth-fixtures`: Authenticated test fixtures — adds register/login helpers to conftest.py so tests can call auth-protected endpoints
- `secret-key-validation`: Strict SECRET_KEY validation at startup — fails fast with a clear error when the env var is missing instead of silently generating an ephemeral key

### Modified Capabilities

## Impact

- `app/routers/sleep.py`, `app/routers/hydration.py`, `app/routers/body_metrics.py`, `app/routers/recovery.py` — new endpoints added
- `app/models.py` — may need `SleepEntryUpdate`, `HydrationEntryUpdate`, `BodyMetricEntryUpdate`, `RecoveryEntryUpdate` Pydantic schemas
- `app/security.py` — startup behavior change (breaking in dev if SECRET_KEY not set)
- `tests/conftest.py` — new fixtures; existing fixture subjects that need auth will now work correctly
