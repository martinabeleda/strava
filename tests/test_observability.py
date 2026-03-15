from unittest.mock import MagicMock, patch

from fastapi import FastAPI

from strava.config import Settings
from strava.observability import (
    configure_logfire,
    configure_migration_observability,
    configure_observability,
)


def build_settings(**overrides):
    values = {
        "PROJECT_NAME": "strava-test",
        "ENVIRONMENT": "test",
        "POSTGRES_SERVER": "localhost",
        "POSTGRES_PASSWORD": "password",
        "POSTGRES_DB": "test",
        "LOGFIRE_SEND_TO_LOGFIRE": False,
        "LOGFIRE_TOKEN": "test-token",
    }
    values.update(overrides)
    return Settings(**values)


def test_configure_logfire_uses_default_service_name():
    settings = build_settings()

    with patch("strava.observability.logfire.configure") as configure:
        configure_logfire(settings)

    configure.assert_called_once_with(
        service_name="strava-test",
        environment="test",
        send_to_logfire=False,
        token="test-token",
    )


def test_configure_observability_wires_logfire():
    app = FastAPI()
    engine = MagicMock()
    settings = build_settings()

    with patch("strava.observability.logfire.configure") as configure:
        with patch("strava.observability.logfire.instrument_fastapi") as instrument_fastapi:
            with patch(
                "strava.observability.logfire.instrument_sqlalchemy"
            ) as instrument_sqlalchemy:
                configure_observability(app, settings, engine)

    configure.assert_called_once_with(
        service_name="strava-test",
        environment="test",
        send_to_logfire=False,
        token="test-token",
    )
    instrument_fastapi.assert_called_once_with(app)
    instrument_sqlalchemy.assert_called_once_with(engine)


def test_configure_migration_observability_uses_alembic_service_name():
    engine = MagicMock()
    settings = build_settings()

    with patch("strava.observability.logfire.configure") as configure:
        with patch("strava.observability.logfire.instrument_sqlalchemy") as instrument_sqlalchemy:
            configure_migration_observability(settings, engine)

    configure.assert_called_once_with(
        service_name="strava-test-alembic",
        environment="test",
        send_to_logfire=False,
        token="test-token",
    )
    instrument_sqlalchemy.assert_called_once_with(engine)
