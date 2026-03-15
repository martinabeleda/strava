# strava

![built and test](https://github.com/martinabeleda/strava/actions/workflows/build_and_test.yml/badge.svg)

A strava clone service for storing running, hiking and ski routes

## Developing

Run the service using docker-compose:

```shell
cp .env.example .env
docker compose up --build
```

The dev compose setup reads `LOGFIRE_TOKEN` from `.env` and passes it into the `service` container so Logfire can export telemetry.
Set `OPENAI_API_KEY` in `.env` as well if you want to use the conversational route search endpoint.

## Local development with uv

Install dependencies and development tooling with [uv](https://docs.astral.sh/uv/):

```shell
uv sync --dev
```

Run checks and tests:

```shell
uv run ruff format --check .
uv run ruff check .
uv run pytest -s --junitxml=./test-report.xml --cov=./ --cov-report=xml .
```

## Load testing

Install the development dependencies first:

```shell
uv sync --dev
```

With the local compose stack running on `http://localhost:8080`, start Locust with:

```shell
make load-test
```

That opens the Locust UI on `http://localhost:8089` and targets `http://localhost:8080` by default.

To generate report files locally, run:

```shell
make load-test-report
```

That writes artifacts to `loadtest/reports/` by default:

- `loadtest/reports/locust.html`
- `loadtest/reports/locust_stats.csv`
- `loadtest/reports/locust_failures.csv`
- `loadtest/reports/locust_exceptions.csv`

You can override the defaults with `LOCUST_USERS`, `LOCUST_SPAWN_RATE`, `LOCUST_RUN_TIME`, `LOCUST_HOST`, `LOAD_TEST_REPORT_DIR`, and `LOAD_TEST_REPORT_PREFIX`.

To run headless against local compose:

```shell
LOCUST_HOST=http://localhost:8080 uv run locust -f loadtest/locustfile.py --headless --users 10 --spawn-rate 2 --run-time 1m
```

To point the same test at a dev or prod service in a cluster, change only the target host and, if needed, the API prefix:

```shell
LOCUST_HOST=https://strava.dev.example.com STRAVA_API_PREFIX=/strava/v1 uv run locust -f loadtest/locustfile.py --headless --users 25 --spawn-rate 5 --run-time 5m
```

## User guide

This service manages creating routes for activities much like strava does. A route can have a `name` and `description`, is an `activity` that can be one of `RUNNING`, `HIKING` or `SKIING` and has a `route`. We use geojson to describe the route and specifically a route is a 2D `LineString` to make things simple.

### Creating a route

Let's create our first route:

```shell
curl -X 'POST' \
  'http://0.0.0.0:8080/strava/v1/routes/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Sydney Harbour Loop",
  "route": {
    "type": "LineString",
    "coordinates": [
      [151.2093, -33.8688],
      [151.2153, -33.8568],
      [151.2217, -33.8523]
    ]
  },
  "activity": "RUNNING",
  "description": "A run from Circular Quay up toward the Opera House"
}' | jq
```

### Failing request example

This request uses an invalid `activity` value and should return `422 Unprocessable Entity`:

```shell
curl -X 'POST' \
  'http://0.0.0.0:8080/strava/v1/routes/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "broken route",
  "route": {
    "type": "LineString",
    "coordinates": [
      [0.0, 0.0],
      [1.0, 1.0]
    ]
  },
  "activity": "SWIMMING",
  "description": "this should fail"
}' | jq
```

This request uses an invalid `bbox` value and should also return `422 Unprocessable Entity`:

```shell
curl -X 'GET' \
  'http://0.0.0.0:8080/strava/v1/routes/?bbox=1.0,2.0,3.0' \
  -H 'accept: application/json' | jq
```

### Listing routes

Now we can list the routes we've created:

```shell
curl -X 'GET' \
  'http://0.0.0.0:8080/strava/v1/routes/' \
  -H 'accept: application/json' | jq
```

### Conversational route search

This endpoint uses `pydantic_ai` with the OpenAI Python library to translate natural language into route filters. When a place is mentioned, the agent can resolve it to a bounding box before querying the database.

```shell
curl -X 'POST' \
  'http://0.0.0.0:8080/strava/v1/routes/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Running routes in Sydney Australia"
  }' | jq
```

### Spatial queries

We also provide an endpoint for doing spatial queries (intersection) given a `Geometry`. This can be any of the [geometry types](https://github.com/developmentseed/geojson-pydantic/blob/b20bd7ed7c3475d6df650430c864259bb246fcb0/geojson_pydantic/geometries.py#L197) in the [geojson spec](https://www.rfc-editor.org/rfc/rfc7946#section-3.1).

To execute a spatial query, `POST` a geojson containing your query shape to `/strava/v1/routes/intersect`:

```shell
curl -X 'POST' \
  'http://localhost:8080/strava/v1/routes/intersect' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "Polygon",
    "coordinates": [
      [
        [-123.98835979521789,49.415858366810966],
        [-122.91169963896789,49.729333082944635],
        [-122.01082073271789,49.27270395054359],
        [-122.25251995146789,48.73940752346975],
        [-123.98835979521789,49.415858366810966]
      ]
    ]
  }' | jq
```

## Creating a new migration

To create a new migration, run the docker compose and open a shell into the service container:

```shell
docker exec -it strava-service-1 bash
```

Then use alembic's autogenerate feature:

```shell
alembic revision --autogenerate -m "Added route table"
```
