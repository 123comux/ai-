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

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")


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


def parse_json_field(value: str, default=None):
    """Parse a JSON string field."""
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value) if value else (default or [])
    except (json.JSONDecodeError, TypeError):
        return default or []


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

    # Seed default directions
    default_directions = [
        {"name": "AI 算法工程师", "description": "机器学习、深度学习、大模型微调", "color": "#165dff", "topic_key": "Machine Learning", "sort_order": 1},
        {"name": "AI 产品经理", "description": "AI 产品设计、Prompt Engineering", "color": "#7c3aed", "topic_key": "AI/ML", "sort_order": 2},
        {"name": "AIGC 应用人才", "description": "AI 绘画、AI 写作、AI 视频", "color": "#00b42a", "topic_key": "Generative AI", "sort_order": 3},
        {"name": "数据分析工程师", "description": "Python 数据分析、SQL、BI", "color": "#ff7d00", "topic_key": "Data Science", "sort_order": 4},
        {"name": "AI 应用开发", "description": "大模型 API、RAG、Agent", "color": "#f53f3f", "topic_key": "LLM", "sort_order": 5},
    ]
    for d in default_directions:
        insert_row("directions", d)
    print(f"  Seeded {len(default_directions)} directions")

    # Seed menu items
    default_menus = [
        {"icon": "📊", "label": "岗位能力对标", "path": "/pages/jobMatching/index", "section": "mine", "sort_order": 1},
        {"icon": "📁", "label": "我的作品集", "path": "/pages/portfolio/index", "section": "mine", "sort_order": 2},
        {"icon": "📝", "label": "学习记录", "path": "/pages/learningRecord/index", "section": "mine", "sort_order": 3},
        {"icon": "🎯", "label": "学习目标", "path": "/pages/goals/index", "section": "mine", "sort_order": 4},
        {"icon": "⭐", "label": "我的收藏", "path": "/pages/favorites/index", "section": "mine", "sort_order": 5},
        {"icon": "⚙️", "label": "设置", "path": "/pages/settings/index", "section": "mine", "sort_order": 6},
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
    print("✅ Database initialization complete!")