# strava

![built and test](https://github.com/martinabeleda/strava/actions/workflows/build_and_test.yml/badge.svg)

A strava clone service for storing running, hiking and ski routes

## Developing

Run the service using docker-compose:

```shell
docker compose up --build
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
  "name": "string",
  "route": {"coordinates": [[-123.14551851584325, 49.290388113192755], [-123.14204237295995, 49.292879203437025], [-123.1387378914536, 49.29335501534475], [-123.13590547873387, 49.29523022931998], [-123.1352617485703, 49.29648966134556], [-123.13375971152196, 49.29699342514521], [-123.13247225119481, 49.29693745164395], [-123.13097021414647, 49.29763711584072], [-123.1301119072617, 49.29774906119049], [-123.12929651572118, 49.296797517612724], [-123.1279661400498, 49.29620935304344], [-123.12659284903417, 49.29738480058477], [-123.1242754204453, 49.29783258275063], [-123.1228162987412, 49.29772063759056], [-123.12084219290624, 49.29844827658597], [-123.11775228812108, 49.2981124445384], [-123.11706564261327, 49.2987281348776], [-123.11672231985936, 49.29973561156925], [-123.11672231985936, 49.30057515974646], [-123.11783811880956, 49.30023934219185], [-123.11929724051366, 49.299567700217544], [-123.12204382254491, 49.300071432556415], [-123.12487623526464, 49.30096694400129], [-123.12624952628026, 49.3025340498737], [-123.12951109244237, 49.30270195111855], [-123.13242933585057, 49.30522040114175], [-123.13543340994725, 49.30689929631448], [-123.13680670096288, 49.30986520464599], [-123.1396391136826, 49.312942845266775], [-123.14152738882909, 49.3138940771045], [-123.14581892325292, 49.31327857624819], [-123.1506254418076, 49.31238328854618], [-123.15268537833104, 49.31109628396722], [-123.15268537833104, 49.30992116346436], [-123.15405866934667, 49.309305612966384], [-123.15500280691991, 49.30852217393646], [-123.15603277518163, 49.306787371749415], [-123.15663359000096, 49.30197437492583], [-123.15946600272069, 49.3010229129263], [-123.15809271170507, 49.2987281348776], [-123.15732023550878, 49.29777661020238], [-123.154659484166, 49.29772063759056], [-123.15259954764257, 49.296489224048315], [-123.15268537833104, 49.29536973049374], [-123.15011045767675, 49.293914350859595], [-123.14925215079198, 49.2921790343646], [-123.14727804495702, 49.29066757990154], [-123.14551851584325, 49.290388113192755]], "type": "LineString"},
  "activity": "RUNNING",
  "description": "string"
}' | jq
```

### Listing routes

Now we can list the routes we've created:

```shell
curl -X 'GET' \
  'http://0.0.0.0:8080/strava/v1/routes/' \
  -H 'accept: application/json' | jq
```

### Spatial queries

We also provide an endpoint for doing spatial queries (intersection) given a `Geometry`. This can be any of the [geometry types](https://github.com/developmentseed/geojson-pydantic/blob/b20bd7ed7c3475d6df650430c864259bb246fcb0/geojson_pydantic/geometries.py#L197) in the [geojson spec](https://www.rfc-editor.org/rfc/rfc7946#section-3.1).

To execute a spatial query, `POST` a geojson containing your query shape to `/strava/v1/routes/intersect`:

```shell
curl -X 'POST' \
  'http://localhost:8080/strava/v1/routes/intersect' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"type":"Polygon","coordinates":[[[-123.98835979521789,49.415858366810966],[-122.91169963896789,49.729333082944635],[-122.01082073271789,49.27270395054359],[-122.25251995146789,48.73940752346975],[-123.98835979521789,49.415858366810966]]]}' | jq
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
