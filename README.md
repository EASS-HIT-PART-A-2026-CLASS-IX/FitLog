# FitLog

Personal fitness and nutrition tracking system. FastAPI backend, Streamlit dashboard, AI coaching via Groq, and optional Redis caching — all runnable locally with a single `uv` command or as a Docker Compose stack.

---

## Features

- **Workout tracking** — log exercises, sets, reps, and weight per session
- **Nutrition logging** — daily macro entries with AI-powered food analysis (describe a meal, get macros back)
- **Wellness tracking** — sleep quality, hydration, body metrics, recovery scores, and daily step counts
- **Fitness profiles** — multiple goal-based profiles per user (muscle, weight loss, endurance, etc.) with per-profile goal targets
- **Analytics dashboard** — weekly volume charts, strength progression, body metrics trend, nutrition trend, and wellness trend; all Redis-cached
- **AI fitness coach** — floating chat button powered by Groq (Llama 3.3 70B); coach reads your profile and recent logs before answering
- **JWT authentication** — bcrypt passwords, 24-hour tokens, per-IP login rate limiting
- **Protein target calculator** — evidence-based g/kg multipliers per goal

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.115+, Python 3.12, `uv` |
| ORM / DB | SQLModel + SQLAlchemy async, SQLite (dev) / PostgreSQL (prod) |
| Migrations | Alembic async, SQLite batch mode |
| Frontend | Streamlit 1.28+ |
| AI | Groq API via openai-compatible client (`openai` SDK) |
| Cache | Redis 7 (falls back to in-process dict when Redis is absent) |
| Auth | python-jose (JWT), bcrypt |
| Charts | Plotly |
| Container | Docker + Docker Compose |

---

## Quick Start (local, no Docker)

### Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) — install once with `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A [Groq API key](https://console.groq.com) (free tier is sufficient)

### 1. Clone and install

```bash
git clone <repo-url>
cd FitLog
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```dotenv
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
GROQ_API_KEY=gsk_your_key_here
```

Everything else has working defaults for local development.

### 3. Start the backend

```bash
uv run uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/

### 4. Start the frontend (separate terminal)

```bash
uv run streamlit run frontend/app.py
```

Dashboard: http://127.0.0.1:8501

### 5. (Optional) Run the database migrations

The API auto-creates tables on first boot via `SQLModel.metadata.create_all`. To apply Alembic-tracked migrations instead:

```bash
uv run alembic upgrade head
```

### 6. (Optional) Seed sample data

```bash
uv run python scripts/seed.py
```

Creates one user, six exercises, four workout logs, and three days of macros.

---

## Docker Compose

The full stack (API + Streamlit frontend + Redis) runs with one command.

### Prerequisites

- Docker Engine 24+ and Docker Compose v2

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, GROQ_API_KEY, and PUBLIC_API_BASE
```

`PUBLIC_API_BASE` must be the URL your **browser** can reach the API at. For local Docker this is `http://localhost:8000`. For a remote server, use the server's IP or domain.

### 2. Start all services

```bash
docker compose up -d
```

### 3. Apply migrations

```bash
docker compose exec api uv run alembic upgrade head
```

### 4. (Optional) Seed data

```bash
docker compose exec api uv run python scripts/seed.py
```

### Service ports

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Frontend | http://localhost:8501 |
| Redis | localhost:6379 (internal only) |

### Useful commands

```bash
docker compose logs -f api        # stream backend logs
docker compose logs -f frontend   # stream frontend logs
docker compose ps                 # check service health
docker compose down               # stop all services
docker compose down -v            # stop and delete volumes (resets DB)
```

---

## Environment Variables

All variables are read from `.env` (or the process environment). The `Settings` class in `app/config.py` is the single source of truth.

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | yes | — | JWT signing key, minimum 32 characters |
| `GROQ_API_KEY` | yes | — | Groq API key from console.groq.com |
| `DATABASE_URL` | no | `sqlite+aiosqlite:///./fitlog.db` | SQLAlchemy async DB URL |
| `REDIS_URL` | no | `redis://localhost:6379/0` | Redis connection URL |
| `JWT_ALGORITHM` | no | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | no | `1440` | Token lifetime (24 h) |
| `APP_ENV` | no | `development` | `development` or `production` |
| `CORS_ORIGINS` | no | localhost:8501 | Comma-separated allowed origins |
| `PUBLIC_API_BASE` | Docker only | `http://localhost:8000` | Browser-reachable API URL for Streamlit |
| `GROQ_MODEL` | no | `llama-3.3-70b-versatile` | Groq model ID |
| `CACHE_TTL_ANALYTICS` | no | `300` | Analytics cache TTL in seconds |
| `CACHE_TTL_FOOD_ANALYSIS` | no | `86400` | Food analysis cache TTL in seconds |

