# FitLog — EX3 Implementation Notes

**Due:** 2026-07-01  
**Repo:** FitLog — Full-Stack Fitness Tracking Microservices

---

## 1. Three Cooperating Services

| Service | Start command | Port |
|---------|---------------|------|
| FastAPI backend | `uv run uvicorn app.main:app --reload` | 8000 |
| SQLite/SQLModel persistence | embedded in backend | — |
| Streamlit frontend | `uv run streamlit run frontend/app.py` | 8501 |
| Groq AI assistant (4th service) | loaded by backend on demand | — |

### Architecture

```
Streamlit (8501)
      │ HTTP
      ▼
FastAPI (8000)
  ├── SQLite via aiosqlite    ← persistence layer
  ├── Redis (optional)        ← analytics cache + rate-limit store
  └── Groq API                ← 4th microservice (LLM tool)
```

All services run locally with `docker compose up` or individually with `uv run`.

### Key files

```
app/
  main.py          FastAPI entry point, router registration, CORS
  db.py            SQLModel table definitions (User, FitnessProfile,
                   Exercise, WorkoutLog, MacroEntry, SleepEntry,
                   HydrationEntry, BodyMetricEntry, RecoveryEntry)
  models.py        Pydantic request/response models
  config.py        pydantic-settings Settings class
  database.py      Async engine, get_session, WAL+PRAGMA setup
  security.py      bcrypt hashing, JWT creation/validation
  cache.py         Redis-backed cache with in-process fallback
  routers/
    auth.py        POST /auth/register, /auth/login, /auth/me
    profile.py     FitnessProfile CRUD, protein-target calculator
    exercises.py   Exercise CRUD (per-user)
    workout_logs.py Workout log CRUD
    macros.py      Nutrition CRUD + Groq food analysis
    analytics.py   Workout summary + progress analytics (EX3 enhancement)
    ai_assistant.py POST /ai/chat — Groq LLM with user context
    sleep.py / hydration.py / body_metrics.py / recovery.py
frontend/
  app.py           Streamlit UI (all pages + auth flow)
  _ai_fab.py       Floating AI coach button (JS injected via components.html)
scripts/
  refresh.py       Async cache refresh (Session 09 deliverable)
  demo.py          End-to-end demo script
  seed.py          Sample data seeder
tests/             pytest suite (11+ test files, auth fixtures)
docs/
  EX3-notes.md     This file
  runbooks/compose.md  Docker Compose operational guide
```

---

## 2. Docker Compose Orchestration (`compose.yaml`)

Services: `redis`, `api`, `frontend`.  
See [docs/runbooks/compose.md](runbooks/compose.md) for full operating instructions.

```bash
# Start everything
docker compose up --build -d

# Verify
curl http://127.0.0.1:8000/       # {"status":"ok"}
docker compose exec redis redis-cli ping   # PONG
```

### Health / rate-limit headers

The login endpoint enforces 10 req/60s per email address.  
Verify with:

```bash
curl -s -D - -o /dev/null -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"x@x.com","password":"x"}'
```

### Running Schemathesis in CI

```bash
uv run schemathesis run http://127.0.0.1:8000/openapi.json --checks all
```

---

## 3. Async Cache Refresh — `scripts/refresh.py` (Session 09)

### What it does

| Feature | Implementation |
|---------|---------------|
| Bounded concurrency | `asyncio.Semaphore(5)` — max 5 simultaneous refreshes |
| Redis idempotency | `SETEX refresh:idempotency:{profile_id} 3600 in_progress` prevents duplicate runs within 1 hour |
| Retries | Exponential backoff: 2^N seconds, up to 3 attempts |
| Async HTTP | `httpx.AsyncClient` calls `GET /analytics/{id}/workout-summary` |

### Usage

```bash
# Set a valid JWT for authenticated API calls
export REFRESH_API_TOKEN="<token from /auth/login>"

# Refresh one profile
uv run python scripts/refresh.py --profile-id <UUID>

# Refresh all profiles (bounded concurrency)
uv run python scripts/refresh.py --all
```

### Redis trace example

```
[INFO] Refreshing 3 profile(s) (max 5 concurrent)

[CACHE] SET refresh:idempotency:abc-123 → 'in_progress' (TTL: 3600s)
[CACHE] SETEX workout_summary:abc-123 → refreshed
[LOG]   Refreshed profile abc-123
        - Total workouts: 12
        - Total volume:   8400 kg
        - Most worked:    legs

[CACHE] SET refresh:idempotency:def-456 → 'in_progress' (TTL: 3600s)
[SKIP]  ghi-789 — refresh already in progress

==============================
  Successful : 2
  Failed     : 0
  Skipped    : 1
==============================
```

### anyio test

