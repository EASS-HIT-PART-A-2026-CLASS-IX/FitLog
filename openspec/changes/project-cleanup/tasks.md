## 1. Delete unnecessary root files

- [x] 1.1 Delete `NUL` (empty Windows artifact)
- [x] 1.2 Delete `check_schema.py` (one-off SQLite debug script)
- [x] 1.3 Delete `test_fix.py` (ad-hoc integration smoke test)
- [x] 1.4 Delete `FIXES_COMPLETED.md` (historical changelog)
- [x] 1.5 Delete `INTEGRATION_REPORT.md` (one-time report)
- [x] 1.6 Delete `PERFORMANCE_OPTIMIZATIONS.md` (internal dev notes)
- [x] 1.7 Delete `PERFORMANCE_TESTING.md` (internal dev checklist)
- [x] 1.8 Delete `SUBMISSION.md` (grading submission doc)

## 2. Remove dead code module

- [x] 2.1 Delete `app/repository.py` (in-memory repo replaced by SQLModel persistence)

## 3. Fix test infrastructure

- [x] 3.1 Remove `from app.repository import ...` from `tests/conftest.py`
- [x] 3.2 Remove the `clear_repos` autouse fixture from `tests/conftest.py`

## 4. Verify

- [x] 4.1 Grep the codebase for `app.repository` — confirm zero remaining references in code (docs-only references are acceptable)
- [x] 4.2 Run `pytest tests/` and confirm all tests pass
