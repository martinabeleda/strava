# Feature: Route Search / Filtering

## Goal

Add optional query parameters to `GET /strava/v1/routes/` so clients can filter
routes by activity type, name substring, and bounding box without breaking
existing behaviour.

## New query parameters

| Parameter    | Type   | Example                      | Description                                    |
|-------------|--------|------------------------------|------------------------------------------------|
| `activity`  | enum   | `?activity=RUNNING`          | Filter by activity type (RUNNING/HIKING/SKIING)|
| `name`      | string | `?name=morning`              | Case-insensitive substring match on route name |
| `bbox`      | string | `?bbox=-122.5,37.7,-122.4,37.8` | Bounding box filter: `minLon,minLat,maxLon,maxLat`. Returns routes whose geometry intersects the bbox. |

All parameters are optional and combinable. Existing `offset`/`limit` still work.

## Implementation plan

### 1. `strava/routes/routes.py` — `list_items` endpoint

Add three optional query params. Build the SQLAlchemy query conditionally:

```python
async def list_items(
    offset: int = 0,
    limit: int = 50,
    activity: Optional[Activity] = None,
    name: Optional[str] = None,
    bbox: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Route)
    if activity:
        query = query.filter(Route.activity == activity)
    if name:
        query = query.filter(Route.name.ilike(f"%{name}%"))
    if bbox:
        minx, miny, maxx, maxy = [float(v) for v in bbox.split(",")]
        envelope = f"POLYGON(({minx} {miny},{maxx} {miny},{maxx} {maxy},{minx} {maxy},{minx} {miny}))"
        query = query.filter(func.ST_Intersects(Route.route, envelope))
    results = query.offset(offset).limit(limit).all()
    ...
```

- Validate bbox has exactly 4 comma-separated floats; return HTTP 422 otherwise.
- Use `ST_Intersects` (PostGIS) for the bbox check — consistent with the existing
  `/intersect` endpoint.

### 2. Unit tests — `tests/test_routes.py`

Add a `TestListRoutesFiltering` class with mocked DB:

- `test_filter_by_activity` — verifies `filter` is called when `activity` param given
- `test_filter_by_name` — verifies `ilike` filter applied
- `test_filter_by_bbox` — verifies `ST_Intersects` filter applied
- `test_invalid_bbox_returns_422` — non-numeric / wrong count of values → 422
- `test_filters_are_optional` — no params → same behaviour as before (no filter call)

### 3. Acceptance tests — `tests/acceptance/test_routes.py`

Add `TestListRoutesFiltering` class hitting real PostGIS:

- Create ROUTE_A (HIKING) and ROUTE_B (RUNNING) as fixtures.
- `test_filter_by_activity_running` — only ROUTE_B returned
- `test_filter_by_activity_hiking` — only ROUTE_A returned
- `test_filter_by_name_partial` — search `"Sprint"` returns only ROUTE_B
- `test_filter_by_bbox_covers_route_a` — bbox covering ROUTE_A coords returns only ROUTE_A
- `test_combined_filters` — activity + name, single result

## Out of scope

- Sorting / ordering
- Full-text search (trigram index)
- Bounding-box stored as a separate column
