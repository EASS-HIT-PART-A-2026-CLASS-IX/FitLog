# Architecture Improvements — Tasks

## 1. Configuration (P0)
- [x] 1.1 Create `app/config.py` with `Settings(BaseSettings)` subclass
- [x] 1.2 Replace `os.getenv` in `app/security.py` with `settings.secret_key`
- [x] 1.3 Replace `os.getenv` in `app/tasks.py` with `settings.redis_url`
- [x] 1.4 Replace `os.getenv` in `app/routers/ai_assistant.py` with `settings.groq_api_key`
- [x] 1.5 Replace `os.getenv` in `app/database.py` with `settings.database_url`
- [x] 1.6 Update `.env.example` with all required variables

## 2. Error Handling (P0)
- [x] 2.1 Create `app/exceptions.py` with `FitLogError` hierarchy
- [x] 2.2 Implement `register_exception_handlers(app)` helper
- [x] 2.3 Call it from `app/main.py`
- [x] 2.4 Migrate all routers from HTTPException → FitLogError subclasses
  - [x] auth.py (AuthError, ConflictError, DomainValidationError, NotFoundError, RateLimitError)
  - [x] profile.py (NotFoundError)
  - [x] exercises.py (NotFoundError)
  - [x] workout_logs.py (NotFoundError)
  - [x] macros.py (NotFoundError, ExternalServiceError)
  - [x] analytics.py (NotFoundError)
  - [x] sleep.py (NotFoundError)
  - [x] hydration.py (NotFoundError)
  - [x] body_metrics.py (NotFoundError)
  - [x] recovery.py (NotFoundError)

## 3. CORS Hardening (P0)
- [x] 3.1 Remove `allow_origins=["*"]` from `main.py`
- [x] 3.2 Use `settings.cors_origins` instead
- [x] 3.3 Restrict methods and headers to explicit set

## 4. Structured Logging (P1)
- [x] 4.1 Configure `logging.dictConfig` in `main.py`
- [x] 4.2 Replace `print()` in `tasks.py` with logger
- [x] 4.3 Fix `datetime.utcnow()` → `datetime.now(timezone.utc)` in tasks.py
- [x] 4.4 Fix Groq exception detail leakage in `ai_assistant.py` and `macros.py`
- [x] 4.5 Add rate limiting on login endpoint in `auth.py`

## 5. Analytics API (P1)
- [x] 5.1 `GET /analytics/summary`
- [x] 5.2 `GET /analytics/workout-volume`
- [x] 5.3 `GET /analytics/strength-progress`
- [x] 5.4 `GET /analytics/body-metrics-trend`
- [x] 5.5 `GET /analytics/nutrition-trend`
- [x] 5.6 `GET /analytics/wellness-trend`

## 6. Repository Pattern (P2)
- [ ] 6.1 Create `app/repositories/base.py` with `BaseRepository[T]`
- [ ] 6.2 Create concrete repos for each aggregate
- [ ] 6.3 Refactor routers to use repos

## 7. Database Migrations (P2)
- [x] 7.1 Init Alembic with async template (`uv run alembic init --template async alembic`)
- [x] 7.2 Configure `alembic/env.py` to use `settings.database_url` + `SQLModel.metadata`
- [ ] 7.3 Generate baseline migration: `uv run alembic revision --autogenerate -m "baseline"`

## 8. Caching Layer (P3)
- [x] 8.1 Create `app/cache.py` with Redis wrapper + in-process fallback
- [x] 8.2 Cache `GET /analytics/summary` (5-min TTL via `settings.cache_ttl_analytics`)
- [x] 8.3 Cache food analysis in `POST /macros/analyze-food` (24-hr TTL via `settings.cache_ttl_food_analysis`)
