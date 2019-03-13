#!/usr/bin/env python3

from flask import Flask
from sqlalchemy import create_engine
import secrets 

from .core import bp as core_bp, models as core_models

from .middleware.AuthMiddleware import AuthMiddleware


class CseUserSession:
    def __init__(self, token):
        self.token = token 
        self.db_name = None
        self.db = None
    
def create_app(config=None):
    """
    Creates an Flask application instance.

    Optionally takes in a configuration object OR fully-qualified object path. Config may also be provided through
    a pyfile pointed by FLASK_CORE_CONFIG envvar.

    :param config: Configuration object or string
    :return: Flask application instance
    """
    app = Flask(__name__)

    if config:
        app.config.from_object(config)

    # Attempt to load config from pyfile as well, if it exists
    app.config.from_envvar("FLASK_CORE_CONFIG", silent=True)
    db_config = config["DB_CONFIG"]
    # set up root access 
    app.root_db = create_engine(f"{db_config["DB_PROTOCOL"]}://{db_config["DB_ROOT_USERNAME"]}:{db_config["DB_ROOT_PASSWORD"]}@{db_config["DB_HOST"]}")

    # chuck schema into db via root connection
    app.root_db.exeucte(db_config["DB_SCHEMA"])
    passwd = secrets.token_hex(16)
    app.shared_password = passwd

    if db_config["DB_MODE"] == "GLOBAL":
        #TODO: make this work for all sql types
        app.root_db.execute("CREATE USER global_user WITH PASSWORD %s",(passwd,))
        app.root_db.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {db_config['DB_BASE']} TO global_user")
    
    app.register_blueprint(core_bp)

    # Add a map of k(zid) -> v(Session)
    app.active_sessions = {}

    # Authentication middleware
    app.wsgi_app = AuthMiddleware(app.wsgi_app)

    # TODO: insert logging middleware


    return app
