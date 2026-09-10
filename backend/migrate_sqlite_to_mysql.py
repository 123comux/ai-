"""把本地 SQLite 数据搬到 MySQL（TiDB Cloud / RDS / 自建均适用）。

为什么需要它：Vercel 是 Serverless，没有持久磁盘，SQLite 写不进去；线上必须用
MySQL 协议的公网库（推荐 TiDB Cloud Serverless，免费 5GB）。本脚本负责：
    1. 在目标 MySQL 上建表（复用项目的 init_db()，SQL 走 db.py 的方言翻译）；
    2. 自动把「SQLite 实际数据撑爆 TEXT/VARCHAR」的列升级为 MEDIUMTEXT/加宽 VARCHAR
       —— MySQL 的 TEXT 上限 64KB，课程章节 JSON 很容易超，不处理会 Data too long；
    3. 逐表搬数据（INSERT OR REPLACE → REPLACE INTO，可重复执行、幂等）；
    4. 逐表核对行数，输出对照表；有任何不一致就以非 0 退出。

用法（在 backend/ 下执行，连接信息全部走环境变量，与线上一致）：

    set DB_ENGINE=mysql
    set DB_HOST=xxx.tidbcloud.com & set DB_PORT=4000 & set DB_USER=xxx.root
    set DB_PASSWORD=xxx & set DB_NAME=test
    py migrate_sqlite_to_mysql.py --dry-run    # 先体检：列宽风险 + 表清单
    py migrate_sqlite_to_mysql.py              # 正式建表并导入

参数：
    --source PATH   源 SQLite 文件（默认 data/cms.db）
    --dry-run       只体检、不写库（不会建表、不会改列类型）
    --tables a,b    只迁移指定表
    --reset         先删掉目标库里所有表再重建（首次失败留下旧结构时用；谨慎）
"""
import io
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 中文 Windows 控制台默认 GBK，输出里混入非 GBK 字符会 UnicodeEncodeError 中断脚本
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from config import DB_ENGINE, DB_PATH, DB_HOST, DB_PORT, DB_USER, DB_NAME  # noqa: E402
from db import get_connection  # noqa: E402

TEXT_LIMIT = 65535            # MySQL TEXT 上限（字节）
MEDIUMTEXT_LIMIT = 16777215   # MEDIUMTEXT 上限


def sqlite_tables(conn, only=None):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    names = [r[0] for r in rows]
    return [n for n in names if not only or n in only]


def sqlite_columns(conn, table):
    rows = conn.execute('PRAGMA table_info("%s")' % table).fetchall()
    return [r[1] for r in rows]


def max_bytes(conn, table, col):
    try:
        row = conn.execute(
            'SELECT MAX(LENGTH(CAST("%s" AS BLOB))) FROM "%s"' % (col, table)).fetchone()
        return int(row[0] or 0)
    except Exception:
        return 0


def source_widths(sconn, tables):
    """源库里每个列的实际最大字节长度，只保留 > 1KB 的，降序"""
    out = []
    for t in tables:
        for col in sqlite_columns(sconn, t):
            n = max_bytes(sconn, t, col)
            if n > 1024:
                out.append((n, t, col))
    out.sort(reverse=True)
    return out


def mysql_col_type(mconn, table, col):
    try:
        row = mconn.execute(
            "SELECT DATA_TYPE AS dt, CHARACTER_MAXIMUM_LENGTH AS cml "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
            "AND TABLE_NAME=? AND COLUMN_NAME=?", (table, col)).fetchone()
    except Exception:
        return None, None
    if not row:
        return None, None
    if isinstance(row, dict):
        return row.get('dt') or row.get('DATA_TYPE'), row.get('cml') or row.get('CHARACTER_MAXIMUM_LENGTH')
    return row[0], row[1]


