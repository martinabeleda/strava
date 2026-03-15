import logfire
from fastapi import FastAPI
from sqlalchemy.engine import Engine

from strava.config import Settings


def configure_observability(app: FastAPI, settings: Settings, engine: Engine) -> None:
    logfire.configure(
        service_name=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        send_to_logfire=settings.LOGFIRE_SEND_TO_LOGFIRE,
    )
    logfire.instrument_fastapi(app)
    logfire.instrument_sqlalchemy(engine)
