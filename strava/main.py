from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from strava.config import settings
from strava.db.session import engine
from strava.observability import configure_observability
from strava.routes import routes
from strava.services import get_route_search_service

v1_router = APIRouter()
v1_router.include_router(routes.router)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await get_route_search_service().aclose()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
configure_observability(app, settings, engine)
app.include_router(v1_router, prefix=settings.API_V1_STR)
