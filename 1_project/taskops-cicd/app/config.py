"""Application configuration sourced from environment variables.

No secrets are hardcoded here. Values are read at import/construction time so
that tests can override them via the environment or the ``create_app`` factory.
"""

from __future__ import annotations

import os


def _read_int(name: str, default: int) -> int:
    """Read an integer environment variable, falling back to ``default``."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class Config:
    """Base configuration read from the process environment."""

    # Never hardcode a real secret. In production FLASK_SECRET_KEY must be set;
    # the dev fallback is clearly non-secret and only keeps local runs working.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-insecure-change-me")

    # Path to the SQLite database file.
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "taskops.db")

    # Maximum allowed length for a task title.
    MAX_TITLE_LENGTH = _read_int("MAX_TITLE_LENGTH", 120)

    @classmethod
    def as_dict(cls) -> dict[str, object]:
        """Return the config as a dict suitable for ``app.config.update``."""
        return {
            "SECRET_KEY": cls.SECRET_KEY,
            "DATABASE_PATH": cls.DATABASE_PATH,
            "MAX_TITLE_LENGTH": cls.MAX_TITLE_LENGTH,
        }
