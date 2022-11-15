from fastapi import APIRouter, FastAPI

from strava.config import settings
from strava.routes import routes

v1_router = APIRouter()
v1_router.include_router(routes.router)

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(v1_router, prefix=settings.API_V1_STR)
