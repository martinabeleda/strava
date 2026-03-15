from unittest.mock import MagicMock, patch

from strava.db.depends import get_db


class TestGetDb:
    def test_yields_session_and_closes_it(self):
        fake_session = MagicMock()

        with patch("strava.db.depends.SessionLocal", return_value=fake_session):
            db = get_db()
            assert next(db) is fake_session
            with patch.object(fake_session, "close") as close:
                try:
                    next(db)
                except StopIteration:
                    pass
                close.assert_called_once()


class TestDbBase:
    def test_base_module_exposes_route_model(self):
        from strava.db.base import Base, Route

        assert Route.__table__.name == "route"
        assert "route" in Base.metadata.tables
