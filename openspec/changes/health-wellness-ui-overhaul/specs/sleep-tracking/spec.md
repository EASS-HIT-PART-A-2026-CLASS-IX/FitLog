## ADDED Requirements

### Requirement: User can log a sleep entry
The system SHALL allow an authenticated user to create a sleep entry with date, sleep_hours (0.5–24), sleep_quality (1–5 integer scale), and optional notes.

#### Scenario: Successful sleep log
- **WHEN** user submits a sleep entry with date "2026-03-31", sleep_hours 7.5, sleep_quality 4, notes "Slept well"
- **THEN** system creates the entry linked to the user's active profile and returns the entry with a generated ID

#### Scenario: Invalid sleep hours rejected
- **WHEN** user submits a sleep entry with sleep_hours 0 or greater than 24
- **THEN** system returns a 422 validation error

### Requirement: User can list sleep entries
The system SHALL return a paginated list of the user's sleep entries, filtered by profile_id, ordered by date descending.

#### Scenario: List sleep entries for a profile
- **WHEN** user requests sleep entries with profile_id and limit=10, offset=0
- **THEN** system returns up to 10 sleep entries for that profile, newest first

#### Scenario: Empty list when no entries exist
- **WHEN** user requests sleep entries and none exist for the profile
- **THEN** system returns an empty array

### Requirement: User can delete a sleep entry
The system SHALL allow a user to delete their own sleep entry by ID.

#### Scenario: Successful deletion
- **WHEN** user deletes a sleep entry they own
- **THEN** system removes the entry and returns 204

#### Scenario: Cannot delete another user's entry
- **WHEN** user attempts to delete a sleep entry owned by a different user
- **THEN** system returns 404
