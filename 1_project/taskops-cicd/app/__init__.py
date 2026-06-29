"""Application factory for TaskOps."""

from __future__ import annotations

import logging
import sys
from collections.abc import Mapping
from typing import Any

from flask import Flask

from .config import Config
from .database import close_db, init_db


def _configure_logging(app: Flask) -> None:
    """Send application logs to stdout in a consistent format."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    # Avoid duplicate handlers if the factory runs more than once.
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    """Create and configure a Flask application instance.

    ``test_config`` allows tests to override configuration (for example
    ``DATABASE_PATH``) without touching the process environment.
    """
    app = Flask(__name__)
    app.config.update(Config.as_dict())

    if test_config:
        app.config.update(test_config)

    _configure_logging(app)

    # Tear down the request-scoped DB connection after each request.
    app.teardown_appcontext(close_db)

    # Register HTTP routes.
    from .routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    # Create the schema on startup within an app context.
    with app.app_context():
        init_db()

    app.logger.info(
        "TaskOps started (database=%s, max_title=%s)",
        app.config["DATABASE_PATH"],
        app.config["MAX_TITLE_LENGTH"],
    )

    return app
