# Acceptance Test Plan

Add database-backed acceptance tests using a dedicated Docker Compose stack to
spin up a real PostGIS instance, run the Alembic migrations, start the service,
and test all three API endpoints over HTTP — including the `ST_INTERSECTS`
spatial query.

## Why

The unit tests mock the DB session entirely, so they can't catch:
- Incorrect SQL / ORM query construction
- GeoAlchemy2 ↔ PostGIS serialisation bugs
- Migration regressions (schema out of sync with models)
- `ST_INTERSECTS` returning wrong results for given geometries

## Approach: docker-compose + HTTP acceptance tests

A dedicated `docker-compose.test.yml` brings up three services:

- `db` — `postgis/postgis:15-3.3` on port `5433` with `POSTGRES_DB=test`
- `migration` — runs `alembic upgrade head` once, depends on `db` healthy
- `service` — the FastAPI app on port `8081`, depends on migration completing

Tests in `tests/acceptance/` make real HTTP calls via `httpx` to `localhost:8081`.
A session-scoped SQLAlchemy engine connects directly to the test DB on port `5433`
to `TRUNCATE TABLE route` before each test, keeping tests isolated without
restarting the stack.

No new Python dependencies required — `httpx` and `sqlalchemy` are already in
the project.

## File Layout

```
docker-compose.test.yml              # dedicated test stack (POSTGRES_DB=test)
tests/
├── conftest.py                      # existing unit-test fixtures
├── test_schemas.py
├── test_config.py
├── test_geometry.py
├── test_routes.py
└── acceptance/
    ├── __init__.py
    ├── conftest.py                  # engine + clean_db + base_url fixtures
    └── test_routes.py              # HTTP acceptance tests
```

## Running Tests

```bash
# Unit tests only (no Docker required)
uv run pytest

# Acceptance tests (requires compose stack)
docker compose -f docker-compose.test.yml up --build --wait
uv run pytest tests/acceptance -v
docker compose -f docker-compose.test.yml down -v
```

`norecursedirs = ["acceptance"]` in `pyproject.toml` ensures `uv run pytest`
never collects `tests/acceptance` automatically.

## Environment Variables

| Variable      | Default                                         | Purpose                        |
|---------------|-------------------------------------------------|--------------------------------|
| `SERVICE_URL` | `http://localhost:8081`                         | Base URL of the running service |
| `TEST_DB_URL` | `postgresql://postgres:password@localhost:5433/test` | Direct DB access for truncation |

## Test Coverage

### `TestListRoutes`
- Empty DB returns `[]`
- Inserted route appears in list response
- `offset` / `limit` pagination is respected

### `TestCreateRoute`
- Response contains assigned `id`
- Geometry round-trips correctly (GeoJSON in → GeoJSON out)
- All three `Activity` values persist and are returned correctly
- Route is persisted to the DB (visible via list endpoint)

### `TestSpatialQuery`
- Empty DB returns `[]`
- Route that intersects the query polygon is returned
- Route that does not intersect is excluded
- Point that lies on a route returns that route

## CI — `.github/workflows/build_and_test.yml`

The `acceptance-test` job:
1. Installs Python deps with `uv`
2. Builds and starts the compose stack with `docker compose up --build --wait`
3. Runs `uv run pytest tests/acceptance -v`
4. Tears down with `docker compose down -v` (runs even on failure)

`ubuntu-latest` has Docker available, so no extra setup is needed.
