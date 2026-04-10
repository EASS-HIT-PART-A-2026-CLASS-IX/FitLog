## ADDED Requirements

### Requirement: Custom Plotly dark template defined at module level
A Plotly template named `"fitlog_dark"` SHALL be defined at module startup using `go.layout.Template`. It SHALL set: `paper_bgcolor="#0f172a"`, `plot_bgcolor="#1e293b"`, `font_color="#f1f5f9"`, grid lines `#334155`, and a color sequence of `["#22c55e", "#0ea5e9", "#a78bfa", "#f59e0b", "#ef4444"]`.

#### Scenario: Template registered at import
- **WHEN** `frontend/app.py` is imported/started
- **THEN** `pio.templates["fitlog_dark"]` SHALL exist and `pio.templates.default` SHALL be `"fitlog_dark"`

### Requirement: All existing charts use the dark template automatically
Every Plotly chart created with `px.*` or `go.Figure()` in the app SHALL inherit the `fitlog_dark` template without any per-chart `template=` argument needed.

#### Scenario: Bar chart on dark background
- **WHEN** the Nutrition macro breakdown bar chart renders
- **THEN** its background SHALL be `#0f172a` and bars SHALL use green/blue series colors

#### Scenario: Line chart on dark background
- **WHEN** the Wellness weight-trend line chart renders
- **THEN** its background SHALL be dark and the line SHALL use the green accent color

### Requirement: Chart axis labels readable on dark background
All chart axis text, tick labels, and legends SHALL use `#f1f5f9` (light) so they are legible against the dark plot background.

#### Scenario: Axis text visible
- **WHEN** any chart is displayed
- **THEN** axis titles and tick marks SHALL NOT be dark-on-dark (i.e., not `#333` on `#1e293b`)
