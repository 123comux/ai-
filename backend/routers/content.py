"""
Public Content API - serves dynamic content to frontend.
Eliminates hard-coded data from frontend pages.

Also provides FAQ public API for the learning community.
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


# ============ 提示词模板库（四大场景，直接复制即用） ============

PROMPT_TEMPLATES = [
    # 学生专用
    {"category": "学生", "title": "写作业/作业解答", "template": "你是一名优秀的{学科}老师。请帮我解答这道题：{题目}。要求：分步骤讲解、给出答案、说明解题思路。"},
    {"category": "学生", "title": "写报告/总结", "template": "请帮我写一份关于《{主题}》的{字数}字报告，要求：结构清晰、数据详实、结论明确。"},
    {"category": "学生", "title": "复盘总结", "template": "请帮我复盘{事件/活动}，要求：分析做得好的地方、待改进之处、下次的改进计划。"},
    {"category": "学生", "title": "论文润色", "template": "请帮我润色这段论文：{文本}。要求：语言更学术、逻辑更连贯、保持原意。"},
    # 职场专用
    {"category": "职场", "title": "写周报", "template": "请帮我写本周工作总结。本周完成：{事项}。格式：本周完成/下周计划/需要支持。"},
    {"category": "职场", "title": "写方案", "template": "请帮我写一份《{项目}》方案，目标：{目标}。要求：背景分析、方案设计、实施步骤、预算。"},
    {"category": "职场", "title": "写话术", "template": "请帮我写一段{场景}话术，对象：{对象}。语气：{语气}。要达成的目标：{目标}。"},
    {"category": "职场", "title": "工作总结", "template": "请帮我写工作总结，背景：{工作内容}。要求：突出成果、数据量化、总结不足。"},
    # 编程专用
    {"category": "编程", "title": "代码纠错", "template": "请帮我找出这段代码的问题：{代码}。要求：指出 bug、说明原因、给出修复后的代码。"},
    {"category": "编程", "title": "代码解释", "template": "请解释这段代码的功能：{代码}。要求：逐行/分块解释、说明用到的技术。"},
    {"category": "编程", "title": "生成注释", "template": "请为这段代码生成注释：{代码}。要求：中文注释、解释每个函数和关键逻辑。"},
    {"category": "编程", "title": "写函数", "template": "请用{语言}写一个函数，功能：{需求}。要求：考虑边界情况、附测试用例。"},
    # 面试求职
    {"category": "求职", "title": "简历优化", "template": "请帮我优化这份简历：{简历内容}。要求：突出亮点、量化成果、符合{目标岗位}要求。"},
    {"category": "求职", "title": "面试话术", "template": "请帮我准备{岗位}面试，常见问题：{问题}。要求：给出参考答案、要点提示。"},
    {"category": "求职", "title": "自我介绍", "template": "请帮我写一段{时长}的自我介绍，应聘：{岗位}。突出：{优势}。"},
]


@router.get("/prompt-templates")
def get_prompt_templates(category: str = ""):
    """Get prompt templates, optionally filtered by category (学生/职场/编程/求职)."""
    if category:
        return [t for t in PROMPT_TEMPLATES if t["category"] == category]
    return PROMPT_TEMPLATES


@router.get("/prompt-templates/categories")
def get_prompt_categories():
    """Get available template categories."""
    cats = list(dict.fromkeys(t["category"] for t in PROMPT_TEMPLATES))
    return {"categories": cats}


# ============ FAQ 常见问题库（公开接口） ============
from pydantic import BaseModel

@router.get("/faq")
def get_faq(category: str = ""):
    """获取 FAQ 常见问题列表（公开接口，无需登录）。"""
    if category:
        return query_all("faq_items", {"category": category, "is_active": 1}, "sort_order")
    return query_all("faq_items", {"is_active": 1}, "sort_order")


@router.get("/faq/categories")
def get_faq_categories():
    """获取 FAQ 分类列表。"""
    from database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM faq_items WHERE is_active=1 ORDER BY category").fetchall()
    conn.close()
    return {"categories": [r["category"] for r in rows]}