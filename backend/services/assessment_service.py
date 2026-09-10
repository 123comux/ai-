"""Assessment service - generates and scores assessments with per-dimension ability report."""

import json
import logging
import random
from pathlib import Path
from typing import Optional

from models.schemas import AssessmentQuestion, AssessmentResult
from fsx import safe_write_json

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def load_questions() -> list[AssessmentQuestion]:
    """Load assessment questions from processed data."""
    path = PROCESSED_DIR / "assessment_questions.json"
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [AssessmentQuestion(**q) for q in data]


def get_assessment(topic: Optional[str] = None, count: int = 10) -> list[AssessmentQuestion]:
    """Get a random set of assessment questions.

    When no topic filter, draw a balanced sample: at least one question per
    available dimension so every ability is probed.
    """
    all_q = load_questions()

    if topic:
        filtered = [q for q in all_q if q.topic.lower() == topic.lower()]
    else:
        filtered = all_q

    if not filtered:
        return []

    if topic is None:
        # Balanced sampling: 每维度尽量均分题目，保证每个能力的分数有区分度。
        # 用轮询（round-robin）而非直接 slice，避免"某维度题库不足时拿不到足够的题"。
        dims = list(dict.fromkeys(getattr(q, 'dimension', getattr(q, 'topic', 'unknown')) for q in filtered))
        buckets: dict[str, list] = {}
        for q in filtered:
            d = getattr(q, 'dimension', getattr(q, 'topic', 'unknown'))
            buckets.setdefault(d, []).append(q)
        for t in buckets:
            random.shuffle(buckets[t])

        selected = []
        idx = 0
        while len(selected) < count:
            added = False
            for t in dims:
                if len(selected) >= count:
                    break
                if idx < len(buckets[t]):
                    selected.append(buckets[t][idx])
                    added = True
            if not added:
                break
            idx += 1
        return selected[:count]

    random.shuffle(filtered)
    return filtered[:count]


# 零基础AI能力测评六维度 (matches assessment_questions.json "dimension" field)
DIMENSIONS = {
    "AI基础认知": "AI基础认知",
    "AI工具使用": "AI工具使用",
    "提示词能力": "提示词能力",
    "场景应用": "场景应用",
    "AI工作流": "AI工作流",
    "AI思维": "AI思维",
}


def _level_from_score(score: int) -> str:
    if score >= 85:
        return "expert"
    if score >= 70:
        return "advanced"
    if score >= 50:
        return "intermediate"
    return "beginner"


def _recommend_direction(dim_scores: dict[str, int]) -> str:
    """Map per-dimension scores to a recommended learning path."""
    cognition = dim_scores.get("AI基础认知", 0)
    tools = dim_scores.get("AI工具使用", 0)
    prompting = dim_scores.get("提示词能力", 0)
    scenario = dim_scores.get("场景应用", 0)
    workflow = dim_scores.get("AI工作流", 0)
    thinking = dim_scores.get("AI思维", 0)

    candidates = [
        ("从零开始学AI（小白推荐）", cognition + tools),
        ("AI办公提效（职场推荐）", prompting + scenario),
        ("AI项目实战（进阶推荐）", scenario + workflow),
        ("系统掌握AI应用（深度推荐）", prompting + workflow + thinking),
    ]
    candidates.sort(key=lambda x: x[1], reverse=True)
    best, best_score = candidates[0]

    return best if best_score > 0 else "从零开始学AI（小白推荐）"


def score_assessment(answers: list[int], question_ids: list[str], user_id: int = None) -> AssessmentResult:
    """Score answers, build a per-dimension ability report, persist it, and return it."""
    all_q = load_questions()
    q_map = {q.id: q for q in all_q}

    correct = 0
    total = len(answers)
    topic_stats: dict[str, dict] = {}

    for qid, ans in zip(question_ids, answers):
        if qid not in q_map:
            continue
        q = q_map[qid]
        dim = getattr(q, 'dimension', q.topic)
        if dim not in topic_stats:
            topic_stats[dim] = {"correct": 0, "total": 0}
        topic_stats[dim]["total"] += 1
        if ans == q.correct_answer:
            correct += 1
            topic_stats[dim]["correct"] += 1

    # Per-dimension scores (0-100)，只统计能映射到标准六维的题目
    dim_scores: dict[str, int] = {}
    for dim, stats in topic_stats.items():
        if dim not in DIMENSIONS:
            continue
        cn = DIMENSIONS[dim]
        ratio = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        dim_scores[cn] = round(ratio * 100)

    # Overall score as mean of dimension scores (not raw ratio, so all dims weigh equally)
    overall = round(sum(dim_scores.values()) / len(dim_scores)) if dim_scores else 0

    # 每个维度仅 3~4 题，分数粒度很陡（3 题: 0/33/67/100；4 题: 0/25/50/75/100）。
    # 用 >=60 / <40 作为优势/薄弱分界：2/3、3/4 即算优势，1/3、1/4 即算薄弱。
    strengths = []
    weaknesses = []
    for cn, score in dim_scores.items():
        if score >= 60:
            strengths.append(cn)
        elif score < 40:
            weaknesses.append(cn)

    level = _level_from_score(overall)
    recommended = _recommend_direction(dim_scores)

    result = AssessmentResult(
        score=overall,
        total=total,
        level=level,
        strengths=strengths,
        weaknesses=weaknesses,
        recommended_direction=recommended,
    )

    # Persist a full AbilityReport so home/mine pages reflect fresh assessment.
    _persist_ability_report(dim_scores, overall, level, strengths, weaknesses, recommended, user_id=user_id)

    return result


def _persist_ability_report(
    dim_scores: dict[str, int],
    overall: int,
    level: str,
    strengths: list[str],
    weaknesses: list[str],
    recommended: str,
    user_id: int = None,
) -> None:
    """Write the latest assessment into ability_report.json (global demo fallback)
    AND, when a user is identified, into the per-user user_ability_reports table
    so each user's 我的页 reflects their own result (multi-tenant isolation).
    """
    # Fixed order for a stable radar chart (零基础AI六维度)
    order = ["AI基础认知", "AI工具使用", "提示词能力", "场景应用", "AI工作流", "AI思维"]
    dimensions = [
        {"label": dim, "score": dim_scores.get(dim, 0), "maxScore": 100}
        for dim in order
    ]
    level_cn = {
        "expert": "专家",
        "advanced": "高级",
        "intermediate": "中级",
        "beginner": "初级",
    }.get(level, "初级")
    report = {
        "overallScore": overall,
        "level": level_cn,
        "dimensions": dimensions,
        "strengths": [f"{s}掌握较好" if len(strengths) else s for s in strengths],
        "weaknesses": [f"{w}需要加强" for w in weaknesses] or ["各维度有待均衡提升"],
        "recommendedDirection": recommended,
        "estimatedHours": 100 + max(0, overall) * 2,
    }

    # 1) Global demo fallback (used by job-matching when no per-user report exists)
    #    容错：Serverless 只读文件系统 / 文件被占用，失败仅告警，绝不阻断测评响应
    safe_write_json(PROCESSED_DIR / "ability_report.json", report)

    # 2) Per-user persistence (multi-tenant isolation)
    if user_id is not None:
        try:
            from database import save_user_ability_report
            save_user_ability_report(user_id, {
                "overall_score": overall,
                "level": level_cn,
                "dimensions": dimensions,
                "strengths": report["strengths"],
                "weaknesses": report["weaknesses"],
                "recommended_direction": recommended,
                "estimated_hours": report["estimatedHours"],
            })
        except Exception:
            pass  # never let persistence break the assessment response
