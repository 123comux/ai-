"""Videos API router."""

import json
from datetime import datetime
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


def _load_watched() -> dict[str, str]:
    """Load watched videos: {video_id: watched_at_iso}. Empty dict if none."""
    path = PROCESSED_DIR / "video_progress.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    watched = data.get("watched", {})
    if isinstance(watched, list):
        # 旧格式兼容：["video-1", ...] -> {"video-1": ""}
        return {vid: "" for vid in watched}
    return watched if isinstance(watched, dict) else {}


def _save_watched(watched: dict[str, str]) -> None:
    path = PROCESSED_DIR / "video_progress.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"watched": watched}, f, ensure_ascii=False, indent=2)


def _mark_completed(videos: list[VideoItem], watched: dict[str, str]) -> list[VideoItem]:
    for v in videos:
        v.completed = v.id in watched
    return videos


@router.get("", response_model=list[VideoItem])
async def list_videos(
    course_id: str = Query(None, description="Filter by course ID"),
):
    """List all videos, optionally filtered by course_id."""
    items = _load_videos()
    if course_id:
        items = [v for v in items if v.courseId == course_id]
    watched = _load_watched()
    return _mark_completed(items, watched)


@router.get("/{video_id}", response_model=VideoItem)
async def get_video(video_id: str):
    """Get a single video by ID."""
    items = _load_videos()
    for v in items:
        if v.id == video_id:
            watched = _load_watched()
            return _mark_completed([v], watched)[0]
    raise HTTPException(status_code=404, detail="Video not found")


@router.get("/course/{course_id}", response_model=list[VideoItem])
async def get_course_videos(course_id: str):
    """Get all videos for a course, with watched flags."""
    items = _load_videos()
    result = [v for v in items if v.courseId == course_id]
    watched = _load_watched()
    return _mark_completed(result, watched)


@router.post("/{video_id}/complete")
async def complete_video(video_id: str):
    """Mark a video as watched by the user (persisted), recording the timestamp."""
    items = _load_videos()
    if not any(v.id == video_id for v in items):
        raise HTTPException(status_code=404, detail="Video not found")
    watched = _load_watched()
    # 记录看完时间（自然日统计需要）
    watched[video_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _save_watched(watched)
    return {"video_id": video_id, "watched_count": len(watched)}