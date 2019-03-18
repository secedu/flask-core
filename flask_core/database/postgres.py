#!/usr/bin/env python3

from .database import Database


class Postgres(Database):
    def init_isolation(self, schema_name, tables):
        # Check if the isolation already exists
        rv = self.app.db.execute(
            f"SELECT COUNT(schema_name) FROM information_schema.schemata WHERE schema_name='{schema_name}'"
        ).fetchone()[0]

        # Check if the schema already exists
        if rv != 0:
            return

        self.app.db.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

        for table in tables:
            self.app.db.execute(f"CREATE TABLE {schema_name}.{table} AS TABLE public.{table}")
