"""Videos API router."""

import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from models.schemas import VideoItem
from auth_utils import get_optional_user
from database import record_user_video, safe_load_json

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/videos", tags=["videos"])


def _load_videos() -> list[VideoItem]:
    data = safe_load_json(PROCESSED_DIR / "videos.json", [])
    return [VideoItem(**v) for v in data]


def _load_watched() -> dict[str, dict]:
    """Load watched videos: {video_id: {at, minutes}}. Empty dict if none.

    Supports legacy formats:
    - list ["video-1", ...] -> {"video-1": {"at": ""}}
    - dict {"video-1": "2026-..."} -> {"video-1": {"at": "2026-..."}}
    """
    data = safe_load_json(PROCESSED_DIR / "video_progress.json", {})
    if not isinstance(data, dict):
        return {}
    watched = data.get("watched", {})
    if isinstance(watched, list):
        return {vid: {"at": "", "minutes": 0} for vid in watched}
    if isinstance(watched, dict):
        result = {}
        for vid, val in watched.items():
            if isinstance(val, dict):
                result[vid] = val
            else:
                # 旧格式：值可能是时间字符串
                result[vid] = {"at": val if isinstance(val, str) else "", "minutes": 0}
        return result
    return {}


def _save_watched(watched: dict[str, dict]) -> None:
    path = PROCESSED_DIR / "video_progress.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"watched": watched}, f, ensure_ascii=False, indent=2)


def _mark_completed(videos: list[VideoItem], watched: dict[str, dict]) -> list[VideoItem]:
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


class CompleteRequest(BaseModel):
    """Mark video as watched, with optional actual watch minutes."""
    minutes: int = 0


@router.post("/{video_id}/complete")
async def complete_video(video_id: str, request: Request, req: CompleteRequest | None = None):
    """Mark a video as watched by the user (persisted), recording timestamp and watch minutes."""
    items = _load_videos()
    if not any(v.id == video_id for v in items):
        raise HTTPException(status_code=404, detail="Video not found")
    watched = _load_watched()
    minutes = (req.minutes if req else 0) or 0
    # 记录看完时间与观看分钟（用于自然日/时长统计）
    watched[video_id] = {
        "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "minutes": minutes,
    }
    _save_watched(watched)
    # 按用户隔离：登录态下同步写入 user_video_progress（供押金三锁计算）
    user = await get_optional_user(request)
    if user:
        record_user_video(user["id"], video_id, minutes)
    return {"video_id": video_id, "watched_count": len(watched), "minutes": minutes}