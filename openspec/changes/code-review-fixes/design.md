## Context

FitLog has two generations of routers: the mature routers (`workout_logs.py`, `macros.py`) with full CRUD, and the newer wellness routers (`sleep.py`, `hydration.py`, `body_metrics.py`, `recovery.py`) added in the `health-wellness-ui-overhaul` change that only have POST, GET-list, and DELETE. Tests are structurally broken because they call auth-protected endpoints without tokens. The `SECRET_KEY` fallback silently regenerates on every restart, invalidating sessions.

## Goals / Non-Goals

**Goals:**
- Bring wellness routers to full CRUD parity with `workout_logs.py`
- Make test fixtures produce authenticated requests
- Fail loudly at startup if `SECRET_KEY` is missing so developers notice immediately

**Non-Goals:**
- Adding rate limiting, pagination to the new endpoints, or Alembic migrations
- Changing any existing endpoint signatures or response shapes
- Refactoring the `workout_logs.py` or `macros.py` routers

## Decisions

**D1 — Partial-update schemas (Optional fields)**
Update schemas for wellness entries will use all-optional fields (like Pydantic `Optional[...]`) so callers can PATCH individual fields. This matches the pattern in `workout_logs.py` which already has an update body. Only fields provided will be overwritten.

*Alternative considered:* Full-replacement PUT with all fields required — rejected because it forces callers to re-send unchanged fields and is less ergarious for a mobile/frontend that may only update one slider.

**D2 — Ownership validated on GET/{id} and PUT/{id}**
Both new endpoints filter by `owner_id == current_user.id` before returning or updating, the same pattern used in DELETE. This prevents horizontal privilege escalation.

**D3 — Conftest auth fixtures use real endpoints**
`registered_user` fixture calls `POST /auth/register` then `POST /auth/token` to get a real JWT. `auth_headers` returns the `Authorization: Bearer <token>` dict. This tests the full auth stack and avoids mocking.

*Alternative:* Create a token directly with `create_access_token()` — rejected because it bypasses registration and doesn't test the full user creation path.

**D4 — SECRET_KEY startup behavior**
`app/security.py` will raise a `RuntimeError` at import time if `SECRET_KEY` is not set and `APP_ENV != "development"`. In development (default), it keeps the current warning-and-generate behavior to avoid breaking local runs without a `.env` file.

*Alternative:* Always fail — rejected because it would break all existing developer setups without a migration period.

## Risks / Trade-offs

- **Generated key still used in development** → Developers who run without `.env` will still lose sessions on restart; accepted trade-off since production is protected.
- **Optional-field update schemas** → A caller sending `{}` (empty body) will make no changes and get a 200 back — this is intentional but should be documented in the endpoint summary.
- **Test fixtures call real endpoints** → If the auth endpoints have a bug, all tests fail. This is the correct behavior (integration tests should catch auth bugs).

## Migration Plan

1. Add update Pydantic schemas to `app/models.py`
2. Add `GET /{id}` and `PUT /{id}` to each wellness router
3. Update `tests/conftest.py` with auth fixtures
4. Update `app/security.py` with env-aware startup check
5. No database schema changes needed; no rollback required
