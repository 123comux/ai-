"""Projects API router - reads from CMS database (数据源统一：projects 表驱动，后台可即时生效)."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Request

from models.schemas import ProjectItem
from auth_utils import get_optional_user
from fsx import safe_write_json
from database import (
    record_user_project,
    get_user_project_progress,
    query_all,
    parse_json_field,
    safe_load_json,
)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/projects", tags=["projects"])

# 项目按难度从入门到高级排序（项目页默认展示顺序）
_DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}


def _difficulty_sort_key(p: ProjectItem) -> tuple:
    return (_DIFFICULTY_ORDER.get(p.difficulty.lower(), 9), p.id)


def _db_to_project(row: dict) -> ProjectItem:
    """数据库行 → ProjectItem（snake_case 列 → 前端字段，含分步实践指南 steps）。"""
    return ProjectItem(
        id=row["id"],
        title=row["title"],
        description=row.get("description", ""),
        tech_stack=parse_json_field(row.get("tech_stack", "[]"), []),
        difficulty=row.get("difficulty", "beginner"),
        estimated_hours=row.get("estimated_hours", 0),
        topics_covered=parse_json_field(row.get("topics_covered", "[]"), []),
        source=row.get("source", ""),
        coverImg=row.get("cover_img", ""),
        stepCount=row.get("step_count", 0),
        status=row.get("status", "available"),
        progress=row.get("progress", 0),
        isFree=bool(row.get("is_free", 1)),
        price=row.get("price", 0),
        steps=parse_json_field(row.get("steps", "[]"), []),
    )


def _load_projects() -> list[ProjectItem]:
    """从 projects 表读取启用项目（后台管理即可即时生效）。"""
    rows = query_all("projects", {"is_active": 1})
    return [_db_to_project(r) for r in rows]


def _load_progress() -> dict[str, int]:
    """Load project progress: {project_id: completed_steps_count}."""
    data = safe_load_json(PROCESSED_DIR / "project_progress.json", {})
    return data if isinstance(data, dict) else {}


def _save_progress(progress: dict[str, int]) -> None:
    # 只读环境（Vercel）自动跳过：进度真身在 user_project_progress 表
    safe_write_json(PROCESSED_DIR / "project_progress.json", progress)


def _apply_progress(project: ProjectItem, completed: int) -> ProjectItem:
    """Merge persisted progress into a project: set progress %, first unfinished step = current."""
    total = len(project.steps)
    project.progress = round(completed / total * 100) if total else 0
    if total == 0:
        return project
    for i, step in enumerate(project.steps):
        if i < completed:
            step["status"] = "completed"
        elif i == completed:
            step["status"] = "current"
        else:
            step["status"] = "pending"
    project.status = "completed" if completed >= total else "in_progress"
    return project


def _get_project(project_id: str) -> ProjectItem | None:
    for p in _load_projects():
        if p.id == project_id:
            return p
    return None


def _progress_for(user_id: int | None) -> dict[str, int]:
    """登录用户以 DB 进度为准（数据隔离），匿名用户回退全局文件进度。"""
    if user_id is not None:
        return get_user_project_progress(user_id)
    return _load_progress()


@router.get("", response_model=list[ProjectItem])
async def list_projects(
    request: Request,
    difficulty: str = Query(None, description="Filter by difficulty"),
    tech: str = Query(None, description="Filter by tech stack keyword"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all projects (with user progress merged)."""
    items = _load_projects()
    filtered = items
    if difficulty:
        filtered = [p for p in filtered if p.difficulty.lower() == difficulty.lower()]
    if tech:
        filtered = [p for p in filtered if any(tech.lower() in t.lower() for t in p.tech_stack)]
    filtered = sorted(filtered, key=_difficulty_sort_key)
    user = await get_optional_user(request)
    progress = _progress_for(user["id"] if user else None)
    result = [_apply_progress(p, progress.get(p.id, 0)) for p in filtered]
    return result[offset:offset + limit]


@router.get("/topics")
async def project_topics():
    """Get unique project difficulty levels."""
    items = _load_projects()
    topics = sorted(set(p.difficulty for p in items if p.difficulty))
    return {"topics": topics}


@router.get("/{project_id}", response_model=ProjectItem)
async def get_project(project_id: str, request: Request):
    """Get a single project by ID (with user progress merged)."""
    project = _get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    user = await get_optional_user(request)
    progress = _progress_for(user["id"] if user else None)
    return _apply_progress(project, progress.get(project_id, 0))


@router.post("/{project_id}/advance")
async def advance_project(project_id: str, request: Request):
    """Advance a project by one step (user completes the current step).

    登录用户进度写入 user_project_progress（DB，数据隔离）；
    匿名用户回退全局 project_progress.json。
    """
    project = _get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    user = await get_optional_user(request)
    total = len(project.steps)

    if user:
        # 登录用户：DB 为准，读写均走 user_project_progress
        completed = get_user_project_progress(user["id"]).get(project_id, 0)
        if completed < total:
            completed += 1
            record_user_project(user["id"], project_id, completed)
        return _apply_progress(project, completed)

    # 匿名用户：全局文件进度
    progress = _load_progress()
    completed = progress.get(project_id, 0)
    if completed < total:
        completed += 1
        progress[project_id] = completed
        _save_progress(progress)
    return _apply_progress(project, completed)