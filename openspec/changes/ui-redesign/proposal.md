## Why

The current FitLog frontend uses a generic indigo/white Streamlit theme that doesn't feel like a fitness product — it looks like a generic SaaS dashboard. A dark athletic theme with purpose-built navigation components will make the app feel professional, cohesive, and appropriate for a fitness domain while also demonstrating UI craft for the EX2/EX3 rubric ("user guidance" and "working flows" criteria).

## What Changes

- Replace the entire CSS design system in `frontend/app.py` with a dark athletic theme (`#0f172a` background, `#22c55e` green accent, `#0ea5e9` blue secondary)
- Add `streamlit-antd-components` package: replace the current horizontal `st.tabs()` navigation with a sidebar menu with sport icons per section
- Add `streamlit-shadcn-ui` package: replace plain `st.metric()` calls and plain containers with styled metric cards and shadcn-style UI elements
- Redesign all six sections: Dashboard, Training, Nutrition, Wellness, Profile, AI Assistant
- Update chart color palettes (Plotly/Altair) to match the new theme
- No API changes, no backend changes, no functional changes

## Capabilities

### New Capabilities

- `dark-theme-design-system`: The CSS design tokens, color palette, typography, and global styles that define the new dark athletic look
- `sidebar-navigation`: Sidebar-based navigation using `streamlit-antd-components` with icons, replacing the horizontal tab bar
- `styled-metric-cards`: Reusable styled metric/stat cards using `streamlit-shadcn-ui` across Dashboard and Wellness screens
- `themed-charts`: Plotly chart theme configuration matching the dark background and green/blue accent palette

### Modified Capabilities

## Impact

- `frontend/app.py` — complete rewrite of CSS block and all screen render functions (no logic changes)
- `pyproject.toml` — add `streamlit-antd-components` and `streamlit-shadcn-ui` dependencies
- No backend files touched
