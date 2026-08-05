"""Projects API router."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from models.schemas import ProjectItem

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/projects", tags=["projects"])


def _load_projects() -> list[ProjectItem]:
    path = PROCESSED_DIR / "projects.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [ProjectItem(**p) for p in data]


@router.get("", response_model=list[ProjectItem])
async def list_projects(
    difficulty: str = Query(None, description="Filter by difficulty"),
    tech: str = Query(None, description="Filter by tech stack keyword"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all projects."""
    items = _load_projects()
    filtered = items
    if difficulty:
        filtered = [p for p in filtered if p.difficulty.lower() == difficulty.lower()]
    if tech:
        filtered = [p for p in filtered if any(tech.lower() in t.lower() for t in p.tech_stack)]
    return filtered[offset:offset + limit]


@router.get("/topics")
async def project_topics():
    """Get unique project difficulty levels."""
    items = _load_projects()
    topics = sorted(set(p.difficulty for p in items if p.difficulty))
    return {"topics": topics}


@router.get("/{project_id}", response_model=ProjectItem)
async def get_project(project_id: str):
    """Get a single project by ID."""
    items = _load_projects()
    for p in items:
        if p.id == project_id:
            return p
    raise HTTPException(status_code=404, detail="Project not found")