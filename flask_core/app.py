#!/usr/bin/env python3
import logging
import os

from flask import Flask, g
from sqlalchemy import create_engine

from flask_core.helpers import log_request
from flask_core.core import bp as core_bp, models as core_models
from flask_core.middleware.handler import Handler


def create_app(config=None):
    """
    Creates an Flask application instance.

    Optionally takes in a configuration object OR fully-qualified object path. Config may also be provided through
    a pyfile pointed by FLASK_CORE_CONFIG envvar.

    If DB_CONNECTION_STRING is provided, a SQLAlchemy object will be instantiated and available at app.db

    :param config: Configuration object or string
    :return: Flask application instance
    """
    app = Flask(__name__)

    if config:
        app.config.from_object(config)

    # Bootstrap our logging under gunicorn
    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # Attempt to load config from pyfile as well, if it exists
    app.config.from_envvar("FLASK_CORE_CONFIG", silent=True)

    # setup our database connection
    if "DB_CONNECTION_STRING" in app.config:
        app.db = create_engine(
            app.config["DB_CONNECTION_STRING"], pool_pre_ping=app.config.get("DB_AUTO_RECONNECT", True)
        )

    # Register core blueprints
    app.register_blueprint(core_bp)

    # Register all our middleware
    app.wsgi_app = Handler(app.wsgi_app)

    # Register our logging helper
    app.before_request(log_request)

    return app
