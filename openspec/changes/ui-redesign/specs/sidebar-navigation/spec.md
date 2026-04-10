## ADDED Requirements

### Requirement: Sidebar menu replaces tab bar
The horizontal `st.tabs()` navigation SHALL be replaced with `sac.menu()` from `streamlit-antd-components` rendered in `st.sidebar`. The menu SHALL contain items: Dashboard, Training, Nutrition, Wellness, Profile — each with a relevant sport/health icon.

#### Scenario: Menu renders in sidebar
- **WHEN** the app loads
- **THEN** a vertical menu with five labeled items SHALL appear in the left sidebar

#### Scenario: Correct icon per section
- **WHEN** the menu is visible
- **THEN** Dashboard shows a dashboard/grid icon, Training shows a trophy or dumbbell icon, Nutrition shows a heart or leaf icon, Wellness shows a medicine or pulse icon, Profile shows a user icon

#### Scenario: Active item highlighted in green
- **WHEN** a menu item is selected
- **THEN** it SHALL be visually highlighted with the brand green accent

### Requirement: Navigation state preserved across reruns
The selected menu item SHALL be stored in `st.session_state` so that Streamlit reruns (caused by widget interactions) do not reset navigation to the first tab.

#### Scenario: Form submission stays on current section
- **WHEN** a user fills in a form on the Training section and submits
- **THEN** after the rerun the Training section SHALL still be displayed (not Dashboard)

### Requirement: All existing sections accessible
Every section that was accessible via the old tab bar (Dashboard, Training, Nutrition, Wellness, Profile) SHALL remain accessible via the new sidebar menu with identical functionality.

#### Scenario: All five sections reachable
- **WHEN** each menu item is clicked in turn
- **THEN** the correct section content SHALL render with no errors
