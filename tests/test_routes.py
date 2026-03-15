from unittest.mock import patch

from geojson_pydantic import LineString as GeoJsonLineString

BASE_URL = "/strava/v1/routes"

VALID_ROUTE_PAYLOAD = {
    "name": "Morning Run",
    "route": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
    "activity": "RUNNING",
    "description": "Test route",
}

MOCK_LINESTRING = GeoJsonLineString(type="LineString", coordinates=[(0.0, 0.0), (1.0, 1.0)])


class TestListRoutes:
    def test_empty_list(self, client, mock_db):
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert response.json() == []

    def test_default_pagination(self, client, mock_db):
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        client.get(f"{BASE_URL}/")
        mock_db.query.return_value.offset.assert_called_once_with(0)
        mock_db.query.return_value.offset.return_value.limit.assert_called_once_with(50)

    def test_custom_pagination(self, client, mock_db):
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        client.get(f"{BASE_URL}/?offset=10&limit=5")
        mock_db.query.return_value.offset.assert_called_once_with(10)
        mock_db.query.return_value.offset.return_value.limit.assert_called_once_with(5)


class TestCreateRoute:
    def test_missing_body(self, client):
        response = client.post(f"{BASE_URL}/", json={})
        assert response.status_code == 422

    def test_invalid_activity(self, client):
        payload = {**VALID_ROUTE_PAYLOAD, "activity": "SWIMMING"}
        response = client.post(f"{BASE_URL}/", json=payload)
        assert response.status_code == 422

    def test_invalid_geometry_type(self, client):
        payload = {**VALID_ROUTE_PAYLOAD, "route": {"type": "Point", "coordinates": [0.0, 0.0]}}
        response = client.post(f"{BASE_URL}/", json=payload)
        assert response.status_code == 422

    def test_create_success(self, client, mock_db):
        def fake_refresh(obj):
            obj.id = 1
            obj.route = "LINESTRING (0 0, 1 1)"

        mock_db.refresh.side_effect = fake_refresh

        with patch("strava.routes.routes.wkt_to_linestring", return_value=MOCK_LINESTRING):
            response = client.post(f"{BASE_URL}/", json=VALID_ROUTE_PAYLOAD)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Morning Run"
        assert data["activity"] == "RUNNING"
        assert data["id"] == 1

    def test_create_calls_db_add_and_commit(self, client, mock_db):
        def fake_refresh(obj):
            obj.id = 1
            obj.route = "LINESTRING (0 0, 1 1)"

        mock_db.refresh.side_effect = fake_refresh

        with patch("strava.routes.routes.wkt_to_linestring", return_value=MOCK_LINESTRING):
            client.post(f"{BASE_URL}/", json=VALID_ROUTE_PAYLOAD)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestListRoutesFiltering:
    def test_filter_by_activity(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get(f"{BASE_URL}/?activity=RUNNING")
        assert response.status_code == 200
        mock_db.query.return_value.filter.assert_called()

    def test_filter_by_name(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get(f"{BASE_URL}/?name=morning")
        assert response.status_code == 200
        mock_db.query.return_value.filter.assert_called()

    def test_filter_by_bbox(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get(f"{BASE_URL}/?bbox=-1.0,-1.0,2.0,2.0")
        assert response.status_code == 200
        mock_db.query.return_value.filter.assert_called()

    def test_invalid_bbox_wrong_count(self, client, mock_db):
        response = client.get(f"{BASE_URL}/?bbox=1.0,2.0,3.0")
        assert response.status_code == 422

    def test_invalid_bbox_non_numeric(self, client, mock_db):
        response = client.get(f"{BASE_URL}/?bbox=a,b,c,d")
        assert response.status_code == 422

    def test_invalid_activity(self, client, mock_db):
        response = client.get(f"{BASE_URL}/?activity=SWIMMING")
        assert response.status_code == 422

    def test_no_filters_no_filter_call(self, client, mock_db):
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        mock_db.query.return_value.filter.assert_not_called()


class TestSpatialQuery:
    def test_invalid_geometry(self, client):
        response = client.post(f"{BASE_URL}/intersect", json={"type": "Invalid"})
        assert response.status_code == 422

    def test_missing_body(self, client):
        response = client.post(f"{BASE_URL}/intersect")
        assert response.status_code == 422

    def test_empty_results(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        payload = {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}
        response = client.post(f"{BASE_URL}/intersect", json=payload)
        assert response.status_code == 200
        assert response.json() == []

    def test_accepts_polygon_geometry(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        payload = {
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]],
        }
        response = client.post(f"{BASE_URL}/intersect", json=payload)
        assert response.status_code == 200
