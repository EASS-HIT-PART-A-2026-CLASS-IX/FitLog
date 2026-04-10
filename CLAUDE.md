# FitLog — Project Guide for Claude

## Stack
- **Backend**: FastAPI + SQLModel (SQLite via aiosqlite), Python 3.12, `uv` package manager
- **Frontend**: Streamlit (`frontend/app.py` + `frontend/_ai_fab.py`)
- **Auth**: JWT (python-jose), bcrypt passwords
- **AI**: Groq API (OpenAI-compatible client), model in `settings.groq_model`
- **Cache**: Redis with in-process fallback (`app/cache.py`)
- **Migrations**: Alembic async, SQLite batch mode enabled

## Run the project
```bash
# Backend (port 8000)
uv run uvicorn app.main:app --reload

# Frontend (port 8501) — separate terminal
uv run streamlit run frontend/app.py
```

## Key files
| File | Purpose |
|---|---|
| `app/main.py` | FastAPI app, router registration, exception handlers |
| `app/db.py` | SQLModel table definitions (User, FitnessProfile, Exercise, WorkoutLog, MacroEntry, SleepEntry, HydrationEntry, BodyMetricEntry, RecoveryEntry) |
| `app/models.py` | Pydantic request/response models |
| `app/config.py` | `Settings` (pydantic-settings), single source of truth for env vars |
| `app/database.py` | Async engine, `get_session` dependency, WAL/PRAGMA setup |
| `app/exceptions.py` | Custom error hierarchy: `FitLogError`, `NotFoundError`, `AuthError`, `ConflictError`, `DomainValidationError`, `RateLimitError`, `ExternalServiceError` |
| `app/cache.py` | `cache` singleton (Redis or in-memory), `analytics_key()`, `food_key()` |
| `app/routers/auth.py` | Register, login, JWT helpers, rate limiter |
| `app/routers/exercises.py` | Exercise CRUD |
| `app/routers/workout_logs.py` | Workout log CRUD, profile-scoped |
| `app/routers/macros.py` | Macro CRUD + AI food analysis (Groq) |
| `app/routers/ai_assistant.py` | `POST /ai/chat` — Groq chat with user context |
| `app/routers/analytics.py` | Summary analytics, Redis-cached |
| `app/routers/profile.py` | FitnessProfile CRUD, protein-target endpoint |
| `frontend/app.py` | Streamlit UI — all pages, CSS, API helpers |
| `frontend/_ai_fab.py` | Floating AI coach button (pure JS injected via `components.html`) |
| `alembic/env.py` | Async Alembic config, SQLite batch mode |
| `.env` | Local secrets — never commit |

## Data model relationships
- `User` → many `FitnessProfile`, `Exercise`, `WorkoutLog`, `MacroEntry`, `SleepEntry`, `HydrationEntry`, `BodyMetricEntry`, `RecoveryEntry`
- All workout/nutrition/wellness data is scoped by `owner_id` (user) AND optionally `profile_id` (active profile)
- All IDs are `str(uuid4())`

## Routing conventions
- All routers enforce auth via `Depends(get_current_user_from_header)` — reads `Authorization: Bearer <token>` header
- Never raise `HTTPException` — always use the custom exception classes from `app/exceptions.py`
- Errors return `{"error_code": "...", "detail": "..."}` JSON

## Frontend conventions
- All API calls go through `_get()`, `_post()`, `_delete()` helpers in `app.py`
- Auth token stored in `st.session_state.token`
- Active profile in `st.session_state.selected_profile_id` (str) and `st.session_state.selected_profile_name`
- Data fetchers are `@st.cache_data(ttl=N)` functions keyed by `(token, pid)`; call `.clear()` after mutations
- Sidebar nav: active section = styled `st.markdown` div (no button); inactive = `st.button`
- No emoji in UI — use plain text, monograms, or `×` for delete buttons
- Section headers use `_section_hdr(title)` — renders as small uppercase muted label

## Environment variables (see `.env.example`)
```
SECRET_KEY=...
GROQ_API_KEY=...
DATABASE_URL=sqlite+aiosqlite:///fitlog.db
REDIS_URL=redis://localhost:6379/0   # optional, falls back to in-memory
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GROQ_MODEL=llama-3.3-70b-versatile
```

## Common gotchas
- **SQLAlchemy AsyncSession**: not safe for concurrent coroutines — use sequential awaits, not `asyncio.gather` with the same session
- **Alembic + SQLite**: `render_as_batch=True` required in `env.py` for ALTER TABLE support
- **Streamlit widget keys**: never set `st.session_state[widget_key]` after the widget has rendered in the same run — causes `StreamlitAPIException`
- **Exercise ownership**: exercises are per-user, not shared. Users seed their own library via the Exercises tab in Workouts
