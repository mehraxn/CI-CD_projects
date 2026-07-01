"""Application settings sourced from environment variables.

All values have safe defaults so the app can boot without any configuration.
Configuration is read once at import time.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the KubeNotes API."""

    app_env: str
    log_level: str
    secret_key: str

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from the process environment with safe defaults."""
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            # Default is intentionally obviously-insecure so it is never
            # mistaken for a real secret in production.
            secret_key=os.getenv("APP_SECRET_KEY", "dev-insecure-change-me"),
        )


settings = Settings.from_env()
