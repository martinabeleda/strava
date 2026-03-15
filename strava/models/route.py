from geoalchemy2 import Geometry
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from strava.db.base_class import Base
from strava.schemas.routes import Activity


class Route(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    route: Mapped[object] = mapped_column(Geometry("LINESTRING", spatial_index=True))
    activity: Mapped[Activity] = mapped_column(Enum(Activity))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
