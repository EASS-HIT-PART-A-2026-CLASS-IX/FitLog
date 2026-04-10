## Why

The project accumulated debugging scripts, one-off test files, documentation artifacts from past submissions, and a dead code module (`repository.py`) that was replaced by SQLModel persistence. An empty `NUL` file (Windows redirect artifact) also sits in the root. These clutter the workspace, confuse contributors, and make the project look unfinished.

## What Changes

- **Remove** `NUL` — empty Windows artifact, no purpose
- **Remove** `check_schema.py` — one-off SQLite debugging script, not part of the app
- **Remove** `test_fix.py` — ad-hoc integration smoke test, superseded by `tests/`
- **Remove** `FIXES_COMPLETED.md` — historical changelog, not needed going forward
- **Remove** `INTEGRATION_REPORT.md` — one-time report, not needed going forward
- **Remove** `PERFORMANCE_OPTIMIZATIONS.md` — internal dev notes, not user-facing docs
- **Remove** `PERFORMANCE_TESTING.md` — internal dev checklist, not user-facing docs
- **Remove** `SUBMISSION.md` — grading submission doc, not relevant to the live project
- **Remove** `app/repository.py` — dead code (in-memory repo replaced by `app/db.py` + `app/database.py`). Only referenced by `tests/conftest.py` which still imports it; that import must be cleaned up.
- **Update** `tests/conftest.py` — remove the `app.repository` import and the `clear_repos` fixture that references the deleted module
- **Keep** `fitlog.http` — useful API playground for developers (VS Code REST Client)
- **Keep** `scripts/` — `seed.py` and `demo.py` are useful dev tools; `refresh.py` is the EX3 async requirement
- **Keep** `app/tasks.py` — Celery task definitions, part of async architecture

## Capabilities

### New Capabilities
- `dead-file-removal`: Identify and safely delete unnecessary root-level files and dead code modules
- `test-fixture-repair`: Update test infrastructure to remove references to deleted modules

### Modified Capabilities
<!-- No existing specs are being modified — this is a cleanup-only change -->

## Impact

- **Root directory**: 7 files removed (`NUL`, `check_schema.py`, `test_fix.py`, `FIXES_COMPLETED.md`, `INTEGRATION_REPORT.md`, `PERFORMANCE_OPTIMIZATIONS.md`, `PERFORMANCE_TESTING.md`, `SUBMISSION.md`)
- **app/**: `repository.py` removed
- **tests/conftest.py**: `clear_repos` fixture and `app.repository` import removed — tests that depend on in-memory repos will need the fixture replaced or removed
- **No API changes, no database changes, no breaking changes**
