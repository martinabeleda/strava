import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    return TestClient()


def test_dummy():
    pass
