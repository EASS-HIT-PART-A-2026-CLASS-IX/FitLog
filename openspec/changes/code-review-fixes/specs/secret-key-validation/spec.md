## ADDED Requirements

### Requirement: Startup fails fast in production when SECRET_KEY is missing
`app/security.py` SHALL raise a `RuntimeError` at import time if the `SECRET_KEY` environment variable is not set and the `APP_ENV` environment variable is not `"development"`.

#### Scenario: Production startup without SECRET_KEY
- **WHEN** the application starts with `APP_ENV=production` and no `SECRET_KEY` env var
- **THEN** the import of `app.security` SHALL raise `RuntimeError` with a message instructing the operator to set `SECRET_KEY`

#### Scenario: Development startup without SECRET_KEY
- **WHEN** the application starts with `APP_ENV=development` (or `APP_ENV` unset) and no `SECRET_KEY`
- **THEN** a random key SHALL be generated with a printed warning (existing behavior preserved)

#### Scenario: Any environment with SECRET_KEY set
- **WHEN** `SECRET_KEY` is present in the environment
- **THEN** it SHALL be used as-is with no warning or error
