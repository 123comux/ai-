"""功能使用权限接口：导语配置（公开）+ 试用/解锁状态查询。

供冷启动引导弹窗与页面提醒使用。路径前缀 /api/access 在 ACCESS_EXEMPT_PREFIXES 中，
即使试用期已结束也能正常读取状态，保证"锁定态用户能看到解锁入口"。"""

from fastapi import APIRouter, Depends

from config import (
    ACCESS_ALL_FREE,
    ACCESS_TRIAL_DAYS,
    ACCESS_TRIAL_WARN_SECONDS,
    DEPOSIT_CURRENCY,
    DEPOSIT_DEFAULT_AMOUNT,
    DEPOSIT_REFUND_WORKING_DAYS,
)
from auth_utils import get_current_user
from services.access_service import resolve_access
from services.ai_quota import ai_quota_remaining

router = APIRouter(prefix="/api/access", tags=["access"])

# 功能介绍图文（冷启动弹窗展示；图标用 emoji，不依赖外部图片资源，离线可用）
FEATURE_INTRO = [
    {"icon": "🧭", "title": "AI 能力测评", "desc": "10 分钟定位你的 AI 水平与推荐方向，生成专属能力报告"},
    {"icon": "📚", "title": "七阶段课程", "desc": "从大模型基础到求职备战，章节讲解 + 作业 + AI 评审"},
    {"icon": "🛠️", "title": "实战项目", "desc": "动手完成能写进简历的 AI Agent 项目，一步步带你做"},
    {"icon": "🗺️", "title": "学习路径", "desc": "按目标自动规划每日学习，进度一目了然"},
    {"icon": "🤖", "title": "AI 导师", "desc": "遇到问题随时提问，7×24 小时 AI 导师陪伴"},
    {"icon": "💼", "title": "求职匹配", "desc": "岗位要求全面解析，帮你补齐能力短板"},
]
# ACCESS_ALL_FREE=true（演示/公测）时导语变为全部免费；否则保留押金式培训流程说明。
if ACCESS_ALL_FREE:
    USAGE_INTRO = (
        "打开小程序 → 全部功能免费开放，无需付费即可使用 → 按学习路径完成七阶段课程与实战项目 → 达标后可申请能力认证。"
    )
else:
    USAGE_INTRO = (
        f"打开小程序 → 免费试用 {ACCESS_TRIAL_DAYS} 天全部功能自由体验 → 试用到期后缴纳押金 "
        f"¥{int(DEPOSIT_DEFAULT_AMOUNT)} 解锁持续使用 → 完成七阶段学习与考核达标后，押金全额原路退还。"
    )


def _config() -> dict:
    return {
        "trial_days": ACCESS_TRIAL_DAYS,
        "trial_warn_seconds": ACCESS_TRIAL_WARN_SECONDS,
        "deposit_amount": DEPOSIT_DEFAULT_AMOUNT,
        "currency": DEPOSIT_CURRENCY,
        "refund_rules": {
            "amount": "达标考核通过后押金全额原路退还",
            "timing": f"最终考核通过后 {DEPOSIT_REFUND_WORKING_DAYS} 个工作日内到账",
            "failed": "未达标：押金转为培训费，可续学一期",
            "anti_fraud": "同一身份限退费 1 次；考核含 AI 监考 + 人工复核",
        },
        "features": FEATURE_INTRO,
        "usage_intro": USAGE_INTRO,
    }


@router.get("/intro")
async def access_intro():
    """功能说明配置（公开）：冷启动弹窗在登录态确认前即可渲染。"""
    return _config()


@router.get("/status")
async def access_status(user: dict = Depends(get_current_user)):
    """当前用户的功能使用权限状态（服务端时间计算，客户端时间无法影响结果）。"""
    state = resolve_access(user["id"])
    state["ai_quota"] = ai_quota_remaining(user["id"])
    return {**state, "config": _config()}