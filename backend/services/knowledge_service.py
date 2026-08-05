"""Knowledge base service - loads and queries processed data."""

import json
from pathlib import Path
from typing import Optional

from models.schemas import KnowledgeItem, KnowledgeResponse

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

_knowledge_base: list[KnowledgeItem] | None = None


def load_knowledge_base() -> list[KnowledgeItem]:
    """Load knowledge base from processed data."""
    global _knowledge_base
    if _knowledge_base is not None:
        return _knowledge_base

    path = PROCESSED_DIR / "knowledge_base.json"
    if not path.exists():
        _knowledge_base = []
        return _knowledge_base

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _knowledge_base = [KnowledgeItem(**item) for item in data]
    return _knowledge_base


def query_knowledge(query: str, topic: Optional[str] = None, limit: int = 10) -> KnowledgeResponse:
    """Query knowledge base by keyword matching."""
    items = load_knowledge_base()

    query_lower = query.lower()
    results = []

    for item in items:
        # Filter by topic if specified
        if topic and item.topic.lower() != topic.lower():
            continue

        # Simple keyword matching in title and content
        if query_lower in item.title.lower() or query_lower in item.content.lower():
            results.append(item)

        # Also check tags
        if any(query_lower in tag.lower() for tag in item.tags):
            results.append(item)

    # Deduplicate
    seen = set()
    unique_results = []
    for r in results:
        if r.id not in seen:
            seen.add(r.id)
            unique_results.append(r)

    return KnowledgeResponse(
        results=unique_results[:limit],
        total=len(unique_results),
    )


def get_topics() -> list[str]:
    """Get all available topics."""
    items = load_knowledge_base()
    topics = sorted(set(item.topic for item in items if item.topic))
    return topics