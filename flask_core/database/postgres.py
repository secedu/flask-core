#!/usr/bin/env python3

from .database import Database


class Postgres(Database):
    def init_isolation(self, schema_name, tables):
        """
        Creates a new schema with passed in tables and copies data from the public schema.

        :param schema_name: Schema name
        :param tables: Tables to copy from public schema
        :return: None
        """

        # Check if the isolation already exists
        rv = self.app.db.execute(
            f"SELECT COUNT(schema_name) FROM information_schema.schemata WHERE schema_name='{schema_name}'"
        ).fetchone()[0]

        # Check if the schema already exists
        if rv != 0:
            return

        self.app.db.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

        # TODO: figure out if we can copy the schema and populate it without having to do separate create and inserts
        for table in tables:
            self.app.db.execute(f"CREATE TABLE {schema_name}.{table} (like public.{table} including all)")
            self.app.db.execute(f"INSERT INTO {schema_name}.{table} SELECT * FROM public.{table}")
