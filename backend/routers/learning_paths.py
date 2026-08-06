"""Learning paths API router.

Paths can be returned either from the static enriched data or generated
dynamically from the user's ability report recommendation direction.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from models.schemas import LearningPathItem, LearningPathNode

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/learning-paths", tags=["learning-paths"])


def _load_paths() -> list[LearningPathItem]:
    # Try enriched data first, fall back to original
    path = PROCESSED_DIR / "enriched_learning_paths.json"
    if not path.exists():
        path = PROCESSED_DIR / "learning_paths.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [LearningPathItem(**p) for p in data]


def _load_json(filename: str):
    path = PROCESSED_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# direction family -> (course ids in order, project ids in order)
_DIRECTION_PLAN = {
    "大模型应用开发": (
        ["course-5", "course-0", "course-2"],
        ["project-8", "project-2", "project-5"],
    ),
    "机器学习工程师": (
        ["course-5", "course-4", "course-0"],
        ["project-3", "project-7"],
    ),
    "深度学习工程师": (
        ["course-5", "course-0", "course-1"],
        ["project-0", "project-6"],
    ),
    "数据科学家": (
        ["course-5", "course-4", "course-0"],
        ["project-9", "project-3"],
    ),
    "AI 应用开发": (
        ["course-5", "course-0", "course-2"],
        ["project-8", "project-2"],
    ),
}

# fallback plan when direction is not in the map above
_DEFAULT_PLAN = (
    ["course-5", "course-0", "course-1"],
    ["project-3", "project-8"],
)


def _build_path(direction: str) -> LearningPathItem:
    """Build a LearningPathItem for a recommended direction, grounded in real courses/projects."""
    courses, projects = _DIRECTION_PLAN.get(direction, _DEFAULT_PLAN)

    course_titles = {
        "course-5": "Python 编程基础",
        "course-0": "机器学习入门",
        "course-1": "深度学习与神经网络",
        "course-2": "大模型应用开发",
        "course-4": "数据分析与可视化",
    }
    project_titles = {
        "project-8": "AI Chatbot 对话机器人",
        "project-2": "RAG 问答系统",
        "project-5": "LLM 微调实战",
        "project-3": "客户流失预测",
        "project-7": "推荐系统实战",
        "project-0": "图像分类 CNN 实战",
        "project-6": "时序预测实战",
        "project-9": "数据管道 ETL 实战",
    }

    nodes: list[LearningPathNode] = []
    for i, cid in enumerate(courses):
        nodes.append(
            LearningPathNode(
                id=f"gen-{direction}-course-{i}",
                title=course_titles.get(cid, cid),
                type="course",
                items=[cid],
                status="current" if i == 0 else "locked",
                progress=0,
                courseId=cid,
            )
        )
    for j, pid in enumerate(projects):
        nodes.append(
            LearningPathNode(
                id=f"gen-{direction}-project-{j}",
                title=project_titles.get(pid, pid),
                type="project",
                items=[pid],
                status="locked",
                progress=0,
                courseId=None,
            )
        )

    return LearningPathItem(
        id=f"path-{direction}",
        direction=direction,
        title=f"{direction}学习路径",
        nodes=nodes,
        totalWeeks=len(nodes),
        currentWeek=1,
        createdAt="2026-08-07",
    )


def _recommended_direction() -> str | None:
    """Read the recommended direction from the persisted ability report."""
    report = _load_json("ability_report.json")
    if report:
        return report.get("recommendedDirection")
    return None


@router.get("", response_model=list[LearningPathItem])
async def list_paths(direction: str | None = Query(None, description="Filter / generate path for a direction")):
    """List learning paths.

    - With ?direction=X: return a single path generated for that direction.
    - Without params: return static enriched paths plus (if available) a
      dynamically generated path for the user's recommended direction.
    """
    if direction:
        return [_build_path(direction)]

    paths = _load_paths()
    rec_dir = _recommended_direction()
    if rec_dir and not any(p.direction == rec_dir for p in paths):
        paths.insert(0, _build_path(rec_dir))
    return paths


@router.get("/{path_id}", response_model=LearningPathItem)
async def get_path(path_id: str):
    """Get a single learning path by ID."""
    # Prefer the static set; fall back to generating for a direction-name ID.
    items = _load_paths()
    for p in items:
        if p.id == path_id:
            return p
    if path_id.startswith("path-"):
        direction = path_id[len("path-"):]
        if direction in _DIRECTION_PLAN or direction == "AI 工程师":
            return _build_path(direction)
    raise HTTPException(status_code=404, detail="Learning path not found")
