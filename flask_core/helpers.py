#!/usr/bin/env python3

import urllib.parse


def get_database_type(uri):
    db_scheme = urllib.parse.urlparse(uri).scheme
    type = db_scheme.split("+")[0]

    return type