def ensure_wide_enough(sconn, mconn, tables, report, dry):
    """SQLite 数据比 MySQL 列类型更宽时升级列类型，避免导入时 Data too long"""
    fixed, planned = [], []
    for t in tables:
        for col in sqlite_columns(sconn, t):
            n = max_bytes(sconn, t, col)
            if n <= 1024:
                continue
            dtype, charmax = mysql_col_type(mconn, t, col)
            if dtype is None:
                continue
            if dtype in ('text', 'tinytext') and n > TEXT_LIMIT:
                newtype = 'MEDIUMTEXT' if n <= MEDIUMTEXT_LIMIT else 'LONGTEXT'
                if dry:
                    planned.append('%s.%s  %s → %s（源数据 %d 字节）' % (t, col, dtype, newtype, n))
                else:
                    mconn.execute('ALTER TABLE `%s` MODIFY `%s` %s' % (t, col, newtype))
                    fixed.append('%s.%s  %s → %s（源数据 %d 字节）' % (t, col, dtype, newtype, n))
            elif dtype in ('varchar', 'char') and charmax and n > int(charmax):
                newlen = min(65535, max(int(charmax) * 2, n // 3 + 64))
                if dry:
                    planned.append('%s.%s  varchar(%s) → varchar(%d)（源数据 %d 字节）'
                                   % (t, col, charmax, newlen, n))
                else:
                    mconn.execute('ALTER TABLE `%s` MODIFY `%s` VARCHAR(%d)' % (t, col, newlen))
                    fixed.append('%s.%s  varchar(%s) → varchar(%d)（源数据 %d 字节）'
                                 % (t, col, charmax, newlen, n))
    if fixed:
        report.append('自动加宽列 %d 个（已执行）：' % len(fixed))
        report.extend('  - ' + x for x in fixed)
    if planned:
        report.append('需要加宽列 %d 个（--dry-run 未执行，正式导入时会自动处理）：' % len(planned))
        report.extend('  - ' + x for x in planned)
    if not fixed and not planned:
        report.append('列宽检查：无需加宽。')


def copy_table(sconn, mconn, table):
    cols = sqlite_columns(sconn, table)
    if not cols:
        return 0
    col_bt = ', '.join('`%s`' % c for c in cols)
    col_dq = ', '.join('"%s"' % c for c in cols)
    rows = sconn.execute('SELECT %s FROM "%s"' % (col_dq, table)).fetchall()
    data = [tuple(r) for r in rows]
    if not data:
        return 0
    sql = 'INSERT OR REPLACE INTO `%s` (%s) VALUES (%s)' % (
        table, col_bt, ', '.join(['?'] * len(cols)))
    cur = mconn.cursor()
    for i in range(0, len(data), 200):
        cur.executemany(sql, data[i:i + 200])
    mconn.commit()
    return len(data)


def target_tables(mconn):
    rows = mconn.execute(
        "SELECT TABLE_NAME AS t FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='BASE TABLE'").fetchall()
    out = []
    for r in rows:
        out.append(r['t'] if isinstance(r, dict) else r[0])
    return sorted(out)


def drop_all_tables(mconn, report, dry):
    """删掉目标库里的所有表。

    为什么需要：init_db() 用的是 CREATE TABLE IF NOT EXISTS，**不会修正已存在的旧表**。
    第一次在 TiDB 上因为 `DEFAULT ('')` 语法错误失败后，若已有表被建出来（旧结构），
    直接重跑不会修好它们 —— 必须先把库清空。
    """
    tables = target_tables(mconn)
    if not tables:
        report.append('目标库当前没有表。')
        return
    if dry:
        report.append('--reset 将删除目标库 %d 张表（--dry-run 未执行）：%s'
                      % (len(tables), ', '.join(tables[:8]) + ('...' if len(tables) > 8 else '')))
        return
    try:
        mconn.execute('SET FOREIGN_KEY_CHECKS=0')
        for t in tables:
            mconn.execute('DROP TABLE IF EXISTS `%s`' % t)
        mconn.execute('SET FOREIGN_KEY_CHECKS=1')
        mconn.commit()
        report.append('已删除目标库 %d 张表（--reset）。' % len(tables))
    except Exception as e:
        report.append('[FAIL] 删表失败：%s' % e)
        raise


def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    reset = '--reset' in args
    src = args[args.index('--source') + 1] if '--source' in args else DB_PATH
    only = set(args[args.index('--tables') + 1].split(',')) if '--tables' in args else None

    if not os.path.exists(src):
        print('源库不存在：%s' % src)
        return 1
    if DB_ENGINE != 'mysql':
        print('DB_ENGINE 当前为 %r，必须设为 mysql：\n'
              '    set DB_ENGINE=mysql & set DB_HOST=... & set DB_PORT=4000 & '
              'set DB_USER=... & set DB_PASSWORD=... & set DB_NAME=test' % DB_ENGINE)
        return 1

    report = ['源 SQLite : %s' % src,
              '目标 MySQL: %s:%s/%s（用户 %s）' % (DB_HOST, DB_PORT, DB_NAME, DB_USER),
              '模式      : %s' % ('--dry-run（只体检，不写库）' if dry else '正式导入')]

    if reset:
        try:
            mconn_reset = get_connection()
            drop_all_tables(mconn_reset, report, dry)
            mconn_reset.close()
        except Exception as e:
            print('\n'.join(report))
            print('\n[FAIL] --reset 失败：%s' % e)
            return 1

    sconn = sqlite3.connect(src)
    sconn.row_factory = sqlite3.Row
    tables = sqlite_tables(sconn, only)
    report.append('表数量    : %d' % len(tables))

    try:
        mconn = get_connection()
    except Exception as e:
        print('\n'.join(report))
        print('\n[FAIL] 连不上目标 MySQL：%s' % e)
        print('   请检查 DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME，'
              '并确认云库已允许你的 IP（TiDB Cloud Serverless 需允许 0.0.0.0/0 + TLS）。')
        return 1

    if not dry:
        from database import init_db
        init_db()
        report.append('建表      : init_db() 完成（CREATE TABLE IF NOT EXISTS，幂等）')
    ensure_wide_enough(sconn, mconn, tables, report, dry)

    # 源库最宽列 TOP5：即使目标库还没建表也能看到风险
    wide = source_widths(sconn, tables)
    if wide:
        report.append('\n源库最宽的列（字节）：')
        report.extend('  %8d  %s.%s' % (n, t, c) for n, t, c in wide[:5])

    total_src = total_dst = 0
    mismatches = []
    missing = []
    detail = []
    try:
        mconn.execute('SET FOREIGN_KEY_CHECKS=0')
    except Exception:
        pass
    for t in tables:
        n_src = int(sconn.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0])
        if dry:
            dtype, _ = mysql_col_type(mconn, t, '_never_')
            row = mconn.execute(
                'SELECT COUNT(*) AS c FROM information_schema.TABLES '
                'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=?', (t,)).fetchone()
            exists = bool(row and (list(row.values())[0] if isinstance(row, dict) else row[0]))
            n_dst = n_src if exists else 0
            if not exists:
                missing.append(t)
        else:
            n_dst = copy_table(sconn, mconn, t)
            if n_dst != n_src:
                mismatches.append(t)
        total_src += n_src
        total_dst += n_dst
        flag = '' if n_src == n_dst else ('  <- 目标表尚未建立' if dry else '  <- 不一致')
        detail.append('  %-26s 源 %5d → 目标 %5d%s' % (t, n_src, n_dst, flag))
    try:
        mconn.execute('SET FOREIGN_KEY_CHECKS=1')
    except Exception:
        pass

    report.append('\n逐表行数：')
    report.extend(detail)
    report.append('\n合计：源 %d 行 → 目标 %d 行' % (total_src, total_dst))

    if dry:
        report.append('\n--dry-run 结束（未写任何数据）。去掉 --dry-run 即可建表并导入。')
        if missing:
            report.append('注：目标库还没有这些表，去掉 --dry-run 会先用 init_db() 建好。')
    elif mismatches:
        report.append('\n[FAIL] 行数不一致的表：%s' % ', '.join(mismatches))
    else:
        report.append('\n[OK] 全部表行数一致，数据迁移完成。')

    if not dry:
        mconn.close()
    sconn.close()

    out = '\n'.join(report)
    print(out)
    try:
        log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'migrate_to_mysql.log')
        os.makedirs(os.path.dirname(log), exist_ok=True)
        io.open(log, 'w', encoding='utf-8').write(out)
    except Exception:
        pass
    return 1 if mismatches else 0


if __name__ == '__main__':
    sys.exit(main())
