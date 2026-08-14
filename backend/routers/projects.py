"""Projects API router."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Request

from models.schemas import ProjectItem
from auth_utils import get_optional_user
from database import record_user_project, safe_load_json

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/projects", tags=["projects"])

# 项目按难度从入门到高级排序（项目页默认展示顺序）
_DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}


def _difficulty_sort_key(p: ProjectItem) -> tuple:
    return (_DIFFICULTY_ORDER.get(p.difficulty.lower(), 9), p.id)


def _load_projects() -> list[ProjectItem]:
    # Try enriched data first, fall back to original
    path = PROCESSED_DIR / "enriched_projects.json"
    if not path.exists():
        path = PROCESSED_DIR / "projects.json"
    data = safe_load_json(path, [])
    return [ProjectItem(**p) for p in data]


def _load_progress() -> dict[str, int]:
    """Load project progress: {project_id: completed_steps_count}."""
    data = safe_load_json(PROCESSED_DIR / "project_progress.json", {})
    return data if isinstance(data, dict) else {}


def _save_progress(progress: dict[str, int]) -> None:
    path = PROCESSED_DIR / "project_progress.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


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


@router.get("", response_model=list[ProjectItem])
async def list_projects(
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
    progress = _load_progress()
    result = [_apply_progress(p, progress.get(p.id, 0)) for p in filtered]
    return result[offset:offset + limit]


@router.get("/topics")
async def project_topics():
    """Get unique project difficulty levels."""
    items = _load_projects()
    topics = sorted(set(p.difficulty for p in items if p.difficulty))
    return {"topics": topics}


@router.get("/{project_id}", response_model=ProjectItem)
async def get_project(project_id: str):
    """Get a single project by ID (with user progress merged)."""
    project = _get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    progress = _load_progress()
    return _apply_progress(project, progress.get(project_id, 0))


@router.post("/{project_id}/advance")
async def advance_project(project_id: str, request: Request):
    """Advance a project by one step (user completes the current step).

    Persists completed-step count in project_progress.json.
    When authenticated, also records per-user progress (data isolation).
    """
    project = _get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    user = await get_optional_user(request)
    progress = _load_progress()
    completed = progress.get(project_id, 0)
    total = len(project.steps)
    if completed >= total:
        if user:
            record_user_project(user["id"], project_id, completed)
        return _apply_progress(project, completed)  # 已完成，幂等返回

    completed += 1
    progress[project_id] = completed
    _save_progress(progress)
    if user:
        record_user_project(user["id"], project_id, completed)
    return _apply_progress(project, completed)