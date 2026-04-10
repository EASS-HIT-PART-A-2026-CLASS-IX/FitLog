## ADDED Requirements

### Requirement: User can log hydration intake
The system SHALL allow an authenticated user to create a hydration entry with date, water_ml (integer, 1–10000), and optional notes.

#### Scenario: Successful hydration log
- **WHEN** user submits a hydration entry with date "2026-03-31", water_ml 2500, notes "Good hydration day"
- **THEN** system creates the entry linked to the user's active profile and returns the entry with a generated ID

#### Scenario: Invalid water_ml rejected
- **WHEN** user submits a hydration entry with water_ml 0 or greater than 10000
- **THEN** system returns a 422 validation error

### Requirement: User can list hydration entries
The system SHALL return a paginated list of the user's hydration entries, filtered by profile_id, ordered by date descending.

#### Scenario: List hydration entries for a profile
- **WHEN** user requests hydration entries with profile_id and limit=10, offset=0
- **THEN** system returns up to 10 hydration entries for that profile, newest first

### Requirement: User can delete a hydration entry
The system SHALL allow a user to delete their own hydration entry by ID.

#### Scenario: Successful deletion
- **WHEN** user deletes a hydration entry they own
- **THEN** system removes the entry and returns 204

#### Scenario: Cannot delete another user's entry
- **WHEN** user attempts to delete a hydration entry owned by a different user
- **THEN** system returns 404
