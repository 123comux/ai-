"""
数据库访问模块：所有内容类型的 CRUD。

连接层见 db.py（SQLite 默认 / MySQL 生产双引擎），此处保持对外 API 不变：
业务代码 `from database import get_connection` 即可，无需感知底层引擎。
"""
import json
import os
from datetime import datetime
from typing import Any, Optional

from db import get_connection
from config import DB_PATH, DB_ENGINE


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cur = conn.cursor()

    # ============ Content Tables ============

    # Banners - home page carousel
    cur.execute("""
        CREATE TABLE IF NOT EXISTS banners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            image_url TEXT NOT NULL,
            link_url TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Learning directions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS directions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            color TEXT NOT NULL DEFAULT '#165dff',
            topic_key TEXT NOT NULL DEFAULT '',
            icon TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Courses
    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id VARCHAR(100) PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            cover_img TEXT NOT NULL DEFAULT '',
            topic TEXT NOT NULL DEFAULT '',
            difficulty TEXT NOT NULL DEFAULT 'beginner',
            estimated_hours REAL NOT NULL DEFAULT 0,
            lessons INTEGER NOT NULL DEFAULT 0,
            progress REAL NOT NULL DEFAULT 0,
            is_free INTEGER NOT NULL DEFAULT 1,
            price REAL NOT NULL DEFAULT 0,
            source TEXT NOT NULL DEFAULT '',
            chapters TEXT NOT NULL DEFAULT '[]',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Projects
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id VARCHAR(100) PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            cover_img TEXT NOT NULL DEFAULT '',
            tech_stack TEXT NOT NULL DEFAULT '[]',
            difficulty TEXT NOT NULL DEFAULT 'beginner',
            estimated_hours REAL NOT NULL DEFAULT 0,
            step_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'available',
            progress REAL NOT NULL DEFAULT 0,
            is_free INTEGER NOT NULL DEFAULT 1,
            price REAL NOT NULL DEFAULT 0,
            topics_covered TEXT NOT NULL DEFAULT '[]',
            steps TEXT NOT NULL DEFAULT '[]',
            source TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    # 兼容旧库：为缺少 steps 列的 projects 表补列（保存分步实践指南，数据源统一后用）
    try:
        cur.execute("ALTER TABLE projects ADD COLUMN steps TEXT NOT NULL DEFAULT '[]'")
    except Exception:
        pass

    # Videos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id VARCHAR(100) PRIMARY KEY,
            title TEXT NOT NULL,
            subtitle TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            core_info TEXT NOT NULL DEFAULT '[]',
            narrative TEXT NOT NULL DEFAULT '',
            visual TEXT NOT NULL DEFAULT '',
            quality TEXT NOT NULL DEFAULT '{}',
            url TEXT NOT NULL,
            cover_url TEXT NOT NULL DEFAULT '',
            duration INTEGER NOT NULL DEFAULT 0,
            chapter TEXT NOT NULL DEFAULT '',
            course_id TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Learning paths
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_paths (
            id VARCHAR(100) PRIMARY KEY,
            direction TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            total_weeks INTEGER NOT NULL DEFAULT 0,
            current_week INTEGER NOT NULL DEFAULT 0,
            nodes TEXT NOT NULL DEFAULT '[]',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Learning stats
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learning_days INTEGER NOT NULL DEFAULT 0,
            total_hours REAL NOT NULL DEFAULT 0,
            completed_projects INTEGER NOT NULL DEFAULT 0,
            completed_lessons INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Learning records
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            duration INTEGER NOT NULL DEFAULT 0,
            lessons_completed INTEGER NOT NULL DEFAULT 0,
            exercises_done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Job matching
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_matching (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL DEFAULT '',
            match_score REAL NOT NULL DEFAULT 0,
            required_skills TEXT NOT NULL DEFAULT '[]',
            gap_skills TEXT NOT NULL DEFAULT '[]',
            recommended_courses TEXT NOT NULL DEFAULT '[]',
            recommended_projects TEXT NOT NULL DEFAULT '[]',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Assessment results
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            overall_score REAL NOT NULL DEFAULT 0,
            level TEXT NOT NULL DEFAULT '初级',
            dimensions TEXT NOT NULL DEFAULT '[]',
            strengths TEXT NOT NULL DEFAULT '[]',
            weaknesses TEXT NOT NULL DEFAULT '[]',
            recommended_direction TEXT NOT NULL DEFAULT '',
            estimated_hours INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Menu items (for mine page, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icon TEXT NOT NULL DEFAULT '',
            label TEXT NOT NULL,
            path TEXT NOT NULL DEFAULT '',
            section TEXT NOT NULL DEFAULT 'mine',
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Learning goals (mine page)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            target_date TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Favorites (mine page: favorited courses/projects)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type VARCHAR(50) NOT NULL,
            item_id VARCHAR(100) NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            cover_img TEXT NOT NULL DEFAULT '',
            detail_path TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(item_type, item_id)
        )
    """)

    # Admin users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 每日 AI 打卡（学习激励）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            checkin_date VARCHAR(20) NOT NULL,  -- YYYY-MM-DD
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, checkin_date)
        )
    """)

    # 学习社区帖子
    cur.execute("""
        CREATE TABLE IF NOT EXISTS community_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'general',
            likes INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 学习社区回复
    cur.execute("""
        CREATE TABLE IF NOT EXISTS community_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 分享解锁记录（社交裂变：分享课程解锁进阶内容）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS share_unlocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            share_type VARCHAR(50) NOT NULL DEFAULT 'course',
            share_target VARCHAR(200) NOT NULL,
            unlocked_content TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, share_type, share_target)
        )
    """)

    # 好友组队学习
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code VARCHAR(100) NOT NULL UNIQUE,
            owner_id INTEGER NOT NULL,
            member_count INTEGER NOT NULL DEFAULT 1,
            max_members INTEGER NOT NULL DEFAULT 5,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(team_id, user_id)
        )
    """)

    # FAQ 知识库（答疑管理：常见问题沉淀）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faq_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            sort_order INTEGER NOT NULL DEFAULT 0,
            view_count INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ============ 用户体系（多用户隔离） ============

    # Users - 微信授权登录后的真实用户
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            openid VARCHAR(200) NOT NULL UNIQUE,
            unionid TEXT NOT NULL DEFAULT '',
            nickname TEXT NOT NULL DEFAULT '',
            avatar TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 按用户隔离的学习进度（替代全局 JSON 单例）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_video_progress (
            user_id INTEGER NOT NULL,
            video_id VARCHAR(100) NOT NULL,
            watched_at TEXT NOT NULL DEFAULT (datetime('now')),
            minutes INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, video_id)
        )
    """)

    # 按用户隔离的章节完成记录（七阶段课程为文字章节，完课率按章节计，不依赖遗留视频库）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_chapter_progress (
            user_id INTEGER NOT NULL,
            course_id VARCHAR(100) NOT NULL,
            chapter_id VARCHAR(100) NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, course_id, chapter_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_project_progress (
            user_id INTEGER NOT NULL,
            project_id VARCHAR(100) NOT NULL,
            completed_steps INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, project_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_path_progress (
            user_id INTEGER NOT NULL,
            path_id VARCHAR(100) NOT NULL,
            completed_nodes TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, path_id)
        )
    """)

    # 七阶段考核成绩（考核锁用）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_stage_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stage INTEGER NOT NULL,
            score REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 用户能力报告存档（按用户隔离）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_ability_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            overall_score REAL NOT NULL DEFAULT 0,
            level TEXT NOT NULL DEFAULT '',
            dimensions TEXT NOT NULL DEFAULT '[]',
            strengths TEXT NOT NULL DEFAULT '[]',
            weaknesses TEXT NOT NULL DEFAULT '[]',
            recommended_direction TEXT NOT NULL DEFAULT '',
            estimated_hours INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 押金 / 报名（押金式培训核心）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            amount REAL NOT NULL DEFAULT 0,
            currency TEXT NOT NULL DEFAULT 'CNY',
            status TEXT NOT NULL DEFAULT 'active',
            enrolled_at TEXT NOT NULL DEFAULT (datetime('now')),
            deadline_at TEXT NOT NULL DEFAULT '',
            time_lock_passed INTEGER NOT NULL DEFAULT 0,
            course_completion_rate REAL NOT NULL DEFAULT 0,
            homework_passed INTEGER NOT NULL DEFAULT 0,
            assessment_avg_score REAL NOT NULL DEFAULT 0,
            project_submitted INTEGER NOT NULL DEFAULT 0,
            project_passed INTEGER NOT NULL DEFAULT 0,
            refund_eligible INTEGER NOT NULL DEFAULT 0,
            refund_amount REAL NOT NULL DEFAULT 0,
            refund_at TEXT NOT NULL DEFAULT '',
            refund_txn TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 作业题库（七阶段各一题，支撑过程锁「每阶段作业提交并通过」）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS homework_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage INTEGER NOT NULL UNIQUE,
            course_id TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL,
            requirement TEXT NOT NULL,
            rubric TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 用户作业提交与 AI 评审记录（每阶段一次，可重交覆盖；status: pending/passed/rejected）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS homework_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stage INTEGER NOT NULL,
            course_id TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL,
            ai_score REAL NOT NULL DEFAULT 0,
            ai_feedback TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, stage)
        )
    """)

    # goals / favorites 增加 user_id，实现多用户隔离（默认 0 = 历史全局数据）
    try:
        cur.execute("ALTER TABLE goals ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE favorites ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
    except Exception:
        pass

    # 学员自填资料（年级/专业/目标方向）同步到后端，避免只存本地丢失
    for _col in ("grade", "major", "target_direction"):
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {_col} TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass

    # 退费申请时间（防刷：人工复核队列）
    try:
        cur.execute("ALTER TABLE user_deposits ADD COLUMN refund_requested_at TEXT NOT NULL DEFAULT ''")
    except Exception:
        pass
    # 真实微信支付：支付单号 / 微信交易号 / 支付完成时间
    for _col in ("out_trade_no", "transaction_id", "paid_at"):
        try:
            cur.execute(f"ALTER TABLE user_deposits ADD COLUMN {_col} TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass

    # 功能使用权限：5 天免费试用期起点（服务端首次确认时间，用户不可篡改）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            trial_started_at TEXT NOT NULL DEFAULT '',
            admin_override TEXT NOT NULL DEFAULT '',  -- ''=按规则, 'lock'=强制锁定, 'unlock'=强制解锁
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    # 兼容旧库：为缺少 admin_override 列的 user_access 表补列（后台用户权限/试用管理用）
    try:
        cur.execute("ALTER TABLE user_access ADD COLUMN admin_override TEXT NOT NULL DEFAULT ''")
    except Exception:
        pass

    # AI 每日调用计数（未缴押金/试用期用户限流用）。每用户每天每个功能一行。
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_usage_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            usage_date VARCHAR(20) NOT NULL,  -- YYYY-MM-DD
            feature VARCHAR(50) NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, usage_date, feature)
        )
    """)

    seed_homework_questions(cur)
    backfill_project_steps_from_json(cur)
    seed_learning_paths_from_direction_plan(cur)

    conn.commit()
    conn.close()
    # 注意：Windows 默认 GBK 控制台无法输出 emoji，用 ASCII 避免 UnicodeEncodeError
    print(f"[DB] initialized at {DB_PATH}")


# ============ CRUD Helpers ============

def row_to_dict(row) -> dict:
    """把查询行转 dict：sqlite3.Row 或 MySQL DictCursor 的 dict 均可。"""
    return dict(row)


def query_all(table: str, where: Optional[dict] = None, order_by: str = "id") -> list[dict]:
    """Query all rows from a table."""
    conn = get_connection()
    if where:
        conditions = " AND ".join(f"{k}=?" for k in where)
        rows = conn.execute(f"SELECT * FROM {table} WHERE {conditions} ORDER BY {order_by}",
                            list(where.values())).fetchall()
    else:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def query_one(table: str, id_value: Any) -> Optional[dict]:
    """Query a single row by id."""
    conn = get_connection()
    row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (id_value,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def insert_row(table: str, data: dict) -> int:
    """Insert a row and return the id."""
    conn = get_connection()
    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    cur = conn.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
        list(data.values())
    )
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def update_row(table: str, id_value: Any, data: dict) -> bool:
    """Update a row by id."""
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k}=?" for k in data)
    conn = get_connection()
    cur = conn.execute(
        f"UPDATE {table} SET {sets} WHERE id=?",
        list(data.values()) + [id_value]
    )
    conn.commit()
    affected = cur.rowcount > 0
    conn.close()
    return affected


def delete_row(table: str, id_value: Any) -> bool:
    """Delete a row by id."""
    conn = get_connection()
    cur = conn.execute(f"DELETE FROM {table} WHERE id=?", (id_value,))
    conn.commit()
    affected = cur.rowcount > 0
    conn.close()
    return affected


def safe_load_json(path, default=None):
    """Load JSON from a path, returning `default` on missing OR corrupt file.

    Used by content routers so a missing/garbled processed JSON never raises a 500.
    """
    import json as _json
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json.load(f)
    except (FileNotFoundError, OSError, _json.JSONDecodeError, ValueError):
        return default


def parse_json_field(value: str, default=None):
    """Parse a JSON string field."""
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value) if value else (default or [])
    except (json.JSONDecodeError, TypeError):
        return default or []


def backfill_project_steps_from_json(cur=None):
    """把 processed 的 projects JSON 中的分步实践指南（steps）回填进 projects 表。

    数据源统一（videos/projects 改数据库驱动）后，分步实践指南 `steps` 需以数据库为准；
    旧库/新库首次初始化时 projects 表的 steps 列为空，这里从种子 JSON 幂等回填：
    - 仅回填 steps 仍为空的记录，不覆盖后台已编辑的值；
    - 缺失/损坏的 JSON 或已无匹配 id 时静默跳过，不影响启动。
    """
    conn = None
    if cur is None:
        conn = get_connection()
        cur = conn.cursor()
    from pathlib import Path as _P
    data_dir = _P(__file__).resolve().parent / "data" / "processed"
    path = data_dir / "enriched_projects.json"
    if not path.exists():
        path = data_dir / "projects.json"
    if not path.exists():
        if conn is not None:
            conn.close()
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            projects = json.load(f)
    except (OSError, json.JSONDecodeError):
        if conn is not None:
            conn.close()
        return
    for p in projects:
        pid = p.get("id")
        steps = p.get("steps")
        if not pid or not steps:
            continue
        row = cur.execute("SELECT steps FROM projects WHERE id=?", (pid,)).fetchone()
        if row is None or parse_json_field(row["steps"] if row else "[]"):
            continue
        cur.execute(
            "UPDATE projects SET steps=?, updated_at=datetime('now') WHERE id=?",
            (json.dumps(steps, ensure_ascii=False), pid),
        )
    if conn is not None:
        conn.commit()
        conn.close()


# ============ 学习路径（方向路径）种子 ============

# 方向 → (按序课程 id, 按序项目 id)。这是学习路径列表的"内容蓝图"：
# 后台管理可直接编辑 learning_paths 表中的方向路径，改动即时生效。
# 分享「大模型基础 + Agent 概念」打底，再按方向追加差异化技术模块。
_LEARNING_DIRECTION_PLAN = {
    "大模型应用开发": (
        ["s1-llm-basics", "s1-prompt", "s1-api-dev", "s1-ollama", "s2-agent-core", "s3-rag", "s3-langchain", "s6-rag-project"],
        ["project-3", "project-0", "project-4"],
    ),
    "机器学习工程师": (
        ["s1-llm-basics", "s1-api-dev", "s1-ollama", "s2-agent-core", "s2-agent-arch", "s3-rag", "s5-observability"],
        ["project-0", "project-3", "project-4"],
    ),
    "深度学习工程师": (
        ["s1-llm-basics", "s1-api-dev", "s1-ollama", "s2-agent-core", "s3-langgraph", "s3-agentic-rag"],
        ["project-4", "project-3"],
    ),
    "数据科学家": (
        ["s1-llm-basics", "s1-prompt", "s1-api-dev", "s2-agent-core", "s3-rag", "s5-observability", "s5-deploy"],
        ["project-0", "project-4", "project-3"],
    ),
    "AI 应用开发": (
        ["s1-llm-basics", "s1-api-dev", "s2-tool-calling", "s3-langchain", "s3-langgraph", "s4-multi-agent", "s5-deploy", "s6-rag-project", "s6-cs-agent", "s7-career"],
        ["project-1", "project-4", "project-2"],
    ),
    "计算机视觉工程师": (
        ["s1-llm-basics", "s1-api-dev", "s1-ollama", "s2-tool-calling", "s3-mcp", "s4-orchestration"],
        ["project-4", "project-0"],
    ),
}

# 兜底蓝图：方向不在上面差异化蓝图时使用（作为 on-demand 兜底路径，不入列表 Tab）
_DEFAULT_PLAN = (
    ["s1-llm-basics", "s1-prompt", "s1-api-dev", "s1-ollama", "s2-agent-core", "s3-rag", "s3-langchain"],
    ["project-3", "project-4"],
)

# 旧版 pipeline 遗留的方向路径（path-2026* 阶段式静态路径），已被方向蓝图取代。
# 保留在表里以便追溯，但默认停用，不作为列表Tab展示。
_LEGACY_PATH_IDS = {"path-2026", "path-2026-rag", "path-2026-agent", "path-2026-fullstack"}


def seed_learning_paths_from_direction_plan(cur=None, force=False):
    """把方向蓝图（学习路径的"内容"）灌入 learning_paths 表，作为数据库驱动的种子。

    数据源统一（learning_paths 改数据库驱动）后：
    - 方向路径内容（含节点课程序列、标题、进度锚点）以数据库为准，后台可编辑、即时生效；
    - 仅当表中缺少对应 id 时才插入（不覆盖后台已编辑的内容），force=True 可整体重建；
    - 课程/项目标题从 courses/projects 表实时读取（存在则用中文展示名，否则回退 id）。
    """
    conn = None
    if cur is None:
        conn = get_connection()
        cur = conn.cursor()

    def _titles(table, id_col, id_val):
        row = cur.execute(f"SELECT {id_col}, title FROM {table} WHERE id=?", (id_val,)).fetchone()
        return (row["title"] if row else id_val)

    def _course_title(cid):
        return _titles("courses", "id", cid)

    def _project_title(pid):
        return _titles("projects", "id", pid).replace("Project: ", "", 1)

    def _build(direction, courses, projects):
        nodes = []
        for i, cid in enumerate(courses):
            nodes.append({
                "id": f"gen-{direction}-course-{i}",
                "title": _course_title(cid),
                "type": "course",
                "items": [cid],
                "status": "current" if i == 0 else "locked",
                "progress": 0,
                "courseId": cid,
            })
        for j, pid in enumerate(projects):
            nodes.append({
                "id": f"gen-{direction}-project-{j}",
                "title": _project_title(pid),
                "type": "project",
                "items": [pid],
                "status": "locked",
                "progress": 0,
                "courseId": None,
            })
        return {
            "id": f"path-{direction}",
            "direction": direction,
            "title": f"{direction}学习路径",
            "description": "",
            "nodes": nodes,
            "total_weeks": len(nodes),
            "current_week": 1,
            "created_at": "2026-08-07",
        }

    try:
        for direction, (courses, projects) in _LEARNING_DIRECTION_PLAN.items():
            path = _build(direction, courses, projects)
            row = cur.execute("SELECT id FROM learning_paths WHERE id=?", (path["id"],)).fetchone()
            if row is not None and not force:
                continue  # 已有内容，尊重后台编辑
            cur.execute(
                """INSERT INTO learning_paths
                   (id, direction, title, description, total_weeks, current_week, nodes, is_active, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, datetime('now'))
                   ON CONFLICT(id) DO UPDATE SET
                     direction=excluded.direction, title=excluded.title,
                     description=excluded.description, total_weeks=excluded.total_weeks,
                     current_week=excluded.current_week, nodes=excluded.nodes, updated_at=datetime('now')
                """,
                (path["id"], direction, path["title"], path["description"],
                 path["total_weeks"], path["current_week"],
                 json.dumps(path["nodes"], ensure_ascii=False), path["created_at"]),
            )
        # 停用旧版遗留路径，避免作为列表 Tab 展示（保留行以便追溯/恢复）
        for legacy_id in _LEGACY_PATH_IDS:
            cur.execute("UPDATE learning_paths SET is_active=0 WHERE id=?", (legacy_id,))
    finally:
        if conn is not None:
            conn.commit()
            conn.close()


# ============ 用户体系 Helpers ============

def get_user_by_openid(openid: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE openid=?", (openid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user(user_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(openid: str, nickname: str = "", avatar: str = "", unionid: str = "") -> dict:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO users (openid, nickname, avatar, unionid) VALUES (?,?,?,?)",
        (openid, nickname, avatar, unionid),
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return get_user(uid)


def update_user_profile(
    user_id: int,
    nickname: str,
    avatar: str,
    grade: str = "",
    major: str = "",
    target_direction: str = "",
) -> None:
    """更新用户资料（昵称/头像 + 学员自填的年级/专业/目标方向），同步落库。"""
    conn = get_connection()
    conn.execute(
        "UPDATE users SET nickname=?, avatar=?, grade=?, major=?, target_direction=? WHERE id=?",
        (nickname, avatar, grade, major, target_direction, user_id),
    )
    conn.commit()
    conn.close()


def record_user_video(user_id: int, video_id: str, minutes: int = 0) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO user_video_progress (user_id, video_id, minutes) VALUES (?,?,?) "
        "ON CONFLICT(user_id, video_id) DO UPDATE SET watched_at=datetime('now'), minutes=excluded.minutes",
        (user_id, video_id, minutes),
    )
    conn.commit()
    conn.close()


def get_user_watched_video_ids(user_id: int) -> set:
    conn = get_connection()
    rows = conn.execute("SELECT video_id FROM user_video_progress WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return {r["video_id"] for r in rows}


def record_user_chapter(user_id: int, course_id: str, chapter_id: str) -> None:
    """记录用户完成某课程章节（七阶段文字课程按章节计进度/完课率）。"""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO user_chapter_progress (user_id, course_id, chapter_id) VALUES (?,?,?)",
        (user_id, course_id, chapter_id),
    )
    conn.commit()
    conn.close()


def get_user_completed_chapter_ids(user_id: int, course_id: str) -> set:
    conn = get_connection()
    rows = conn.execute(
        "SELECT chapter_id FROM user_chapter_progress WHERE user_id=? AND course_id=?",
        (user_id, course_id),
    ).fetchall()
    conn.close()
    return {r["chapter_id"] for r in rows}


def count_user_completed_chapters(user_id: int) -> int:
    """统计用户已完成的章节总数（押金完课率用）。"""
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM user_chapter_progress WHERE user_id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    return int(row["c"]) if row else 0


def get_user_video_progress(user_id: int) -> list:
    """Return per-user video progress rows: {video_id, watched_at, minutes}."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT video_id, watched_at, minutes FROM user_video_progress WHERE user_id=? ORDER BY watched_at",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_completed_project_count(user_id: int) -> int:
    """Count projects whose completed steps >= total steps (fully done by this user)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT p.step_count, COALESCE(up.completed_steps, 0) AS done "
        "FROM projects p LEFT JOIN user_project_progress up "
        "ON up.project_id=p.id AND up.user_id=? "
        "WHERE p.step_count > 0",
        (user_id,),
    ).fetchall()
    conn.close()
    return sum(1 for r in rows if r["done"] >= r["step_count"])


def get_latest_user_ability_report(user_id: int) -> Optional[dict]:
    """Return the user's most recent ability report row, or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM user_ability_reports WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def count_user_watched_videos(user_id: int) -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(DISTINCT video_id) AS c FROM user_video_progress WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return int(row["c"]) if row else 0


