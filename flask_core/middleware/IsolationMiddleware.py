#!/usr/bin/env python3

import importlib
import os
import urllib.parse


class IsolationMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.app = wsgi_app.__self__

        self.isolation_lib = None
        self.isolation_tables = [t for t in os.environ.get("FLASK_CORE_ISOLATE_TABLES", "").split(",") if t.strip()]

        try:
            db_scheme = urllib.parse.urlparse(self.app.config["DB_CONNECTION_STRING"]).scheme
        except Exception as e:
            self.app.logger.error(f"Couldn't pick up database connection URI. error({e})")
        else:
            # Try import the appropriate adapter
            type = db_scheme.split("+")[0]

            try:
                self.isolation_lib = getattr(importlib.import_module(f"flask_core.database.{type}"), type.title())(
                    self.app
                )
            except ModuleNotFoundError:
                self.app.logger.error(f"Couldn't import database isolation adapter {type}.{type.title()}")

    def __call__(self, environ, start_response):
        if not self.isolation_lib or not self.isolation_tables:
            return None

        zid = self.app.config["AUTH_CHECKER"].check_auth(environ)
        if not zid:
            raise RuntimeError("No zID available for DB isolation.")

        self.isolation_lib.init_isolation(zid, self.isolation_tables)

        return None
