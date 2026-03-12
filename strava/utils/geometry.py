from geoalchemy2.shape import to_shape
from geojson_pydantic import LineString
from shapely.geometry import mapping, shape


def geojson_to_wkt(geojson) -> str:
    """Convert a GeoJSON geometry to a WKT string."""
    return shape(geojson).wkt


def wkt_to_linestring(wkt_element) -> LineString:
    """Convert a GeoAlchemy2 WKT element to a GeoJSON LineString."""
    return LineString(**mapping(to_shape(wkt_element)))
