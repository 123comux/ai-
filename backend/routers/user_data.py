"""User data API router."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from models.schemas import AbilityReport, LearningRecord, JobMatchingResult, LearningStats

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/user", tags=["user-data"])


def _load_json(filename: str):
    path = PROCESSED_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Data file not found: {filename}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/ability-report", response_model=AbilityReport)
async def get_ability_report():
    """Get user ability report."""
    data = _load_json("ability_report.json")
    return AbilityReport(**data)


@router.get("/learning-records", response_model=list[LearningRecord])
async def get_learning_records():
    """Get learning records list."""
    data = _load_json("learning_records.json")
    return [LearningRecord(**r) for r in data]


@router.get("/job-matching", response_model=JobMatchingResult)
async def get_job_matching():
    """Get job matching result."""
    data = _load_json("job_matching.json")
    return JobMatchingResult(**data)


@router.get("/learning-stats", response_model=LearningStats)
async def get_learning_stats():
    """Get learning statistics from real user progress (video_progress).

    - learningDays: 连续学习天数（从今天往前，连续有学习行为的自然日数）
    - totalHours: 已看完视频的时长总和（秒转小时）
    - completedLessons: 已看完视频数
    - completedProjects: 各学习路径中已完成的项目节点数（实时）
    """
    videos = []
    if (PROCESSED_DIR / "videos.json").exists():
        try:
            videos = _load_json("videos.json")
        except Exception:
            videos = []
    if not isinstance(videos, list):
        videos = []

    # watched: {video_id: watched_at_str}
    watched = {}
    if (PROCESSED_DIR / "video_progress.json").exists():
        try:
            progress = _load_json("video_progress.json")
            raw = progress.get("watched", {})
            if isinstance(raw, dict):
                watched = raw
            elif isinstance(raw, list):
                watched = {vid: "" for vid in raw}
        except Exception:
            watched = {}

    watched_videos = [v for v in videos if v.get("id") in watched]
    watched_count = len(watched_videos)
    total_seconds = sum(v.get("duration", 0) for v in watched_videos)

    # 连续学习天数：从今天往前，统计连续有学习行为的自然日
    from datetime import datetime, timedelta
    learning_dates = set()
    for ts in watched.values():
        if not ts:
            continue
        try:
            d = datetime.strptime(ts[:10], "%Y-%m-%d").date()
            learning_dates.add(d)
        except ValueError:
            continue

    streak = 0
    if learning_dates:
        today = datetime.now().date()
        cur = today
        # 今天若还没有学习行为，从昨天开始算（保持 streak 展示，不因今天未学就清零）
        if cur not in learning_dates:
            cur -= timedelta(days=1)
        while cur in learning_dates:
            streak += 1
            cur -= timedelta(days=1)

    # 完成项目：path_progress 中已完成的项目节点（type=project）数
    projects_done = 0
    path_progress = None
    if (PROCESSED_DIR / "path_progress.json").exists():
        try:
            path_progress = _load_json("path_progress.json")
        except Exception:
            path_progress = None
    if isinstance(path_progress, dict):
        for path_id, node_ids in path_progress.items():
            if not isinstance(node_ids, list):
                continue
            for nid in node_ids:
                if "-project-" in nid:
                    projects_done += 1

    return LearningStats(
        learningDays=streak,
        totalHours=round(total_seconds / 3600),
        completedProjects=projects_done,
        completedLessons=watched_count,
    )