> Generate a secret key: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Project Structure

```
FitLog/
├── app/
│   ├── main.py            # FastAPI app, middleware, router registration
│   ├── config.py          # pydantic-settings: single source of truth for env vars
│   ├── db.py              # SQLModel table definitions (all 9 domain tables)
│   ├── models.py          # Pydantic request/response schemas
│   ├── database.py        # Async engine, session factory, PRAGMA setup
│   ├── security.py        # bcrypt hashing, JWT encode/decode
│   ├── cache.py           # Redis cache with in-process fallback
│   ├── exceptions.py      # Domain exception hierarchy + FastAPI handlers
│   ├── tasks.py           # Celery task definitions (optional background workers)
│   └── routers/
│       ├── auth.py        # POST /auth/register, /auth/login, GET /auth/me
│       ├── profile.py     # CRUD /profile + protein target calculator
│       ├── exercises.py   # CRUD /exercises
│       ├── workout_logs.py# CRUD /logs
│       ├── macros.py      # CRUD /macros + AI food analysis
│       ├── analytics.py   # GET /analytics/* (summary, volume, strength, trends)
│       ├── sleep.py       # CRUD /sleep
│       ├── hydration.py   # CRUD /hydration
│       ├── body_metrics.py# CRUD /body-metrics
│       ├── recovery.py    # CRUD /recovery
│       ├── steps.py       # CRUD /steps
│       └── ai_assistant.py# POST /ai/chat
├── frontend/
│   ├── app.py             # Streamlit dashboard (all pages)
│   └── _ai_fab.py         # Floating AI coach button (injected JS)
├── alembic/
│   ├── env.py             # Async Alembic config, SQLite batch mode
│   └── versions/
│       └── 465e559af203_baseline.py
├── tests/
│   ├── conftest.py
│   └── test_*.py          # pytest test suite
├── scripts/
│   ├── seed.py            # Sample data seeder
│   ├── refresh.py         # Async cache refresh utility
│   └── demo.py            # End-to-end walkthrough script
├── docs/
│   ├── SETTINGS-GUIDE.md
│   ├── SETTINGS-WALKTHROUGH.md
│   └── runbooks/
│       └── compose.md     # Docker Compose operations guide
├── Dockerfile             # Backend container image
├── Dockerfile.frontend    # Frontend container image
├── docker-compose.yml     # Three-service stack (api + frontend + redis)
├── alembic.ini
├── pyproject.toml
├── fitlog.http            # VS Code REST Client playground
├── .env.example
└── CLAUDE.md              # AI assistant project guide
```

---

## API Overview

All protected endpoints require `Authorization: Bearer <token>` header. Errors always return `{"detail": "...", "error": {"code": "...", "message": "..."}}`.

| Tag | Prefix | Key endpoints |
|---|---|---|
| Health | `/` | `GET /` |
| Authentication | `/auth` | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Profiles | `/profile` | CRUD + `GET /profile/{id}/protein-target`, `GET/PUT /profile/{id}/goals` |
| Exercises | `/exercises` | CRUD — user-owned exercise library |
| Workout Logs | `/logs` | CRUD — per-session sets/reps/weight entries |
| Macros | `/macros` | CRUD + `POST /macros/analyze-food` (AI food analysis) |
| Analytics | `/analytics` | `GET /analytics/summary`, `/workout-volume`, `/strength-progress`, `/body-metrics-trend`, `/nutrition-trend`, `/wellness-trend` |
| Sleep | `/sleep` | CRUD |
| Hydration | `/hydration` | CRUD |
| Body Metrics | `/body-metrics` | CRUD |
| Recovery | `/recovery` | CRUD |
| Steps | `/steps` | CRUD |
| AI Assistant | `/ai` | `POST /ai/chat` |

