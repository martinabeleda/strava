from typing import List

from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from geoalchemy2.shape import to_shape
from geojson_pydantic import LineString
from geojson_pydantic.geometries import Geometry
from shapely.geometry import mapping, shape
from sqlalchemy import func
from sqlalchemy.orm import Session

from strava import schemas
from strava.db.depends import get_db
from strava.models.route import Route

router = APIRouter(prefix="/routes")


@router.get("/", response_model=List[schemas.Route])
async def list_items(offset: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all the routes created so far"""
    results = db.query(Route).offset(offset).limit(limit).all()
    for result in results:
        result.route = LineString(**mapping(to_shape(result.route)))
    return results


@router.post("/", response_model=schemas.Route)
async def create_route(
    route_in: schemas.RouteCreate,
    db: Session = Depends(get_db),
):
    """Create a new route"""
    route_in_data = jsonable_encoder(route_in, exclude={"route"})
    route_in_data["route"] = shape(route_in.route).wkt
    db_obj = Route(**route_in_data)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    db_obj.route = LineString(**mapping(to_shape(db_obj.route)))
    return db_obj


@router.post("/intersect", response_model=List[schemas.Route])
async def route_spatial_query(
    geometry: Geometry = Body(...),
    db: Session = Depends(get_db),
):
    """Find the routes that intersect with a geometry"""
    geom = shape(geometry).wkt
    routes = db.query(Route).filter(func.ST_INTERSECTS(Route.route, geom)).all()
    for route in routes:
        route.route = LineString(**mapping(to_shape(route.route)))
    return routes
