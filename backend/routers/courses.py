"""Courses API router - reads from CMS database."""
import json
from fastapi import APIRouter, HTTPException, Query

from database import query_all, query_one, parse_json_field

router = APIRouter(prefix="/api/courses", tags=["courses"])


def _db_to_course(row: dict) -> dict:
    """Convert database row to course dict."""
    chapters = parse_json_field(row.get("chapters", "[]"))
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row.get("description", ""),
        "coverImg": row.get("cover_img", ""),
        "topic": row.get("topic", ""),
        "difficulty": row.get("difficulty", "beginner"),
        "estimated_hours": row.get("estimated_hours", 0),
        "lessons": row.get("lessons", 0),
        "progress": row.get("progress", 0),
        "isFree": bool(row.get("is_free", 1)),
        "price": row.get("price", 0),
        "source": row.get("source", ""),
        "chapters": chapters,
        "category": row.get("topic", ""),
        "duration": row.get("estimated_hours", 0) * 60,
    }


@router.get("")
async def list_courses(
    topic: str = Query(None, description="Filter by topic"),
    difficulty: str = Query(None, description="Filter by difficulty"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all courses from CMS database."""
    rows = query_all("courses", {"is_active": 1})
    courses = [_db_to_course(r) for r in rows]
    if topic:
        courses = [c for c in courses if c["topic"].lower() == topic.lower() or c["category"].lower() == topic.lower()]
    if difficulty:
        courses = [c for c in courses if c["difficulty"].lower() == difficulty.lower()]
    return courses[offset:offset + limit]


@router.get("/topics")
async def course_topics():
    """Get unique course topics."""
    rows = query_all("courses", {"is_active": 1})
    topics = sorted(set(r["topic"] for r in rows if r["topic"]))
    return {"topics": topics}


@router.get("/{course_id}")
async def get_course(course_id: str):
    """Get a single course by ID."""
    row = query_one("courses", course_id)
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    return _db_to_course(row)