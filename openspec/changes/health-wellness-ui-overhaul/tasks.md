## 1. Fix UI Flicker & Polish (quick wins first)

- [x] 1.1 Remove spinner/status wrappers from cached API calls in `frontend/app.py` to eliminate the "get_macros is running" flicker
- [x] 1.2 Add session_state first-load flag to show a single loading placeholder on initial dashboard load only

## 2. Backend — New Health Models in `app/db.py`

- [x] 2.1 Add `SleepEntry` SQLModel table (date, sleep_hours, sleep_quality, notes, owner_id, profile_id)
- [x] 2.2 Add `HydrationEntry` SQLModel table (date, water_ml, notes, owner_id, profile_id)
- [x] 2.3 Add `BodyMetricEntry` SQLModel table (date, weight_kg, body_fat_pct, waist_cm, resting_hr, notes, owner_id, profile_id)
- [x] 2.4 Add `RecoveryEntry` SQLModel table (date, soreness_level, energy_level, stress_level, mood, notes, owner_id, profile_id)
- [x] 2.5 Add relationships for new models on the `User` model

## 3. Backend — Pydantic Schemas in `app/models.py`

- [x] 3.1 Add Create/Out schemas for SleepEntry (SleepEntryCreate, SleepEntryOut)
- [x] 3.2 Add Create/Out schemas for HydrationEntry (HydrationEntryCreate, HydrationEntryOut)
- [x] 3.3 Add Create/Out schemas for BodyMetricEntry (BodyMetricEntryCreate, BodyMetricEntryOut)
- [x] 3.4 Add Create/Out schemas for RecoveryEntry (RecoveryEntryCreate, RecoveryEntryOut)
- [x] 3.5 Expand FitnessProfile goal validation to accept the new goal options (weight_loss, maintenance, general_health, endurance, flexibility, hypertrophy, strength, athletic_performance) while keeping fit/muscle

## 4. Backend — API Routers

- [x] 4.1 Create `app/routers/sleep.py` with POST /sleep/, GET /sleep/, DELETE /sleep/{id} endpoints
- [x] 4.2 Create `app/routers/hydration.py` with POST /hydration/, GET /hydration/, DELETE /hydration/{id} endpoints
- [x] 4.3 Create `app/routers/body_metrics.py` with POST /body-metrics/, GET /body-metrics/, DELETE /body-metrics/{id} endpoints
- [x] 4.4 Create `app/routers/recovery.py` with POST /recovery/, GET /recovery/, DELETE /recovery/{id} endpoints
- [x] 4.5 Register all new routers in `app/main.py`

## 5. Frontend — Expanded Goal Options

- [x] 5.1 Update profile creation form in `frontend/app.py` to show the full list of goal options with user-friendly labels

## 6. Frontend — AI Assistant on Dashboard

- [x] 6.1 Remove the floating chat widget (`show_ai_chatbot` with position:fixed CSS)
- [x] 6.2 Add an inline AI assistant panel in the right column of the dashboard with chat input, quick-action buttons, and message history

## 7. Frontend — Wellness Tab

- [x] 7.1 Add "Wellness" tab to main navigation (between Nutrition and Profile)
- [x] 7.2 Add Sleep sub-tab with log form (date, hours, quality 1-5, notes) and history view
- [x] 7.3 Add Hydration sub-tab with log form (date, water_ml, notes) and history view
- [x] 7.4 Add Body Metrics sub-tab with log form (date, weight, body_fat, waist, resting_hr, notes) and history view
- [x] 7.5 Add Recovery sub-tab with log form (date, soreness/energy/stress/mood 1-5, notes) and history view

## 8. Frontend — Wellness Dashboard Summary

- [x] 8.1 Add cached API client functions for sleep, hydration, body_metrics, recovery data
- [x] 8.2 Add wellness summary card on dashboard showing today's sleep, water, weight, and recovery scores
- [x] 8.3 Add 7-day trend indicators (up/down/stable) for weight and sleep when sufficient data exists

## 9. Tests

- [x] 9.1 Add tests for sleep CRUD endpoints
- [x] 9.2 Add tests for hydration CRUD endpoints
- [x] 9.3 Add tests for body metrics CRUD endpoints
- [x] 9.4 Add tests for recovery CRUD endpoints
- [x] 9.5 Add test for expanded goal validation (new values accepted, invalid rejected)
