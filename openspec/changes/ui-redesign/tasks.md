## 1. Dependencies

- [x] 1.1 Add `streamlit-antd-components>=0.3.0` to `pyproject.toml` dependencies
- [x] 1.2 Add `streamlit-shadcn-ui>=0.1.0` to `pyproject.toml` dependencies
- [x] 1.3 Run `uv sync` and confirm both packages install without conflicts

## 2. Plotly Dark Template

- [x] 2.1 Add `import plotly.graph_objects as go` and `import plotly.io as pio` imports at the top of `frontend/app.py`
- [x] 2.2 Define the `fitlog_dark` Plotly template after imports: set `paper_bgcolor="#0f172a"`, `plot_bgcolor="#1e293b"`, `font_color="#f1f5f9"`, gridline color `#334155`, color sequence `["#22c55e", "#0ea5e9", "#a78bfa", "#f59e0b", "#ef4444"]`
- [x] 2.3 Set `pio.templates.default = "fitlog_dark"` so all charts inherit it automatically

## 3. Dark CSS Design System

- [x] 3.1 Replace the entire existing `st.markdown("""<style>...</style>""")` CSS block with the new dark theme
- [x] 3.2 Define `:root` tokens: `--bg: #0f172a`, `--surface: #1e293b`, `--surface-2: #273549`, `--border: #334155`, `--text: #f1f5f9`, `--muted: #94a3b8`, `--green: #22c55e`, `--green-dark: #16a34a`, `--blue: #0ea5e9`, `--radius: 12px`, `--radius-sm: 8px`
- [x] 3.3 Add global dark overrides: `.main { background: var(--bg); }`, `.block-container { max-width: 1200px; padding-top: 1rem; }`
- [x] 3.4 Override Streamlit inputs for dark theme: text inputs, number inputs, selectboxes → `background: var(--surface)`, `color: var(--text)`, `border-color: var(--border)`
- [x] 3.5 Override `stButton > button` → `background: var(--green)`, `color: #0f172a`, `font-weight: 700`; hover → `background: var(--green-dark)`
- [x] 3.6 Add dark card styles: `.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; }`
- [x] 3.7 Override sidebar background: `[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }`
- [x] 3.8 Override dataframe/table backgrounds to dark surface

## 4. Sidebar Navigation

- [x] 4.1 Add `import streamlit_antd_components as sac` import (wrapped in try/except with a fallback flag)
- [x] 4.2 Remove the `st.tabs()` call and the tab-based routing block
- [x] 4.3 In `st.sidebar`, render the FitLog logo/title and the `sac.menu()` with items: Dashboard (icon `appstore`), Training (icon `trophy`), Nutrition (icon `heart`), Wellness (icon `medicine-box`), Profile (icon `user`)
- [x] 4.4 Store the selected menu item in `st.session_state["active_section"]` defaulting to `"Dashboard"`
- [x] 4.5 Replace tab routing with `if/elif` blocks keyed on `st.session_state["active_section"]`
- [x] 4.6 Add fallback: if `sac` import failed, render `st.radio()` in sidebar as navigation fallback

## 5. Styled Metric Cards — Dashboard

- [x] 5.1 Add `import streamlit_shadcn_ui as ui` import (wrapped in try/except, set `HAS_SHADCN = True/False`)
- [x] 5.2 In the Dashboard section, replace custom HTML metric card `st.markdown()` calls with `ui.metric_card(title=..., content=..., description=...)` when `HAS_SHADCN` is True
- [x] 5.3 Add fallback: when `HAS_SHADCN` is False, use `st.metric()` for the same values
- [x] 5.4 Confirm the four dashboard stats render correctly: Today's Calories, Protein, Workouts This Week, Water Today

## 6. Styled Metric Cards — Wellness

- [x] 6.1 In the Wellness section's daily summary row, replace HTML metric cards with `ui.metric_card()` calls (sleep hours, water ml, latest weight, average recovery score)
- [x] 6.2 Confirm the fallback to `st.metric()` also works here

## 7. Screen-by-screen Visual QA

- [x] 7.1 Dashboard: dark background, green metric cards, dark charts, AI assistant panel readable
- [x] 7.2 Training: exercise list, workout log form, history table all readable on dark surface
- [x] 7.3 Nutrition: food log form, macro bar chart (dark + green bars), daily summary readable
- [x] 7.4 Wellness: all four sub-tabs (Sleep, Hydration, Body Metrics, Recovery) render correctly with dark forms and cards
- [x] 7.5 Profile: profile creation/display form readable; protein target card styled correctly
- [x] 7.6 Sidebar: all five nav items visible, active item highlighted green, icons present

## 8. Final Check

- [x] 8.1 Run the app (`uv run streamlit run frontend/app.py`) and confirm no Python errors or import failures
- [ ] 8.2 Log in, navigate to each section, submit at least one form — confirm all API calls still work
- [ ] 8.3 Confirm the Plotly charts render on dark background in at least Nutrition and Wellness sections
