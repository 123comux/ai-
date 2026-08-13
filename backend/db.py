"""数据库方言层：SQLite（默认，本地/测试）与 MySQL（生产）双引擎。

设计目标：业务代码（database.py / routers/*）零改动，只换 get_connection()。
- DB_ENGINE 未设或为 sqlite → 返回 sqlite3 连接（保持原有行为）；
- DB_ENGINE=mysql → 返回 _MySQLConn 包装器，SQL 在 execute 时做方言翻译：
    · 占位符    ? → %s
    · 时间函数  datetime('now') → NOW()，date('now') → CURDATE()
    · upsert    INSERT OR REPLACE → REPLACE INTO；ON CONFLICT(..) DO UPDATE SET x=excluded.x → ON DUPLICATE KEY UPDATE x=VALUES(x)
    · PRAGMA    直接跳过（MySQL 无此概念）
    · DDL       AUTOINCREMENT → AUTO_INCREMENT；TEXT NOT NULL DEFAULT (datetime('now')) → DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
翻译函数为纯函数（见 test），可在无 MySQL 环境下单测。
"""
import re
import sqlite3

import pymysql
import pymysql.cursors

from config import (
    DB_ENGINE, DB_PATH, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
)


# ---------- 方言翻译（纯函数，可单测） ----------

_DATETIME_DEFAULT_RE = re.compile(r"TEXT NOT NULL DEFAULT \(datetime\('now'\)\)")
# MySQL 8 的 TEXT/BLOB 列默认值必须是表达式形式：DEFAULT '' → DEFAULT ('')
_TEXT_STRING_DEFAULT_RE = re.compile(r"DEFAULT '([^']*)'")
_CONFLICT_RE = re.compile(r"ON CONFLICT\([^)]*\) DO UPDATE SET ")
_EXCLUDED_RE = re.compile(r"(\w+)=excluded\.(\w+)")


def _replace_placeholders(sql: str) -> str:
    """把 `?` 占位符替换成 `%s`，但跳过单引号字符串内的字面 `?`（如 URL 'index?id='）。

    SQLite 字符串内转义用 `''`，本库 SQL 无此类字面，简单开关即可正确。
    """
    out = []
    in_str = False
    for ch in sql:
        if ch == "'":
            in_str = not in_str
            out.append(ch)
        elif ch == "?" and not in_str:
            out.append("%s")
        else:
            out.append(ch)
    return "".join(out)


def to_mysql(sql: str) -> str:
    """把 SQLite 写法的 DML/SELECT/ALTER 翻译成 MySQL 语法。"""
    s = sql
    s = s.replace("datetime('now')", "NOW()")
    s = s.replace("date('now')", "CURDATE()")
    s = s.replace("INSERT OR REPLACE INTO", "REPLACE INTO")
    s = s.replace("INSERT OR IGNORE INTO", "INSERT IGNORE INTO")
    s = _CONFLICT_RE.sub("ON DUPLICATE KEY UPDATE ", s)
    s = _EXCLUDED_RE.sub(r"\1=VALUES(\2)", s)
    s = _replace_placeholders(s)
    return s


def to_mysql_ddl(sql: str) -> str:
    """把 SQLite 建表语句翻译成 MySQL 可执行版本。"""
    s = sql
    s = s.replace("AUTOINCREMENT", "AUTO_INCREMENT")
    s = _DATETIME_DEFAULT_RE.sub("DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP", s)
    s = _TEXT_STRING_DEFAULT_RE.sub(r"DEFAULT ('\1')", s)  # DEFAULT '' → DEFAULT ('')
    return s


def _is_ddl(sql: str) -> bool:
    up = sql.lstrip().upper()
    return up.startswith(("CREATE TABLE", "ALTER TABLE"))


# ---------- MySQL 连接包装（对外暴露 sqlite3 类似的 execute/commit/close） ----------

class _MySQLCursor:
    """薄包装：execute 时做方言翻译，其余委托给 pymysql 的 DictCursor（行=dict）。"""

    def __init__(self, raw):
        self._raw = raw

    def execute(self, sql: str, params=None):
        up = sql.lstrip().upper()
        if up.startswith("PRAGMA"):
            return None
        target = to_mysql_ddl(sql) if _is_ddl(sql) else to_mysql(sql)
        self._raw.execute(target, params or ())
        return self._raw

    def executemany(self, sql: str, seq_of_params):
        self._raw.executemany(to_mysql(sql), seq_of_params)

    def fetchone(self):
        return self._raw.fetchone()

    def fetchall(self):
        return self._raw.fetchall()

    def fetchmany(self, size=None):
        return self._raw.fetchmany(size)

    @property
    def lastrowid(self):
        return self._raw.lastrowid

    @property
    def rowcount(self):
        return self._raw.rowcount

    def close(self):
        return self._raw.close()


class _MySQLConn:
    """MySQL 连接包装：与 sqlite3.Connection 的常用子集对齐。"""

    def __init__(self):
        self._conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def execute(self, sql: str, params=None) -> _MySQLCursor:
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def cursor(self) -> _MySQLCursor:
        return _MySQLCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_connection():
    """返回一个连接：sqlite3（默认）或 MySQL 包装（DB_ENGINE=mysql）。"""
    if DB_ENGINE == "mysql":
        return _MySQLConn()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
