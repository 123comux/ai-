"""Knowledge base API router."""

from fastapi import APIRouter, HTTPException, Query

from models.schemas import KnowledgeItem, KnowledgeResponse
from services.knowledge_service import load_knowledge_base, query_knowledge, get_topics

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/search", response_model=KnowledgeResponse)
async def search_knowledge(
    query: str = Query(..., description="Search query"),
    topic: str = Query(None, description="Filter by topic"),
    limit: int = Query(10, ge=1, le=100),
):
    """Search the knowledge base."""
    return query_knowledge(query, topic, limit)


@router.get("/topics")
async def list_topics():
    """List all available topics."""
    return {"topics": get_topics()}


@router.get("/count")
async def count_knowledge():
    """Get total knowledge item count."""
    items = load_knowledge_base()
    return {"total": len(items)}


@router.get("/browse", response_model=list[KnowledgeItem])
async def browse_knowledge(
    topic: str = Query(None, description="Filter by topic"),
    source: str = Query(None, description="Filter by source dataset"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Browse knowledge base with pagination."""
    items = load_knowledge_base()

    filtered = items
    if topic:
        filtered = [i for i in filtered if i.topic.lower() == topic.lower()]
    if source:
        filtered = [i for i in filtered if i.source.lower() == source.lower()]

    return filtered[offset:offset + limit]