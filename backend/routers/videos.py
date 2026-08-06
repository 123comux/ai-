"""Videos API router."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from models.schemas import VideoItem

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/videos", tags=["videos"])


def _load_videos() -> list[VideoItem]:
    path = PROCESSED_DIR / "videos.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [VideoItem(**v) for v in data]


@router.get("", response_model=list[VideoItem])
async def list_videos(
    course_id: str = Query(None, description="Filter by course ID"),
):
    """List all videos, optionally filtered by course_id."""
    items = _load_videos()
    if course_id:
        items = [v for v in items if v.courseId == course_id]
    return items


@router.get("/{video_id}", response_model=VideoItem)
async def get_video(video_id: str):
    """Get a single video by ID."""
    items = _load_videos()
    for v in items:
        if v.id == video_id:
            return v
    raise HTTPException(status_code=404, detail="Video not found")


@router.get("/course/{course_id}", response_model=list[VideoItem])
async def get_course_videos(course_id: str):
    """Get all videos for a course."""
    items = _load_videos()
    result = [v for v in items if v.courseId == course_id]
    return result