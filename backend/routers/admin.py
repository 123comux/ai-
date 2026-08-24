"""
CMS Admin API - CRUD endpoints for all content types.
"""
import hashlib
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, Field

from database import (
    query_all, query_one, insert_row, update_row, delete_row, parse_json_field, get_connection,
    save_admin_session, get_admin_session, delete_admin_session,
)
from cache import clear as cache_clear

router = APIRouter(prefix="/api/admin", tags=["admin"])

# ============ Auth ============

# admin token 已持久化到 admin_sessions 表（重启不失效），无需进程内存缓存。


def verify_token(request: Request) -> str:
    """Verify admin auth token (read Authorization header from Request).

    注意：必须用 Request 手动读 header——带 prefix 的 APIRouter 里 Header(None)
    参数注入会失效（FastAPI 已知行为），导致 auth 恒为 None。
    token 存库并带过期时间，后端重启后会话仍有效。
    """
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "Missing authorization header")
    token = auth.replace("Bearer ", "")
    session = get_admin_session(token)
    if not session:
        raise HTTPException(401, "Invalid or expired token")
    return session["username"]


@router.post("/login")
def admin_login(username: str, password: str):
    """Login and get auth token."""
    users = query_all("admin_users", {"username": username})
    if not users:
        raise HTTPException(401, "Invalid credentials")
    user = users[0]
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    if user["password_hash"] != pwd_hash:
        raise HTTPException(401, "Invalid credentials")
    # 生成 token 并持久化（7 天有效，重启不失效）
    import secrets
    from datetime import datetime, timedelta
    token = f"admin_{secrets.token_hex(16)}"
    expires_at = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    save_admin_session(token, username, user.get("role", "admin"), expires_at)
    return {"token": token, "username": username, "role": user.get("role", "admin")}


@router.post("/logout")
def admin_logout(request: Request):
    """退出登录：删除当前会话 token（可选，前端登出时调用）。"""
    from routers.admin import verify_token as _vt
    _vt(request)  # 校验有效性
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    token = auth.replace("Bearer ", "") if auth else ""
    if token:
        delete_admin_session(token)
    return {"ok": True}


# ============ Generic CRUD Helpers ============

TABLE_CONFIG = {
    "banners": {"fields": ["title", "description", "image_url", "link_url", "sort_order", "is_active"], "label": "轮播图"},
    "directions": {"fields": ["name", "description", "color", "topic_key", "icon", "sort_order", "is_active"], "label": "学习方向"},
    "courses": {"fields": ["id", "title", "description", "cover_img", "topic", "difficulty", "estimated_hours", "lessons", "progress", "is_free", "price", "source", "chapters", "is_active"], "label": "课程"},
    "projects": {"fields": ["id", "title", "description", "cover_img", "tech_stack", "difficulty", "estimated_hours", "step_count", "status", "progress", "is_free", "price", "topics_covered", "steps", "source", "is_active"], "label": "实战项目"},
    "videos": {"fields": ["id", "title", "subtitle", "description", "core_info", "narrative", "visual", "quality", "url", "cover_url", "duration", "chapter", "course_id", "is_active"], "label": "视频"},
    "learning_paths": {"fields": ["id", "direction", "title", "description", "total_weeks", "current_week", "nodes", "is_active"], "label": "学习路径"},
    "menu_items": {"fields": ["icon", "label", "path", "section", "sort_order", "is_active"], "label": "菜单项"},
    "job_matching": {"fields": ["job_title", "company", "match_score", "required_skills", "gap_skills", "recommended_courses", "recommended_projects", "is_active"], "label": "岗位对标"},
    "learning_stats": {"fields": ["learning_days", "total_hours", "completed_projects", "completed_lessons"], "label": "学习统计"},
    "learning_records": {"fields": ["date", "duration", "lessons_completed", "exercises_done"], "label": "学习记录"},
    # 用户体系
    "users": {"fields": ["id", "openid", "nickname", "avatar", "grade", "major", "target_direction", "created_at"], "label": "用户"},
    "user_deposits": {"fields": ["user_id", "amount", "currency", "status", "enrolled_at", "deadline_at", "refund_amount", "refund_at"], "label": "押金记录"},
    "user_ability_reports": {"fields": ["user_id", "overall_score", "level", "dimensions", "recommended_direction", "created_at"], "label": "能力报告"},
    # 平台化：打卡/社区/FAQ
    "checkins": {"fields": ["user_id", "checkin_date", "note", "created_at"], "label": "打卡记录"},
    "community_posts": {"fields": ["user_id", "title", "content", "category", "likes", "created_at"], "label": "社区帖子"},
    "community_replies": {"fields": ["post_id", "user_id", "content", "created_at"], "label": "社区回复"},
    "faq_items": {"fields": ["question", "answer", "category", "sort_order", "view_count", "is_active"], "label": "常见问题库"},
    "teams": {"fields": ["name", "code", "owner_id", "member_count", "max_members"], "label": "学习小组"},
    "team_members": {"fields": ["team_id", "user_id", "joined_at"], "label": "小组成员"},
    "share_unlocks": {"fields": ["user_id", "share_type", "share_target", "unlocked_content"], "label": "分享解锁"},
}


