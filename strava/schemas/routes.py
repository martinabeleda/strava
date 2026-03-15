from enum import Enum
from typing import Optional

from geojson_pydantic import LineString
from pydantic import BaseModel, ConfigDict


class Activity(str, Enum):
    RUNNING = "RUNNING"
    HIKING = "HIKING"
    SKIING = "SKIING"


class RouteBase(BaseModel):
    """Represents a new route"""

    name: str
    route: LineString
    activity: Activity
    description: Optional[str]


class RouteCreate(RouteBase):
    pass


class RouteInDB(RouteCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Route(RouteInDB):
    pass


class BoundingBox(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def to_query_value(self) -> str:
        return f"{self.min_lon},{self.min_lat},{self.max_lon},{self.max_lat}"


class RouteSearchRequest(BaseModel):
    query: str


class RouteSearchInterpretation(BaseModel):
    activity: Optional[Activity] = None
    name: Optional[str] = None
    bbox: Optional[BoundingBox] = None


class RouteSearchResponse(BaseModel):
    query: str
    filters: RouteSearchInterpretation
    routes: list[Route]
