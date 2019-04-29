#!/usr/bin/env python3

import importlib
import os
import types
from contextlib import contextmanager
from functools import partial

from flask_core.helpers import get_database_type


class IsolationMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.app = wsgi_app.__self__

        self.isolation_lib = None
        self.isolation_tables = self.app.config["ISOLATION_TABLES"]

        type = get_database_type(self.app.config["DB_CONNECTION_STRING"])

        try:
            self.isolation_lib = getattr(importlib.import_module(f"flask_core.database.{type}"), type.title())(self.app)
        except ModuleNotFoundError:
            self.app.logger.error(f"Couldn't import database isolation adapter {type}.{type.title()}")

        self.app.config["ISOLATION_ENABLED"] = (
            self.app.config["ENABLE_ISOLATION"] and self.isolation_lib and self.isolation_tables
        )

        self.app.logger.info("Database isolation %s", "enabled" if self.app.config["ISOLATION_ENABLED"] else "disabled")

        # Bind our isolate method on and add our flask instance onto it
        self.app.db.isolate = partial(types.MethodType(self._isolate, self.app), db=self.app.db)

    def __call__(self, environ, start_response):
        """
        Handles instantiation of the isolation strategy. Delegates isolation to configured isolation library as defined
        above.

        :param environ:
        :param start_response:
        :return:
        """
        if not self.app.config["ISOLATION_ENABLED"]:
            return None

        zid = self.app.config["AUTH_CHECKER"].check_auth(environ)
        if not zid:
            raise RuntimeError("No zID provided by auth for DB isolation.")

        self.isolation_lib.init_isolation(zid, self.isolation_tables)

        return None

    @staticmethod
    @contextmanager
    def _isolate(app, db, ns=None):
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

        conn = db.connect()
        db_type = get_database_type(app.config["DB_CONNECTION_STRING"])

        if app.config["ISOLATION_ENABLED"]:
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
