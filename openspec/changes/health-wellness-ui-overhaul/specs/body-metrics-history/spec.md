## ADDED Requirements

### Requirement: User can log body metrics
The system SHALL allow an authenticated user to create a body metric entry with date, weight_kg (required, 20–500), and optional fields: body_fat_pct (1–70), waist_cm (30–250), resting_hr (20–250), notes.

#### Scenario: Successful body metrics log with all fields
- **WHEN** user submits a body metric entry with date "2026-03-31", weight_kg 78.5, body_fat_pct 18.0, waist_cm 82, resting_hr 62, notes "Morning measurement"
- **THEN** system creates the entry linked to the user's active profile and returns the entry with a generated ID

#### Scenario: Successful log with only required fields
- **WHEN** user submits a body metric entry with date "2026-03-31", weight_kg 78.5 (no optional fields)
- **THEN** system creates the entry successfully

#### Scenario: Invalid body_fat_pct rejected
- **WHEN** user submits a body metric entry with body_fat_pct 0 or greater than 70
- **THEN** system returns a 422 validation error

### Requirement: User can list body metric entries
The system SHALL return a paginated list of the user's body metric entries, filtered by profile_id, ordered by date descending.

#### Scenario: List body metrics with weight trend
- **WHEN** user requests body metric entries with profile_id
- **THEN** system returns entries ordered by date descending, each including all recorded fields

### Requirement: User can delete a body metric entry
The system SHALL allow a user to delete their own body metric entry by ID.

#### Scenario: Successful deletion
- **WHEN** user deletes a body metric entry they own
- **THEN** system removes the entry and returns 204

#### Scenario: Cannot delete another user's entry
- **WHEN** user attempts to delete a body metric entry owned by a different user
- **THEN** system returns 404
