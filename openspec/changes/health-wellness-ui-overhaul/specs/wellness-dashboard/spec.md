## ADDED Requirements

### Requirement: Dashboard shows daily wellness summary
The system SHALL display a wellness summary section on the dashboard showing today's logged data across all health categories: sleep hours, water intake, latest body weight, and recovery mood/energy — when data is available.

#### Scenario: Full wellness data available
- **WHEN** user has logged sleep, hydration, body metrics, and recovery entries for today
- **THEN** dashboard shows a wellness summary card with sleep hours, water ml, weight kg, and average recovery score

#### Scenario: Partial data available
- **WHEN** user has logged only sleep and hydration for today
- **THEN** dashboard shows available data and displays "—" for missing categories

#### Scenario: No wellness data
- **WHEN** user has no wellness entries for today
- **THEN** dashboard shows the wellness summary with all values as "—" and a prompt to start logging

### Requirement: Weekly wellness trends shown on dashboard
The system SHALL display a simple 7-day trend indicator (up/down/stable) for weight and sleep when sufficient data exists (at least 2 entries in the past 7 days).

#### Scenario: Weight trending down
- **WHEN** user has 3+ body metric entries in the past 7 days and latest weight is lower than earliest
- **THEN** dashboard shows a downward trend indicator next to weight

#### Scenario: Insufficient data for trends
- **WHEN** user has fewer than 2 entries in the past 7 days for a category
- **THEN** no trend indicator is shown for that category
