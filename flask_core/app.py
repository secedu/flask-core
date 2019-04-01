#!/usr/bin/env python3
import logging
import os

from flask import Flask
from sqlalchemy import create_engine

from flask_core.helpers import log_request
from flask_core.core import bp as core_bp
from flask_core.middleware.handler import Handler


def grep_flag(response):
    from flask import g, current_app
    if not current_app.config["AUTO_GENERATED_FLAGS"]:
        return response
    try:
        data = str(response.get_data(), "utf-8")
        zid = g.zid
        for f in current_app.config["FLAG_IDS"]:
            data = data.replace(f"flag{{_{f}}}", current_app.gen_flag(zid, f))
        data = bytes(data, "utf-8")
        response.set_data(data)
    except Exception:
        pass
    return response


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

    # Set up magic flag generator (ty closure)
    app.after_request(grep_flag)

    # Register our logging helper
    app.before_request(log_request)
    return app
