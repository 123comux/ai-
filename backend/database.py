"""
SQLite database module for content management.
Provides CRUD operations for all content types.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "cms.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


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
            name TEXT NOT NULL UNIQUE,
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
            id TEXT PRIMARY KEY,
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
            id TEXT PRIMARY KEY,
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
            source TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Videos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
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
            id TEXT PRIMARY KEY,
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
            item_type TEXT NOT NULL,
            item_id TEXT NOT NULL,
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
            username TEXT NOT NULL UNIQUE,
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
            checkin_date TEXT NOT NULL,  -- YYYY-MM-DD
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
            share_type TEXT NOT NULL DEFAULT 'course',
            share_target TEXT NOT NULL,
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
            code TEXT NOT NULL UNIQUE,
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
            openid TEXT NOT NULL UNIQUE,
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
            video_id TEXT NOT NULL,
            watched_at TEXT NOT NULL DEFAULT (datetime('now')),
            minutes INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, video_id)
        )
    """)

    # 按用户隔离的章节完成记录（五阶段课程为文字章节，完课率按章节计，不依赖遗留视频库）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_chapter_progress (
            user_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            chapter_id TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, course_id, chapter_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_project_progress (
            user_id INTEGER NOT NULL,
            project_id TEXT NOT NULL,
            completed_steps INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, project_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_path_progress (
            user_id INTEGER NOT NULL,
            path_id TEXT NOT NULL,
            completed_nodes TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, path_id)
        )
    """)

    # 五阶段考核成绩（考核锁用）
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

    # 作业题库（五阶段各一题，支撑过程锁「每阶段作业提交并通过」）
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

    seed_homework_questions(cur)

    conn.commit()
    conn.close()
    # 注意：Windows 默认 GBK 控制台无法输出 emoji，用 ASCII 避免 UnicodeEncodeError
    print(f"[DB] initialized at {DB_PATH}")


# ============ CRUD Helpers ============

def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to dict."""
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
    """记录用户完成某课程章节（五阶段文字课程按章节计进度/完课率）。"""
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


# ============ 作业提交 / 评审 Helpers ============

# 五阶段作业题库：对齐五阶段课程主题，支撑过程锁「每阶段作业提交并通过」
HOMEWORK_QUESTIONS = [
    {
        "stage": 1,
        "course_id": "stage-1-cognition",
        "title": "认知阶段作业：说说 AI 的能与不能",
        "requirement": "用你自己的话解释「AI 是什么、能帮你做什么、有什么局限」，并举例一个你生活/学习中已经在用的 AI 场景（100 字以上）。",
        "rubric": "① 能准确区分 AI 的能力与局限（不吹不贬）；② 有具体的生活例子；③ 表述清晰、有自己的话。",
    },
    {
        "stage": 2,
        "course_id": "stage-2-basics",
        "title": "入门阶段作业：一次真实的 AI 使用体验",
        "requirement": "选一个 AI 工具（对话 / AI 写作 / AI 绘图任选其一），描述你的完整使用过程：你输入了什么、AI 输出了什么、你觉得哪里好用、哪里不满意（100 字以上）。",
        "rubric": "① 描述的是真实使用过程而非设想；② 能区分 AI 输出的好坏；③ 有自己的观察和感受。",
    },
    {
        "stage": 3,
        "course_id": "stage-3-advanced",
        "title": "进阶阶段作业：写一个四段式提示词",
        "requirement": "针对一个你要真实完成的任务，写一个「四段式提示词」（清晰任务 / 角色设定 / 场景目标 / 限制格式），并逐段说明你这样写的作用。",
        "rubric": "① 四段齐全且结构清晰；② 任务具体可执行；③ 每段说明到位（为什么这样写）。",
    },
    {
        "stage": 4,
        "course_id": "stage-4-practice",
        "title": "实战阶段作业：用 AI 完成一个真实任务",
        "requirement": "用 AI 完成一个真实场景任务（周报生成 / 活动策划 / PPT 文案任选其一）：提交你的完整提示词、AI 输出结果，并说明你如何修改让它变得更好。",
        "rubric": "① 任务真实具体；② 提示词完整可复现；③ 展示了结果与迭代改进的过程。",
    },
    {
        "stage": 5,
        "course_id": "stage-5-mastery",
        "title": "熟练阶段作业：设计一个 AI 自动化工作流",
        "requirement": "把一个重复性任务设计成「AI 自动化工作流」：写出流程的每一步、每一步用什么提示词或工具、以及如何保证输出质量（含人工复核点）。",
        "rubric": "① 流程可执行、步骤清晰；② 每步有落地提示词；③ 考虑了边界情况和质量复核。",
    },
]


def seed_homework_questions(cur=None):
    """幂等灌入五阶段作业题库（按 stage 去重，重复运行不产生重复题）。"""
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

def seed_from_json():
    """Seed database from existing JSON files."""
    data_dir = os.path.join(os.path.dirname(__file__), "data", "processed")

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
        {"title": "AI 能力测评", "description": "测测你的 AI 水平", "image_url": "https://picsum.photos/id/160/750/400", "link_url": "/pages/assessment/index", "sort_order": 1},
        {"title": "实战项目", "description": "做出可写进简历的作品", "image_url": "https://picsum.photos/id/201/750/400", "link_url": "/pages/project/index", "sort_order": 2},
        {"title": "岗位对标", "description": "看看你离目标岗位差多少", "image_url": "https://picsum.photos/id/119/750/400", "link_url": "/pages/jobMatching/index", "sort_order": 3},
    ]
    for b in default_banners:
        insert_row("banners", b)
    print(f"  Seeded {len(default_banners)} banners")

    # Seed default directions (对应零基础五阶段课程：认知/入门/进阶/实战/熟练)
    default_directions = [
        {"name": "零基础认知", "description": "了解 AI 能做什么、不能做什么", "color": "#165dff", "topic_key": "认知", "sort_order": 1},
        {"name": "入门实践", "description": "认识主流 AI 工具，开始动手用", "color": "#7c3aed", "topic_key": "入门", "sort_order": 2},
        {"name": "提示词进阶", "description": "写出高质量提示词，让 AI 更懂你", "color": "#00b42a", "topic_key": "进阶", "sort_order": 3},
        {"name": "场景实战", "description": "用 AI 解决工作学习中的真实问题", "color": "#ff7d00", "topic_key": "实战", "sort_order": 4},
        {"name": "熟练精通", "description": "建立自动化工作流，善用 AI", "color": "#f53f3f", "topic_key": "熟练", "sort_order": 5},
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


if __name__ == "__main__":
    # Remove old database if exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database: {DB_PATH}")
    init_db()
    seed_from_json()
    print("[DB] initialization complete!")