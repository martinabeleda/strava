from unittest.mock import MagicMock, patch

from geojson_pydantic import LineString
from shapely.geometry import LineString as ShapelyLineString

from strava.utils.geometry import geojson_to_wkt, wkt_to_linestring

LINESTRING_GEOJSON = {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}


class TestGeojsonToWkt:
    def test_linestring(self):
        wkt = geojson_to_wkt(LINESTRING_GEOJSON)
        assert wkt == "LINESTRING (0 0, 1 1)"

    def test_returns_string(self):
        assert isinstance(geojson_to_wkt(LINESTRING_GEOJSON), str)

    def test_three_point_linestring(self):
        geojson = {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]]}
        wkt = geojson_to_wkt(geojson)
        assert "LINESTRING" in wkt
        assert "2 2" in wkt

    def test_contains_coordinates(self):
        wkt = geojson_to_wkt(LINESTRING_GEOJSON)
        assert "0 0" in wkt
        assert "1 1" in wkt


class TestWktToLinestring:
    def test_returns_linestring_type(self):
        shapely_line = ShapelyLineString([(0, 0), (1, 1)])
        mock_wkt_element = MagicMock()

        with patch("strava.utils.geometry.to_shape", return_value=shapely_line):
            result = wkt_to_linestring(mock_wkt_element)

        assert isinstance(result, LineString)

    def test_geometry_type_field(self):
        shapely_line = ShapelyLineString([(0, 0), (1, 1)])
        mock_wkt_element = MagicMock()

        with patch("strava.utils.geometry.to_shape", return_value=shapely_line):
            result = wkt_to_linestring(mock_wkt_element)

        assert result.type == "LineString"

    def test_coordinate_count(self):
        shapely_line = ShapelyLineString([(0, 0), (1, 1)])
        mock_wkt_element = MagicMock()

        with patch("strava.utils.geometry.to_shape", return_value=shapely_line):
            result = wkt_to_linestring(mock_wkt_element)

        assert len(result.coordinates) == 2

    def test_passes_wkt_element_to_to_shape(self):
        shapely_line = ShapelyLineString([(0, 0), (1, 1)])
        mock_wkt_element = MagicMock()

        with patch("strava.utils.geometry.to_shape", return_value=shapely_line) as mock_to_shape:
            wkt_to_linestring(mock_wkt_element)

        mock_to_shape.assert_called_once_with(mock_wkt_element)
