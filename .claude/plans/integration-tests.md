# Integration Test Plan

Add database-backed integration tests using `testcontainers` to spin up a real
PostGIS instance, run the Alembic migrations, and test all three API endpoints
against actual SQL — including the `ST_INTERSECTS` spatial query.

## Why

The unit tests mock the DB session entirely, so they can't catch:
- Incorrect SQL / ORM query construction
- GeoAlchemy2 ↔ PostGIS serialisation bugs
- Migration regressions (schema out of sync with models)
- `ST_INTERSECTS` returning wrong results for given geometries

## Approach: testcontainers-python

Use `testcontainers[postgres]` to spin up `postgis/postgis:15-3.3` (same image
as docker-compose.yml) inside the test process. No external DB required — works
locally and in CI.

Session-scoped fixture creates the container once per test run; each test wraps
its writes in a transaction that rolls back, keeping tests isolated and fast.

## Steps

### 1. Add dependency

```toml
# pyproject.toml [dependency-groups] dev
"testcontainers[postgres]>=4.0.0",
```

### 2. Create `tests/integration/conftest.py`

Session-scoped fixtures:

```
container      — starts postgis/postgis:15-3.3, exposes a random port
engine         — SQLAlchemy engine pointed at the container
tables         — runs alembic upgrade head (or create_all) once
db_session     — per-test: opens a transaction, yields session, rolls back
client         — FastAPI TestClient with get_db overridden to use db_session
```

Key detail: use a nested transaction (SAVEPOINT) so each test rolls back
without restarting the container:

```python
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

### 3. Create `tests/integration/test_routes_integration.py`

#### `TestListRoutes`
- Empty DB returns `[]`
- Inserted route appears in list response
- `offset` / `limit` pagination is respected

#### `TestCreateRoute`
- POST creates a row in the `route` table
- Response contains the assigned `id`
- Geometry round-trips correctly (GeoJSON in → GeoJSON out)
- All three `Activity` values persist and are returned correctly

#### `TestSpatialQuery`
- Route that intersects the query geometry is returned
- Route that does not intersect is excluded
- Query with a Point geometry that lies on a route returns that route
- Empty DB returns `[]`

### 4. CI — `.github/workflows/test.yml`

No extra services block needed; testcontainers handles the container lifecycle
via the Docker socket. Ensure the runner has Docker available (standard on
`ubuntu-latest`).

## File Layout After

```
tests/
├── conftest.py                          # existing unit-test fixtures
├── test_schemas.py
├── test_config.py
├── test_geometry.py
├── test_routes.py
└── integration/
    ├── __init__.py
    ├── conftest.py                      # container + session fixtures
    └── test_routes_integration.py      # DB-backed endpoint tests
```

## Notes

- Run unit tests only: `uv run pytest tests/ --ignore=tests/integration`
- Run integration tests only: `uv run pytest tests/integration`
- Run everything: `uv run pytest`
- The container adds ~10–15 s startup overhead once per session, then individual
  tests run at near-unit-test speed due to the rollback strategy.
