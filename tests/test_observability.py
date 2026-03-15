from typing import Any, cast
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
        "LOGFIRE_CODE_SOURCE_REPOSITORY": "https://github.com/martinabeleda/strava",
    }
    values.update(overrides)
    return cast(Any, Settings)(**values)


def test_configure_logfire_uses_default_service_name(monkeypatch):
    settings = build_settings()
    code_source = object()
    monkeypatch.delenv("GITHUB_SHA", raising=False)

    with patch(
        "strava.observability.logfire.CodeSource", return_value=code_source
    ) as build_code_source:
        with patch("strava.observability.logfire.configure") as configure:
            configure_logfire(settings)

    build_code_source.assert_called_once_with(
        repository="https://github.com/martinabeleda/strava",
        revision="main",
    )

    configure.assert_called_once_with(
        service_name="strava-test",
        environment="test",
        send_to_logfire=False,
        token="test-token",
        code_source=code_source,
    )


def test_configure_observability_wires_logfire():
    app = FastAPI()
    engine = MagicMock()
    settings = build_settings()
    code_source = object()

    with (
        patch("strava.observability.logfire.CodeSource", return_value=code_source),
        patch("strava.observability.logfire.configure") as configure,
        patch("strava.observability.logfire.instrument_fastapi") as instrument_fastapi,
        patch("strava.observability.logfire.instrument_httpx") as instrument_httpx,
        patch("strava.observability.logfire.instrument_openai") as instrument_openai,
        patch("strava.observability.logfire.instrument_pydantic_ai") as instrument_pydantic_ai,
        patch("strava.observability.logfire.instrument_sqlalchemy") as instrument_sqlalchemy,
        patch(
            "strava.observability.logfire.instrument_system_metrics"
        ) as instrument_system_metrics,
    ):
        configure_observability(app, settings, engine)

    configure.assert_called_once_with(
        service_name="strava-test",
        environment="test",
        send_to_logfire=False,
        token="test-token",
        code_source=code_source,
    )
    instrument_fastapi.assert_called_once_with(app)
    instrument_httpx.assert_called_once_with()
    instrument_openai.assert_called_once_with()
    instrument_pydantic_ai.assert_called_once_with()
    instrument_sqlalchemy.assert_called_once_with(engine)
    instrument_system_metrics.assert_called_once_with()


def test_configure_migration_observability_uses_alembic_service_name():
    engine = MagicMock()
    settings = build_settings()
    code_source = object()

    with patch("strava.observability.logfire.CodeSource", return_value=code_source):
        with patch("strava.observability.logfire.configure") as configure:
            with patch(
                "strava.observability.logfire.instrument_sqlalchemy"
            ) as instrument_sqlalchemy:
                configure_migration_observability(settings, engine)

    configure.assert_called_once_with(
        service_name="strava-test-alembic",
        environment="test",
        send_to_logfire=False,
        token="test-token",
        code_source=code_source,
    )
    instrument_sqlalchemy.assert_called_once_with(engine)
