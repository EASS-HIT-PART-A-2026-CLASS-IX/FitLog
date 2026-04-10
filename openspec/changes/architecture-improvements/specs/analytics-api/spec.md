# Analytics API — Personal Progress Dashboard

## Summary

Extends `app/routers/analytics.py` with six new endpoints that power a personal
progress dashboard. All endpoints are authenticated via
`get_current_user_from_header` and scope every query to the requesting user's
data. Empty datasets return empty lists (no 500 errors).

---

## New Pydantic Schemas (`app/models.py`)

| Schema | Purpose |
|---|---|
| `AnalyticsSummaryOut` | Dashboard header: streak, weekly workouts, avg calories, weight change |
| `WeeklyVolumeOut` | Per-ISO-week volume bucket |
| `StrengthProgressOut` | Per-date max weight + Epley 1RM |
| `BodyMetricsTrendOut` | Per-day weight, BMI, body fat |
| `NutritionTrendOut` | Per-day calories and macros |
| `WellnessTrendOut` | Per-day sleep, hydration, composite recovery score |

---

## Endpoints

### `GET /analytics/summary`

Returns a dashboard-level snapshot.

**Response** `200 AnalyticsSummaryOut`
```json
{
  "workouts_this_week": 4,
  "workouts_goal": 5,
  "avg_calories_7d": 2100.0,
  "calorie_goal": 2500.0,
  "weight_change_30d": -1.2,
  "current_streak_days": 6,
  "total_workouts_all_time": 87
}
```

**Logic**
- `workouts_this_week` — `WorkoutLog` entries where `log_date >= Monday of current week`
- `avg_calories_7d` — mean of `MacroEntry.calories` over last 7 days; 0 if no data
- `weight_change_30d` — `BodyMetricEntry` last weight minus first weight in last 30 days;
  0 if fewer than 2 data points
- `current_streak_days` — consecutive calendar days backward from today that contain
  at least one `WorkoutLog` entry

---

### `GET /analytics/workout-volume?weeks=8`

Weekly training volume over the last N weeks.

**Query params**
| Param | Default | Range | Description |
|---|---|---|---|
| `weeks` | 8 | 1–52 | Look-back window in weeks |

**Response** `200 list[WeeklyVolumeOut]` sorted ascending by week

```json
[
  {"week": "2026-W10", "total_volume": 12500.0, "session_count": 3}
]
```

**Logic** — Volume = `sum(sets × reps × weight_kg)` per ISO week label (e.g. `"2026-W10"`).

---

### `GET /analytics/strength-progress?exercise_name=Bench+Press&weeks=12`

Strength progression for a named exercise.

**Query params**
| Param | Default | Range | Description |
|---|---|---|---|
| `exercise_name` | required | — | Case-insensitive exercise name |
| `weeks` | 12 | 1–104 | Look-back window in weeks |

**Response** `200 list[StrengthProgressOut]` sorted ascending by date

```json
[
  {"date": "2026-01-15", "max_weight_kg": 80.0, "estimated_1rm": 92.0}
]
```

**Logic**
- Resolves exercise by name against the user's `Exercise` table
- Per date, keeps the log with the highest `weight_kg`
- Epley formula: `estimated_1rm = weight × (1 + reps / 30)`

---

### `GET /analytics/body-metrics-trend?days=90`

Body composition over time.

**Query params**
| Param | Default | Range |
|---|---|---|
| `days` | 90 | 1–730 |

**Response** `200 list[BodyMetricsTrendOut]` sorted ascending by date

```json
[
  {"date": "2026-01-01", "weight_kg": 82.5, "bmi": 24.1, "body_fat_pct": 18.2}
]
```

**Logic** — BMI derived from `weight_kg / (height_cm/100)²` using the height stored
in the user's first `FitnessProfile`. `bmi` and `body_fat_pct` are `null` when the
relevant fields are missing.

---

### `GET /analytics/nutrition-trend?days=30`

Daily macro and calorie totals.

**Query params**
| Param | Default | Range |
|---|---|---|
| `days` | 30 | 1–365 |

**Response** `200 list[NutritionTrendOut]` sorted ascending by date

```json
[
  {"date": "2026-01-01", "calories": 2100.0, "protein_g": 150.0, "carbs_g": 210.0, "fat_g": 70.0}
]
```

**Logic** — Multiple `MacroEntry` rows on the same date are summed.

---

### `GET /analytics/wellness-trend?days=14`

Combined sleep, hydration, and recovery trend.

**Query params**
| Param | Default | Range |
|---|---|---|
| `days` | 14 | 1–365 |

**Response** `200 list[WellnessTrendOut]` sorted ascending by date

```json
[
  {
    "date": "2026-01-01",
    "sleep_hours": 7.5,
    "sleep_quality": 4,
    "hydration_ml": 2200.0,
    "recovery_score": 3.83
  }
]
```

**Logic**
- `sleep_hours` / `sleep_quality` — from `SleepEntry`; latest entry wins per day
- `hydration_ml` — sum of `HydrationEntry.water_ml` per day
- `recovery_score` (1–5) — composite: `1 + ((energy + (6 - soreness) + mood) - 3) / 12 × 4`
  Raw score ranges 3–15 (all fields at worst vs best); linearly mapped to 1–5
- Dates where any of the three sources has data appear in the response; missing
  fields are `null`

---

## Files Changed

| File | Change |
|---|---|
| `app/routers/analytics.py` | Added 6 new endpoints; preserved legacy `/{profile_id}/workout-summary` |
| `app/models.py` | Added 6 new Pydantic response schemas |
| `app/main.py` | No change — `analytics.router` was already registered |

---

## Authentication

All new endpoints use:
```python
current_user: User = Depends(get_current_user_from_header)
```
Every query is filtered by `owner_id == current_user.id`, so users can only see
their own data.
