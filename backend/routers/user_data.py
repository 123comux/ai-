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
    """Get learning statistics, computed dynamically from runtime progress data.

    - learningDays: 学习记录天数
    - totalHours: 学习总时长（分钟转小时）
    - completedLessons: 学习记录累计完成课程数
    - completedProjects: 各学习路径中已完成的项目节点数（实时）
    """
    records = _load_json("learning_records.json") if (PROCESSED_DIR / "learning_records.json").exists() else []
    if not isinstance(records, list):
        records = []

    days = len(records)
    total_minutes = sum(r.get("duration", 0) for r in records if isinstance(r, dict))
    lessons = sum(r.get("lessonsCompleted", 0) for r in records if isinstance(r, dict))

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
        learningDays=days,
        totalHours=round(total_minutes / 60),
        completedProjects=projects_done,
        completedLessons=lessons,
    )