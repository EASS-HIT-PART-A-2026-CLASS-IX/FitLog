## ADDED Requirements

### Requirement: Dashboard stats use shadcn metric cards
The Dashboard section's top stat row (calories, protein, workouts this week, water intake) SHALL use `ui.metric_card(title, content, description)` from `streamlit-shadcn-ui` instead of custom HTML `<div class="metric-card">` strings.

#### Scenario: Metric card renders with correct values
- **WHEN** the Dashboard loads and the API returns profile + macro data
- **THEN** each metric card SHALL display the correct title, value, and subtitle

#### Scenario: Metric cards render on dark background
- **WHEN** the dark theme is active
- **THEN** metric cards SHALL use a dark surface (`#1e293b`) with light text, not a white card on a dark page

### Requirement: Wellness summary uses metric cards
The Wellness section's daily summary row (sleep hours, water ml, weight, recovery score) SHALL also use `ui.metric_card()` for visual consistency with the Dashboard.

#### Scenario: Wellness cards match Dashboard style
- **WHEN** the Wellness section is open
- **THEN** the summary cards SHALL be visually identical in style to the Dashboard metric cards

### Requirement: Fallback to st.metric on import error
If `streamlit-shadcn-ui` is not installed or raises an ImportError, the app SHALL fall back to `st.metric()` calls with no crash.

#### Scenario: Graceful degradation
- **WHEN** `import streamlit_shadcn_ui as ui` fails
- **THEN** the app SHALL catch the ImportError and render `st.metric()` instead, displaying a console warning
