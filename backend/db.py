import pymysql
from flask import g

from config import Config


class Row(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"Row 中没有此列: {name}")

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)

    def __iter__(self):
        return iter(self.values())


class RowCursor:
    def __init__(self, raw_cursor):
        self._cursor = raw_cursor

    def _wrap(self, row):
        return Row(row) if row is not None else None

    def _wrap_multi(self, rows):
        return [Row(r) for r in rows] if rows else []

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def execute(self, query, args=None):
        return self._cursor.execute(query, args)

    def executemany(self, query, args):
        return self._cursor.executemany(query, args)

    def fetchone(self):
        return self._wrap(self._cursor.fetchone())

    def fetchmany(self, size=None):
        rows = self._cursor.fetchmany(size) if size else self._cursor.fetchmany()
        return self._wrap_multi(rows)

    def fetchall(self):
        return self._wrap_multi(self._cursor.fetchall())

    def __iter__(self):
        return self

    def __next__(self):
        return self._wrap(next(self._cursor))

    def close(self):
        self._cursor.close()


class _ConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return RowCursor(self._conn.cursor(pymysql.cursors.DictCursor))

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def get_connection():
    if 'db_conn' not in g:
        raw_conn = pymysql.connect(**Config.DB_CONFIG)
        g.db_conn = _ConnectionWrapper(raw_conn)
    return g.db_conn


def close_connection(exception=None):
    conn = g.pop('db_conn', None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
