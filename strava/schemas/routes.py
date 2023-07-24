from enum import Enum
from typing import Optional

from geojson_pydantic import LineString
from pydantic import ConfigDict, BaseModel


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
