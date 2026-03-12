from typing import List

from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from geojson_pydantic.geometries import Geometry
from sqlalchemy import func
from sqlalchemy.orm import Session

from strava import schemas
from strava.db.depends import get_db
from strava.models.route import Route
from strava.utils.geometry import geojson_to_wkt, wkt_to_linestring

router = APIRouter(prefix="/routes")


@router.get("/", response_model=List[schemas.Route])
async def list_items(offset: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all the routes created so far"""
    results = db.query(Route).offset(offset).limit(limit).all()
    for result in results:
        result.route = wkt_to_linestring(result.route)
    return results


@router.post("/", response_model=schemas.Route)
async def create_route(
    route_in: schemas.RouteCreate,
    db: Session = Depends(get_db),
):
    """Create a new route"""
    route_in_data = jsonable_encoder(route_in, exclude={"route"})
    route_in_data["route"] = geojson_to_wkt(route_in.route)
    db_obj = Route(**route_in_data)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    db_obj.route = wkt_to_linestring(db_obj.route)
    return db_obj


@router.post("/intersect", response_model=List[schemas.Route])
async def route_spatial_query(
    geometry: Geometry = Body(...),
    db: Session = Depends(get_db),
):
    """Find the routes that intersect with a geometry"""
    geom = geojson_to_wkt(geometry)
    routes = db.query(Route).filter(func.ST_INTERSECTS(Route.route, geom)).all()
    for route in routes:
        route.route = wkt_to_linestring(route.route)
    return routes
