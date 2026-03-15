from typing import Any, Literal, Optional, cast

from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/strava/v1"

    PROJECT_NAME: str
    ENVIRONMENT: str = "development"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    NOMINATIM_SEARCH_URL: str = "https://nominatim.openstreetmap.org/search"
    NOMINATIM_TIMEOUT_SECONDS: float = 10.0
    ROUTE_SEARCH_MOCK_RESPONSE: str | None = None
    LOGFIRE_SEND_TO_LOGFIRE: bool | Literal["if-token-present"] = "if-token-present"
    LOGFIRE_TOKEN: str | None = None
    LOGFIRE_CODE_SOURCE_REPOSITORY: str = "https://github.com/martinabeleda/strava"
    LOGFIRE_CODE_SOURCE_REVISION: str | None = None

    POSTGRES_SERVER: str
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        host = info.data.get("POSTGRES_SERVER")
        if not host:
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=host,
            path=info.data.get("POSTGRES_DB") or "",
        )

    model_config = SettingsConfigDict(case_sensitive=True)


def load_settings() -> Settings:
    """Instantiate env-backed settings at the one place static typing cannot express."""
    # Pydantic loads required fields from environment variables at runtime, but `ty`
    # only sees the generated constructor signature and assumes those fields must be
    # passed explicitly.
    return cast(Any, Settings)()


settings = load_settings()
