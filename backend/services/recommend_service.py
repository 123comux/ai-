"""Course recommendation service.

Recommends real courses from the course catalog based on keyword/topic
matching. Falls back gracefully if the old TF-IDF model is unavailable.
"""

import json
from pathlib import Path
from typing import Optional

from config import PROCESSED_DIR


def _load_courses() -> list[dict]:
    """Load the real course catalog."""
    path = PROCESSED_DIR / "enriched_courses.json"
    if not path.exists():
        path = PROCESSED_DIR / "courses.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# topic key -> 中文话题别名（用于关键词匹配）
_TOPIC_ALIASES = {
    "Machine Learning": ["机器学习", "machine learning", "ml"],
    "Deep Learning": ["深度学习", "deep learning", "神经网络", "neural"],
    "Large Language Models": ["大模型", "llm", "大语言模型", "langchain", "rag", "agent"],
    "NLP": ["自然语言", "nlp", "文本", "词向量", "bert"],
    "Data Science": ["数据科学", "数据分析", "data science", "pandas", "sql"],
    "Python": ["python", "编程", "编程与工具"],
    "Computer Vision": ["计算机视觉", "cv", "图像", "目标检测", "opencv"],
    "Reinforcement Learning": ["强化学习", "rl", "q-learning", "dqn"],
}

# BERT 预测 topic_key -> 课程 topic key（用于 AI 分析后的课程命中）
_BERT_TOPIC_TO_COURSE = {
    "machine_learning": "Machine Learning",
    "deep_learning": "Deep Learning",
    "data_science": "Data Science",
    "programming": "Python",
    "math_stats": "Data Science",
    "llm": "Large Language Models",
    "nlp": "NLP",
    "computer_vision": "Computer Vision",
    "reinforcement_learning": "Reinforcement Learning",
}


def _ai_analyze(interest: str) -> tuple[str | None, float]:
    """Use the BERT assessment model to analyze the interest text.

    Returns (course topic key | None, confidence). Falls back to (None, 0.0)
    when the AI model isn't available so recommendation never breaks.
    """
    try:
        from services.assessment_ai_service import analyze_content
        result = analyze_content(interest)
        topic_key = result.get("topic_key", "")
        confidence = float(result.get("confidence", 0.0))
        course_topic = _BERT_TOPIC_TO_COURSE.get(topic_key)
        return course_topic, confidence
    except Exception:
        return None, 0.0


def recommend_courses_keyword_only(
    interest: str,
    limit: int = 10,
    topic: Optional[str] = None,
) -> list[dict]:
    """Pure keyword-based recommendation, used for fast responses."""
    return _recommend(interest=interest, limit=limit, topic=topic, use_ai=False)


def recommend_courses(
    interest: str,
    limit: int = 10,
    topic: Optional[str] = None,
) -> list[dict]:
    """Recommend real courses based on user interest (keyword + alias matching).

    Deliberately does NOT call the BERT model: cold-load takes ~107s and its
    Chinese classification is unreliable, which would make recommendation slow
    and inaccurate. Keyword/alias matching is fast and accurate for the known
    course topics.

    Args:
        interest: User's interest text (e.g. "大模型" / "LLM" / "机器学习")
        limit: Max number of recommendations
        topic: Optional topic filter (exact topic key)

    Returns:
        List of recommended courses with match scores (0-1)
    """
    return _recommend(interest=interest, limit=limit, topic=topic, use_ai=False)


def _recommend(
    interest: str,
    limit: int = 10,
    topic: Optional[str] = None,
    use_ai: bool = False,
) -> list[dict]:
    courses = _load_courses()
    if not courses:
        return []

    interest_lower = (interest or "").lower()

    # AI 分析已弃用（BERT 冷加载 107s + 分类不准），保持 use_ai 参数仅为兼容，
    # 实际始终走关键词匹配。
    ai_topic = None
    ai_confidence = 0.0

    # Determine which topic the interest maps to (via aliases, as fallback)
    matched_topic_key = None
    for key, aliases in _TOPIC_ALIASES.items():
        if any(alias in interest_lower for alias in aliases):
            matched_topic_key = key
            break
    # BERT 结果优先于关键词别名（AI 更准）
    effective_topic = ai_topic or matched_topic_key

    results = []
    for c in courses:
        title = c.get("title", "")
        topic_key = c.get("topic", "")
        desc = c.get("description", "")

        # Topic filter (explicit)
        if topic and topic_key.lower() != topic.lower():
            continue

        score = 0.0
        if effective_topic is not None and topic_key == effective_topic:
            # BERT/关键词命中目标方向：分数随 AI confidence 加权
            score = 0.85 + 0.15 * ai_confidence if ai_topic else 1.0
        elif interest_lower and topic_key.lower() == interest_lower:
            score = 1.0
        elif effective_topic is None:
            # interest 没映射到明确方向：跨所有课程关键词匹配
            if interest_lower and interest_lower in title.lower():
                score = 0.9
            elif interest_lower and interest_lower in desc.lower():
                score = 0.7
        # else: interest mapped to a topic, this course belongs to another
        # -> keep low score to pad the list

        if score == 0:
            score = 0.3 if effective_topic is not None else 0.15

        results.append({
            "id": c.get("id", ""),
            "title": title,
            "topic": topic_key,
            "source": c.get("source", "catalog"),
            "difficulty": c.get("difficulty", ""),
            "score": round(score, 3),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return [r for r in results if r["score"] > 0][:limit]


def get_model_info() -> dict:
    """Get recommender info."""
    courses = _load_courses()
    return {
        "total_items": len(courses),
        "model_type": "课程目录关键词匹配",
        "status": "available",
    }
