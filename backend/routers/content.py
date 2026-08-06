"""
Public Content API - serves dynamic content to frontend.
Eliminates hard-coded data from frontend pages.
"""
from fastapi import APIRouter

from database import query_all

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/banners")
def get_banners():
    """Get active banners for home page carousel."""
    return query_all("banners", {"is_active": 1}, "sort_order")


@router.get("/directions")
def get_directions():
    """Get active learning directions for home page."""
    return query_all("directions", {"is_active": 1}, "sort_order")


@router.get("/menu-items")
def get_menu_items(section: str = "mine"):
    """Get menu items for a section."""
    return query_all("menu_items", {"section": section, "is_active": 1}, "sort_order")