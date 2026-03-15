from fastapi import APIRouter, FastAPI

from strava.config import settings
from strava.db.session import engine
from strava.observability import configure_observability
from strava.routes import routes

v1_router = APIRouter()
v1_router.include_router(routes.router)

app = FastAPI(title=settings.PROJECT_NAME)
configure_observability(app, settings, engine)
app.include_router(v1_router, prefix=settings.API_V1_STR)
