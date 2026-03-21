import os

import pytest
import sqlalchemy

SERVICE_URL = os.environ.get("SERVICE_URL", "http://localhost:18081")
TEST_DB_URL = os.environ.get("TEST_DB_URL", "postgresql://postgres:password@localhost:15433/test")


@pytest.fixture(scope="session")
def base_url() -> str:
    return SERVICE_URL


@pytest.fixture(scope="session")
def engine():
    eng = sqlalchemy.create_engine(TEST_DB_URL)
    yield eng
    eng.dispose()


@pytest.fixture(autouse=True)
def clean_db(engine):
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("TRUNCATE TABLE route CASCADE"))
        conn.commit()
