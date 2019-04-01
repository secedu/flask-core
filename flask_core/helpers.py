#!/usr/bin/env python3
import json
import urllib.parse


def get_database_type(uri):
    """
    Parses the provided database URI and returns the database schema.

    Splits on + to avoid returning a configured driver.

    Example URI could be postgres+psycopg2://user:pass@host/database

    :param uri: Database connection URI
    :return:
    """
    db_scheme = urllib.parse.urlparse(uri).scheme
    type = db_scheme.split("+")[0]

    # Apply filters
    if type == "postgresql":
        type = "postgres"

    return type


def log_request():
    from flask import g, current_app, request

    log_line = "[REQUEST] {}".format(
        json.dumps(
            {
                "zid": getattr(g, "zid", "unknown user"),
                "method": request.method,
                "uri": request.url,
                "payload": request.form,
            }
        )
    ).strip("\n")

    current_app.logger.info(log_line)
