## ADDED Requirements

### Requirement: Fetch single wellness entry by ID
Each wellness router (sleep, hydration, body_metrics, recovery) SHALL expose a `GET /{id}` endpoint that returns the entry with the given ID, provided it belongs to the authenticated user.

#### Scenario: Entry found
- **WHEN** an authenticated user sends `GET /sleep/{id}` with an ID that belongs to them
- **THEN** the system SHALL return 200 with the full entry object

#### Scenario: Entry not found or belongs to another user
- **WHEN** an authenticated user sends `GET /sleep/{id}` with an ID that does not exist or belongs to a different user
- **THEN** the system SHALL return 404

#### Scenario: Unauthenticated request
- **WHEN** a request is made without a valid Bearer token
- **THEN** the system SHALL return 401

### Requirement: Update a wellness entry
Each wellness router SHALL expose a `PUT /{id}` endpoint that accepts a partial-update body (all fields optional) and merges the provided fields into the existing entry.

#### Scenario: Partial update succeeds
- **WHEN** an authenticated user sends `PUT /sleep/{id}` with `{"sleep_hours": 8.0}` for an entry they own
- **THEN** the system SHALL update only `sleep_hours`, leave other fields unchanged, and return 200 with the updated entry

#### Scenario: No fields provided
- **WHEN** an authenticated user sends `PUT /sleep/{id}` with an empty body `{}`
- **THEN** the system SHALL return 200 with the entry unchanged

#### Scenario: Entry not found
- **WHEN** the target entry does not exist or belongs to another user
- **THEN** the system SHALL return 404

#### Scenario: Invalid field value
- **WHEN** the body contains a field value that fails schema validation (e.g. `sleep_quality: 99`)
- **THEN** the system SHALL return 422

#### Scenario: Applies to all four routers
- **WHEN** the same PUT /{id} pattern is applied to hydration, body_metrics, and recovery
- **THEN** each SHALL behave identically to the sleep router with their respective fields
