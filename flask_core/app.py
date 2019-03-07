#!/usr/bin/env python3

from flask import Flask
from sqlalchemy import create_engine

from .core import (
    bp as core_bp,
    models as core_models,
)


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

    # Attempt to load config from pyfile as well, if it exists
    app.config.from_envvar("FLASK_CORE_CONFIG", silent=True)

    if "DB_CONNECTION_STRING" in app.config:
        # setup our database connection
        app.db = create_engine(app.config["DB_CONNECTION_STRING"])

    app.register_blueprint(core_bp)

    # TODO: insert logging middleware

    return app
