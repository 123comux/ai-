"""Learning paths API router.

Paths can be returned either from the static enriched data or generated
dynamically from the user's ability report recommendation direction.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Request

from models.schemas import LearningPathItem, LearningPathNode
from auth_utils import get_optional_user
from database import (
    record_user_path_node,
    safe_load_json,
    query_one,
    parse_json_field,
    get_user_completed_chapter_ids,
)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/learning-paths", tags=["learning-paths"])


def _load_paths() -> list[LearningPathItem]:
    # Try enriched data first, fall back to original
    path = PROCESSED_DIR / "enriched_learning_paths.json"
    if not path.exists():
        path = PROCESSED_DIR / "learning_paths.json"
    data = safe_load_json(path, [])
    return [LearningPathItem(**p) for p in data]


def _load_json(filename: str):
    return safe_load_json(PROCESSED_DIR / filename, None)


# direction family -> (course ids in order, project ids in order)
# 每个方向差异化选课，让用户能切换不同学习路径。
# 课程/项目均取当前种子数据中的真实 id（2026 七阶段课程体系，旧 stage-N/course-N 已不再存在）。
# 所有方向共享「大模型基础 + Agent 概念」打底，再按方向追加差异化技术模块。
_DIRECTION_PLAN = {
    "大模型应用开发": (
        ["s1-llm-basics", "s1-prompt", "s1-api-dev", "s1-ollama", "s2-agent-core", "s3-rag", "s3-langchain", "s6-rag-project"],
        ["project-3", "project-0", "project-4"],
    ),
    "机器学习工程师": (
        ["s1-llm-basics", "s1-api-dev", "s1-ollama", "s2-agent-core", "s2-agent-arch", "s3-rag", "s5-observability"],
        ["project-0", "project-3", "project-4"],
    ),
    "深度学习工程师": (
        ["s1-llm-basics", "s1-api-dev", "s1-ollama", "s2-agent-core", "s3-langgraph", "s3-agentic-rag"],
        ["project-4", "project-3"],
    ),
    "数据科学家": (
        ["s1-llm-basics", "s1-prompt", "s1-api-dev", "s2-agent-core", "s3-rag", "s5-observability", "s5-deploy"],
        ["project-0", "project-4", "project-3"],
    ),
    "AI 应用开发": (
        ["s1-llm-basics", "s1-api-dev", "s2-tool-calling", "s3-langchain", "s3-langgraph", "s4-multi-agent", "s5-deploy", "s6-rag-project", "s6-cs-agent", "s7-career"],
        ["project-1", "project-4", "project-2"],
    ),
    "计算机视觉工程师": (
        ["s1-llm-basics", "s1-api-dev", "s1-ollama", "s2-tool-calling", "s3-mcp", "s4-orchestration"],
        ["project-4", "project-0"],
    ),
}

# fallback plan when direction is not in the map above
_DEFAULT_PLAN = (
    ["s1-llm-basics", "s1-prompt", "s1-api-dev", "s1-ollama", "s2-agent-core", "s3-rag", "s3-langchain"],
    ["project-3", "project-4"],
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


def _course_chapter_progress(user_id: int | None, course_id: str) -> tuple[int, int]:
    """返回课程 (已完成章节数, 总章节数)。

    五阶段课程为文字章节，进度按章节计（与押金完课率同口径）。
    未登录或课程无章节时返回 (0, 0)。
    """
    if user_id is None:
        return (0, 0)
    row = query_one("courses", course_id)
    if not row:
        return (0, 0)
    chapters = parse_json_field(row.get("chapters", "[]"))
    total = len(chapters)
    if total == 0:
        return (0, 0)
    done = get_user_completed_chapter_ids(user_id, course_id)
    completed = sum(1 for c in chapters if c.get("id") in done)
    return (completed, total)


def _apply_user_progress(path: LearningPathItem, completed: set[str], user_id: int | None = None) -> LearningPathItem:
    """Merge user-completed node ids + chapter-completed state into a path's nodes.

    - Course node progress = 该用户已学完章节 / 总章节（章节粒度，学完一章进度就涨）
    - 课程章节全部学完的节点自动视为完成（无需手动"标记完成"），但仅在前面节点都已
      完成时生效（保持顺序解锁），这样路径里重复出现的已学课程能直接解锁下一节。
    - 旧版按"看完视频数"计；遗留视频库已清理为占位，现统一改为按章节完成度。
    """
    node_progress: dict[str, int] = {}
    auto_completed: set[str] = set()
    for node in path.nodes:
        if node.type == "course" and node.courseId:
            done, total = _course_chapter_progress(user_id, node.courseId)
            if total:
                node_progress[node.id] = round(done / total * 100)
                if done == total:
                    auto_completed.add(node.id)

    all_completed = {n.id for n in path.nodes if n.status == "completed"} | completed
    current_set = False
    for node in path.nodes:
        node_done = node.id in all_completed
        # 自动完成仅当前面尚未出现未完成节点（保持顺序解锁）
        auto_done = (not current_set) and (node.id in auto_completed)
        if node_done or auto_done:
            node.status = "completed"
            node.progress = node_progress.get(node.id, 100)
        elif not current_set:
            node.status = "current"
            node.progress = node_progress.get(node.id, 0)
            current_set = True
        else:
            node.status = "locked"
            node.progress = node_progress.get(node.id, 0)
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
async def list_paths(request: Request, direction: str | None = Query(None, description="Filter / generate path for a direction")):
    """List learning paths.

    - With ?direction=X: return a single path generated for that direction.
    - Without params: return all direction plans (each with its own course/project set),
      so the user can browse and switch between learning directions.
    """
    progress = _load_progress()
    user = await get_optional_user(request)
    user_id = user["id"] if user else None

    if direction:
        path = _build_path(direction)
        return [_apply_user_progress(path, set(progress.get(path.id, [])), user_id)]

    paths = []
    # 推荐方向排最前，其余方向按顺序列出
    rec_dir = _recommended_direction()
    directions = list(_DIRECTION_PLAN.keys())
    if rec_dir and rec_dir in directions:
        directions.remove(rec_dir)
        directions.insert(0, rec_dir)
    for d in directions:
        path = _build_path(d)
        paths.append(_apply_user_progress(path, set(progress.get(path.id, [])), user_id))
    return paths


@router.post("/{path_id}/nodes/{node_id}/complete")
async def complete_node(path_id: str, node_id: str, request: Request):
    """Mark a node as completed; the next locked node becomes current.

    Persists completion in path_progress.json so it survives restarts.
    For course nodes, the course's chapters must be completed first (五阶段课程按章节计进度).
    """
    base = _get_base_path(path_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    node = next((n for n in base.nodes if n.id == node_id), None)
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found in path")

    # 按用户隔离：登录态下校验章节完成度 + 同步写入 user_path_progress（押金三锁/学习档案）
    user = await get_optional_user(request)
    user_id = user["id"] if user else None

    # 解锁约束：locked 节点不可越级完成；auto-completed（章节学完自动完成）的节点
    # 允许再次"标记完成"（幂等），避免误报"请先完成前一个节点"
    progress = _load_progress()
    completed = set(progress.get(path_id, []))
    if node.id in completed:
        return _apply_user_progress(base, completed, user_id)
    effective = _apply_user_progress(base, completed, user_id)
    node_effective = next((n for n in effective.nodes if n.id == node_id), None)
    if node_effective is None or node_effective.status == "locked":
        raise HTTPException(status_code=400, detail="请先完成前一个节点")

    # 课程节点：登录态下先校验该课程章节已学完（五阶段课程为文字章节，按章节计进度；
    # 未登录时不做章节门槛，保持与全局路径进度的宽松行为一致）
    if node.type == "course" and node.courseId and user:
        done, total = _course_chapter_progress(user_id, node.courseId)
        if total and done < total:
            raise HTTPException(
                status_code=400,
                detail=f"还有 {total - done}/{total} 个章节未学完，请先完成课程内容再标记完成",
            )

    completed.add(node_id)
    progress[path_id] = sorted(completed)
    _save_progress(progress)

    if user:
        record_user_path_node(user_id, path_id, node_id)

    return _apply_user_progress(base, completed, user_id)


@router.get("/{path_id}", response_model=LearningPathItem)
async def get_path(path_id: str, request: Request):
    """Get a single learning path by ID."""
    base = _get_base_path(path_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    progress = _load_progress()
    user = await get_optional_user(request)
    return _apply_user_progress(base, set(progress.get(path_id, [])), user["id"] if user else None)
