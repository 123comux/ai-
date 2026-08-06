"""Learning paths API router."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from models.schemas import LearningPathItem

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
router = APIRouter(prefix="/api/learning-paths", tags=["learning-paths"])


def _load_paths() -> list[LearningPathItem]:
    # Try enriched data first, fall back to original
    path = PROCESSED_DIR / "enriched_learning_paths.json"
    if not path.exists():
        path = PROCESSED_DIR / "learning_paths.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [LearningPathItem(**p) for p in data]


@router.get("", response_model=list[LearningPathItem])
async def list_paths():
    """List all learning paths."""
    return _load_paths()


@router.get("/{path_id}", response_model=LearningPathItem)
async def get_path(path_id: str):
    """Get a single learning path by ID."""
    items = _load_paths()
    for p in items:
        if p.id == path_id:
            return p
    raise HTTPException(status_code=404, detail="Learning path not found")