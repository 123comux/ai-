"""User data API router.

All endpoints are multi-tenant aware: when a valid Bearer token is present the
data is scoped to that user (from the user_* tables); when absent, a global
demo fallback (data/processed/*.json) is used so the product still renders.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends

from models.schemas import AbilityReport, LearningRecord, JobMatchingResult, LearningStats
from database import (
    get_latest_user_ability_report,
    get_user_video_progress,
    get_user_completed_project_count,
    parse_json_field,
    safe_load_json,
)
from auth_utils import get_optional_user

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/user", tags=["user-data"])


def _load_json(filename: str):
    """Load a processed JSON file; returns None on missing/malformed (no 500)."""
    return safe_load_json(PROCESSED_DIR / filename, None)


@router.get("/ability-report", response_model=AbilityReport)
async def get_ability_report(request: Request):
    """User's latest ability report (per-user), with global demo fallback."""
    user = await get_optional_user(request)
    if user:
        row = get_latest_user_ability_report(user["id"])
        if row:
            return AbilityReport(
                overallScore=row["overall_score"],
                level=row["level"],
                dimensions=parse_json_field(row["dimensions"], []),
                strengths=parse_json_field(row["strengths"], []),
                weaknesses=parse_json_field(row["weaknesses"], []),
                recommendedDirection=row["recommended_direction"],
                estimatedHours=row["estimated_hours"],
            )
    # Fallback to the seeded global demo report
    data = _load_json("ability_report.json")
    if not data:
        return AbilityReport(
            overallScore=0, level="初级", dimensions=[],
            strengths=[], weaknesses=[], recommendedDirection="", estimatedHours=0,
        )
    return AbilityReport(**data)


@router.get("/learning-records", response_model=list[LearningRecord])
async def get_learning_records(request: Request):
    """Per-user learning records aggregated from watched-video timestamps."""
    user = await get_optional_user(request)
    if not user:
        return []
    rows = get_user_video_progress(user["id"])
    day_map: dict[str, dict] = {}
    for r in rows:
        at = (r.get("watched_at") or "")[:10]
        if not at:
            continue
        minutes = int(r.get("minutes") or 0)
        day_map.setdefault(at, {"duration": 0, "lessons": 0})
        day_map[at]["duration"] += minutes
        day_map[at]["lessons"] += 1
    records = [
        LearningRecord(
            date=d[5:],  # MM-DD
            duration=v["duration"],
            lessonsCompleted=v["lessons"],
            exercisesDone=0,
        )
        for d, v in sorted(day_map.keys(), reverse=True)
    ]
    return records[:30]


@router.get("/job-matching", response_model=JobMatchingResult)
async def get_job_matching():
    """Get the seeded job matching result (demo)."""
    data = _load_json("job_matching.json")
    if not data:
        return JobMatchingResult(
            jobTitle="", company="", matchScore=0, requiredSkills=[],
            gapSkills=[], recommendedCourses=[], recommendedProjects=[],
        )
    return JobMatchingResult(**data)


