"""微信订阅消息推送：access_token 缓存 + subscribeMessage.send + 业务通知封装。

前提：小程序后台已申请订阅消息模板并把 template_id 填入 backend/.env。
模板 ID 未配置（空）时所有发送函数静默跳过，不抛错、不影响主流程。
"""
import logging
import time

import requests

from config import (
    WECHAT_APPID, WECHAT_SECRET, WX_ACCESS_TOKEN_URL, WX_SUBSCRIBE_SEND_URL,
    WX_SUB_TEMPLATE_CHECKIN, WX_SUB_TEMPLATE_HOMEWORK, WX_SUB_TEMPLATE_LEARNING,
)

logger = logging.getLogger(__name__)

# access_token 缓存：{token, expires_at}，提前 5 分钟过期刷新
_token_cache = {"token": "", "expires_at": 0}


def get_access_token() -> str:
    """获取并缓存微信小程序 access_token（有效期 7200s）。"""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]
    if not WECHAT_APPID or not WECHAT_SECRET:
        return ""
    resp = requests.get(WX_ACCESS_TOKEN_URL, params={
        "grant_type": "client_credential",
        "appid": WECHAT_APPID,
        "secret": WECHAT_SECRET,
    }, timeout=10)
    data = resp.json()
    token = data.get("access_token", "")
    if not token:
        logger.warning("[wxmsg] get_access_token failed: %s", data.get("errmsg", data))
        return ""
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + int(data.get("expires_in", 7200)) - 300
    return token


def send_subscribe_message(openid: str, template_id: str, data: dict, page: str = "") -> bool:
    """发送一条订阅消息。返回是否成功发送（模板未配置/无 openid 视为跳过并返回 False）。"""
    if not openid or not template_id:
        return False
    token = get_access_token()
    if not token:
        logger.warning("[wxmsg] skip send (no access_token), openid=%s", openid)
        return False
    payload = {
        "touser": openid,
        "template_id": template_id,
        "page": page,
        "data": data,
    }
    try:
        resp = requests.post(
            WX_SUBSCRIBE_SEND_URL + "?access_token=" + token,
            json=payload,
            timeout=10,
        )
        res = resp.json()
        if res.get("errcode") not in (0, None):
            # 43101=用户未订阅/取消订阅，属正常；其余记日志
            logger.warning("[wxmsg] send errcode=%s errmsg=%s openid=%s", res.get("errcode"), res.get("errmsg"), openid)
        return res.get("errcode") == 0
    except Exception as e:  # noqa: BLE001 —— 推送失败不影响主流程
        logger.warning("[wxmsg] send exception: %s", e)
        return False


# ---------- 业务通知封装 ----------

def notify_checkin(user: dict, streak: int) -> bool:
    """打卡成功提醒：模板字段 thing1=打卡成功，number2=连续天数。"""
    if not WX_SUB_TEMPLATE_CHECKIN:
        return False
    return send_subscribe_message(
        user.get("openid", ""), WX_SUB_TEMPLATE_CHECKIN,
        {
            "thing1": {"value": "今日 AI 学习打卡成功"},
            "number2": {"value": streak},
        },
        page="pages/community/index",
    )


def notify_homework_result(user: dict, stage: int, score: float, passed: bool) -> bool:
    """作业评审结果通知：模板字段 thing1=阶段作业，phrase2=通过/未通过，number3=评分。"""
    if not WX_SUB_TEMPLATE_HOMEWORK:
        return False
    stage_names = {1: "认知", 2: "入门", 3: "进阶", 4: "实战", 5: "熟练"}
    name = stage_names.get(stage, f"第{stage}阶段")
    return send_subscribe_message(
        user.get("openid", ""), WX_SUB_TEMPLATE_HOMEWORK,
        {
            "thing1": {"value": f"{name}阶段作业评审完成"},
            "phrase2": {"value": "通过" if passed else "未通过（可重交）"},
            "number3": {"value": int(score)},
        },
        page="pages/deposit/index",
    )


def notify_learning_milestone(user: dict, message: str) -> bool:
    """学习里程碑提醒（完课/连续天数等）：模板字段 thing1=提醒内容。"""
    if not WX_SUB_TEMPLATE_LEARNING:
        return False
    return send_subscribe_message(
        user.get("openid", ""), WX_SUB_TEMPLATE_LEARNING,
        {"thing1": {"value": message[:20]}},
        page="pages/home/index",
    )
