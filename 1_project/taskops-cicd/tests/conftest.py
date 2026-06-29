"""Shared pytest fixtures."""

from __future__ import annotations

import os
import tempfile

import pytest

from app import create_app


@pytest.fixture()
def app():
    """Create an app instance backed by a throwaway SQLite file."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    application = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": db_path,
            "SECRET_KEY": "test-secret",
        }
    )

    yield application

    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()
