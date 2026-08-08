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


# 技能关键词 → 能力报告维度 的映射（用于判定是否已掌握）
SKILL_DIMENSION_MAP = [
    (["python", "编程", "代码", "开发", "typescript", "javascript", "java", "c++", "go", "html", "css", "vue", "react", "框架", "接口"], "编程基础"),
    (["数学", "线性代数", "概率", "统计", "微积分", "离散"], "数学基础"),
    (["机器学习", "scikit", "sklearn", "回归", "分类", "聚类", "模型"], "机器学习"),
    (["深度学习", "神经网络", "cnn", "rnn", "transformer", "pytorch", "tensorflow", "bert"], "深度学习"),
    (["大模型", "llm", "langchain", "rag", "agent", "prompt", "微调", "gpt", "生成式", "aigc"], "大模型应用"),
    (["项目", "工程", "部署", "运维", "docker", "k8s", "ci", "架构", "微服务"], "项目经验"),
]

# 匹配分权重（按能力报告维度）
DIMENSION_SCORE_THRESHOLD = 30  # 维度得分 >= 该值视为"基础已具备"


def _skill_mastered(skill: str, dimensions: dict) -> bool:
    """判断技能是否已掌握：技能关键词命中能力维度，且该维度得分 >= 阈值。"""
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
        # 技能不在映射里，按整体水平（overall 平均维度分）判断
        avg = sum(dimensions.values()) / len(dimensions) if dimensions else 0
        return avg >= DIMENSION_SCORE_THRESHOLD
    return best_score >= DIMENSION_SCORE_THRESHOLD


@router.post("/job-matching/analyze", response_model=JobMatchingResult)
async def analyze_job_matching(body: dict):
    """Analyze a job description against the user's ability report.

    - Empty description -> raise 400 (需要输入)
    - AI (Zhipu GLM) 提取岗位技能清单、推荐课程/项目、匹配分
    - mastered 由后端基于能力报告维度得分判定（避免 AI 误判）
    - AI 失败时回退到关键词提取
    """
    job_description = (body.get("job_description") or "").strip()
    if not job_description:
        raise HTTPException(status_code=400, detail="请输入岗位描述")

    ability = _load_json("ability_report.json")
    dimensions = {d.get("label"): d.get("score", 0) for d in ability.get("dimensions", [])}
    weaknesses = ability.get("weaknesses", [])
    strengths = ability.get("strengths", [])

    def _build_result(job_title: str, ai_match_score: int, raw_skills: list, gaps: list, courses: list, projects: list) -> JobMatchingResult:
        """从 AI 提取的原始技能列表，结合能力报告判定 mastered，并由后端计算 matchScore。"""
        required = []
        for s in raw_skills:
            name = s.get("name") if isinstance(s, dict) else str(s)
            if not name:
                continue
            required.append({"name": name, "mastered": _skill_mastered(name, dimensions)})
        if not required:
            required = [{"name": "Python", "mastered": _skill_mastered("Python", dimensions)}]
        # 匹配分 = 已掌握技能占比 * 100（真实反映用户对岗位的匹配度）
        mastered_count = sum(1 for s in required if s["mastered"])
        calc_score = round(mastered_count / len(required) * 100) if required else 50
        # 融合 AI 参考分（若 AI 提供），避免单来源偏差
        final_score = int(calc_score * 0.7 + max(0, min(100, ai_match_score)) * 0.3)
        # 待提升技能 = 岗位未掌握技能；AI gaps 只保留非抽象维度名的项
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