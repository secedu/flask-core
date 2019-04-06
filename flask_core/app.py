#!/usr/bin/env python3
import logging
import os
import sys
import textwrap

from flask import Flask
from sqlalchemy import create_engine

from flask_core.helpers import log_request
from flask_core.core import bp as core_bp
from flask_core.middleware.handler import Handler
from flask_core.flag import grep_flag


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

    if config is None:
        config = app.config

    # Attempt to load config from pyfile as well, if it exists
    config.from_envvar("FLASK_CORE_CONFIG", silent=True)

    # Complain about the config.py not existing if its defined
    if "FLASK_CORE_CONFIG" in os.environ and not os.path.isfile(os.environ["FLASK_CORE_CONFIG"]):
        print(
            textwrap.dedent(
                """
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            !!!!!!   FLASK CORE CONFIG DEFINED BUT DOESN'T EXIST   !!!!!!
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            FLASK_CORE_CONFIG = %s
        """
                % (os.environ["FLASK_CORE_CONFIG"])
            ),
            file=sys.stderr,
        )

    # Validate our config
    if "validate" in dir(config):
        config.validate()

    # Load our config options into flask
    app.config.from_object(config)

    # Bootstrap our logging under gunicorn
    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # Log out our config so its visible
    app.logger.info("Running configuration:")
    for k, v in app.config.items():
        app.logger.info("\t%s -> %s", k, v)

    # setup our database connection
    app.db = None
    if "DB_CONNECTION_STRING" in app.config and app.config["DB_CONNECTION_STRING"] is not None:
        app.db = create_engine(
            app.config["DB_CONNECTION_STRING"], pool_pre_ping=app.config.get("DB_AUTO_RECONNECT", True)
        )

    # Register core blueprints
    app.register_blueprint(core_bp)

    # Register all our middleware
    app.wsgi_app = Handler(app.wsgi_app)

    # Set up magic flag generator
    app.after_request(grep_flag)

    # Register our logging helper
    app.before_request(log_request)

    return app
