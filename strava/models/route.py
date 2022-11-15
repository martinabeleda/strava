from sqlalchemy import Column, Integer, String, Enum
from geoalchemy2 import Geometry

from strava.db.base_class import Base
from strava.schemas.routes import Activity


class RouteModel(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    route = Column(Geometry("LINESTRING"))
    activity = Column(Enum(Activity))
    description = Column(String, nullable=True)
