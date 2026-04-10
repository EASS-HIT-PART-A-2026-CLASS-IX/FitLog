## ADDED Requirements

### Requirement: Unnecessary root files are removed
The project root SHALL NOT contain the following files after cleanup: `NUL`, `check_schema.py`, `test_fix.py`, `FIXES_COMPLETED.md`, `INTEGRATION_REPORT.md`, `PERFORMANCE_OPTIMIZATIONS.md`, `PERFORMANCE_TESTING.md`, `SUBMISSION.md`.

#### Scenario: Root directory is clean
- **WHEN** a contributor lists the project root directory
- **THEN** none of the 8 identified dead files are present

### Requirement: Dead code module is removed
The file `app/repository.py` (in-memory repository, replaced by SQLModel persistence) SHALL be deleted from the project.

#### Scenario: repository.py no longer exists
- **WHEN** the app package is inspected
- **THEN** `app/repository.py` does not exist

#### Scenario: No code imports the deleted module
- **WHEN** the codebase is searched for `from app.repository` or `import app.repository`
- **THEN** zero matches are found
