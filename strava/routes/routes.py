from typing import List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


from strava.schemas.routes import Route, RouteCreate
from strava.models.route import RouteModel
from strava.config import settings
from strava.db.depends import get_db

router = APIRouter(prefix=settings.API_V1_STR)


@router.get("/", response_model=List[Route])
def list_items():
    pass


@router.get("/{id}", response_model=Route)
def get_item():
    pass


@router.post("/", response_model=Route)
def create_route(
    route_in: RouteCreate,
    db: Session = Depends(get_db),
):
    """Create a new route"""
    route_in_data = jsonable_encoder(route_in)
    db_obj = RouteModel(**route_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
