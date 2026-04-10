## ADDED Requirements

### Requirement: Dark color palette applied globally
The app SHALL use a dark athletic color palette injected via a `<style>` block: background `#0f172a`, surface `#1e293b`, border `#334155`, primary text `#f1f5f9`, muted text `#94a3b8`, green accent `#22c55e`, blue accent `#0ea5e9`.

#### Scenario: Dark background renders on all pages
- **WHEN** any page of the app is loaded
- **THEN** the main background SHALL be `#0f172a` (not white or light gray)

#### Scenario: Streamlit widgets adopt dark surface
- **WHEN** a text input, selectbox, or number input is rendered
- **THEN** its background SHALL be `#1e293b` and text SHALL be `#f1f5f9`

#### Scenario: Brand green applied to primary buttons
- **WHEN** a `st.button()` is rendered
- **THEN** its background SHALL be `#22c55e` and text SHALL be dark (`#0f172a`)

### Requirement: Inter font used throughout
The app SHALL import Inter from Google Fonts and apply it as the global font family.

#### Scenario: Font loads on first render
- **WHEN** the page loads
- **THEN** all text elements SHALL render in Inter (300–800 weight range loaded)

### Requirement: CSS design tokens defined as variables
All color, radius, and shadow values SHALL be defined as CSS custom properties (`--var`) so they can be referenced consistently.

#### Scenario: Token consistency
- **WHEN** the CSS block is inspected
- **THEN** color values SHALL appear only in the `:root` token block, not hardcoded in component rules
