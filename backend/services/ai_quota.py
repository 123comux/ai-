"""AI 每日额度限流：未缴押金用户设每日调用上限，已缴押金用户不限。

设计要点：
- 匿名（未登录）用户有请求打过来但无身份可追踪 → 不计数也不限流，保持原有公开行为
  （/api/assessment 等本就允许匿名测评；强制登录会破坏该语义）。
- 已缴押金（deposit_paid=True，含退费流程中/续学）用户不限流。
- 未缴押金的已登录用户（含 5 天试用期内）：今日所有 AI 功能总调用数 >=
  AI_DAILY_LIMIT_DEFAULT 时拒绝（429）。试用结束会被全局 access 中间件 403 拦截
  （/api/ai 相关路径非豁免前缀），此处限流覆盖"试用期内"与"试用结束但押金未缴"。
- fastapi.Depends 用法见 routers/ai.py。
"""

from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from config import AI_DAILY_LIMIT_DEFAULT, AI_FEATURES
from database import get_ai_usage_total, increment_ai_usage
from services.access_service import resolve_access


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def check_ai_quota(user: Optional[dict], feature: str, now: Optional[datetime] = None) -> dict:
    """检查并（未超限时）计入一次 AI 调用。

    返回该次调用应归属的用户（None 表示匿名，不计入）。超限时抛 429。
    feature 必须是 AI_FEATURES 之一。
    """
    if feature not in AI_FEATURES:
        feature = "tutor"  # 未知功能按导师计，防漏统计
    # 匿名用户无身份可追踪，不计数不限流
    if user is None:
        return None
    # 已缴押金（含退费流程中/续学）用户不限
    if resolve_access(user["id"], now)["deposit_paid"]:
        return user
    # 未缴押金：检查今日累计是否已达上限
    today = (now or datetime.now()).strftime("%Y-%m-%d")
    used = get_ai_usage_total(user["id"], today)
    if used >= AI_DAILY_LIMIT_DEFAULT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "ai_quota_exceeded",
                "message": f"今日 AI 免费额度已用完（{AI_DAILY_LIMIT_DEFAULT} 次）。缴纳押金即可无限使用，或明日再试。",
                "quota": {"used": used, "limit": AI_DAILY_LIMIT_DEFAULT, "date": today},
            },
        )
    increment_ai_usage(user["id"], today, feature)
    return user


def ai_quota_remaining(user_id: int, now: Optional[datetime] = None) -> dict:
    """查看某用户今日 AI 额度剩余（供状态接口展示）。"""
    if resolve_access(user_id, now)["deposit_paid"]:
        return {"limited": False, "used": 0, "limit": None}
    today = (now or datetime.now()).strftime("%Y-%m-%d")
    used = get_ai_usage_total(user_id, today)
    return {"limited": True, "used": used, "limit": AI_DAILY_LIMIT_DEFAULT, "remaining": max(AI_DAILY_LIMIT_DEFAULT - used, 0)}
