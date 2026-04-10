## 1. Pydantic Update Schemas in app/models.py

- [ ] 1.1 Add `SleepEntryUpdate` schema with all-optional fields: `entry_date`, `sleep_hours`, `sleep_quality`, `notes`
- [ ] 1.2 Add `HydrationEntryUpdate` schema with all-optional fields: `entry_date`, `water_ml`, `notes`
- [ ] 1.3 Add `BodyMetricEntryUpdate` schema with all-optional fields: `entry_date`, `weight_kg`, `body_fat_pct`, `waist_cm`, `resting_hr`, `notes`
- [ ] 1.4 Add `RecoveryEntryUpdate` schema with all-optional fields: `entry_date`, `soreness_level`, `energy_level`, `stress_level`, `mood`, `notes`

## 2. GET /{id} endpoint on wellness routers

- [ ] 2.1 Add `GET /{entry_id}` to `app/routers/sleep.py` — fetch by `SleepEntry.id` AND `owner_id == current_user.id`, return 404 if not found
- [ ] 2.2 Add `GET /{entry_id}` to `app/routers/hydration.py` — same ownership pattern
- [ ] 2.3 Add `GET /{entry_id}` to `app/routers/body_metrics.py` — same ownership pattern
- [ ] 2.4 Add `GET /{entry_id}` to `app/routers/recovery.py` — same ownership pattern

## 3. PUT /{id} endpoint on wellness routers

- [ ] 3.1 Add `PUT /{entry_id}` to `app/routers/sleep.py` — accept `SleepEntryUpdate`, apply only non-None fields, return updated `SleepEntryOut`
- [ ] 3.2 Add `PUT /{entry_id}` to `app/routers/hydration.py` — accept `HydrationEntryUpdate`
- [ ] 3.3 Add `PUT /{entry_id}` to `app/routers/body_metrics.py` — accept `BodyMetricEntryUpdate`
- [ ] 3.4 Add `PUT /{entry_id}` to `app/routers/recovery.py` — accept `RecoveryEntryUpdate`

## 4. Test auth fixtures in tests/conftest.py

- [ ] 4.1 Add `registered_user` fixture: POST to `/auth/register` with a unique username (uuid4-based), assert 201, return response JSON
- [ ] 4.2 Add `auth_headers` fixture: depends on `registered_user`, POST to `/auth/token`, assert 200, return `{"Authorization": "Bearer <token>"}`
- [ ] 4.3 Update `sample_exercise` fixture to depend on `auth_headers` and include it in the POST request
- [ ] 4.4 Update `sample_profile` fixture to depend on `auth_headers` and include it in the POST request

## 5. SECRET_KEY startup validation in app/security.py

- [ ] 5.1 After the existing `SECRET_KEY` env var read, add a check: if `SECRET_KEY` is missing AND `os.getenv("APP_ENV", "development") != "development"`, raise `RuntimeError("SECRET_KEY environment variable must be set in production")`
- [ ] 5.2 Keep existing warning-and-generate behavior for the development path unchanged

## 6. Verify

- [ ] 6.1 Run `pytest tests/` and confirm all existing tests still pass
- [ ] 6.2 Manually verify that `GET /sleep/{id}` returns 200 for an existing entry and 404 for a missing one
- [ ] 6.3 Manually verify that `PUT /sleep/{id}` with a partial body updates only the supplied fields