Full interactive documentation is available at `/docs` (Swagger UI) and `/redoc` when the API is running.

---

## Running Tests

```bash
uv run pytest tests/ -v
```

To run with coverage:

```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Course Exercise Checklist

FitLog is the submission project for a three-part university course on full-stack microservices. The table below maps each graded requirement to the relevant files.

### EX1 — FastAPI Foundations

| Requirement | Status | Where |
|---|---|---|
| CRUD endpoints for core resource | Done | `app/routers/exercises.py`, `workout_logs.py`, `macros.py` |
| SQLModel + SQLite persistence | Done | `app/db.py`, `app/database.py` |
| Alembic migrations | Done | `alembic/versions/` |
| pytest + TestClient tests | Done | `tests/test_exercises.py`, `test_workout_logs.py`, `test_macros.py`, … |
| README with uv + run + test instructions | Done | This file |
| **Bonus** — seed script | Done | `scripts/seed.py` |
| **Bonus** — `.http` playground | Done | `fitlog.http` |

### EX2 — Frontend Connected to Backend

| Requirement | Status | Where |
|---|---|---|
| Streamlit dashboard reusing EX1 API | Done | `frontend/app.py` |
| List existing entries | Done | All sections: Workouts, Nutrition, Wellness |
| Add new entry in under a minute | Done | Forms on every section page |
| One small extra | Done | AI food analysis (`POST /macros/analyze-food`), analytics dashboard, AI coach FAB |
| Run side-by-side documentation | Done | [Quick Start](#quick-start-local-no-docker) section above |

### EX3 — Full-Stack Microservices Final Project

| Requirement | Status | Where |
|---|---|---|
| Three cooperating services | Done | FastAPI backend + SQLite/SQLModel + Streamlit frontend |
| Fourth microservice | Done | Groq LLM AI coach (`app/routers/ai_assistant.py`) |
| `docker-compose.yml` + Redis | Done | `docker-compose.yml` |
| Compose runbook | Done | `docs/runbooks/compose.md` |
| `scripts/refresh.py` with bounded concurrency + Redis idempotency | Done | `scripts/refresh.py` |
| `pytest.mark.anyio` async test | **Missing** | Add one test to `tests/` using `pytest.mark.anyio` |
| JWT-protected routes | Done | All protected routes via `get_current_user_from_header` |
| bcrypt hashed credentials | Done | `app/security.py` |
| Per-IP login rate limiting | Done | `app/routers/auth.py` — 10 attempts/60 s |
| Test failing on expired/missing token | **Missing** | Add to `tests/test_auth_security.py` |
| Session 11 docs (rotation steps) | Done | `docs/EX3-notes.md` |
| Thoughtful enhancement | Done | Wellness tracking, strength progression, AI food analysis |
| Tests covering the enhancement | Done | `tests/test_ai_assistant.py`, `test_body_metrics.py`, … |
| Demo script | Done | `scripts/demo.py` |

**Two gaps remaining for full EX3 marks:**

1. Add a `pytest.mark.anyio` test (Session 09 requirement). Example — test `scripts/refresh.py` directly:

```python
# tests/test_refresh.py
import pytest
import pytest_asyncio

@pytest.mark.anyio
async def test_refresh_runs_without_error():
    from scripts.refresh import run_refresh
    await run_refresh(dry_run=True)
```

2. Add auth-failure tests (Session 11 requirement):

```python
# tests/test_auth_security.py
def test_expired_token_is_rejected(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer expired.token.here"})
    assert response.status_code == 401

def test_missing_token_is_rejected(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
```

---

## Contributing

1. Fork the repository and create a feature branch from `main`.
2. Install dev dependencies: `uv sync --extra dev`
3. Write tests for new functionality before implementing it (see `tests/`).
4. Ensure all existing tests pass: `uv run pytest tests/`
5. Follow the existing code conventions:
   - Type annotations on all function signatures
   - Raise `FitLogError` subclasses from `app/exceptions.py` — never `HTTPException`
   - Use `app/config.py` settings — no hardcoded values
   - Keep routers thin: validate input, call logic, return response
6. Open a pull request with a clear description of the change.
