"""Assessment service - generates and scores assessments with per-dimension ability report."""

import json
import random
from pathlib import Path
from typing import Optional

from models.schemas import AssessmentQuestion, AssessmentResult

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
        # Balanced sampling: group by topic, take floor(count / n_topics) from each,
        # fill the remainder round-robin from leftover questions.
        random.shuffle(filtered)
        topics = list(dict.fromkeys(q.topic for q in filtered))
        per_topic = max(1, count // len(topics)) if len(topics) > 0 else count
        buckets: dict[str, list] = {}
        for q in filtered:
            buckets.setdefault(q.topic, []).append(q)
        selected = []
        for t in topics:
            selected.extend(buckets[t][:per_topic])
        # Fill remaining slots with any leftover questions
        used_ids = {q.id for q in selected}
        for q in filtered:
            if len(selected) >= count:
                break
            if q.id not in used_ids:
                selected.append(q)
                used_ids.add(q.id)
        return selected[:count]

    random.shuffle(filtered)
    return filtered[:count]


# Dimension name -> canonical key used in the report and direction mapping
DIMENSIONS = {
    "Python": "编程基础",
    "Math": "数学基础",
    "Machine Learning": "机器学习",
    "Deep Learning": "深度学习",
    "Large Language Models": "大模型应用",
    "Project": "项目经验",
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
    """Map per-dimension scores to a recommended career direction."""
    ml = dim_scores.get("机器学习", 0)
    dl = dim_scores.get("深度学习", 0)
    llm = dim_scores.get("大模型应用", 0)
    prog = dim_scores.get("编程基础", 0)
    data = dim_scores.get("数学基础", 0)

    # Strongest axis wins, with sensible career mapping.
    candidates = [
        ("大模型应用开发", llm),
        ("机器学习工程师", ml),
        ("深度学习工程师", dl),
        ("数据科学家", max(data, prog)),
    ]
    candidates.sort(key=lambda x: x[1], reverse=True)
    best, best_score = candidates[0]

    # Tie-break: if LLM and ML are close, prefer the one with higher absolute score.
    return best if best_score > 0 else "AI 应用开发"


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
        if q.topic not in topic_stats:
            topic_stats[q.topic] = {"correct": 0, "total": 0}
        topic_stats[q.topic]["total"] += 1
        if ans == q.correct_answer:
            correct += 1
            topic_stats[q.topic]["correct"] += 1

    # Per-dimension scores (0-100)
    dim_scores: dict[str, int] = {}
    for topic, stats in topic_stats.items():
        cn = DIMENSIONS.get(topic, topic)
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
    # Fixed order for a stable radar chart
    order = ["编程基础", "数学基础", "机器学习", "深度学习", "大模型应用", "项目经验"]
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
    path = PROCESSED_DIR / "ability_report.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

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
