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
另外 MySQL 的取值会做类型归一化（见 _norm_row）：DATETIME → 字符串、Decimal → int/float，
让业务代码在两种引擎下拿到的类型一致。
"""
import datetime
import os
import re
import sqlite3
import tempfile
from decimal import Decimal

import pymysql
import pymysql.cursors

from config import (
    DB_ENGINE, DB_PATH, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
    DB_SSL_CA, DB_SSL_REQUIRED,
)

_ssl_ca_path_cache = None


def _ssl_ca_path() -> str:
    """DB_SSL_CA 支持「PEM 文件路径」或「PEM 内容」；内容形式落盘到临时文件。

    Vercel 环境变量里塞多行 PEM 会被转义，直接写文件最稳。
    """
    global _ssl_ca_path_cache
    if _ssl_ca_path_cache:
        return _ssl_ca_path_cache
    raw = (DB_SSL_CA or "").strip()
    if not raw:
        return ""
    if "BEGIN CERTIFICATE" in raw or "\\n" in raw:
        pem = raw.replace("\\n", "\n")
        fd, path = tempfile.mkstemp(prefix="db_ca_", suffix=".pem")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(pem if pem.endswith("\n") else pem + "\n")
        _ssl_ca_path_cache = path
    else:
        _ssl_ca_path_cache = raw
    return _ssl_ca_path_cache


def _ssl_kwargs() -> dict:
    """pymysql 的 ssl 参数：给了 CA 就严格校验，否则按需只加密不校验。"""
    ca = _ssl_ca_path()
    if ca:
        return {"ssl": {"ca": ca}}          # 严格校验（推荐：TiDB 下载的 CA）
    if DB_SSL_REQUIRED:
        # 不给 CA 时 pymysql 的行为：verify_mode=CERT_NONE + 不校验主机名 = 只加密
        return {"ssl": {"check_hostname": False}}
    return {}


# ---------- 取值归一化：让 MySQL 的结果类型与 SQLite 一致 ----------
#
# 为什么需要：SQLite 是动态类型，`created_at` 这类列（DDL 里 TEXT，MySQL 侧被翻成
# DATETIME）读出来是字符串；而 MySQL 驱动会把 DATETIME 转成 datetime 对象、
# 把 SUM()/DECIMAL 转成 Decimal。业务代码与 Pydantic 模型都按字符串处理，
# 不归一化就会出现「SQLite 正常、MySQL 报 ValidationError」这种只有上线才暴露的 bug。

def _norm_value(v):
    if isinstance(v, datetime.datetime):          # 必须先于 date 判断（datetime 是 date 子类）
        return v.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(v, datetime.date):
        return v.strftime('%Y-%m-%d')
    if isinstance(v, datetime.timedelta):         # MySQL TIME
        total = int(v.total_seconds())
        return '%02d:%02d:%02d' % (total // 3600, (total % 3600) // 60, total % 60)
    if isinstance(v, Decimal):                    # SUM()/DECIMAL → int 或 float
        return int(v) if v == v.to_integral_value() else float(v)
    return v


def _norm_row(row):
    if row is None:
        return None
    if isinstance(row, dict):
        return {k: _norm_value(v) for k, v in row.items()}
    if isinstance(row, (tuple, list)):
        return tuple(_norm_value(v) for v in row)
    return row


# ---------- 方言翻译（纯函数，可单测） ----------

_DATETIME_DEFAULT_RE = re.compile(r"TEXT NOT NULL DEFAULT \(datetime\('now'\)\)")
# MySQL 不允许 TEXT/BLOB 直接做键（报 1170 used in key specification without a key length），
# 把 `TEXT PRIMARY KEY` / `TEXT NOT NULL UNIQUE` 自动降级成 VARCHAR(255) 保底。
_TEXT_IN_KEY_RE = re.compile(r"\bTEXT(\s+NOT\s+NULL)?(\s+)(PRIMARY\s+KEY|UNIQUE)\b", re.I)
# TEXT/BLOB 族的默认值：MySQL 8 要求写成表达式 `DEFAULT ('')`，但 **TiDB 解析不了表达式默认值**
# （实测 `(1064) ... near ''\')'`），而 MySQL 5.7/TiDB 又不接受 TEXT 上的普通字面默认值（1101）。
# 两边都兼容的唯一写法是「TEXT 列不带默认值」：改为 NOT NULL 无默认，由写入方显式给值。
# 见 https://github.com/pingcap/tidb/issues/45506 与 #59878。
# 匹配：列名 + TEXT/BLOB 族类型 + 类型后约束（不含逗号/括号）+ DEFAULT '字面量'
_COL_TEXT_DEFAULT_RE = re.compile(
    r"(\w+)(\s+(?:TINY|MEDIUM|LONG)?(?:TEXT|BLOB)\b[^,()]*?)\s+DEFAULT\s+'(?:[^']|'')*'", re.I)
# `TEXT ... DEFAULT '<短标量>'` 改成 VARCHAR(1000) 并**保留默认值**：
# 这类列实际都是短字符串（''、'CNY'、'admin'、'中级' …，实测最长 484 字节），
# VARCHAR 在 MySQL 与 TiDB 上都支持普通字面默认值，于是 app 里「插入时省略该列」
# 的写法（create_user 不传 grade、upsert_deposit 不传 currency）两个引擎都不会报 1364。
# 例外是 JSON 容器默认值 '[]' / '{}'：它们底下的列可能存很大的 JSON（章节 JSON 实测 23KB），
# 必须保持 TEXT —— 这类列由写入方显式给值，默认值在 _strip_text_defaults 里去掉。
_TEXT_SCALAR_DEFAULT_RE = re.compile(
    r"\b(?:TINY|MEDIUM|LONG)?TEXT(\s+NOT\s+NULL)?(\s+)(DEFAULT\s+'(?!\[\]|\{\})[^']*')", re.I)
_CONFLICT_RE = re.compile(r"ON\s+CONFLICT\s*\([^)]*\)\s*DO\s+UPDATE\s+SET\s*", re.I)
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


def _strip_text_defaults(sql: str) -> str:
    """去掉 TEXT/BLOB 族列上的 DEFAULT 子句（MySQL 8 与 TiDB 唯一都接受的写法）。

    不用「一行一列」的假设：正则锚定在列定义内部，用 `[^,()]*` 保证不会跨过列分隔符
    或括号，所以多行建表与单行建表都适用。
    """
    return _COL_TEXT_DEFAULT_RE.sub(r"\1\2", sql)


def to_mysql_ddl(sql: str) -> str:
    """把 SQLite 建表语句翻译成 MySQL/TiDB 都能执行的版本。"""
    s = sql
    s = s.replace("AUTOINCREMENT", "AUTO_INCREMENT")
    s = _DATETIME_DEFAULT_RE.sub("DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP", s)
    s = _TEXT_IN_KEY_RE.sub(r"VARCHAR(255)\1\2\3", s)       # TEXT 做键 → VARCHAR(255)
    # 短标量默认值的文本列 → VARCHAR(1000)（保留默认值，两个引擎都支持字面默认值）
    s = _TEXT_SCALAR_DEFAULT_RE.sub(r"VARCHAR(1000)\1\2\3", s)
    s = _strip_text_defaults(s)                            # 其余 TEXT 列的 DEFAULT 去掉
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
        # 返回 self（而不是裸 pymysql cursor），保证 `conn.execute(sql).fetchone()`
        # 这种链式写法也会走类型归一化。
        return self

    def executemany(self, sql: str, seq_of_params):
        self._raw.executemany(to_mysql(sql), seq_of_params)

    def fetchone(self):
        return _norm_row(self._raw.fetchone())

    def fetchall(self):
        rows = self._raw.fetchall()
        return [_norm_row(r) for r in rows] if rows is not None else rows

    def fetchmany(self, size=None):
        rows = self._raw.fetchmany(size) if size else self._raw.fetchmany()
        return [_norm_row(r) for r in rows] if rows is not None else rows

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
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30,
            **(_ssl_kwargs()),
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
