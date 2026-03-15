import pytest
from geojson_pydantic import LineString
from pydantic import ValidationError

from strava.schemas.routes import Activity, RouteCreate, RouteInDB

VALID_LINESTRING = {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}
VALID_ROUTE = LineString.model_validate(VALID_LINESTRING)


class TestActivity:
    def test_valid_values(self):
        assert Activity.RUNNING == "RUNNING"
        assert Activity.HIKING == "HIKING"
        assert Activity.SKIING == "SKIING"


class TestRouteCreate:
    def test_valid_route(self):
        route = RouteCreate(
            name="Morning Run",
            route=VALID_ROUTE,
            activity=Activity.RUNNING,
            description="A nice run",
        )
        assert route.name == "Morning Run"
        assert route.activity == Activity.RUNNING
        assert route.description == "A nice run"

    def test_description_optional(self):
        route = RouteCreate(
            name="Morning Run",
            route=VALID_ROUTE,
            activity=Activity.RUNNING,
            description=None,
        )
        assert route.description is None

    def test_all_activities_valid(self):
        for activity in Activity:
            route = RouteCreate(
                name="Test",
                route=VALID_ROUTE,
                activity=activity,
                description=None,
            )
            assert route.activity == activity

    def test_invalid_activity(self):
        with pytest.raises(ValidationError):
            RouteCreate.model_validate(
                {
                    "name": "Morning Run",
                    "route": VALID_LINESTRING,
                    "activity": "SWIMMING",
                    "description": None,
                }
            )

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            RouteCreate.model_validate(
                {
                    "route": VALID_LINESTRING,
                    "activity": Activity.RUNNING,
                    "description": None,
                }
            )

    def test_missing_activity(self):
        with pytest.raises(ValidationError):
            RouteCreate.model_validate(
                {
                    "name": "Morning Run",
                    "route": VALID_LINESTRING,
                    "description": None,
                }
            )

    def test_missing_route(self):
        with pytest.raises(ValidationError):
            RouteCreate.model_validate(
                {
                    "name": "Morning Run",
                    "activity": Activity.RUNNING,
                    "description": None,
                }
            )

    def test_invalid_geometry_type(self):
        with pytest.raises(ValidationError):
            RouteCreate.model_validate(
                {
                    "name": "Morning Run",
                    "route": {"type": "Point", "coordinates": [0.0, 0.0]},
                    "activity": Activity.RUNNING,
                    "description": None,
                }
            )

    def test_invalid_geometry_missing_coordinates(self):
        with pytest.raises(ValidationError):
            RouteCreate.model_validate(
                {
                    "name": "Morning Run",
                    "route": {"type": "LineString"},
                    "activity": Activity.RUNNING,
                    "description": None,
                }
            )


class TestRouteInDB:
    def test_requires_id(self):
        with pytest.raises(ValidationError):
            RouteInDB.model_validate(
                {
                    "name": "Morning Run",
                    "route": VALID_LINESTRING,
                    "activity": Activity.RUNNING,
                    "description": None,
                }
            )

    def test_valid_with_id(self):
        route = RouteInDB(
            id=1,
            name="Morning Run",
            route=VALID_ROUTE,
            activity=Activity.RUNNING,
            description=None,
        )
        assert route.id == 1
        assert route.name == "Morning Run"
