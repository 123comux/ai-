"""Courses API router - reads from CMS database."""
import json
from fastapi import APIRouter, HTTPException, Query

from database import query_all, query_one, parse_json_field

router = APIRouter(prefix="/api/courses", tags=["courses"])


def _normalize_chapters(raw: list) -> list:
    """Normalize chapter structure: alias content_summary -> summary, ensure sections array,
    map to expected frontend schema (title, summary, duration_minutes, sections, video_bv)."""
    out = []
    for ch in (raw or []):
        sections_raw = ch.get("sections") or ch.get("sub_chapters") or ch.get("subsections") or []
        sections_norm = []
        for i, sec in enumerate(sections_raw):
            sections_norm.append({
                "id": sec.get("id") or f"{ch.get('id', 'ch')}-sec-{i+1}",
                "title": sec.get("title") or sec.get("name") or f"第{i+1}小节",
                "content": sec.get("content") or sec.get("description") or sec.get("summary") or "",
                "knowledge_points": sec.get("knowledge_points") or sec.get("keyPoints") or sec.get("key_points") or [],
                "case": sec.get("case") or sec.get("case_study") or sec.get("example") or "",
            })
        out.append({
            "id": ch.get("id") or "",
            "title": ch.get("title") or ch.get("name") or "",
            "summary": ch.get("summary") or ch.get("content_summary") or ch.get("description") or "",
            "duration_minutes": ch.get("duration_minutes") or ch.get("duration") or 0,
            "video_bv": ch.get("video_bv") or ch.get("bvid") or "",
            "video_page": ch.get("video_page") or ch.get("page") or 1,
            "sections": sections_norm,
        })
    return out


def _db_to_course(row: dict) -> dict:
    """Convert database row to course dict."""
    chapters_raw = parse_json_field(row.get("chapters", "[]"))
    chapters = _normalize_chapters(chapters_raw)
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