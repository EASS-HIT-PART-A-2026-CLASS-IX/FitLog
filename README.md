# 🏋️ FitLog – Fitness & Nutrition Tracking API

FitLog is a full-stack fitness tracking system: FastAPI backend + Streamlit frontend. 

---

**Project Status:**
- ✅ **EX1** – FastAPI Foundations (Backend) – COMPLETE
- ✅ **EX2** – Friendly Interface (Frontend) – COMPLETE  
- ✅ **EX3** – Full-Stack Microservices Build – COMPLETE
  - ✅ Three cooperating services (FastAPI, Streamlit, Celery)
  - ✅ Docker Compose orchestration (PostgreSQL + Redis)
  - ✅ Async refresh with idempotency & bounded concurrency
  - ✅ Security baseline (JWT + password hashing)
  - ✅ Enhancement feature (Workout Summary Analytics)
  - ✅ Comprehensive tests (29 tests passing)
  - ✅ Complete documentation & demo

## Setup

### Prerequisites
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager

```bash
# Install uv if you don't have it
pip install uv
```

### Create environment & install dependencies

```bash
cd FitLog
uv venv
uv sync
```

### Configure your API key

```bash
# Copy the example env file
copy .env.example .env
# Edit .env and add your Gemini API key (already pre-filled for you)
```

---

## Running the API

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:
- **Swagger UI (interactive):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Health check:** http://127.0.0.1:8000/

---

## Running the Frontend (EX2)

Start the API first (see above), then in a separate terminal:

```bash
uv run streamlit run frontend/streamlit_app.py
```

The dashboard will open at: **http://127.0.0.1:8501**

See [frontend/README.md](frontend/README.md) for details on using the dashboard.

---

## Running the Full Stack (EX3) with Docker Compose

For the complete microservices architecture with PostgreSQL, Redis, and Celery workers:

```bash
# Build and start all services
docker compose up -d

# Check status
docker compose ps

# Initialize database
docker compose exec api uv run alembic upgrade head

# Seed sample data
docker compose exec api uv run python scripts/seed.py
```

**Services available:**
- **API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

See [docs/runbooks/compose.md](docs/runbooks/compose.md) for complete Docker Compose guide.

---

## New EX3 Features

### 🆕 Workout Summary Analytics

**Endpoint:** `GET /analytics/{profile_id}/workout-summary`

Get personalized workout insights:

```json
{
  "user_id": "uuid",
  "name": "Alex Fitness",
  "total_workouts": 4,
  "total_volume_kg": 2840.0,
  "most_worked_muscle_group": "legs",
  "workouts_per_week": 1,
  "recommendation": "You're lifting with great volume! Keep pushing leg volume..."
}
```

### 🆕 Async Cache Refresh

**Script:** `scripts/refresh.py`

Refresh user caches with bounded concurrency and Redis idempotency:

```bash
# Refresh single user
uv run python scripts/refresh.py --user-id <UUID>

# Refresh all users
uv run python scripts/refresh.py --all
```

Features:
- Max 5 concurrent tasks
- Redis-backed idempotency
- Exponential backoff retries
- Comprehensive logging

### 🆕 Security Layer

- Password hashing with bcrypt
- JWT token generation & validation (24-hour expiry)
- Role-based access control (RBAC)
- Token rotation & revocation

### 🆕 Celery Async Tasks

Background task processing with Redis broker:

```python
# Generate workout summary with caching
generate_workout_summary(user_id)

# Analyze nutrition patterns
analyze_nutrition(user_id)

# Send weekly digest
send_weekly_digest(user_id)

# Refresh all user caches (idempotent)
refresh_user_cache(user_id)
```

See [app/tasks.py](app/tasks.py) for implementation.

---

## Interactive Demo

Run the complete demo that walks through all features:

```bash
uv run python scripts/demo.py
```

The demo:
1. ✅ Creates a user profile
2. ✅ Calculates protein target
3. ✅ Adds exercises
4. ✅ Logs workouts
5. ✅ Tracks macros
6. ✅ Views workout summary
7. ✅ Chats with AI

---

## Running Tests

```bash
uv run pytest tests/ -v
```

Expected output: **23 tests passing** ✅

---

## Seeding Sample Data (Bonus)

Start the API first, then in a separate terminal:

```bash
uv run python scripts/seed.py
```

