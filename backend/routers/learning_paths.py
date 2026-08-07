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
# 每个方向差异化选课，让用户能切换不同学习路径
_DIRECTION_PLAN = {
    "大模型应用开发": (
        ["course-5", "course-2", "course-0", "course-1", "course-3"],
        ["project-8", "project-2", "project-5", "project-1"],
    ),
    "机器学习工程师": (
        ["course-5", "course-0", "course-4", "course-1", "course-3"],
        ["project-3", "project-7", "project-6", "project-2"],
    ),
    "深度学习工程师": (
        ["course-5", "course-1", "course-6", "course-0", "course-3"],
        ["project-0", "project-4", "project-6", "project-1"],
    ),
    "数据科学家": (
        ["course-5", "course-4", "course-0", "course-3", "course-1"],
        ["project-9", "project-3", "project-6", "project-7"],
    ),
    "AI 应用开发": (
        ["course-5", "course-2", "course-3", "course-0", "course-7"],
        ["project-8", "project-2", "project-1", "project-5"],
    ),
    "计算机视觉工程师": (
        ["course-5", "course-6", "course-1", "course-0", "course-3"],
        ["project-4", "project-0", "project-6", "project-2"],
    ),
}

# fallback plan when direction is not in the map above
_DEFAULT_PLAN = (
    ["course-5", "course-0", "course-1"],
    ["project-3", "project-8"],
)


def _course_title(cid: str) -> str:
    """读取课程真实标题（从 enriched_courses 或 courses.json）。"""
    data = _load_json("enriched_courses.json") or _load_json("courses.json") or []
    for c in data:
        if c.get("id") == cid:
            return c.get("title", cid)
    return cid


def _project_title(pid: str) -> str:
    """读取项目真实标题（从 projects.json）。"""
    data = _load_json("projects.json") or []
    for p in data:
        if p.get("id") == pid:
            title = p.get("title", pid)
            # 去掉 "Project: " 前缀，得到中文展示名
            return title.replace("Project: ", "", 1) if title.startswith("Project: ") else title
    return pid


def _build_path(direction: str) -> LearningPathItem:
    """Build a LearningPathItem for a recommended direction, grounded in real courses/projects."""
    courses, projects = _DIRECTION_PLAN.get(direction, _DEFAULT_PLAN)

    nodes: list[LearningPathNode] = []
    for i, cid in enumerate(courses):
        nodes.append(
            LearningPathNode(
                id=f"gen-{direction}-course-{i}",
                title=_course_title(cid),
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
                title=_project_title(pid),
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


# ===== 用户进度持久化 =====
# 用一份 path_progress.json 记录每个路径中已完成的节点，运行时数据（gitignore）。
# 静态路径 JSON 里的 baked 状态 + 用户完成记录合并后，得到最终展示状态。


def _load_progress() -> dict[str, list[str]]:
    data = _load_json("path_progress.json")
    return data if isinstance(data, dict) else {}


def _save_progress(progress: dict[str, list[str]]) -> None:
    path = PROCESSED_DIR / "path_progress.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def _apply_user_progress(path: LearningPathItem, completed: set[str]) -> LearningPathItem:
    """Merge user-completed node ids into a path's node statuses.

    Recomputes a clean chain: completed nodes stay completed, the first
    non-completed node becomes current, everything after stays locked.
    """
    all_completed = {n.id for n in path.nodes if n.status == "completed"} | completed
    current_set = False
    for node in path.nodes:
        if node.id in all_completed:
            node.status = "completed"
            node.progress = 100
        elif not current_set:
            node.status = "current"
            current_set = True
        else:
            node.status = "locked"
            node.progress = 0
    return path


def _get_base_path(path_id: str) -> LearningPathItem | None:
    """Return the un-merged base path (static or generated) by id, if it exists."""
    for p in _load_paths():
        if p.id == path_id:
            return p
    if path_id.startswith("path-"):
        direction = path_id[len("path-"):]
        if direction in _DIRECTION_PLAN or direction == "AI 工程师":
            return _build_path(direction)
    return None


@router.get("", response_model=list[LearningPathItem])
async def list_paths(direction: str | None = Query(None, description="Filter / generate path for a direction")):
    """List learning paths.

    - With ?direction=X: return a single path generated for that direction.
    - Without params: return all direction plans (each with its own course/project set),
      so the user can browse and switch between learning directions.
    """
    progress = _load_progress()

    if direction:
        path = _build_path(direction)
        return [_apply_user_progress(path, set(progress.get(path.id, [])))]

    paths = []
    # 推荐方向排最前，其余方向按顺序列出
    rec_dir = _recommended_direction()
    directions = list(_DIRECTION_PLAN.keys())
    if rec_dir and rec_dir in directions:
        directions.remove(rec_dir)
        directions.insert(0, rec_dir)
    for d in directions:
        path = _build_path(d)
        paths.append(_apply_user_progress(path, set(progress.get(path.id, []))))
    return paths


@router.post("/{path_id}/nodes/{node_id}/complete")
async def complete_node(path_id: str, node_id: str):
    """Mark a node as completed; the next locked node becomes current.

    Persists completion in path_progress.json so it survives restarts.
    For course nodes, the course's videos must all be watched first.
    """
    base = _get_base_path(path_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    node = next((n for n in base.nodes if n.id == node_id), None)
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found in path")

    # 课程节点：先校验该课程全部视频已看完
    if node.type == "course" and node.courseId:
        from routers.videos import _load_videos, _load_watched
        course_videos = [v for v in _load_videos() if v.courseId == node.courseId]
        if course_videos:
            watched = _load_watched()
            un_watched = [v for v in course_videos if v.id not in watched]
            if un_watched:
                raise HTTPException(
                    status_code=400,
                    detail=f"还有 {len(un_watched)}/{len(course_videos)} 个视频未看完：{', '.join(v.id for v in un_watched)}",
                )

    progress = _load_progress()
    completed = set(progress.get(path_id, []))
    completed.add(node_id)
    progress[path_id] = sorted(completed)
    _save_progress(progress)

    return _apply_user_progress(base, completed)


@router.get("/{path_id}", response_model=LearningPathItem)
async def get_path(path_id: str):
    """Get a single learning path by ID."""
    base = _get_base_path(path_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    progress = _load_progress()
    return _apply_user_progress(base, set(progress.get(path_id, [])))
