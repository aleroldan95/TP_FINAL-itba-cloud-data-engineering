from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.inspection import inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.engine import Engine
from models import Base
import pandas as pd


class Postgres:
    def __init__(self, postgres_conn_id):
        self.postgres_conn_id = postgres_conn_id
        self.pg_hook = PostgresHook(postgres_conn_id="postgres_localhost")

    def _get_inspector(self):
        return inspect(self._get_engine())

    def _get_engine(self):
        return self.pg_hook.get_sqlalchemy_engine()

    def _connect(self):
        return self._get_engine().connect()

    @staticmethod
    def _cursor_columns(cursor):
        if hasattr(cursor, "keys"):
            return cursor.keys()
        else:
            return [c[0] for c in cursor.description]

    def insert_from_frame(self, df, table, if_exists="append", index=False, **kwargs):
        connection = self._connect()
        df.to_sql(
            name=table, con=connection, if_exists=if_exists, index=index, **kwargs
        )

    def execute(self, sql, connection=None):
        if connection is None:
            connection = self._connect()
        return connection.execute(sql)

    def to_frame(self, *args, **kwargs):
        cursor = self.execute(*args, **kwargs)
        if not cursor:
            return
        data = cursor.fetchall()
        if data:
            df = pd.DataFrame(data, columns=self._cursor_columns(cursor))
        else:
            df = pd.DataFrame()
        return df
