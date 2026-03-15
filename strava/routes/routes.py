from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from geojson_pydantic.geometries import Geometry
from sqlalchemy import func
from sqlalchemy.orm import Session

from strava import schemas
from strava.db.depends import get_db
from strava.models.route import Route
from strava.schemas.routes import Activity
from strava.utils.geometry import geojson_to_wkt, wkt_to_linestring

router = APIRouter(prefix="/routes")


@router.get("/", response_model=List[schemas.Route])
async def list_items(
    offset: int = 0,
    limit: int = 50,
    activity: Optional[Activity] = None,
    name: Optional[str] = None,
    bbox: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List routes, with optional filters by activity, name substring, and bounding box.

    - **activity**: one of RUNNING, HIKING, SKIING
    - **name**: case-insensitive substring match
    - **bbox**: `minLon,minLat,maxLon,maxLat` — returns routes intersecting the box
    """
    query = db.query(Route)

    if activity:
        query = query.filter(Route.activity == activity)

    if name:
        query = query.filter(Route.name.ilike(f"%{name}%"))

    if bbox:
        parts = bbox.split(",")
        if len(parts) != 4:
            raise HTTPException(
                status_code=422,
                detail="bbox must be 4 comma-separated numbers: minLon,minLat,maxLon,maxLat",
            )
        try:
            minx, miny, maxx, maxy = [float(p) for p in parts]
        except ValueError:
            raise HTTPException(status_code=422, detail="bbox values must be numeric")
        envelope = (
            f"POLYGON(({minx} {miny},{maxx} {miny},{maxx} {maxy},{minx} {maxy},{minx} {miny}))"
        )
        query = query.filter(func.ST_Intersects(Route.route, envelope))

    results = query.offset(offset).limit(limit).all()
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
