"""Learning paths API router (数据源统一：learning_paths 表驱动，后台可即时生效).

方向路径的"内容"（节点课程/项目序列、标题、进度锚点）现以 learning_paths 表为准，
由 database.seed_learning_paths_from_direction_plan 灌入，后台可直接编辑、即时生效。
动态生成逻辑（方向蓝图 _LEARNING_DIRECTION_PLAN）已收敛到 database.py 的种子阶段。
此处保留：推荐方向排序 + per-user 进度合并 + 章节自动完成 + 顺序解锁（运行时逻辑）。
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Request

from models.schemas import LearningPathItem, LearningPathNode
from auth_utils import get_optional_user
from database import (
    record_user_path_node,
    get_user_path_progress,
    get_user_path_completed,
    get_latest_user_ability_report,
    safe_load_json,
    query_all,
    query_one,
    parse_json_field,
    get_user_completed_chapter_ids,
    _DEFAULT_PLAN,
)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/learning-paths", tags=["learning-paths"])


def _load_json(filename: str):
    return safe_load_json(PROCESSED_DIR / filename, None)


def _db_to_path(row: dict) -> LearningPathItem:
    """数据库行 → LearningPathItem（snake_case 列 → 前端字段，nodes 解析为节点列表）。"""
    nodes = parse_json_field(row.get("nodes", "[]"), []) or []
    return LearningPathItem(
        id=row["id"],
        direction=row.get("direction", ""),
        title=row.get("title", ""),
        nodes=[LearningPathNode(**n) for n in nodes] if nodes else [],
        totalWeeks=row.get("total_weeks", 0),
        currentWeek=row.get("current_week", 0),
        createdAt=row.get("created_at", ""),
    )


def _load_paths() -> list[LearningPathItem]:
    """从 learning_paths 表读取启用路径（后台管理即可即时生效）。"""
    rows = query_all("learning_paths", {"is_active": 1})
    return [_db_to_path(r) for r in rows]


def _course_title(cid: str) -> str:
    row = query_one("courses", cid)
    return row.get("title", cid) if row else cid


def _project_title(pid: str) -> str:
    row = query_one("projects", pid)
    if not row:
        return pid
    return row.get("title", pid).replace("Project: ", "", 1)


def _build_default_path(direction: str) -> LearningPathItem:
    """为未命中蓝图的任意方向构建兜底路径（默认课程/项目序列，从数据库取真实标题）。"""
    courses, projects = _DEFAULT_PLAN
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


def _recommended_direction(user_id: int | None = None) -> str | None:
    """Read the user's own recommended direction from their ability report.

    登录用户读自己 DB 里的 recommended_direction（数据隔离），避免把匿名测评
    或全局 demo 的方向算到他头上；仅未登录/无个人报告时回退全局文件。
    """
    if user_id is not None:
        row = get_latest_user_ability_report(user_id)
        if row:
            return row.get("recommended_direction") or None
    report = _load_json("ability_report.json")
    if report:
        return report.get("recommendedDirection")
    return None


# ===== 用户进度持久化 =====
# 登录用户以 DB 的 user_path_progress 为准（数据隔离）；匿名用户回退全局 path_progress.json。


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
    """Return the un-merged base path by id (from DB), with fallback for unknown directions."""
    for p in _load_paths():
        if p.id == path_id:
            return p
    if path_id.startswith("path-"):
        direction = path_id[len("path-"):]
        if direction:
            return _build_default_path(direction)
    return None


@router.get("", response_model=list[LearningPathItem])
async def list_paths(request: Request, direction: str | None = Query(None, description="Filter / generate path for a direction")):
    """List learning paths.

    - With ?direction=X: return a single path for that direction.
    - Without params: return all direction paths, so the user can browse and switch.
    """
    user = await get_optional_user(request)
    user_id = user["id"] if user else None
    # 登录用户以 DB 进度为准（数据隔离），匿名用户回退全局文件
    progress = get_user_path_progress(user_id) if user_id else _load_progress()

    paths = _load_paths()
    if direction:
        path = next((p for p in paths if p.direction == direction), None)
        if path is None:
            path = _build_default_path(direction)
        return [_apply_user_progress(path, set(progress.get(path.id, [])), user_id)]

    # 推荐方向排最前（按当前用户自己的能力报告方向），其余方向保持数据库顺序
    rec_dir = _recommended_direction(user_id)
    if rec_dir:
        rec = [p for p in paths if p.direction == rec_dir]
        rest = [p for p in paths if p.direction != rec_dir]
        paths = rec + rest
    return [_apply_user_progress(p, set(progress.get(p.id, [])), user_id) for p in paths]


@router.post("/{path_id}/nodes/{node_id}/complete")
async def complete_node(path_id: str, node_id: str, request: Request):
    """Mark a node as completed; the next locked node becomes current.

    Persists completion (登录用户写入 DB，匿名写 path_progress.json).
    For course nodes, the course's chapters must be completed first (五阶段课程按章节计进度).
    """
    base = _get_base_path(path_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    node = next((n for n in base.nodes if n.id == node_id), None)
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found in path")

    # 按用户隔离：登录态下进度以 DB 为准（押金三锁/学习档案），匿名用户回退全局文件
    user = await get_optional_user(request)
    user_id = user["id"] if user else None

    if user:
        completed = set(get_user_path_completed(user_id, path_id))
    else:
        progress = _load_progress()
        completed = set(progress.get(path_id, []))

    # 解锁约束：locked 节点不可越级完成；auto-completed（章节学完自动完成）的节点
    # 允许再次"标记完成"（幂等），避免误报"请先完成前一个节点"
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
    if user:
        record_user_path_node(user_id, path_id, node_id)
    else:
        progress[path_id] = sorted(completed)
        _save_progress(progress)

    return _apply_user_progress(base, completed, user_id)


@router.get("/{path_id}", response_model=LearningPathItem)
async def get_path(path_id: str, request: Request):
    """Get a single learning path by ID."""
    base = _get_base_path(path_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    user = await get_optional_user(request)
    user_id = user["id"] if user else None
    if user:
        progress = {path_id: get_user_path_completed(user_id, path_id)}
    else:
        progress = _load_progress()
    return _apply_user_progress(base, set(progress.get(path_id, [])), user_id)
