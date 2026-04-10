## ADDED Requirements

### Requirement: Shared authenticated user fixture
`tests/conftest.py` SHALL provide a `registered_user` fixture that creates a real user via `POST /auth/register` and returns the response data (username, id).

#### Scenario: User created successfully
- **WHEN** a test requests the `registered_user` fixture
- **THEN** the fixture SHALL call `POST /auth/register` with valid credentials and assert a 201 response

#### Scenario: Unique username per test
- **WHEN** multiple tests run in the same session
- **THEN** each `registered_user` fixture call SHALL use a unique username (e.g. via `uuid4`) to avoid conflicts

### Requirement: Shared auth headers fixture
`tests/conftest.py` SHALL provide an `auth_headers` fixture that logs in the `registered_user` and returns a dict suitable for use as request headers: `{"Authorization": "Bearer <token>"}`.

#### Scenario: Login succeeds
- **WHEN** a test requests the `auth_headers` fixture
- **THEN** the fixture SHALL call `POST /auth/token` with the registered credentials and assert a 200 response

#### Scenario: Token included in headers
- **WHEN** a test passes `auth_headers` to a client request (e.g. `client.get("/sleep/", headers=auth_headers)`)
- **THEN** the request SHALL be treated as authenticated by the API

### Requirement: Existing fixtures updated to use auth
The `sample_exercise` and `sample_profile` fixtures in `conftest.py` SHALL accept the `auth_headers` fixture and include it in their POST requests so they continue to assert 201 against auth-protected endpoints.

#### Scenario: sample_profile creates profile with auth
- **WHEN** a test uses `sample_profile`
- **THEN** the fixture SHALL send `Authorization: Bearer <token>` and the profile SHALL be created successfully (201)