@router.get("/tables")
def list_tables():
    """List all available tables."""
    return [{"name": k, "label": v["label"], "fields": v["fields"]} for k, v in TABLE_CONFIG.items()]


@router.get("/dashboard")
def dashboard(request: Request):
    """运营数据看板：用户数、完课率、测评分布、答疑量、押金退费率。"""
    verify_token(request)
    conn = get_connection()
    def count(sql, *args):
        row = conn.execute(sql, args).fetchone()
        return int(row["c"]) if row else 0

    data = {
        "users": count("SELECT COUNT(*) c FROM users"),
        "enrolled_users": count("SELECT COUNT(DISTINCT user_id) c FROM user_deposits WHERE status='active'"),
        "refunded": count("SELECT COUNT(*) c FROM user_deposits WHERE status='refunded'"),
        "checkins": count("SELECT COUNT(*) c FROM checkins"),
        "posts": count("SELECT COUNT(*) c FROM community_posts"),
        "replies": count("SELECT COUNT(*) c FROM community_replies"),
        "videos_watched": count("SELECT COUNT(*) c FROM user_video_progress"),
        "assessments": count("SELECT COUNT(*) c FROM user_ability_reports"),
        "faq_count": count("SELECT COUNT(*) c FROM faq_items WHERE is_active=1"),
        "teams_count": count("SELECT COUNT(*) c FROM teams"),
        "avg_score": None,
        "assess_levels": {},
    }
    row = conn.execute("SELECT AVG(overall_score) a FROM user_ability_reports").fetchone()
    if row and row["a"] is not None:
        data["avg_score"] = round(float(row["a"]), 1)
    lv = conn.execute("SELECT level, COUNT(*) c FROM user_ability_reports GROUP BY level").fetchall()
    data["assess_levels"] = {r["level"]: int(r["c"]) for r in lv}
    conn.close()
    return data


@router.get("/users/permissions")
def list_user_permissions(request: Request):
    """列出全部用户 + 权限/试用/押金状态，供后台「用户权限/试用」管理。

    只读视角：combine 访问记录与押金状态，展示派生权限（不在此处落库试用起点，
    避免后台浏览触发副作用；status 端 /api/access 才会正式确认起点）。
    """
    verify_token(request)
    from database import get_deposit, get_user_access
    from services.access_service import compute_access, _parse_dt

    users = query_all("users")
    result = []
    for u in users:
        uid = u["id"]
        acc = get_user_access(uid)
        dep = get_deposit(uid)
        started = _parse_dt(acc["trial_started_at"]) if acc else None
        deposit_paid = bool(dep and dep.get("status") in ("active", "unlocked"))
        state = compute_access(datetime.now(), started, deposit_paid)
        override = (acc or {}).get("admin_override", "") if acc else ""
        # 后台人工覆盖：与 services.access_service.resolve_access 同一套规则
        if override == "lock":
            state["access_granted"] = False
        elif override == "unlock":
            state["access_granted"] = True
            state["in_trial"] = True
        state["admin_override"] = override
        result.append({
            "id": uid,
            "openid": u.get("openid", ""),
            "nickname": u.get("nickname", ""),
            "created_at": u.get("created_at", ""),
            "trial_started_at": (acc or {}).get("trial_started_at", "") if acc else "",
            "deposit_status": (dep or {}).get("status", "none") if dep else "none",
            "access": state,
        })
    return result


class PermissionUpdate(BaseModel):
    """后台对单个用户权限的修改指令。"""
    action: str  # reset_trial | extend_trial | clear_trial | set_override | clear_override
    days: int = 0
    override: str = ""  # action=set_override 时：'lock' | 'unlock'


