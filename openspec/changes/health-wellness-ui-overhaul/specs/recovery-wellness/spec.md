## ADDED Requirements

### Requirement: User can log recovery and wellness state
The system SHALL allow an authenticated user to create a recovery entry with date, and 1–5 integer scale ratings for: soreness_level, energy_level, stress_level, mood. All four ratings are required. Optional notes field.

#### Scenario: Successful recovery log
- **WHEN** user submits a recovery entry with date "2026-03-31", soreness_level 2, energy_level 4, stress_level 1, mood 5, notes "Feeling great"
- **THEN** system creates the entry linked to the user's active profile and returns the entry with a generated ID

#### Scenario: Invalid rating rejected
- **WHEN** user submits a recovery entry with energy_level 0 or greater than 5
- **THEN** system returns a 422 validation error

### Requirement: User can list recovery entries
The system SHALL return a paginated list of the user's recovery entries, filtered by profile_id, ordered by date descending.

#### Scenario: List recovery entries for a profile
- **WHEN** user requests recovery entries with profile_id and limit=10, offset=0
- **THEN** system returns up to 10 recovery entries for that profile, newest first

### Requirement: User can delete a recovery entry
The system SHALL allow a user to delete their own recovery entry by ID.

#### Scenario: Successful deletion
- **WHEN** user deletes a recovery entry they own
- **THEN** system removes the entry and returns 204

#### Scenario: Cannot delete another user's entry
- **WHEN** user attempts to delete a recovery entry owned by a different user
- **THEN** system returns 404
