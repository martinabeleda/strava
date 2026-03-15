from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from strava.config import Settings


def instantiate_settings() -> "Settings":
    from strava.config import Settings

    return cast(Any, Settings)()


class TestSettings:
    def test_database_uri_assembled(self):
        from strava.config import settings

        uri = str(settings.SQLALCHEMY_DATABASE_URI)
        assert uri.startswith("postgresql://")
        assert "localhost" in uri
        assert "test" in uri

    def test_api_v1_str_default(self):
        from strava.config import settings

        assert settings.API_V1_STR == "/strava/v1"

    def test_project_name(self):
        from strava.config import settings

        assert settings.PROJECT_NAME == "strava-test"

    def test_logfire_send_to_logfire_default(self):
        from strava.config import settings

        assert not settings.LOGFIRE_SEND_TO_LOGFIRE

    def test_environment_default(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        s = instantiate_settings()
        assert s.ENVIRONMENT == "development"

    def test_logfire_token_default(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")
        monkeypatch.delenv("LOGFIRE_TOKEN", raising=False)

        s = instantiate_settings()
        assert s.LOGFIRE_TOKEN is None

    def test_logfire_code_source_repository_default(self):
        from strava.config import settings

        assert settings.LOGFIRE_CODE_SOURCE_REPOSITORY == "https://github.com/martinabeleda/strava"

    def test_settings_from_env(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "my-project")
        monkeypatch.setenv("POSTGRES_SERVER", "db-host")
        monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
        monkeypatch.setenv("POSTGRES_DB", "mydb")

        s = instantiate_settings()
        assert s.PROJECT_NAME == "my-project"
        assert "db-host" in str(s.SQLALCHEMY_DATABASE_URI)
        assert "mydb" in str(s.SQLALCHEMY_DATABASE_URI)

    def test_uri_contains_user(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_USER", "myuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")

        s = instantiate_settings()
        assert "myuser" in str(s.SQLALCHEMY_DATABASE_URI)

    def test_uri_scheme(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")

        s = instantiate_settings()
        assert str(s.SQLALCHEMY_DATABASE_URI).startswith("postgresql://")

    def test_explicit_database_uri_is_preserved(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")
        monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", "postgresql://custom:pass@db/customdb")

        s = instantiate_settings()
        assert str(s.SQLALCHEMY_DATABASE_URI) == "postgresql://custom:pass@db/customdb"

    def test_validator_returns_none_without_host(self):
        from strava.config import Settings

        class Info:
            data = {}

        assert Settings.assemble_db_connection(None, cast(Any, Info())) is None

    def test_logfire_token_from_env(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")
        monkeypatch.setenv("LOGFIRE_TOKEN", "test-token")

        s = instantiate_settings()
        assert s.LOGFIRE_TOKEN == "test-token"

    def test_openai_model_default(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")

        s = instantiate_settings()
        assert s.OPENAI_MODEL == "gpt-4.1-mini"

    def test_nominatim_search_url_default(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")

        s = instantiate_settings()
        assert s.NOMINATIM_SEARCH_URL == "https://nominatim.openstreetmap.org/search"