@router.post("/users/{user_id}/permission")
def update_user_permission(user_id: int, body: PermissionUpdate, request: Request):
    """后台手动调整用户试用/权限（替代直接改库）。

    - reset_trial：把试用期起点重置为服务端当前时间（重新开始 5 天试用）；
    - extend_trial：把试用期起点前移 days 天（延长试用窗口）；
    - clear_trial：清空试用起点（下次请求由服务端重新确认起点）；
    - set_override：设置人工覆盖（'lock' 强制锁定 / 'unlock' 强制解锁）；
    - clear_override：清除人工覆盖，恢复按规则派生。
    """
    verify_token(request)
    from datetime import timedelta
    from database import get_user, get_user_access, upsert_user_access

    if get_user(user_id) is None:
        raise HTTPException(404, "User not found")

    acc = get_user_access(user_id)
    current_start = (acc or {}).get("trial_started_at", "") if acc else ""
    now = datetime.now().replace(microsecond=0)

    if body.action == "reset_trial":
        upsert_user_access(user_id, {"trial_started_at": now.strftime("%Y-%m-%d %H:%M:%S")})
    elif body.action == "extend_trial":
        if current_start:
            base = datetime.strptime(current_start, "%Y-%m-%d %H:%M:%S")
        else:
            base = now
        new_start = (base - timedelta(days=body.days)).strftime("%Y-%m-%d %H:%M:%S")
        upsert_user_access(user_id, {"trial_started_at": new_start})
    elif body.action == "clear_trial":
        upsert_user_access(user_id, {"trial_started_at": ""})
    elif body.action == "set_override":
        if body.override not in ("lock", "unlock"):
            raise HTTPException(400, "override 必须是 lock 或 unlock")
        upsert_user_access(user_id, {"admin_override": body.override})
    elif body.action == "clear_override":
        upsert_user_access(user_id, {"admin_override": ""})
    else:
        raise HTTPException(400, f"未知 action: {body.action}")

    return {"message": f"permission updated: {body.action}"}


@router.get("/{table}")
def read_all(table: str, request: Request):
    """Read all rows from a table."""
    verify_token(request)
    if table not in TABLE_CONFIG:
        raise HTTPException(404, f"Unknown table: {table}")
    return query_all(table)


@router.get("/{table}/{item_id}")
def read_one(table: str, item_id, request: Request):
    """Read a single row."""
    verify_token(request)
    if table not in TABLE_CONFIG:
        raise HTTPException(404, f"Unknown table: {table}")
    row = query_one(table, item_id)
    if not row:
        raise HTTPException(404, f"Item not found in {table}")
    return row


def _invalidate_cache(table: str) -> None:
    """后台修改数据后使相关只读缓存失效。"""
    if table == "courses":
        cache_clear()  # 课程列表 + 各 course:{id} 详情一并失效
    elif table == "directions":
        cache_clear("content:directions")
    elif table == "banners":
        cache_clear("content:banners")


@router.post("/{table}")
def create_item(table: str, data: dict, request: Request):
    """Create a new item."""
    verify_token(request)
    if table not in TABLE_CONFIG:
        raise HTTPException(404, f"Unknown table: {table}")
    # Filter to allowed fields
    allowed = TABLE_CONFIG[table]["fields"]
    clean = {k: v for k, v in data.items() if k in allowed}
    if not clean:
        raise HTTPException(400, "No valid fields provided")
    # Handle JSON fields
    for k, v in clean.items():
        if isinstance(v, (list, dict)):
            clean[k] = json.dumps(v, ensure_ascii=False)
    item_id = insert_row(table, clean)
    _invalidate_cache(table)
    return {"id": item_id, "message": f"Created in {table}"}


@router.put("/{table}/{item_id}")
def update_item(table: str, item_id, data: dict, request: Request):
    """Update an existing item."""
    verify_token(request)
    if table not in TABLE_CONFIG:
        raise HTTPException(404, f"Unknown table: {table}")
    allowed = TABLE_CONFIG[table]["fields"]
    clean = {k: v for k, v in data.items() if k in allowed}
    if not clean:
        raise HTTPException(400, "No valid fields provided")
    for k, v in clean.items():
        if isinstance(v, (list, dict)):
            clean[k] = json.dumps(v, ensure_ascii=False)
    ok = update_row(table, item_id, clean)
    if not ok:
        raise HTTPException(404, f"Item not found in {table}")
    _invalidate_cache(table)
    return {"message": f"Updated in {table}"}


@router.delete("/{table}/{item_id}")
def delete_item(table: str, item_id, request: Request):
    """Delete an item."""
    verify_token(request)
    if table not in TABLE_CONFIG:
        raise HTTPException(404, f"Unknown table: {table}")
    ok = delete_row(table, item_id)
    if not ok:
        raise HTTPException(404, f"Item not found in {table}")
    _invalidate_cache(table)
    return {"message": f"Deleted from {table}"}
