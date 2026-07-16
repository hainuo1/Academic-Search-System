# ============================================================
# db.py —— 数据库连接文件（请求级连接管理）
# ============================================================

import pymysql
from flask import g

from config import Config


class Row(dict):
    """结果行对象：继承 dict，Jinja2 原生支持 doc.FieldName 访问。

    同时支持：
        row['FieldName']   → dict 键访问（Jinja2 会自动转为 row.FieldName）
        row[0]             → 整数下标访问（兼容现有 Python 路由代码）
        row.FieldName      → 属性访问（Python 代码中直接 .FieldName）
        iter(row)          → 可迭代（兼容元组解包 a, b, c = row）
    """

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
    """游标包装器：将 PyMySQL DictCursor 的行转为 Row 对象。"""

    def __init__(self, raw_cursor):
        self._cursor = raw_cursor

    def _wrap(self, row):
        if row is None:
            return None
        return Row(row)

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
        raw_conn = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            port=Config.DB_CONFIG['port'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database=Config.DB_CONFIG['database'],
            charset=Config.DB_CONFIG['charset'],
            autocommit=Config.DB_CONFIG['autocommit'],
        )
        g.db_conn = _ConnectionWrapper(raw_conn)
    return g.db_conn


def close_connection(exception=None):
    conn = g.pop('db_conn', None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