`tests/test_refresh.py` contains five `@pytest.mark.anyio` tests:

```bash
uv run pytest tests/test_refresh.py -v
```

---

## 4. Security Baseline (Session 11)

### Password hashing

`app/security.py` — bcrypt with 12 salt rounds:

```python
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

Legacy PBKDF2 hashes are supported for migration.

### JWT-protected routes

Every router uses `Depends(get_current_user_from_header)`.  
Token payload: `{"user_id": "<uuid>", "email": "...", "exp": ...}`.  
Default expiry: 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

```python
# app/routers/auth.py
async def get_current_user_from_header(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not authorization:
        raise AuthError("Missing authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    payload = verify_token(token)
    if not payload:
        raise AuthError("Invalid or expired token")
    ...
```

### Role model

All resources are owner-scoped: every DB query filters by `owner_id == current_user.id`.  
This prevents horizontal privilege escalation (user A cannot access user B's data).

### Key rotation steps

1. Generate a new secret:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Update `SECRET_KEY` in `.env` and redeploy.
3. All existing tokens are immediately invalidated (they were signed with the old key).
4. Users must log in again to obtain a new token.

### Security tests

`tests/test_auth_security.py` covers:

```bash
uv run pytest tests/test_auth_security.py -v
```

| Test | Asserts |
|------|---------|
| `test_exercises_no_token` | 401 with no Authorization header |
| `test_expired_token_rejected` | 401 with `exp = now - 1s` |
| `test_malformed_token_rejected` | 401 with garbage JWT string |
| `test_token_with_nonexistent_user` | 401/404 for phantom user_id |
| `test_valid_token_accepted` | 200 for fresh token |

---

## 5. Enhancement Feature — Analytics API

`GET /analytics/{profile_id}/workout-summary` is the EX3 enhancement:

- Calculates total volume (`sets × reps × weight_kg`) across all logs
- Identifies most-worked muscle group
- Generates goal-specific recommendation (muscle / weight-loss / general)
- Returns `WorkoutSummaryOut` JSON

Additional analytics endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /analytics/summary` | Dashboard KPIs (streak, weekly workouts, avg calories) |
| `GET /analytics/workout-volume` | Weekly volume aggregated by ISO week |
| `GET /analytics/strength-progress` | Per-exercise 1RM progression |
| `GET /analytics/body-metrics-trend` | Weight, BMI, body fat over time |
| `GET /analytics/nutrition-trend` | Daily macro totals |
| `GET /analytics/wellness-trend` | Sleep, hydration, recovery composite score |

All results are cached in Redis (TTL: configurable) with `app/cache.py`.

### Tests

```bash
uv run pytest tests/test_analytics.py -v
```

---

## 6. Demo Script

```bash
# Requires API running on :8000
uv run python scripts/demo.py

# Or use the shell wrapper:
bash scripts/demo.sh
```

Flow:
1. Registers a fresh demo user (safe to re-run)
2. Creates a fitness profile
3. Shows protein target recommendation
4. Adds 4 exercises to the library
5. Logs 4 workouts
6. Logs daily macros
7. Calls `GET /analytics/{id}/workout-summary` (EX3 enhancement)
8. Optionally calls the AI coach

---

## 7. Test Suite

```bash
# Run everything
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=app --cov-report=term-missing

# Run only security tests
uv run pytest tests/test_auth_security.py -v

# Run only anyio async tests
uv run pytest tests/test_refresh.py -v
```

| File | Focus |
|------|-------|
| `test_auth_security.py` | Expired/missing/tampered tokens |
| `test_analytics.py` | Workout summary + analytics endpoints |
| `test_refresh.py` | `pytest.mark.anyio` async tests |
| `test_exercises.py` | Exercise CRUD |
| `test_workout_logs.py` | Workout log CRUD |
| `test_macros.py` | Nutrition CRUD |
| `test_profile.py` | Fitness profile CRUD |
| `test_body_metrics.py` | Body metrics CRUD |
| `test_sleep.py` | Sleep entry CRUD |
| `test_hydration.py` | Hydration CRUD |
| `test_recovery.py` | Recovery CRUD |

---

## 8. AI Assistance

Built with Claude (Anthropic) as the primary pair-programming tool throughout EX1–EX3.

AI-assisted areas:
- Architecture design (SQLModel schema, router layout, cache strategy)
- Security implementation (bcrypt, JWT, rate limiting)
- Async patterns (anyio tests, bounded semaphore refresh script)
- Docker Compose orchestration
- Analytics feature (volume calculation, 1RM Epley formula, wellness trend)
- Streamlit UI (dark/light theme, profile cards, AI FAB)
- Comprehensive test suite and fixtures

All code was reviewed locally against FastAPI, SQLModel, and httpx documentation before committing.
