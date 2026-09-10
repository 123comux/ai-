"""Videos API router - reads from CMS database (数据源统一：video 表驱动，后台可即时生效)."""

import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from models.schemas import VideoItem, VideoQuality
from auth_utils import get_optional_user
from fsx import safe_write_json
from database import (
    record_user_video,
    get_user_watched_video_ids,
    safe_load_json,
    query_all,
    parse_json_field,
)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/videos", tags=["videos"])


def _db_to_video(row: dict) -> VideoItem:
    """数据库行 → VideoItem（snake_case 列 → camelCase 前端字段）。"""
    quality_dict = parse_json_field(row.get("quality", "{}"), {}) or {}
    quality = VideoQuality(**quality_dict) if quality_dict else None
    return VideoItem(
        id=row["id"],
        title=row["title"],
        subtitle=row.get("subtitle") or None,
        description=row.get("description", ""),
        coreInfo=parse_json_field(row.get("core_info", "[]"), []) or None,
        narrative=row.get("narrative") or None,
        visual=row.get("visual") or None,
        quality=quality,
        url=row.get("url", ""),
        coverUrl=row.get("cover_url", ""),
        duration=row.get("duration", 0),
        chapter=row.get("chapter", ""),
        courseId=row.get("course_id", ""),
    )


def _load_videos() -> list[VideoItem]:
    """从 videos 表读取启用视频（后台管理即可即时生效）。"""
    rows = query_all("videos", {"is_active": 1})
    return [_db_to_video(r) for r in rows]


def _load_watched(user_id: int | None = None) -> dict[str, dict]:
    """读取某用户的"已看完"视频集合：{video_id: {at, minutes}}。

    - 登录用户：按 user_video_progress 表 **per-user** 读取（进度统一 DB，用户间互不影响）；
    - 匿名（未登录）：回退读取全局 video_progress.json（旧版遗留格式）。
    """
    if user_id is not None:
        return {vid: {"at": "", "minutes": 0} for vid in get_user_watched_video_ids(user_id)}
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
    # 只读环境（Vercel）自动跳过：观看记录真身在 user_video_progress 表
    safe_write_json(PROCESSED_DIR / "video_progress.json", {"watched": watched})


def _mark_completed(videos: list[VideoItem], watched: dict[str, dict]) -> list[VideoItem]:
    for v in videos:
        v.completed = v.id in watched
    return videos


@router.get("", response_model=list[VideoItem])
async def list_videos(
    request: Request,
    course_id: str = Query(None, description="Filter by course ID"),
):
    """List all videos, optionally filtered by course_id. 已完成状态按用户隔离。"""
    items = _load_videos()
    if course_id:
        items = [v for v in items if v.courseId == course_id]
    user = await get_optional_user(request)
    watched = _load_watched(user["id"] if user else None)
    return _mark_completed(items, watched)


@router.get("/{video_id}", response_model=VideoItem)
async def get_video(video_id: str, request: Request):
    """Get a single video by ID."""
    items = _load_videos()
    for v in items:
        if v.id == video_id:
            user = await get_optional_user(request)
            watched = _load_watched(user["id"] if user else None)
            return _mark_completed([v], watched)[0]
    raise HTTPException(status_code=404, detail="Video not found")


@router.get("/course/{course_id}", response_model=list[VideoItem])
async def get_course_videos(course_id: str, request: Request):
    """Get all videos for a course, with watched flags (per-user)."""
    items = _load_videos()
    result = [v for v in items if v.courseId == course_id]
    user = await get_optional_user(request)
    watched = _load_watched(user["id"] if user else None)
    return _mark_completed(result, watched)


class CompleteRequest(BaseModel):
    """Mark video as watched, with optional actual watch minutes."""
    minutes: int = 0


@router.post("/{video_id}/complete")
async def complete_video(video_id: str, request: Request, req: CompleteRequest | None = None):
    """Mark a video as watched by the user (persisted), recording timestamp and watch minutes.

    - 登录用户：只写入 user_video_progress 表（per-user），不污染全局 video_progress.json；
    - 匿名：回退写入全局文件（旧版）。
    """
    items = _load_videos()
    if not any(v.id == video_id for v in items):
        raise HTTPException(status_code=404, detail="Video not found")
    minutes = (req.minutes if req else 0) or 0
    user = await get_optional_user(request)
    if user:
        record_user_video(user["id"], video_id, minutes)
        watched_count = len(get_user_watched_video_ids(user["id"]))
    else:
        watched = _load_watched()
        watched[video_id] = {
            "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "minutes": minutes,
        }
        _save_watched(watched)
        watched_count = len(watched)
    return {"video_id": video_id, "watched_count": watched_count, "minutes": minutes}