#!/usr/bin/env python3

import importlib
import os

from flask_core.helpers import get_database_type


class IsolationMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.app = wsgi_app.__self__

        self.isolation_lib = None
        self.isolation_tables = [t for t in os.environ.get("FLASK_CORE_ISOLATE_TABLES", "").split(",") if t.strip()]

        type = get_database_type(os.environ["DB_CONNECTION_STRING"])

        try:
            self.isolation_lib = getattr(importlib.import_module(f"flask_core.database.{type}"), type.title())(self.app)
        except ModuleNotFoundError:
            self.app.logger.error(f"Couldn't import database isolation adapter {type}.{type.title()}")

        self.app.config["FLASK_CORE_ISOLATION_ENABLED"] = self.isolation_lib and self.isolation_tables

        self.app.logger.info("Database isolation %s", self.app.config["FLASK_CORE_ISOLATION_ENABLED"])

    def __call__(self, environ, start_response):
        """
        Handles instantiation of the isolation strategy. Delegates isolation to configured isolation library as defined
        above.

        :param environ:
        :param start_response:
        :return:
        """
        if not self.app.config["FLASK_CORE_ISOLATION_ENABLED"]:
            return None

        zid = self.app.config["AUTH_CHECKER"].check_auth(environ)
        if not zid:
            raise RuntimeError("No zID provided by auth for DB isolation.")

        self.isolation_lib.init_isolation(zid, self.isolation_tables)

        return None