def record_user_project(user_id: int, project_id: str, completed_steps: int) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO user_project_progress (user_id, project_id, completed_steps) VALUES (?,?,?) "
        "ON CONFLICT(user_id, project_id) DO UPDATE SET completed_steps=excluded.completed_steps, updated_at=datetime('now')",
        (user_id, project_id, completed_steps),
    )
    conn.commit()
    conn.close()


def get_user_project_progress(user_id: int) -> dict:
    conn = get_connection()
    rows = conn.execute("SELECT project_id, completed_steps FROM user_project_progress WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return {r["project_id"]: r["completed_steps"] for r in rows}


def record_user_path_node(user_id: int, path_id: str, node_id: str) -> list:
    conn = get_connection()
    row = conn.execute("SELECT completed_nodes FROM user_path_progress WHERE user_id=? AND path_id=?", (user_id, path_id)).fetchone()
    nodes = parse_json_field(row["completed_nodes"]) if row else []
    if node_id not in nodes:
        nodes.append(node_id)
    conn.execute(
        "INSERT INTO user_path_progress (user_id, path_id, completed_nodes) VALUES (?,?,?) "
        "ON CONFLICT(user_id, path_id) DO UPDATE SET completed_nodes=excluded.completed_nodes, updated_at=datetime('now')",
        (user_id, path_id, json.dumps(nodes, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()
    return nodes


def get_user_path_completed(user_id: int, path_id: str) -> list:
    conn = get_connection()
    row = conn.execute("SELECT completed_nodes FROM user_path_progress WHERE user_id=? AND path_id=?", (user_id, path_id)).fetchone()
    conn.close()
    return parse_json_field(row["completed_nodes"]) if row else []


def get_user_path_progress(user_id: int) -> dict:
    """该用户所有学习路径的已完成节点：{path_id: [node_id, ...]}（DB 为准）。"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT path_id, completed_nodes FROM user_path_progress WHERE user_id=?", (user_id,)
    ).fetchall()
    conn.close()
    return {r["path_id"]: parse_json_field(r["completed_nodes"]) for r in rows}


def record_stage_assessment(user_id: int, stage: int, score: float) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO user_stage_assessments (user_id, stage, score) VALUES (?,?,?)",
        (user_id, stage, score),
    )
    conn.commit()
    conn.close()


def get_stage_assessments(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("SELECT stage, score FROM user_stage_assessments WHERE user_id=? ORDER BY stage", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_user_ability_report(user_id: int, data: dict) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO user_ability_reports (user_id, overall_score, level, dimensions, strengths, weaknesses, recommended_direction, estimated_hours) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            user_id,
            data.get("overall_score", data.get("overallScore", 0)),
            data.get("level", ""),
            json.dumps(data.get("dimensions", []), ensure_ascii=False),
            json.dumps(data.get("strengths", []), ensure_ascii=False),
            json.dumps(data.get("weaknesses", []), ensure_ascii=False),
            data.get("recommended_direction", data.get("recommendedDirection", "")),
            data.get("estimated_hours", data.get("estimatedHours", 0)),
        ),
    )
    conn.commit()
    conn.close()


def get_deposit(user_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_deposits WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_deposit(user_id: int, fields: dict) -> dict:
    """Create or update a user's deposit row. Never overwrites created_at/id/user_id."""
    fields = {k: v for k, v in fields.items() if k not in ("id", "user_id", "created_at")}
    fields["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    existing = conn.execute("SELECT id FROM user_deposits WHERE user_id=?", (user_id,)).fetchone()
    if existing:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE user_deposits SET {sets} WHERE user_id=?", list(fields.values()) + [user_id])
    else:
        cols = ["user_id"] + list(fields.keys())
        placeholders = ["?"] + ["?"] * len(fields)
        conn.execute(
            f"INSERT INTO user_deposits ({', '.join(cols)}) VALUES ({', '.join(placeholders)})",
            [user_id] + list(fields.values()),
        )
    conn.commit()
    conn.close()
    return get_deposit(user_id)


def get_user_access(user_id: int) -> Optional[dict]:
    """返回用户的权限记录（含服务端试用期起点），无记录则 None。"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_access WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_user_access(user_id: int, fields: dict) -> dict:
    """创建/更新用户权限记录。trial_started_at 与 admin_override 仅由服务端写入，
    客户端传入的其它字段一律丢弃。"""
    fields = {k: v for k, v in fields.items() if k in ("trial_started_at", "admin_override")}
    fields["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    existing = conn.execute("SELECT id FROM user_access WHERE user_id=?", (user_id,)).fetchone()
    if existing:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE user_access SET {sets} WHERE user_id=?", list(fields.values()) + [user_id])
    else:
        cols = ["user_id"] + list(fields.keys())
        placeholders = ["?"] + ["?"] * len(fields)
        conn.execute(
            f"INSERT INTO user_access ({', '.join(cols)}) VALUES ({', '.join(placeholders)})",
            [user_id] + list(fields.values()),
        )
    conn.commit()
    conn.close()
    return get_user_access(user_id)


# ============ AI 每日调用计数 Helpers（试用/未缴押金用户限流） ============

def get_ai_usage(user_id: int, usage_date: str, feature: str) -> Optional[dict]:
    """查询某用户某天某 AI 功能的用量记录，无记录则 None。"""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM ai_usage_daily WHERE user_id=? AND usage_date=? AND feature=?",
        (user_id, usage_date, feature),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def increment_ai_usage(user_id: int, usage_date: str, feature: str) -> int:
    """把某用户某天某 AI 功能的计数 +1（首次则建行=1），返回最新计数。

    用 upsert（ON CONFLICT / ON DUPLICATE KEY）保证并发下计数不丢。
    """
    conn = get_connection()
    conn.execute(
        "INSERT INTO ai_usage_daily (user_id, usage_date, feature, count) VALUES (?,?,?,1) "
        "ON CONFLICT(user_id, usage_date, feature) DO UPDATE SET count=excluded.count+1, updated_at=datetime('now')",
        (user_id, usage_date, feature),
    )
    conn.commit()
    row = conn.execute(
        "SELECT count FROM ai_usage_daily WHERE user_id=? AND usage_date=? AND feature=?",
        (user_id, usage_date, feature),
    ).fetchone()
    conn.close()
    return int(row["count"]) if row else 1


def get_ai_usage_total(user_id: int, usage_date: str) -> int:
    """某用户某天所有 AI 功能的总调用次数。"""
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(count), 0) AS total FROM ai_usage_daily WHERE user_id=? AND usage_date=?",
        (user_id, usage_date),
    ).fetchone()
    conn.close()
    return int(row["total"]) if row else 0

# 七阶段作业题库：对齐 2026 AI Agent 学习路线七阶段课程，支撑过程锁「每阶段作业提交并通过」
HOMEWORK_QUESTIONS = [
    {
        "stage": 1,
        "course_id": "s1-llm-basics",
        "title": "阶段一作业：用一条 Prompt 完成真实任务",
        "requirement": "选一个真实任务（总结一篇文章 / 生成周报初稿 / 角色扮演练习任选其一），写一条结构清晰的 Prompt（含任务、上下文、输出格式），提交提示词全文与 AI 输出结果，并说明你这样写的作用。",
        "rubric": "① 任务真实具体；② Prompt 要素齐全（任务/上下文/格式）；③ 能说明每段的设计意图。",
    },
    {
        "stage": 2,
        "course_id": "s2-agent-core",
        "title": "阶段二作业：设计一个简单 ReAct Agent 流程",
        "requirement": "以「天气查询 Agent」为例，画出 ReAct 循环：Thought → Action → Observation → … → Final Answer，并说明每一步里 LLM 和你的程序各负责什么。",
        "rubric": "① ReAct 循环正确完整；② 能分清 LLM 与程序职责；③ 体现了工具调用闭环的理解。",
    },
    {
        "stage": 3,
        "course_id": "s3-rag",
        "title": "阶段三作业：实现一个带 RAG 的知识问答",
        "requirement": "用 FastAPI + Chroma 实现最小 RAG：上传/内置一份文档，实现「检索 + 生成 + 引用溯源」问答，提交代码、一次检索问答的输入输出，并说明你的分块策略与引用如何传递。",
        "rubric": "① 检索-生成链路真实可跑；② 引用溯源有实现；③ 能讲清分块与 Embedding 的选择。",
    },
    {
        "stage": 4,
        "course_id": "s4-multi-agent",
        "title": "阶段四作业：设计一个 Supervisor 协作方案",
        "requirement": "为一个任务（如软件开发 / 客服分流）设计 Supervisor 多 Agent 方案：画出主管 + 执行 Agent 的协作图，说明任务怎么分配、Agent 之间怎么通信、出了错怎么办。",
        "rubric": "① 架构图清晰、职责不重叠；② 通信机制明确；③ 考虑了失败处理与成本。",
    },
    {
        "stage": 5,
        "course_id": "s5-deploy",
        "title": "阶段五作业：给 Agent 做 Docker 部署与优化",
        "requirement": "把阶段三的 RAG 问答（或任一 Agent）容器化：编写 Dockerfile 与 docker-compose，加一个性能/成本优化点（缓存或并行），提交 Dockerfile、优化前后对比与部署截图。",
        "rubric": "① Dockerfile 可构建、能一键部署；② 优化点有量化对比；③ 说明生产环境要考虑的安全/监控要点。",
    },
    {
        "stage": 6,
        "course_id": "s6-rag-project",
        "title": "阶段六作业：完成一个可部署的 Agent 项目",
        "requirement": "完成「RAG 知识库问答系统」或「智能客服 Agent」其一：代码放 GitHub、README 讲清架构、Docker 一键部署、有演示页面，提交项目链接与一段 3 分钟的项目讲述文稿。",
        "rubric": "① 项目完整可部署可演示；② 技术选型能讲出理由；③ 覆盖了工程要点（引用/审批/护栏等）。",
    },
    {
        "stage": 7,
        "course_id": "s7-career",
        "title": "阶段七作业：整理简历 + 讲清技术选型",
        "requirement": "完成简历（含 1 个 Agent 项目）并准备「为什么这样设计」的口头讲解：技术选型、难点与解法、效果评估各一段，提交简历要点 + 讲解大纲。",
        "rubric": "① 简历有可展示的 Agent 项目；② 技术选型讲解有深度（不是照搬教程）；③ 覆盖难点与效果。",
    },
]


def seed_homework_questions(cur=None):
    """幂等灌入七阶段作业题库（按 stage 去重，重复运行不产生重复题）。"""
    conn = None
    if cur is None:
        conn = get_connection()
        cur = conn.cursor()
    for q in HOMEWORK_QUESTIONS:
        exists = cur.execute("SELECT id FROM homework_questions WHERE stage=?", (q["stage"],)).fetchone()
        if not exists:
            cur.execute(
                "INSERT INTO homework_questions (stage, course_id, title, requirement, rubric) VALUES (?,?,?,?,?)",
                (q["stage"], q["course_id"], q["title"], q["requirement"], q["rubric"]),
            )
    if conn is not None:
        conn.commit()
        conn.close()


def get_homework_questions() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM homework_questions ORDER BY stage").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_homework_question(stage: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM homework_questions WHERE stage=?", (stage,)).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_homework_submission(user_id: int, stage: int, course_id: str, content: str,
                               ai_score: float, ai_feedback: str, status: str) -> dict:
    """创建或覆盖某用户某阶段的作业提交（重交覆盖上次记录）。"""
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM homework_submissions WHERE user_id=? AND stage=?", (user_id, stage),
    ).fetchone()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if existing:
        conn.execute(
            "UPDATE homework_submissions SET course_id=?, content=?, ai_score=?, ai_feedback=?, "
            "status=?, updated_at=? WHERE id=?",
            (course_id, content, ai_score, ai_feedback, status, now, existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO homework_submissions (user_id, stage, course_id, content, ai_score, ai_feedback, status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (user_id, stage, course_id, content, ai_score, ai_feedback, status, now, now),
        )
    conn.commit()
    conn.close()
    return get_homework_submission(user_id, stage)


def get_homework_submission(user_id: int, stage: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM homework_submissions WHERE user_id=? AND stage=?", (user_id, stage),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_homework_submissions(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM homework_submissions WHERE user_id=? ORDER BY stage", (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_homework_submissions(status: str | None = None) -> list:
    """后台复核用：列出作业提交（可按状态筛选），带用户昵称。

    status 取值：passed / rejected / None（全部）。
    """
    conn = get_connection()
    sql = (
        "SELECT s.*, u.nickname AS user_nickname "
        "FROM homework_submissions s LEFT JOIN users u ON u.id=s.user_id"
    )
    params = []
    if status:
        sql += " WHERE s.status=?"
        params.append(status)
    sql += " ORDER BY s.stage, s.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def admin_judge_homework(submission_id: int, status: str, ai_score: float) -> Optional[dict]:
    """后台人工复核改判作业状态与分数。"""
    if status not in ("passed", "rejected"):
        return None
    conn = get_connection()
    cur = conn.execute(
        "UPDATE homework_submissions SET status=?, ai_score=?, updated_at=datetime('now') WHERE id=?",
        (status, ai_score, submission_id),
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return None
    conn = get_connection()
    sub = conn.execute("SELECT * FROM homework_submissions WHERE id=?", (submission_id,)).fetchone()
    conn.close()
    return dict(sub) if sub else None


# ============ Seed Data ============

def _generate_default_videos(data_dir: str) -> int:
    """seed_data.py 不生成视频数据；原遗留视频库（videos.json）已清理。

    这里按课程生成一批占位视频，保证 videos 表非空、视频页可用；
    后续如需真实视频，替换 videos.json 或按章节 video_bv 关联即可。
    """
    import urllib.parse
    courses_file = os.path.join(data_dir, "enriched_courses.json")
    if not os.path.exists(courses_file):
        courses_file = os.path.join(data_dir, "courses.json")
    if not os.path.exists(courses_file):
        return 0
    with open(courses_file, "r", encoding="utf-8") as f:
        courses = json.load(f)
    videos = []
    for co in courses:
        cid = co.get("id", "")
        title = co.get("title", "") or ""
        videos.append({
            "id": f"video-{cid}",
            "title": f"{title} · 课程视频",
            "subtitle": "",
            "description": "示例视频（原遗留视频库已清理，此为按课程生成的占位）",
            "coreInfo": [],
            "narrative": "",
            "visual": "",
            "quality": {},
            "url": f"https://search.bilibili.com/all?keyword={urllib.parse.quote(title)}",
            "coverUrl": co.get("coverImg", co.get("cover_img", "")),
            "duration": 0,
            "chapter": "",
            "courseId": cid,
        })
    with open(os.path.join(data_dir, "videos.json"), "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    return len(videos)


def seed_from_json():
    """Seed database from existing JSON files."""
    data_dir = os.path.join(os.path.dirname(__file__), "data", "processed")

    # 若处理数据缺失（全新 clone / 全新部署 / CI）：
    # 先由 seed_data 生成基础数据（projects / assessment / knowledge 等非课程数据），
    # 再由 curriculum_2026 覆盖课程/视频/学习路径为新七阶段体系，
    # 保证 `python -m database` 在任何环境都能一键自举出完整种子。
    if not os.path.exists(os.path.join(data_dir, "courses.json")):
        from data_pipeline.seed_data import run as _generate_seed
        _generate_seed()
        from data_pipeline import curriculum_2026
        curriculum_2026.main()

    # Seed courses (use enriched data for coverImg, category, etc.)
    courses_file = os.path.join(data_dir, "enriched_courses.json")
    if not os.path.exists(courses_file):
        courses_file = os.path.join(data_dir, "courses.json")
    if os.path.exists(courses_file):
        with open(courses_file, "r", encoding="utf-8") as f:
            courses = json.load(f)
        for c in courses:
            chapters = c.get("chapters", [])
            insert_row("courses", {
                "id": c["id"],
                "title": c["title"],
                "description": c.get("description", ""),
                "cover_img": c.get("coverImg", c.get("cover_img", "")),
                "topic": c.get("topic", ""),
                "difficulty": c.get("difficulty", "beginner"),
                "estimated_hours": c.get("estimated_hours", 0),
                "lessons": c.get("lessons", len(chapters)),
                "progress": c.get("progress", 0),
                "is_free": c.get("isFree", 1),
                "price": c.get("price", 0),
                "source": c.get("source", ""),
                "chapters": json.dumps(chapters, ensure_ascii=False),
            })
        print(f"  Seeded {len(courses)} courses")

    # Seed projects
    projects_file = os.path.join(data_dir, "projects.json")
    if os.path.exists(projects_file):
        with open(projects_file, "r", encoding="utf-8") as f:
            projects = json.load(f)
        for p in projects:
            insert_row("projects", {
                "id": p["id"],
                "title": p["title"],
                "description": p.get("description", ""),
                "cover_img": p.get("coverImg", p.get("cover_img", "")),
                "tech_stack": json.dumps(p.get("tech_stack", p.get("techStack", [])), ensure_ascii=False),
                "difficulty": p.get("difficulty", "beginner"),
                "estimated_hours": p.get("estimated_hours", 0),
                "step_count": p.get("stepCount", p.get("step_count", 0)),
                "status": p.get("status", "available"),
                "progress": p.get("progress", 0),
                "is_free": p.get("isFree", 1),
                "price": p.get("price", 0),
                "topics_covered": json.dumps(p.get("topics_covered", []), ensure_ascii=False),
                "steps": json.dumps(p.get("steps", []), ensure_ascii=False),
                "source": p.get("source", ""),
            })
        print(f"  Seeded {len(projects)} projects")

    # Seed videos
    videos_file = os.path.join(data_dir, "videos.json")
    if os.path.exists(videos_file):
        with open(videos_file, "r", encoding="utf-8") as f:
            videos = json.load(f)
        for v in videos:
            insert_row("videos", {
                "id": v["id"],
                "title": v["title"],
                "subtitle": v.get("subtitle", ""),
                "description": v.get("description", ""),
                "core_info": json.dumps(v.get("coreInfo", []), ensure_ascii=False),
                "narrative": v.get("narrative", ""),
                "visual": v.get("visual", ""),
                "quality": json.dumps(v.get("quality", {}), ensure_ascii=False),
                "url": v["url"],
                "cover_url": v.get("coverUrl", v.get("cover_url", "")),
                "duration": v.get("duration", 0),
                "chapter": v.get("chapter", ""),
                "course_id": v.get("courseId", v.get("course_id", "")),
            })
        print(f"  Seeded {len(videos)} videos")

    # Seed learning paths
    paths_file = os.path.join(data_dir, "learning_paths.json")
    if os.path.exists(paths_file):
        with open(paths_file, "r", encoding="utf-8") as f:
            paths = json.load(f)
        for p in paths:
            insert_row("learning_paths", {
                "id": p["id"],
                "direction": p.get("direction", ""),
                "title": p.get("title", ""),
                "description": p.get("description", ""),
                "total_weeks": p.get("totalWeeks", p.get("total_weeks", 0)),
                "current_week": p.get("currentWeek", p.get("current_week", 0)),
                "nodes": json.dumps(p.get("nodes", []), ensure_ascii=False),
            })
        print(f"  Seeded {len(paths)} learning paths")

    # Seed learning stats
    stats_file = os.path.join(data_dir, "learning_stats.json")
    if os.path.exists(stats_file):
        with open(stats_file, "r", encoding="utf-8") as f:
            s = json.load(f)
        insert_row("learning_stats", {
            "learning_days": s.get("learningDays", s.get("learning_days", 0)),
            "total_hours": s.get("totalHours", s.get("total_hours", 0)),
            "completed_projects": s.get("completedProjects", s.get("completed_projects", 0)),
            "completed_lessons": s.get("completedLessons", s.get("completed_lessons", 0)),
        })
        print(f"  Seeded learning stats")

    # Seed learning records
    records_file = os.path.join(data_dir, "learning_records.json")
    if os.path.exists(records_file):
        with open(records_file, "r", encoding="utf-8") as f:
            records = json.load(f)
        for r in records:
            insert_row("learning_records", {
                "date": r.get("date", ""),
                "duration": r.get("duration", 0),
                "lessons_completed": r.get("lessonsCompleted", r.get("lessons_completed", 0)),
                "exercises_done": r.get("exercisesDone", r.get("exercises_done", 0)),
            })
        print(f"  Seeded {len(records)} learning records")

    # Seed job matching
    job_file = os.path.join(data_dir, "job_matching.json")
    if os.path.exists(job_file):
        with open(job_file, "r", encoding="utf-8") as f:
            j = json.load(f)
        insert_row("job_matching", {
            "job_title": j.get("jobTitle", j.get("job_title", "")),
            "company": j.get("company", ""),
            "match_score": j.get("matchScore", j.get("match_score", 0)),
            "required_skills": json.dumps(j.get("requiredSkills", j.get("required_skills", [])), ensure_ascii=False),
            "gap_skills": json.dumps(j.get("gapSkills", j.get("gap_skills", [])), ensure_ascii=False),
            "recommended_courses": json.dumps(j.get("recommendedCourses", j.get("recommended_courses", [])), ensure_ascii=False),
            "recommended_projects": json.dumps(j.get("recommendedProjects", j.get("recommended_projects", [])), ensure_ascii=False),
        })
        print(f"  Seeded job matching")

    # Seed assessment result
    report_file = os.path.join(data_dir, "ability_report.json")
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            r = json.load(f)
        insert_row("assessment_results", {
            "overall_score": r.get("overallScore", r.get("overall_score", 0)),
            "level": r.get("level", "初级"),
            "dimensions": json.dumps(r.get("dimensions", []), ensure_ascii=False),
            "strengths": json.dumps(r.get("strengths", []), ensure_ascii=False),
            "weaknesses": json.dumps(r.get("weaknesses", []), ensure_ascii=False),
            "recommended_direction": r.get("recommendedDirection", r.get("recommended_direction", "")),
            "estimated_hours": r.get("estimatedHours", r.get("estimated_hours", 0)),
        })
        print(f"  Seeded assessment result")

    # Seed default banners
    default_banners = [
        {"title": "AI 能力测评", "description": "测测你的 AI 水平", "image_url": "/static/covers/banner-160.png", "link_url": "/pages/assessment/index", "sort_order": 1},
        {"title": "实战项目", "description": "做出可写进简历的作品", "image_url": "/static/covers/banner-201.png", "link_url": "/pages/project/index", "sort_order": 2},
        {"title": "岗位对标", "description": "看看你离目标岗位差多少", "image_url": "/static/covers/banner-119.png", "link_url": "/pages/jobMatching/index", "sort_order": 3},
    ]
    for b in default_banners:
        insert_row("banners", b)
    print(f"  Seeded {len(default_banners)} banners")

    # Seed default directions (对应 2026 AI Agent 学习路线七阶段)
    default_directions = [
        {"name": "阶段一 · AI 大模型基础", "description": "LLM 概念、Prompt、API 调用、Ollama 本地部署", "color": "#165dff", "topic_key": "大模型基础", "sort_order": 1},
        {"name": "阶段二 · Agent 基础概念", "description": "Agent 核心能力、架构模式、工具调用、记忆系统", "color": "#7c3aed", "topic_key": "Agent基础", "sort_order": 2},
        {"name": "阶段三 · Agent 开发实战", "description": "RAG、MCP、Agent Skills、LangChain、LangGraph", "color": "#00b42a", "topic_key": "开发实战", "sort_order": 3},
        {"name": "阶段四 · 多 Agent 系统", "description": "多 Agent 架构、MetaGPT/AutoGen、编排与工程化", "color": "#ff7d00", "topic_key": "多Agent", "sort_order": 4},
        {"name": "阶段五 · 优化和部署", "description": "性能优化、安全可控、监控评估、生产部署", "color": "#f53f3f", "topic_key": "优化部署", "sort_order": 5},
        {"name": "阶段六 · 项目实战", "description": "RAG 知识库问答、智能客服 Agent 求职作品", "color": "#00a0c0", "topic_key": "项目实战", "sort_order": 6},
        {"name": "阶段七 · 求职备战", "description": "简历作品集、高频面试题、项目讲述", "color": "#ff6b81", "topic_key": "求职备战", "sort_order": 7},
    ]
    for d in default_directions:
        insert_row("directions", d)
    print(f"  Seeded {len(default_directions)} directions")

    # Seed menu items
    default_menus = [
        {"icon": "📊", "label": "岗位能力对标", "path": "/pages/jobMatching/index", "section": "mine", "sort_order": 1},
        {"icon": "📁", "label": "我的作品集", "path": "/pages/portfolio/index", "section": "mine", "sort_order": 2},
        {"icon": "🎯", "label": "学习目标", "path": "/pages/goals/index", "section": "mine", "sort_order": 3},
        {"icon": "⭐", "label": "我的收藏", "path": "/pages/favorites/index", "section": "mine", "sort_order": 4},
        {"icon": "⚙️", "label": "设置", "path": "/pages/settings/index", "section": "mine", "sort_order": 5},
    ]
    for m in default_menus:
        insert_row("menu_items", m)
    print(f"  Seeded {len(default_menus)} menu items")

    # Seed admin user (default: admin / admin123)
    # In production, use a proper password hash
    import hashlib
    insert_row("admin_users", {
        "username": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
    })
    print("  Seeded admin user (admin / admin123)")

    # Seed default FAQ items（答疑知识库）
    default_faqs = [
        {"question": "这个平台是免费的吗？", "answer": "核心功能全部免费开放：七阶段 AI Agent 开发课程、AI 导师答疑、实操练习、能力测评、学习档案都不收费。",
         "category": "general", "sort_order": 1, "view_count": 0, "is_active": 1},
        {"question": "押金式培训怎么退费？", "answer": "报名缴纳押金后，90 天内完成七阶段课程（完课率 100%）、每阶段作业通过、七阶段考核均分 ≥85 且实战项目通过，达标后申请退费，经人工复核后全额原路退回。",
         "category": "deposit", "sort_order": 2, "view_count": 0, "is_active": 1},
        {"question": "完不成怎么办？押金会退吗？", "answer": "未在 90 天期限内达标，押金转为培训费，可续学一期，不予退还。请按学习路径合理安排时间。",
         "category": "deposit", "sort_order": 3, "view_count": 0, "is_active": 1},
        {"question": "AI 导师答疑有限制吗？", "answer": "答疑免费开放。基础问题由 AI 导师（课程知识库 RAG）自动解答，复杂问题可咨询社群或助教。",
         "category": "general", "sort_order": 4, "view_count": 0, "is_active": 1},
        {"question": "课程适合零基础吗？", "answer": "适合。课程按 2026 最新 AI Agent 学习路线七阶段设计：大模型基础 → Agent 概念 → 开发实战 → 多 Agent → 优化部署 → 项目实战 → 求职备战，从零讲起，有 Python/FastAPI 基础上手更快。",
         "category": "course", "sort_order": 5, "view_count": 0, "is_active": 1},
        {"question": "如何获得结业认证？", "answer": "完成全部课程、作业与考核，通过实战项目评审后，可申请能力等级认证（结业项目）。",
         "category": "course", "sort_order": 6, "view_count": 0, "is_active": 1},
    ]
    for f in default_faqs:
        insert_row("faq_items", f)
    print(f"  Seeded {len(default_faqs)} FAQ items")

    # 课程/项目已灌入后，方向学习路径再回填一次（init_db 阶段课程未就绪时标题会回退为 id；
    # 这里用真实标题覆盖，保证数据库驱动的学习路径标题正确）。
    seed_learning_paths_from_direction_plan()


if __name__ == "__main__":
    # 仅 SQLite 模式删除旧库文件重建；MySQL 走 CREATE TABLE IF NOT EXISTS（幂等，不清已有数据）。
    if DB_ENGINE != "mysql" and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database: {DB_PATH}")
    init_db()
    seed_from_json()
    print("[DB] initialization complete!")