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
from strava.services.route_search import RouteSearchService, fetch_routes, get_route_search_service
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
    try:
        return fetch_routes(db, offset=offset, limit=limit, activity=activity, name=name, bbox=bbox)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


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


@router.post("/search", response_model=schemas.RouteSearchResponse)
async def conversational_route_search(
    request: schemas.RouteSearchRequest,
    db: Session = Depends(get_db),
    route_search_service: RouteSearchService = Depends(get_route_search_service),
):
    """Search routes from a conversational query."""
    try:
        return await route_search_service.search(request.query, db)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