def _parse_ai_json(text: str) -> dict | None:
    """Extract a JSON object from AI output (tolerates markdown fences/extra text)."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    if m:
        text = m.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


# 技能关键词 → 能力报告维度 的映射（用于判定是否已掌握）
SKILL_DIMENSION_MAP = [
    (["python", "编程", "代码", "开发", "typescript", "javascript", "java", "c++", "go", "html", "css", "vue", "react", "接口", "数据结构"], "编程基础"),
    (["数学", "线性代数", "概率", "统计", "微积分", "离散"], "数学基础"),
    (["机器学习", "scikit", "sklearn", "回归", "分类", "聚类", "模型"], "机器学习"),
    (["深度学习", "神经网络", "cnn", "rnn", "transformer", "pytorch", "tensorflow", "bert"], "深度学习"),
    (["大模型", "llm", "langchain", "rag", "agent", "prompt", "微调", "gpt", "生成式", "aigc"], "大模型应用"),
    (["项目", "工程", "部署", "运维", "docker", "k8s", "ci", "架构", "微服务"], "项目经验"),
]

# 维度得分达标才视为"已掌握"：60 分（满分 100）为掌握线，40-59 为入门，<40 为待提升
DIMENSION_MASTERED_THRESHOLD = 60


def _skill_mastered(skill: str, dimensions: dict) -> bool:
    s = skill.lower()
    best_dimension = None
    best_score = 0
    for keywords, dim in SKILL_DIMENSION_MAP:
        if any(kw in s for kw in keywords):
            d = dimensions.get(dim, 0)
            if d > best_score:
                best_score = d
                best_dimension = dim
    if best_dimension is None:
        avg = sum(dimensions.values()) / len(dimensions) if dimensions else 0
        return avg >= DIMENSION_MASTERED_THRESHOLD
    return best_score >= DIMENSION_MASTERED_THRESHOLD


def _skill_dimension_score(skill: str, dimensions: dict) -> float:
    s = skill.lower()
    best_dimension = None
    best_score = 0
    for keywords, dim in SKILL_DIMENSION_MAP:
        if any(kw in s for kw in keywords):
            d = dimensions.get(dim, 0)
            if d > best_score:
                best_score = d
                best_dimension = dim
    if best_dimension is not None:
        return best_score
    return sum(dimensions.values()) / len(dimensions) if dimensions else 0


@router.post("/job-matching/analyze", response_model=JobMatchingResult)
async def analyze_job_matching(body: dict, request: Request):
    """Analyze a job description against the user's ability report.

    - Empty description -> raise 400 (需要输入)
    - AI (Zhipu GLM) 提取岗位技能清单、推荐课程/项目、匹配分
    - mastered 由后端基于能力报告维度得分判定（避免 AI 误判）
    - AI 失败时回退到关键词提取
    - Ability report is resolved per-user when authenticated.
    """
    job_description = (body.get("job_description") or "").strip()
    if not job_description:
        raise HTTPException(status_code=400, detail="请输入岗位描述")

    # Resolve the user's own ability report when authenticated, else the global demo.
    user = await get_optional_user(request)
    dimensions = None
    weaknesses = []
    strengths = []
    if user:
        row = get_latest_user_ability_report(user["id"])
        if row:
            dims = parse_json_field(row["dimensions"], [])
            dimensions = {d.get("label"): d.get("score", 0) for d in dims}
            weaknesses = parse_json_field(row["weaknesses"], [])
            strengths = parse_json_field(row["strengths"], [])
    if dimensions is None:
        ability = _load_json("ability_report.json") or {}
        dimensions = {d.get("label"): d.get("score", 0) for d in ability.get("dimensions", [])}
        weaknesses = ability.get("weaknesses", [])
        strengths = ability.get("strengths", [])

    def _build_result(job_title: str, ai_match_score: int, raw_skills: list, gaps: list, courses: list, projects: list) -> JobMatchingResult:
        required = []
        for s in raw_skills:
            name = s.get("name") if isinstance(s, dict) else str(s)
            if not name:
                continue
            required.append({"name": name, "mastered": _skill_mastered(name, dimensions)})
        if not required:
            required = [{"name": "Python", "mastered": _skill_mastered("Python", dimensions)}]
        skill_scores = [_skill_dimension_score(s["name"], dimensions) for s in required]
        avg_score = sum(skill_scores) / len(skill_scores) if skill_scores else 50
        mastered_ratio = sum(1 for s in required if s["mastered"]) / len(required) if required else 0
        calc_score = avg_score + mastered_ratio * 15
        final_score = int(calc_score * 0.7 + max(0, min(100, ai_match_score)) * 0.3)
        not_mastered = [s["name"] for s in required if not s["mastered"]]
        ai_gaps = [g for g in gaps if g and g not in dimensions]
        gap = list(dict.fromkeys(not_mastered + ai_gaps))
        if not gap:
            gap = ["持续提升专业技能"]
        return JobMatchingResult(
            jobTitle=job_title,
            company="目标公司",
            matchScore=max(0, min(100, final_score)),
            requiredSkills=required,
            gapSkills=gap[:8],
            recommendedCourses=[c for c in courses if c][:5],
            recommendedProjects=[p for p in projects if p][:5],
        )

    # ---- 尝试智谱 AI：提取技能清单 + 推荐 ----
    ai_result = None
    try:
        from services.zhipu_service import chat_zhipu
        system_prompt = (
            "你是资深 AI 岗位分析专家。根据给定的岗位描述，输出 JSON（不要输出其他文字），"
            "字段：jobTitle(岗位名称), matchScore(0-100 匹配度整数，考虑用户能力报告), "
            "requiredSkills(岗位必备技能的字符串数组), gapSkills(用户可能缺失的技能字符串数组), "
            "recommendedCourses(建议学习的课程名数组), recommendedProjects(建议做的项目名数组)。"
            "注意：requiredSkills 只列技能名，不要判断是否掌握（掌握与否由系统判断）。"
            f"用户能力报告维度与得分：{json.dumps(dimensions, ensure_ascii=False)}；"
            f"待提升：{json.dumps(weaknesses, ensure_ascii=False)}。"
            f"请结合这些维度评估 matchScore（用户能力越匹配得分越高）。"
        )
        resp = chat_zhipu(job_description, system_prompt, max_new_tokens=600, temperature=0.3)
        ai_result = _parse_ai_json(resp.get("answer", ""))
    except Exception:
        ai_result = None

    if ai_result:
        return _build_result(
            job_title=str(ai_result.get("jobTitle") or "目标岗位"),
            ai_match_score=int(ai_result.get("matchScore") or 50),
            raw_skills=ai_result.get("requiredSkills") or [],
            gaps=ai_result.get("gapSkills") or [],
            courses=ai_result.get("recommendedCourses") or [],
            projects=ai_result.get("recommendedProjects") or [],
        )

    # ---- 关键词 fallback ----
    try:
        from services.recommend_service import recommend_courses_keyword_only
        recs = recommend_courses_keyword_only(job_description, limit=4) or []
    except Exception:
        recs = []
    raw_skills = []
    for kw in ["Python", "大模型", "LLM", "RAG", "机器学习", "深度学习", "SQL", "数据分析", "Agent", "微服务", "算法"]:
        if kw.lower() in job_description.lower():
            raw_skills.append(kw)
    return _build_result(
        job_title="目标岗位",
        ai_match_score=50,
        raw_skills=raw_skills,
        gaps=[g for g in weaknesses if g],
        courses=[c.get("title") for c in recs if c.get("title")],
        projects=["完成一个与目标岗位相关的实战项目"],
    )


@router.get("/learning-stats", response_model=LearningStats)
async def get_learning_stats(request: Request):
    """Per-user learning statistics aggregated from user_video_progress + project progress.

    - learningDays: 连续学习天数（从今天往前，连续有学习行为的自然日数）
    - totalMinutes: 已看完视频的时长总和（分钟）
    - completedLessons: 已看完视频数
    - completedProjects: 完成全部步骤的项目数
    """
    user = await get_optional_user(request)
    if not user:
        return LearningStats(learningDays=0, totalMinutes=0, completedProjects=0, completedLessons=0)

    rows = get_user_video_progress(user["id"])
    watched_count = len(rows)
    total_minutes = sum(int(r.get("minutes") or 0) for r in rows)

    # 连续学习天数：从今天往前，统计连续有学习行为的自然日
    learning_dates = set()
    for r in rows:
        at = (r.get("watched_at") or "")[:10]
        if not at:
            continue
        try:
            learning_dates.add(datetime.strptime(at, "%Y-%m-%d").date())
        except ValueError:
            continue

    streak = 0
    if learning_dates:
        today = datetime.now().date()
        cur = today
        if cur not in learning_dates:
            cur -= timedelta(days=1)
        while cur in learning_dates:
            streak += 1
            cur -= timedelta(days=1)

    completed_projects = get_user_completed_project_count(user["id"])

    return LearningStats(
        learningDays=streak,
        totalMinutes=total_minutes,
        completedProjects=completed_projects,
        completedLessons=watched_count,
    )
