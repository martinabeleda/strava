from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from strava.config import settings
from strava.db.depends import get_db
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


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
