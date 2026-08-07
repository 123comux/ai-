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


def recommend_courses(
    interest: str,
    limit: int = 10,
    topic: Optional[str] = None,
) -> list[dict]:
    """Recommend real courses based on user interest (Chinese-friendly keyword match).

    Args:
        interest: User's interest text (e.g. "大模型" / "LLM" / "机器学习")
        limit: Max number of recommendations
        topic: Optional topic filter (exact topic key)

    Returns:
        List of recommended courses with match scores (0-1)
    """
    courses = _load_courses()
    if not courses:
        return []

    interest_lower = (interest or "").lower()

    # Build a searchable text per course: title + topic + description
    results = []
    for c in courses:
        title = c.get("title", "")
        topic_key = c.get("topic", "")
        desc = c.get("description", "")

        # Topic filter (explicit)
        if topic and topic_key.lower() != topic.lower():
            continue

        # Determine which topic the interest maps to (via aliases)
        matched_topic_key = None
        for key, aliases in _TOPIC_ALIASES.items():
            if any(alias in interest_lower for alias in aliases):
                matched_topic_key = key
                break

        score = 0.0
        if matched_topic_key is not None and topic_key == matched_topic_key:
            score = 1.0
        elif interest_lower and topic_key.lower() == interest_lower:
            score = 1.0
        elif matched_topic_key is None:
            # interest didn't map to a specific topic: keyword match across all
            if interest_lower and interest_lower in title.lower():
                score = 0.9
            elif interest_lower and interest_lower in desc.lower():
                score = 0.7
        # else: interest mapped to a topic, this course belongs to another topic
        # -> give a low "related" score so we can still pad the list

        if score == 0:
            # Related courses (different topic but same family) get a small bump;
            # unrelated courses stay at a base low score to fill the list.
            score = 0.3 if matched_topic_key is not None else 0.15

        results.append({
            "id": c.get("id", ""),
            "title": title,
            "topic": topic_key,
            "source": c.get("source", "catalog"),
            "difficulty": c.get("difficulty", ""),
            "score": score,
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
