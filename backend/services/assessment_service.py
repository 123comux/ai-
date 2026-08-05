"""Assessment service - generates and scores assessments."""

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
    """Get a random set of assessment questions."""
    all_q = load_questions()

    if topic:
        filtered = [q for q in all_q if q.topic.lower() == topic.lower()]
    else:
        filtered = all_q

    if not filtered:
        return []

    random.shuffle(filtered)
    return filtered[:count]


def score_assessment(answers: list[int], question_ids: list[str]) -> AssessmentResult:
    """Score assessment answers and generate result."""
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

    # Determine level
    ratio = correct / total if total > 0 else 0
    if ratio >= 0.9:
        level = "expert"
    elif ratio >= 0.7:
        level = "advanced"
    elif ratio >= 0.5:
        level = "intermediate"
    else:
        level = "beginner"

    # Determine strengths and weaknesses
    strengths = []
    weaknesses = []
    for topic, stats in topic_stats.items():
        if stats["total"] > 0:
            topic_ratio = stats["correct"] / stats["total"]
            if topic_ratio >= 0.7:
                strengths.append(topic)
            else:
                weaknesses.append(topic)

    # Recommended direction
    if "Machine Learning" in strengths or "AI/ML" in strengths:
        recommended = "Machine Learning Engineer"
    elif "Programming" in strengths:
        recommended = "AI Developer"
    elif "Data Science" in strengths:
        recommended = "Data Scientist"
    else:
        recommended = "AI Engineer"

    return AssessmentResult(
        score=correct,
        total=total,
        level=level,
        strengths=strengths,
        weaknesses=weaknesses,
        recommended_direction=recommended,
    )