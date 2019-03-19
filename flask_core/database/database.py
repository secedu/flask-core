#!/usr/bin/env python3

from abc import ABC


class Database(ABC):
    def __init__(self, app):
        self.app = app

    def init_isolation(self, schema_name, tables):
        raise NotImplementedError
