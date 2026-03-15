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

    def test_environment_default(self):
        from strava.config import settings

        assert settings.ENVIRONMENT == "development"

    def test_settings_from_env(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "my-project")
        monkeypatch.setenv("POSTGRES_SERVER", "db-host")
        monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
        monkeypatch.setenv("POSTGRES_DB", "mydb")

        from strava.config import Settings

        s = Settings()
        assert s.PROJECT_NAME == "my-project"
        assert "db-host" in str(s.SQLALCHEMY_DATABASE_URI)
        assert "mydb" in str(s.SQLALCHEMY_DATABASE_URI)

    def test_uri_contains_user(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_USER", "myuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")

        from strava.config import Settings

        s = Settings()
        assert "myuser" in str(s.SQLALCHEMY_DATABASE_URI)

    def test_uri_scheme(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")

        from strava.config import Settings

        s = Settings()
        assert str(s.SQLALCHEMY_DATABASE_URI).startswith("postgresql://")

    def test_explicit_database_uri_is_preserved(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "test")
        monkeypatch.setenv("POSTGRES_SERVER", "localhost")
        monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
        monkeypatch.setenv("POSTGRES_DB", "db")
        monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", "postgresql://custom:pass@db/customdb")

        from strava.config import Settings

        s = Settings()
        assert str(s.SQLALCHEMY_DATABASE_URI) == "postgresql://custom:pass@db/customdb"

    def test_validator_returns_none_without_host(self):
        from strava.config import Settings

        class Info:
            data = {}

        assert Settings.assemble_db_connection(None, Info()) is None
