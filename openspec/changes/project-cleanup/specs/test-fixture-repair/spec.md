## ADDED Requirements

### Requirement: conftest.py does not reference deleted modules
`tests/conftest.py` SHALL NOT import `app.repository` or define a `clear_repos` fixture.

#### Scenario: Import removed
- **WHEN** `tests/conftest.py` is read
- **THEN** there is no line containing `from app.repository`

#### Scenario: Dead fixture removed
- **WHEN** `tests/conftest.py` is read
- **THEN** there is no `clear_repos` function definition

### Requirement: Existing tests still pass
The full test suite SHALL pass after the conftest changes.

#### Scenario: Test suite green
- **WHEN** `pytest` is run against the `tests/` directory
- **THEN** all tests pass with exit code 0
