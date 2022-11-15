from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from shapely.geometry import shape, mapping

from geojson_pydantic import LineString
from geoalchemy2.shape import to_shape

from strava import schemas
from strava.models.route import Route
from strava.config import settings
from strava.db.depends import get_db

router = APIRouter(prefix=settings.API_V1_STR)


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
