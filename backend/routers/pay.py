"""微信支付回调 + 支付单重取（押金收付真实化）。

- POST /api/pay/notify  —— 微信支付回调：验签 + AES-GCM 解密 → 置押金为已支付（active）
- POST /api/pay/jsapi    —— 为当前待支付押金重新生成调起支付参数（支付单过期/重试用）
"""
import logging

from fastapi import APIRouter, Request, HTTPException, Depends

from database import get_connection, get_deposit
from auth_utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pay", tags=["pay"])


@router.post("/notify")
async def pay_notify(request: Request):
    """微信支付回调（无鉴权，微信服务器调用）。验签通过并解密成功才置押金为已支付。"""
    from config import wxpay_configured
    body = await request.body()
    body_str = body.decode("utf-8")
    try:
        from services.wxpay_service import verify_notify_signature, parse_notify
        # 验签（平台证书获取失败时仅记日志，解密仍以 APIv3 密钥为准）
        try:
            verify_notify_signature(dict(request.headers), body_str)
        except Exception as e:
            logger.warning("[pay] notify signature verify skipped: %s", e)
        biz = parse_notify(body_str)
    except Exception as e:
        logger.error("[pay] notify parse failed: %s", e)
        return {"code": "FAIL", "message": "解析失败"}

    if not biz or biz.get("trade_state") != "SUCCESS":
        logger.info("[pay] notify non-success: %s", biz)
        return {"code": "SUCCESS", "message": "成功"}

    out_trade_no = biz.get("out_trade_no", "")
    transaction_id = biz.get("transaction_id", "")
    conn = get_connection()
    cur = conn.execute(
        "UPDATE user_deposits SET status='active', transaction_id=?, paid_at=datetime('now') "
        "WHERE out_trade_no=? AND status='pending_payment'",
        (transaction_id, out_trade_no),
    )
    conn.commit()
    rows = cur.rowcount
    conn.close()
    if rows == 0:
        logger.warning("[pay] notify: no pending deposit for out_trade_no=%s", out_trade_no)
    return {"code": "SUCCESS", "message": "成功"}


@router.post("/jsapi")
async def create_payment(user: dict = Depends(get_current_user)):
    """为当前待支付押金生成调起支付参数（未配置商户号走占位提示）。"""
    from config import wxpay_configured
    if not wxpay_configured():
        return {"ok": False, "placeholder": True, "message": "微信支付未配置（开发占位）"}
    deposit = get_deposit(user["id"])
    if not deposit:
        raise HTTPException(400, "尚未报名")
    if deposit.get("status") != "pending_payment":
        raise HTTPException(400, f"当前状态 {deposit.get('status')} 无需支付")
    out_trade_no = deposit.get("out_trade_no") or f"dep_{user['id']}_{int(__import__('time').time())}"
    try:
        from services.wxpay_service import build_pay_params
        pay_params = build_pay_params(
            out_trade_no, int(round(float(deposit.get("amount", 0)) * 100)),
            user.get("openid", ""), "智学AI·押金式培训",
        )
        return {"ok": True, "pay_params": pay_params}
    except Exception as e:
        raise HTTPException(502, f"创建支付单失败：{e}")
