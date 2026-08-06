"""
CMS Admin Panel - serves the admin HTML page.
"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/admin", tags=["admin_panel"])

ADMIN_HTML = os.path.join(os.path.dirname(__file__), "admin_panel.html")


@router.get("", response_class=HTMLResponse)
def admin_panel():
    """Serve the admin panel HTML page."""
    if os.path.exists(ADMIN_HTML):
        with open(ADMIN_HTML, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(404, "Admin panel not found")