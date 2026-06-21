# ============================================================
# db.py —— 数据库连接文件（请求级连接管理）
#
# 作用：利用 Flask 的 g 对象，在请求生命周期内复用同一个连接，
#       请求结束后自动关闭，杜绝连接泄漏。
# ============================================================

import pyodbc
from flask import g
from config import Config


def get_connection():
    """获取当前请求的数据库连接（复用同一个连接）"""
    if 'db_conn' not in g:
        g.db_conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
    return g.db_conn


def close_connection(exception=None):
    """请求结束时自动关闭连接（由 app.teardown_appcontext 调用）"""
    conn = g.pop('db_conn', None)
    if conn is not None:
        try:
            conn.close()
        except pyodbc.ProgrammingError:
            # 如果连接已经关闭，忽略此错误
            pass
        except Exception:
            # 忽略其他关闭异常
            pass