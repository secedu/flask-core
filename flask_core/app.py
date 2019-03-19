#!/usr/bin/env python3
import types

from contextlib import contextmanager
from functools import partial

from flask import Flask, g
from sqlalchemy import create_engine

from flask_core.helpers import get_database_type
from .core import bp as core_bp, models as core_models
from .middleware.handler import Handler


@contextmanager
def _isolate(self, app, ns=None):
    """
    Database helper to isolate database requests.

    To isolate database requests, wrap your statement like so:

    ```python3
    with app.db.isolate() as conn:
        conn.execute('...')  # isolated to zid schemata

    app.db.execute('...')  # NOT isolated to zid schemata
    ```

    :param self:
    :param app:
    :param ns: Namespace to isolate database requests to. If not provided, a best attempt is made to acquire the current
    students zID.
    :return:
    """
    from flask import g

    conn = self.connect()
    db_type = get_database_type(app.config["DB_CONNECTION_STRING"])

    if app.config["FLASK_CORE_ISOLATION_ENABLED"]:
        try:
            ns = ns or g.zid

            if not ns:
                raise AttributeError
        except AttributeError:
            app.logger.error(f"Application couldn't acquire zID and no namespace was provided.")
        else:
            if db_type == "postgres":
                conn.execute(f"SET search_path TO '{ns}'")
            else:
                app.logger.warn(f"DB isolation not available on this database type {db_type}")

    yield conn

    conn.close()


def _register_zid():
    """
    This operates in the flask request context. We pass in the WSGI environ into the configured auth_checker and
    register the provided zID into the request-scoped globals.

    :return: None
    """
    from flask import g, request, current_app

    g.zid = current_app.config["AUTH_CHECKER"].check_auth(request.environ)


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
        app.db = create_engine(app.config["DB_CONNECTION_STRING"])

        # Bind our isolate method on and add our flask instance onto it
        app.db.isolate = partial(types.MethodType(_isolate, app.db), app=app)

    # Attempt to register the zID onto the flask.g object
    app.before_request(_register_zid)

    # Register core blueprints
    app.register_blueprint(core_bp)

    # Register all our middleware
    app.wsgi_app = Handler(app.wsgi_app)

    return app
