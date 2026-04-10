## Context

FitLog is a FastAPI + Streamlit fitness tracker using SQLModel/SQLite with JWT auth. It currently has 4 database tables (users, fitness_profiles, exercises, workout_logs, macro_entries) and a Streamlit frontend with tabs for Dashboard, Training, Nutrition, and Profile. The AI assistant (Groq-powered) is accessed via a floating chat button. The frontend suffers from visible API status flicker during Streamlit re-renders and the AI assistant is not discoverable enough.

## Goals / Non-Goals

**Goals:**
- Add 4 new health tracking domains (sleep, hydration, body metrics, recovery) with full CRUD
- Expand profile goal options beyond `fit | muscle`
- Embed AI assistant directly in the main dashboard for immediate visibility
- Fix the status message flicker ("get_macros is running" blinking)
- Create a Wellness tab that aggregates all health data
- Keep the same tech stack (FastAPI, SQLModel, Streamlit, SQLite)

**Non-Goals:**
- No mobile app or PWA — Streamlit web only
- No real-time sync or WebSocket push
- No third-party integrations (wearables, Apple Health, Google Fit)
- No complex charting library — use Streamlit's built-in metrics and simple HTML
- No database migration tool (Alembic) — SQLModel auto-create for now
- No gamification or social features

## Decisions

### 1. Four new SQLModel tables following existing patterns

**Decision**: Add `SleepEntry`, `HydrationEntry`, `BodyMetricEntry`, `RecoveryEntry` tables following the same structure as `MacroEntry` (owner_id, profile_id, date field, created_at, domain-specific fields).

**Rationale**: Consistent with existing codebase patterns. Each table has its own router, base model, and Pydantic schemas — exactly how workouts and macros work today. No new abstractions needed.

**Alternative considered**: Single `HealthEntry` table with JSON blob for different types. Rejected because it sacrifices type safety, validation, and queryability.

### 2. Expand goal field to free-choice from a wider enum

**Decision**: Change `FitnessProfile.goal` from accepting only `fit | muscle` to accepting `weight_loss | maintenance | general_health | endurance | flexibility | hypertrophy | strength | athletic_performance`. Keep it as a string field with Pydantic validation on input.

**Rationale**: A wider enum is better than free text — it stays structured for AI recommendations while being more expressive. The string field in SQLModel doesn't need schema migration, just validation changes.

### 3. AI assistant embedded in dashboard, not floating button

**Decision**: Replace the floating chat widget with an inline AI panel in the right column of the dashboard. Keep the toggle but make it a visible card with a chat interface, not a position:fixed overlay.

**Rationale**: The floating button CSS doesn't render reliably in Streamlit's iframe-based architecture. An inline panel is native Streamlit and always visible. Users see the AI immediately on login.

### 4. Fix status flicker with Streamlit caching pattern

**Decision**: The blinking "get_macros is running" messages are caused by `st.spinner` or `st.status` calls wrapping cached API functions. Fix by removing spinners from cached calls and only showing loading state on the initial uncached load. Use `st.session_state` flags to track first-load vs re-render.

**Rationale**: Streamlit re-runs the entire script on every interaction. Cached functions return instantly on subsequent runs, but any wrapping spinner/status still flashes briefly. The fix is to not wrap cached calls in status indicators.

### 5. New "Wellness" navigation tab

**Decision**: Add a 5th tab "Wellness" between Nutrition and Profile in the main navigation. This tab has sub-tabs for Sleep, Hydration, Body Metrics, and Recovery — each with a log form and history view.

**Rationale**: Keeps the existing tab structure clean. Users who only want gym + nutrition aren't affected. The dashboard aggregates wellness data for users who track it.

### 6. Backend router structure — one router per domain

**Decision**: Add `routers/sleep.py`, `routers/hydration.py`, `routers/body_metrics.py`, `routers/recovery.py` following the same CRUD pattern as `routers/macros.py`.

**Rationale**: Consistent with existing architecture. Each router is self-contained and testable.

## Risks / Trade-offs

- **[Risk] Dashboard performance with 5+ API calls** → Mitigate with aggressive `@st.cache_data` TTLs and only fetching today's data for the wellness summary.
- **[Risk] Scope creep — too many new tables at once** → Mitigate by keeping each health domain minimal (3-5 fields per model, basic CRUD only, no analytics in v1).
- **[Risk] Goal enum expansion breaks existing profiles** → Mitigate: old values `fit` and `muscle` remain valid in the new enum, so existing data is unaffected.
- **[Trade-off] No database migrations** → SQLModel `create_all()` will add new tables but existing tables are untouched. The `goal` field is already a string so no ALTER needed.
- **[Trade-off] Inline AI panel takes dashboard space** → Acceptable because it replaces the unreliable floating widget and is the user's stated priority.
