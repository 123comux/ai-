"""Courses API router."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from models.schemas import CourseItem

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/courses", tags=["courses"])


def _load_courses() -> list[CourseItem]:
    path = PROCESSED_DIR / "courses.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [CourseItem(**c) for c in data]


@router.get("", response_model=list[CourseItem])
async def list_courses(
    topic: str = Query(None, description="Filter by topic"),
    difficulty: str = Query(None, description="Filter by difficulty"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all courses."""
    items = _load_courses()
    filtered = items
    if topic:
        filtered = [c for c in filtered if c.topic.lower() == topic.lower()]
    if difficulty:
        filtered = [c for c in filtered if c.difficulty.lower() == difficulty.lower()]
    return filtered[offset:offset + limit]


@router.get("/topics")
async def course_topics():
    """Get unique course topics."""
    items = _load_courses()
    topics = sorted(set(c.topic for c in items if c.topic))
    return {"topics": topics}


@router.get("/{course_id}", response_model=CourseItem)
async def get_course(course_id: str):
    """Get a single course by ID."""
    items = _load_courses()
    for c in items:
        if c.id == course_id:
            return c
    raise HTTPException(status_code=404, detail="Course not found")