import pytest
from fastapi.testclient import TestClient

from fast1.app import app


@pytest.fixture
def client():
    return TestClient(app)
