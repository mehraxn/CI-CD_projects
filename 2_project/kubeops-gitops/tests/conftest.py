"""Shared pytest fixtures.

Every test gets a fresh, empty in-memory store so tests are independent.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app, store


@pytest.fixture(autouse=True)
def _reset_store() -> None:
    """Reset the in-memory store before and after each test."""
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client() -> TestClient:
    """A FastAPI TestClient (backed by httpx)."""
    return TestClient(app)
