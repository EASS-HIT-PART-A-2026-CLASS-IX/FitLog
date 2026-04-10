## Context

`frontend/app.py` is a ~1500-line single-file Streamlit app. It uses a hand-rolled CSS design system (CSS variables injected via `st.markdown`) with an indigo/white palette and Inter font. Navigation is `st.tabs()` at the top of the page. Metric displays use plain `st.metric()` and custom HTML `<div class="metric-card">` strings. Charts are Plotly with default colors.

The app has six logical sections: Dashboard, Training (exercises + workout logs), Nutrition (macros + food logging), Wellness (sleep/hydration/body metrics/recovery), Profile, and AI Assistant (inline panel on Dashboard).

## Goals / Non-Goals

**Goals:**
- Dark athletic color palette throughout (`#0f172a` bg, `#1e293b` surface, `#22c55e` green, `#0ea5e9` blue)
- Sidebar navigation with sport icons via `streamlit-antd-components`
- Styled metric/stat cards via `streamlit-shadcn-ui`
- Plotly charts re-themed to dark background with green/blue series colors
- All existing functionality preserved (same API calls, same session state keys, same logic)

**Non-Goals:**
- Any backend changes
- Adding new features or screens
- Responsive/mobile layout (Streamlit handles this automatically)
- Animations beyond CSS transitions

## Decisions

**D1 — `streamlit-antd-components` for navigation**
Replaces `st.tabs()` with `sac.menu()` (sidebar menu). This gives icon support, active state highlighting, and a fixed sidebar that doesn't scroll away. The menu item keys map 1:1 to the existing section names so the rest of the routing code is a simple `if selected == "Dashboard":` swap.

*Alternative:* `streamlit-option-menu` — simpler API but fewer styling options and no icon library. Antd has a full icon set including sport/health icons (Trophy, Heart, Dashboard, etc.).

**D2 — `streamlit-shadcn-ui` for metric cards**
`ui.metric_card(title, content, description)` replaces the custom HTML `metric-card` divs. This is more maintainable than raw HTML strings and auto-respects the dark theme via shadcn's CSS variables.

*Alternative:* Keep custom HTML metric cards — works but requires maintaining a large CSS block. shadcn components are self-contained.

**D3 — CSS design tokens kept for global overrides**
Even with the component libraries, Streamlit's own elements (buttons, inputs, expanders, dataframes) still need CSS overrides. We keep a smaller `<style>` block that sets the dark background, overrides Streamlit's white surfaces, and applies the brand green to buttons/selects. Component library elements are NOT overridden with custom CSS.

**D4 — Plotly chart theme via `plotly.io.templates`**
Define a custom Plotly template (`fitlog_dark`) at module level with dark paper/plot background and a green/blue/teal color sequence. Apply it as the default template so all existing `px.bar()`, `px.line()` etc. calls get the new theme without touching chart code.

*Alternative:* Pass `template=` to each chart call — error-prone and requires touching every chart call site.

**D5 — Single-file stays single-file**
`frontend/app.py` remains one file. The component libraries add imports at the top; CSS block is replaced; nav routing block is replaced; metric card HTML strings are replaced with `ui.metric_card()` calls. No new files needed.

## Risks / Trade-offs

- **`streamlit-shadcn-ui` version compatibility** → Pin to a tested version in `pyproject.toml`. If the package API changes, the metric cards fall back to plain `st.metric()` which still works.
- **`streamlit-antd-components` sidebar takes space** → On narrow screens the sidebar compresses content. Mitigated by setting sidebar to collapsed by default with expand-on-hover, same as current `initial_sidebar_state="collapsed"`.
- **Dark theme + Streamlit's own widgets** → Some Streamlit components (dataframes, date pickers) don't fully respect CSS overrides. These will look slightly inconsistent. Acceptable trade-off.
- **CSS `!important` overrides** → Streamlit requires `!important` to override its own styles. Keep overrides minimal and targeted to avoid future conflicts.

## Migration Plan

1. Add new deps to `pyproject.toml`, run `uv sync`
2. Define Plotly dark template at module top
3. Replace CSS block with dark theme tokens
4. Replace `st.tabs()` navigation with `sac.menu()` sidebar nav
5. Replace metric card HTML with `ui.metric_card()` calls (Dashboard + Wellness)
6. Verify all six screens render correctly and all API calls still work
7. No rollback needed — single file, git revert is instant
