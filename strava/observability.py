import logfire
from fastapi import FastAPI
from sqlalchemy.engine import Engine

from strava.config import Settings


def configure_logfire(settings: Settings, *, service_name: str | None = None) -> None:
    logfire.configure(
        service_name=service_name or settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        send_to_logfire=settings.LOGFIRE_SEND_TO_LOGFIRE,
        token=settings.LOGFIRE_TOKEN,
    )


def configure_observability(app: FastAPI, settings: Settings, engine: Engine) -> None:
    configure_logfire(settings)
    logfire.instrument_fastapi(app)
    logfire.instrument_sqlalchemy(engine)
    logfire.instrument_system_metrics()


def configure_migration_observability(settings: Settings, engine: Engine) -> None:
    configure_logfire(settings, service_name=f"{settings.PROJECT_NAME}-alembic")
    logfire.instrument_sqlalchemy(engine)
