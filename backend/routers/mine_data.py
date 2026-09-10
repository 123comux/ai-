"""Mine page data API router: portfolio, learning goals, favorites.

Backed by SQLite cms.db (via database.py helpers) and processed JSON data files.
"""
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from database import get_connection, insert_row, query_all, query_one, update_row, delete_row, parse_json_field
from auth_utils import get_optional_user


async def _uid(request: Request) -> int:
    """Current user id, or 0 for the legacy global/demo scope (no auth)."""
    user = await get_optional_user(request)
    return user["id"] if user else 0

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/mine", tags=["mine-data"])


def _load_json(filename: str, default=None):
    path = PROCESSED_DIR / filename
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


# ============ Portfolio ============

@router.get("/portfolio")
async def get_portfolio():
    """Get user's project portfolio: projects with progress > 0."""
    projects = _load_json("enriched_projects.json") or _load_json("projects.json") or []
    if not isinstance(projects, list):
        projects = []
    progress = _load_json("project_progress.json", {}) or {}
    if not isinstance(progress, dict):
        progress = {}

    portfolio = []
    for p in projects:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        done = progress.get(pid, 0)
        total = len(p.get("steps", []) or [])
        if not done or not total:
            continue
        tech = p.get("techStack") or p.get("tech_stack") or []
        portfolio.append({
            "id": pid,
            "title": p.get("title", ""),
            "description": p.get("description", ""),
            "coverImg": p.get("coverImg") or p.get("cover_img") or "",
            "techStack": tech if isinstance(tech, list) else [],
            "difficulty": p.get("difficulty", ""),
            "status": "completed" if done >= total else "in_progress",
            "completedSteps": done,
            "totalSteps": total,
        })
    # 完成的排前面，再按进度降序
    portfolio.sort(key=lambda x: (x["status"] != "completed", -x["completedSteps"]))
    return portfolio


# ============ Goals ============

@router.get("/goals")
async def list_goals(request: Request):
    uid = await _uid(request)
    conn = get_connection()
    rows = conn.execute("SELECT * FROM goals WHERE user_id=? ORDER BY sort_order ASC, id DESC", (uid,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/goals")
async def create_goal(body: dict, request: Request):
    uid = await _uid(request)
    title = (body.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="标题不能为空")
    row = {
        "user_id": uid,
        "title": title,
        "description": (body.get("description") or "").strip(),
        "target_date": (body.get("target_date") or "").strip(),
        "status": body.get("status") or "pending",
        "sort_order": int(body.get("sort_order") or 0),
    }
    goal_id = insert_row("goals", row)
    return query_one("goals", goal_id)


@router.put("/goals/{goal_id}")
async def update_goal(goal_id: int, body: dict, request: Request):
    uid = await _uid(request)
    conn = get_connection()
    existing = conn.execute("SELECT * FROM goals WHERE id=? AND user_id=?", (goal_id, uid)).fetchone()
    conn.close()
    if not existing:
        raise HTTPException(status_code=404, detail="目标不存在")
    updates = {}
    for field in ("title", "description", "target_date", "status", "sort_order"):
        if field in body:
            updates[field] = body[field]
    if "title" in updates:
        title = (updates["title"] or "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="标题不能为空")
        updates["title"] = title
    update_row("goals", goal_id, updates)
    return query_one("goals", goal_id)


@router.delete("/goals/{goal_id}")
async def delete_goal(goal_id: int, request: Request):
    uid = await _uid(request)
    conn = get_connection()
    existing = conn.execute("SELECT id FROM goals WHERE id=? AND user_id=?", (goal_id, uid)).fetchone()
    conn.close()
    if not existing:
        raise HTTPException(status_code=404, detail="目标不存在")
    delete_row("goals", goal_id)
    return {"ok": True}


# ============ Favorites ============

def _resolve_favorite(item_type: str, item_id: str) -> dict:
    """Look up title/cover/detail_path from courses or projects table."""
    conn = get_connection()
    page = ""
    if item_type == "course":
        page = "/pages/courseDetail/index?id="
        row = conn.execute(
            "SELECT id, title, cover_img AS coverImg FROM courses WHERE id=?", (item_id,)
        ).fetchone()
    elif item_type == "project":
        page = "/pages/projectDetail/index?id="
        row = conn.execute(
            "SELECT id, title, cover_img AS coverImg FROM projects WHERE id=?", (item_id,)
        ).fetchone()
    else:
        row = None
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"{item_type} 不存在")
    data = dict(row)
    # 详情路径在 Python 侧拼接：SQLite 的 `||` 在 MySQL 里是逻辑或（不是字符串拼接），
    # 写成 SQL 会导致 MySQL/PG 上 detail_path 变成 0/1。
    data["detail_path"] = page + str(data.get("id") or "")
    return data


@router.get("/favorites")
async def list_favorites(request: Request):
    uid = await _uid(request)
    conn = get_connection()
    rows = conn.execute("SELECT * FROM favorites WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/favorites")
async def add_favorite(body: dict, request: Request):
    uid = await _uid(request)
    item_type = body.get("item_type")
    item_id = str(body.get("item_id") or "")
    if item_type not in ("course", "project") or not item_id:
        raise HTTPException(status_code=400, detail="参数错误")
    info = _resolve_favorite(item_type, item_id)
    conn = get_connection()
    exists = conn.execute(
        "SELECT id FROM favorites WHERE item_type=? AND item_id=? AND user_id=?",
        (item_type, item_id, uid),
    ).fetchone()
    conn.close()
    if exists:
        return query_one("favorites", exists["id"])
    fav_id = insert_row("favorites", {
        "user_id": uid,
        "item_type": item_type,
        "item_id": item_id,
        "title": info["title"],
        "cover_img": info["coverImg"],
        "detail_path": info["detail_path"],
    })
    return query_one("favorites", fav_id)


@router.delete("/favorites/{fav_id}")
async def remove_favorite(fav_id: int, request: Request):
    uid = await _uid(request)
    conn = get_connection()
    existing = conn.execute("SELECT id FROM favorites WHERE id=? AND user_id=?", (fav_id, uid)).fetchone()
    conn.close()
    if not existing:
        raise HTTPException(status_code=404, detail="收藏不存在")
    delete_row("favorites", fav_id)
    return {"ok": True}
