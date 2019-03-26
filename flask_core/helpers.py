#!/usr/bin/env python3

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
