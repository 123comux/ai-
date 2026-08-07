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
    """Get learning records from real watched videos (video_progress).

    Groups watched videos by date: duration = 观看分钟累计, lessonsCompleted = 该日看完视频数。
    """
    videos = []
    if (PROCESSED_DIR / "videos.json").exists():
        try:
            videos = _load_json("videos.json")
        except Exception:
            videos = []
    if not isinstance(videos, list):
        videos = []

    watched = {}
    if (PROCESSED_DIR / "video_progress.json").exists():
        try:
            progress = _load_json("video_progress.json")
            raw = progress.get("watched", {})
            if isinstance(raw, dict):
                for vid, val in raw.items():
                    if isinstance(val, dict):
                        watched[vid] = val
                    else:
                        watched[vid] = {"at": val if isinstance(val, str) else "", "minutes": 0}
        except Exception:
            watched = {}

    # 按日期聚合：date -> {duration, lessons}
    from datetime import datetime
    day_map: dict[str, dict] = {}
    video_ids = {v.get("id") for v in videos}
    for vid, w in watched.items():
        if vid not in video_ids:
            continue
        at = w.get("at", "") if isinstance(w, dict) else ""
        minutes = (w.get("minutes", 0) or 0) if isinstance(w, dict) else 0
        date = at[:10] if at else ""
        if not date:
            continue
        day_map.setdefault(date, {"duration": 0, "lessons": 0})
        day_map[date]["duration"] += minutes
        day_map[date]["lessons"] += 1

    records = []
    for date in sorted(day_map.keys(), reverse=True):
        d = day_map[date]
        records.append(LearningRecord(
            date=date[5:],  # MM-DD
            duration=d["duration"],
            lessonsCompleted=d["lessons"],
            exercisesDone=0,
        ))
    return records[:30]


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

    # watched: {video_id: {at, minutes}}（兼容旧格式 {video_id: ts}）
    watched = {}
    if (PROCESSED_DIR / "video_progress.json").exists():
        try:
            progress = _load_json("video_progress.json")
            raw = progress.get("watched", {})
            if isinstance(raw, dict):
                for vid, val in raw.items():
                    if isinstance(val, dict):
                        watched[vid] = val
                    else:
                        watched[vid] = {"at": val if isinstance(val, str) else "", "minutes": 0}
            elif isinstance(raw, list):
                watched = {vid: {"at": "", "minutes": 0} for vid in raw}
        except Exception:
            watched = {}

    watched_videos = [v for v in videos if v.get("id") in watched]
    watched_count = len(watched_videos)
    # 总时长 = 实际观看分钟数累计
    total_minutes = sum(
        (w.get("minutes", 0) or 0) if isinstance(w, dict) else 0
        for w in watched.values()
    )

    # 连续学习天数：从今天往前，统计连续有学习行为的自然日
    from datetime import datetime, timedelta
    learning_dates = set()
    for w in watched.values():
        at = w.get("at", "") if isinstance(w, dict) else ""
        if not at:
            continue
        try:
            d = datetime.strptime(at[:10], "%Y-%m-%d").date()
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

    # 完成项目 = 路径中已完成的项目节点 + 项目页完成全部步骤的项目数
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

    # 项目页直接完成的项目（project_progress 中完成步骤数 == 项目总步骤数）
    project_progress = None
    if (PROCESSED_DIR / "project_progress.json").exists():
        try:
            project_progress = _load_json("project_progress.json")
        except Exception:
            project_progress = None
    if isinstance(project_progress, dict):
        projects_data = []
        if (PROCESSED_DIR / "enriched_projects.json").exists():
            try:
                projects_data = _load_json("enriched_projects.json")
            except Exception:
                projects_data = []
        elif (PROCESSED_DIR / "projects.json").exists():
            try:
                projects_data = _load_json("projects.json")
            except Exception:
                projects_data = []
        total_steps = {p.get("id"): len(p.get("steps", []) or []) for p in projects_data if isinstance(p, dict)}
        for pid, done in project_progress.items():
            if total_steps.get(pid, 0) and done >= total_steps[pid]:
                projects_done += 1

    return LearningStats(
        learningDays=streak,
        totalMinutes=total_minutes,
        completedProjects=projects_done,
        completedLessons=watched_count,
    )