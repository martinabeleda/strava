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
