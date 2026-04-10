## Context

FitLog migrated from in-memory repositories to SQLModel + SQLite persistence in EX3. The old `app/repository.py` in-memory module was left in place, and `tests/conftest.py` still imports it to clear repos between tests. Several root-level markdown docs and one-off scripts were created during development and submission but serve no ongoing purpose. A `NUL` file was accidentally created by a Windows shell redirect.

## Goals / Non-Goals

**Goals:**
- Remove all files identified in the proposal (8 root files + `app/repository.py`)
- Fix `tests/conftest.py` so tests still pass after `repository.py` is deleted
- Leave the project in a clean, shippable state

**Non-Goals:**
- Refactoring any application code beyond the conftest fix
- Changing the database layer, API, or frontend
- Removing `scripts/`, `fitlog.http`, `app/tasks.py`, or any docs under `docs/`

## Decisions

### 1. Delete files outright rather than archiving

**Choice:** `git rm` the files — they stay in git history if ever needed.

**Alternative considered:** Move to an `_archive/` folder. Rejected because it adds clutter and the files are already tracked in git history.

### 2. Fix `conftest.py` by removing the in-memory fixture entirely

**Choice:** Remove the `clear_repos` autouse fixture and the `app.repository` import. The current test suite routes all requests through `TestClient(app)` which hits the real (SQLite) database layer, so the in-memory repo clearing is dead code.

**Alternative considered:** Replace the import with a DB reset fixture. Not needed for this change — database test isolation is already handled by the existing test setup.

### 3. Keep utility files that have ongoing value

`fitlog.http` (API playground), `scripts/seed.py`, `scripts/demo.py`, `scripts/refresh.py`, and `app/tasks.py` all have clear ongoing purpose and are not touched.

## Risks / Trade-offs

- **[Risk] Tests depend on `clear_repos` more than we think** → Mitigation: Run the full test suite after the change to verify. The fixture clears in-memory dicts that aren't used by the DB-backed routers, so impact should be zero.
- **[Risk] A doc file we delete is referenced somewhere** → Mitigation: Grep for filenames before deleting. The files are standalone reports with no inbound links from code.
