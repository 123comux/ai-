"""User data API router."""

import json
import re
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


def _parse_ai_json(text: str) -> dict | None:
    """Extract a JSON object from AI output (tolerates markdown fences/extra text)."""
    text = text.strip()
    # 去掉 ```json ... ``` 围栏
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    if m:
        text = m.group(1).strip()
    # 找到第一个 { 到最后一个 }
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


@router.post("/job-matching/analyze", response_model=JobMatchingResult)
async def analyze_job_matching(body: dict):
    """Analyze a job description against the user's ability report.

    - Empty description -> fall back to default job_matching.json
    - Uses Zhipu GLM-4-flash when key is available; falls back to keyword matching.
    """
    job_description = (body.get("job_description") or "").strip()
    if not job_description:
        data = _load_json("job_matching.json")
        return JobMatchingResult(**data)

    ability = _load_json("ability_report.json")
    dimensions = {d.get("label"): d.get("score", 0) for d in ability.get("dimensions", [])}
    weaknesses = ability.get("weaknesses", [])
    strengths = ability.get("strengths", [])

    # ---- 尝试智谱 AI ----
    ai_result = None
    try:
        from services.zhipu_service import chat_zhipu
        system_prompt = (
            "你是资深 AI 岗位分析专家。根据给定的岗位描述和用户能力报告，输出 JSON（不要输出其他文字），"
            "字段：jobTitle(岗位名称), company(公司或'目标公司'), matchScore(0-100 匹配度整数), "
            "requiredSkills([{name, mastered}] 岗位必备技能及用户是否已掌握, 依据能力报告判断), "
            "gapSkills(用户缺失的技能字符串数组), "
            "recommendedCourses(建议学习的课程名数组), recommendedProjects(建议做的项目名数组)。"
            f"用户能力报告维度与得分：{json.dumps(dimensions, ensure_ascii=False)}；优势：{json.dumps(strengths, ensure_ascii=False)}；待提升：{json.dumps(weaknesses, ensure_ascii=False)}。"
        )
        resp = chat_zhipu(job_description, system_prompt, max_new_tokens=600, temperature=0.3)
        ai_result = _parse_ai_json(resp.get("answer", ""))
    except Exception:
        ai_result = None

    if ai_result:
        required = ai_result.get("requiredSkills") or []
        required_norm = []
        for s in required:
            if isinstance(s, dict):
                required_norm.append({
                    "name": s.get("name", ""),
                    "mastered": bool(s.get("mastered", False)),
                })
            elif isinstance(s, str):
                mastered = any(k in s for k in dimensions)
                required_norm.append({"name": s, "mastered": mastered})
        return JobMatchingResult(
            jobTitle=str(ai_result.get("jobTitle") or "目标岗位"),
            company=str(ai_result.get("company") or "目标公司"),
            matchScore=max(0, min(100, int(ai_result.get("matchScore") or 0))),
            requiredSkills=required_norm,
            gapSkills=[str(s) for s in (ai_result.get("gapSkills") or [])],
            recommendedCourses=[str(s) for s in (ai_result.get("recommendedCourses") or [])],
            recommendedProjects=[str(s) for s in (ai_result.get("recommendedProjects") or [])],
        )

    # ---- 关键词 fallback ----
    try:
        from services.recommend_service import recommend_courses_keyword_only
        recs = recommend_courses_keyword_only(job_description, limit=4) or []
    except Exception:
        recs = []
    required_skills = []
    for kw in ["Python", "大模型", "LLM", "RAG", "机器学习", "深度学习", "SQL", "数据分析", "Agent", "微服务", "算法"]:
        if kw.lower() in job_description.lower():
            mastered = any(kw in w for w in strengths) or any(kw in d for d in dimensions)
            required_skills.append({"name": kw, "mastered": mastered})
    if not required_skills:
        required_skills = [{"name": s, "mastered": any(s in d for d in dimensions)} for s in dimensions]

    gap = [g for g in weaknesses if g] or ["岗位技能待提升"]
    return JobMatchingResult(
        jobTitle="AI 岗位",
        company="目标公司",
        matchScore=50,
        requiredSkills=required_skills,
        gapSkills=gap,
        recommendedCourses=[c.get("title") for c in recs if c.get("title")][:4],
        recommendedProjects=["完成一个与大模型相关的实战项目"],
    )


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