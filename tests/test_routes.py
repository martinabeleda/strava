from fastapi.testclient import TestClient

import pytest


@pytest.fixture
def client() -> TestClient:
    return TestClient()


def test_summy():
    pass
