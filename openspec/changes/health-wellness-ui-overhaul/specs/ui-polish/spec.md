## ADDED Requirements

### Requirement: API status messages do not flicker on screen
The system SHALL NOT display transient status messages (e.g., "get_macros is running") during cached API call re-renders in the Streamlit frontend.

#### Scenario: Cached data loads without visible flicker
- **WHEN** user navigates to the dashboard and API data is already cached
- **THEN** no spinner, status message, or function name text flashes on screen

#### Scenario: First load shows loading state gracefully
- **WHEN** user loads the dashboard for the first time (cache empty)
- **THEN** a single loading indicator is shown, then replaced by content — no individual function names are displayed

### Requirement: AI assistant is embedded in main dashboard
The system SHALL display the AI assistant as an inline chat panel on the main dashboard screen, visible without any toggle action, replacing the floating chat button.

#### Scenario: AI panel visible on dashboard load
- **WHEN** user logs in and sees the dashboard
- **THEN** an AI assistant panel is visible in the right column of the dashboard with a text input and quick-action buttons

#### Scenario: AI chat interaction
- **WHEN** user types a message in the AI panel and submits
- **THEN** the AI response appears in the same panel inline, without opening a separate overlay

### Requirement: Wellness tab in main navigation
The system SHALL add a "Wellness" tab to the main navigation between "Nutrition" and "Profile", containing sub-tabs for Sleep, Hydration, Body Metrics, and Recovery.

#### Scenario: Navigate to Wellness tab
- **WHEN** user clicks the "Wellness" tab
- **THEN** sub-tabs for Sleep, Hydration, Body Metrics, and Recovery are displayed

### Requirement: Expanded goal options in profile creation
The system SHALL accept the following goal values when creating or updating a fitness profile: `weight_loss`, `maintenance`, `general_health`, `endurance`, `flexibility`, `hypertrophy`, `strength`, `athletic_performance`, `fit`, `muscle`.

#### Scenario: Create profile with new goal
- **WHEN** user creates a profile with goal "weight_loss"
- **THEN** system accepts and stores the profile

#### Scenario: Legacy goals still accepted
- **WHEN** user creates a profile with goal "fit" or "muscle"
- **THEN** system accepts and stores the profile (backward compatible)

#### Scenario: Invalid goal rejected
- **WHEN** user creates a profile with goal "invalid_value"
- **THEN** system returns a 422 validation error
