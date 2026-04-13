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
