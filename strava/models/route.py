from geoalchemy2 import Geometry
from sqlalchemy import Column, Enum, Integer, String

from strava.db.base_class import Base
from strava.schemas.routes import Activity


class Route(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    route = Column(Geometry("LINESTRING", spatial_index=True))
    activity = Column(Enum(Activity))
    description = Column(String, nullable=True)
