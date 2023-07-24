from typing import Any, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/strava/v1"

    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI")
    def assemble_db_connection(cls, v, info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            user=info.data["POSTGRES_USER"],
            password=info.data["POSTGRES_PASSWORD"],
            host=info.data["POSTGRES_SERVER"],
            path=f"/{info.data['POSTGRES_DB'] or ''}",
        )

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
