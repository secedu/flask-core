#!/usr/bin/env python3

from flask import Flask, g
from sqlalchemy import create_engine

from .core import bp as core_bp, models as core_models
from .middleware.handler import Handler
import hashlib


def gen_flag(app, zid, flag_id):
    secret = app.config["FLAG_SECRET"]
    wrapper = app.config["FLAG_WRAP"]
    s = secret + zid + str(flag_id)
    b = bytes(s, "utf-8")
    return f"{wrapper}{{{hashlib.sha256(b).hexdigest()}}}"


def check_flag(app, zid, flag):
    for flag_id in app.all_flag_ids:
        if app.gen_flag(zid, flag_id) == flag:
            return True
    return False


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
    app.all_flag_ids = app.config["FLAG_IDS"].split(",")
    app.gen_flag = lambda zid, flag_id: gen_flag(app, zid, flag_id)
    app.check_flag = lambda zid, flag: check_flag(app, zid, flag)
    return app
