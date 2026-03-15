import httpx

BASE_PATH = "/strava/v1/routes"

ROUTE_A = {
    "name": "Alpine Traverse",
    "route": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
    "activity": "HIKING",
    "description": "A scenic hike",
}

ROUTE_B = {
    "name": "Beach Sprint",
    "route": {"type": "LineString", "coordinates": [[10.0, 10.0], [11.0, 11.0]]},
    "activity": "RUNNING",
    "description": None,
}

ROUTE_C = {
    "name": "Sydney Harbour Loop",
    "route": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
    "activity": "RUNNING",
    "description": "A run around Circular Quay",
}

# Polygon that covers (0,0)-(2,2) — intersects ROUTE_A but not ROUTE_B
INTERSECTING_POLYGON = {
    "type": "Polygon",
    "coordinates": [[[-1.0, -1.0], [2.0, -1.0], [2.0, 2.0], [-1.0, 2.0], [-1.0, -1.0]]],
}


class TestListRoutes:
    def test_empty_db_returns_empty_list(self, base_url):
        response = httpx.get(f"{base_url}{BASE_PATH}/")
        assert response.status_code == 200
        assert response.json() == []

    def test_inserted_route_appears_in_list(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        response = httpx.get(f"{base_url}{BASE_PATH}/")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Alpine Traverse"

    def test_pagination_offset_and_limit(self, base_url):
        for route in [ROUTE_A, ROUTE_B]:
            httpx.post(f"{base_url}{BASE_PATH}/", json=route)
        response = httpx.get(f"{base_url}{BASE_PATH}/?offset=1&limit=1")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestCreateRoute:
    def test_response_contains_assigned_id(self, base_url):
        response = httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_geometry_round_trips(self, base_url):
        response = httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        assert response.status_code == 200
        data = response.json()
        assert data["route"]["type"] == "LineString"
        assert data["route"]["coordinates"] == [[0.0, 0.0], [1.0, 1.0]]

    def test_all_activity_values_persist(self, base_url):
        for activity in ["RUNNING", "HIKING", "SKIING"]:
            payload = {**ROUTE_A, "activity": activity, "name": f"Route {activity}"}
            response = httpx.post(f"{base_url}{BASE_PATH}/", json=payload)
            assert response.status_code == 200
            assert response.json()["activity"] == activity

    def test_route_persisted_to_db(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        response = httpx.get(f"{base_url}{BASE_PATH}/")
        assert len(response.json()) == 1

    def test_rejects_invalid_activity(self, base_url):
        response = httpx.post(f"{base_url}{BASE_PATH}/", json={**ROUTE_A, "activity": "SWIMMING"})
        assert response.status_code == 422

    def test_preserves_null_description(self, base_url):
        response = httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_B)
        assert response.status_code == 200
        assert response.json()["description"] is None


class TestSpatialQuery:
    def test_empty_db_returns_empty_list(self, base_url):
        response = httpx.post(f"{base_url}{BASE_PATH}/intersect", json=INTERSECTING_POLYGON)
        assert response.status_code == 200
        assert response.json() == []

    def test_intersecting_route_is_returned(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        response = httpx.post(f"{base_url}{BASE_PATH}/intersect", json=INTERSECTING_POLYGON)
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Alpine Traverse"

    def test_non_intersecting_route_is_excluded(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_B)
        response = httpx.post(f"{base_url}{BASE_PATH}/intersect", json=INTERSECTING_POLYGON)
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Alpine Traverse"

    def test_point_on_route_intersects(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        # (0.5, 0.5) lies exactly on LINESTRING(0 0, 1 1)
        point = {"type": "Point", "coordinates": [0.5, 0.5]}
        response = httpx.post(f"{base_url}{BASE_PATH}/intersect", json=point)
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1


class TestListRoutesFiltering:
    def test_filter_by_activity_returns_only_matching(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)  # HIKING
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_B)  # RUNNING
        response = httpx.get(f"{base_url}{BASE_PATH}/?activity=RUNNING")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["activity"] == "RUNNING"

    def test_filter_by_activity_hiking(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_B)
        response = httpx.get(f"{base_url}{BASE_PATH}/?activity=HIKING")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Alpine Traverse"

    def test_filter_by_name_partial_match(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_B)
        response = httpx.get(f"{base_url}{BASE_PATH}/?name=Sprint")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Beach Sprint"

    def test_filter_by_name_case_insensitive(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        response = httpx.get(f"{base_url}{BASE_PATH}/?name=alpine")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Alpine Traverse"

    def test_filter_by_bbox_covers_route_a_only(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)  # coords (0,0)-(1,1)
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_B)  # coords (10,10)-(11,11)
        response = httpx.get(f"{base_url}{BASE_PATH}/?bbox=-1.0,-1.0,2.0,2.0")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Alpine Traverse"

    def test_combined_activity_and_name_filters(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_B)
        response = httpx.get(f"{base_url}{BASE_PATH}/?activity=RUNNING&name=Beach")
        assert response.status_code == 200
        routes = response.json()
        assert len(routes) == 1
        assert routes[0]["name"] == "Beach Sprint"

    def test_no_match_returns_empty(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        response = httpx.get(f"{base_url}{BASE_PATH}/?activity=SKIING")
        assert response.status_code == 200
        assert response.json() == []

    def test_invalid_bbox_returns_validation_error(self, base_url):
        response = httpx.get(f"{base_url}{BASE_PATH}/?bbox=0.0,1.0,2.0")
        assert response.status_code == 422


class TestConversationalRouteSearch:
    def test_search_returns_structured_filters_and_matching_routes(self, base_url):
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_A)
        httpx.post(f"{base_url}{BASE_PATH}/", json=ROUTE_C)

        response = httpx.post(
            f"{base_url}{BASE_PATH}/search",
            json={"query": "Running routes in Sydney Australia"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["query"] == "Running routes in Sydney Australia"
        assert payload["filters"]["activity"] == "RUNNING"
        assert payload["filters"]["bbox"] == {
            "min_lon": -1.0,
            "min_lat": -1.0,
            "max_lon": 2.0,
            "max_lat": 2.0,
        }
        assert [route["name"] for route in payload["routes"]] == ["Sydney Harbour Loop"]
