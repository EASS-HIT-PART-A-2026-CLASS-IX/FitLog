## Why

FitLog currently tracks only exercise and macros — a narrow view of health. Users can't track sleep, hydration, body metrics over time, or recovery, which are critical for understanding fitness progress holistically. Additionally, the UI has usability issues: API status messages ("get_macros is running") blink on-screen during data loads, the AI assistant is buried behind a small floating button, and the overall layout needs polish to feel professional and easy to navigate. This change broadens FitLog into a complete health & wellness tracker while fixing UX pain points.

## What Changes

- **Add health tracking categories**: sleep, hydration, body metrics (weight/body-fat history), and recovery/wellness logs as new backend models, API routes, and frontend sections
- **Expand goal system**: replace the binary `fit | muscle` profile goal with richer options (`weight_loss`, `maintenance`, `endurance`, `hypertrophy`, `strength`, `general_health`)
- **Redesign main screen layout**: integrate the AI assistant directly into the dashboard as a visible panel instead of a hidden floating chat button
- **Fix status message flicker**: eliminate the visible "get_macros is running" / function status blinking that appears during cached API calls on the frontend
- **Improve navigation & UX**: add a dedicated "Wellness" tab, clean up spacing/layout, and ensure all sections are immediately discoverable

## Capabilities

### New Capabilities
- `sleep-tracking`: Log and view sleep entries (hours, quality, date, notes)
- `hydration-tracking`: Log and view daily water intake (ml, date, notes)
- `body-metrics-history`: Track body composition over time (weight, body fat %, waist measurement, resting heart rate) with trend display
- `recovery-wellness`: Log daily recovery/wellness state (soreness, energy level, stress level, mood) for holistic health view
- `wellness-dashboard`: Aggregate health categories into a unified dashboard with daily wellness summary and weekly trends
- `ui-polish`: Fix API status flicker, promote AI assistant to main screen, improve layout and navigation for a professional user experience

### Modified Capabilities
<!-- No existing specs to modify — this is the first spec-driven change -->

## Impact

- **Backend**: New SQLAlchemy models & migrations for sleep, hydration, body_metrics, recovery tables. New router modules for each category. Changes to profile model (expanded `goal` enum).
- **Frontend**: Major `app.py` restructure — new Wellness tab, AI assistant embedded in dashboard, status message fix, new logging forms and history views for each health category.
- **API**: New REST endpoints under `/sleep/`, `/hydration/`, `/body-metrics/`, `/recovery/`. Existing `/profile/` endpoints affected by expanded goal field.
- **AI Assistant**: Will receive richer context from new health data to give more holistic recommendations.
- **Dependencies**: No new external dependencies expected; uses existing FastAPI + SQLAlchemy + Streamlit stack.