This creates a profile, 6 exercises, 4 workout logs, and 3 days of macros.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| **Profile** | | |
| POST | `/profile/` | Create user profile |
| GET | `/profile/` | List profiles |
| GET | `/profile/{id}` | Get profile |
| PUT | `/profile/{id}` | Update profile |
| DELETE | `/profile/{id}` | Delete profile |
| GET | `/profile/{id}/protein-target` | 🥩 **Protein calculator** |
| **Exercises** | | |
| GET | `/exercises/` | List exercises |
| POST | `/exercises/` | Create exercise |
| GET | `/exercises/{id}` | Get exercise |
| PUT | `/exercises/{id}` | Update exercise |
| DELETE | `/exercises/{id}` | Delete exercise |
| **Workout Logs** | | |
| GET | `/logs/` | List workout logs |
| POST | `/logs/` | Log a workout session |
| GET | `/logs/{id}` | Get log |
| PUT | `/logs/{id}` | Update log |
| DELETE | `/logs/{id}` | Delete log |
| **Macros** | | |
| GET | `/macros/` | List macro entries |
| POST | `/macros/` | Log daily macros |
| GET | `/macros/{id}` | Get macro entry |
| PUT | `/macros/{id}` | Update macro entry |
| DELETE | `/macros/{id}` | Delete macro entry |
| **AI Assistant** | | |
| POST | `/ai/chat` | 🤖 Chat with Fitness AI |

---

## Protein Calculator

`GET /profile/{id}/protein-target`

Returns your personalised daily protein target based on body weight and goal:

| Goal | Multiplier | Use case |
|------|-----------|----------|
| `fit` | **1.6 g / kg** | Maintenance & light recomposition (ISSN Position Stand) |
| `muscle` | **2.2 g / kg** | Hypertrophy & bulking (upper optimal range) |

Example response:
```json
{
  "protein_g": 176.0,
  "goal": "muscle",
  "weight_kg": 80.0,
  "multiplier_g_per_kg": 2.2,
  "recommendation": "Based on your weight of 80.0 kg and your 'muscle' goal..."
}
```

---

## AI Fitness Assistant

`POST /ai/chat`

Powered by **Google Gemini 2.0 Flash**. The assistant has full context of your profile, recent workouts, and nutrition data.

```json
{
  "user_id": "<your-profile-id>",
  "message": "How much protein should I eat today?"
}
```

---

## Project Structure

```
FitLog/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Pydantic domain models (updated with WorkoutSummaryOut)
│   ├── db.py                # 🆕 SQLModel ORM definitions
│   ├── database.py          # 🆕 Database connection & sessions
│   ├── security.py          # 🆕 JWT & password hashing
│   ├── tasks.py             # 🆕 Celery async tasks
│   ├── repository.py        # In-memory data store
│   └── routers/
│       ├── exercises.py     # CRUD /exercises
│       ├── workout_logs.py  # CRUD /logs
│       ├── macros.py        # CRUD /macros
│       ├── profile.py       # CRUD /profile + protein target
│       ├── ai_assistant.py  # POST /ai/chat
│       └── analytics.py     # 🆕 GET /analytics/{id}/workout-summary
├── frontend/                # 🆕 Streamlit dashboard
│   ├── streamlit_app.py     # Dashboard application
│   └── README.md            # Frontend documentation
├── tests/                   # pytest test suite (29 tests)
│   ├── conftest.py
│   ├── test_*.py
│   └── test_analytics.py    # 🆕 Analytics tests
├── scripts/
│   ├── seed.py              # Sample data seeder
│   ├── refresh.py           # 🆕 Async cache refresh with idempotency
│   └── demo.py              # 🆕 Interactive demo script
├── docs/
│   ├── EX3-notes.md         # 🆕 Complete EX3 documentation
│   └── runbooks/
│       └── compose.md       # 🆕 Docker Compose guide
├── compose.yaml             # 🆕 Docker Compose config
├── Dockerfile               # 🆕 Container image
├── fitlog.http              # VS Code REST Client playground
├── pyproject.toml           # Dependencies (updated for EX3)
├── README.md                # This file
└── .env                     # API keys & secrets (not committed)
```

---

## AI Assistance

This project was built with the assistance of **Google Gemini (Antigravity)** as a pair-programming advisor. The AI helped with:
- **EX1 (Backend)**: Architecture decisions, repository pattern, protein calculator, test structure
- **EX2 (Frontend)**: Streamlit dashboard design, API integration, form validation
- **EX3 (Microservices)**: Database schema design, Docker Compose setup, Celery async tasks, security implementation, analytics feature, comprehensive documentation

All AI-generated code was reviewed, tested locally, and validated against the FastAPI, SQLModel, Celery, and Streamlit documentation.
