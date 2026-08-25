"""功能使用权限服务：5 天免费试用 → 缴纳押金解锁。

安全设计（防止客户端时间篡改 / 保证状态一致）：
- 试用期起点 trial_started_at 只由**服务端**在首次确认到该用户请求时写入
  （首次打开小程序或首次使用任一功能，视哪个先到达服务端而定），客户端提交的时间一律忽略。
- 所有试用期倒计时均用**服务端当前时间**计算，与用户设备时钟无关；改本地时间无法延长试用。
- 押金状态每次实时从 user_deposits 读取：缴纳押金（active）后下一次校验即为已解锁，
  天然保证"押金缴纳状态 与 功能权限状态 实时同步一致"，无需额外同步流程。
- 全局 HTTP 中间件为**非豁免路径**的统一授权校验（覆盖全部功能模块，一处生效）；
  /api/auth、/api/access、/api/deposit、/api/pay、/api/admin、/static、/health 等豁免。
- 未携带 / 持有无效 Bearer token 的请求放行给各路由自行处理（公开接口放行、
  需登录的接口由 get_current_user 返回 401），不改变现有公开接口语义。
"""

from datetime import datetime, timedelta
from typing import Callable, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from config import (
    ACCESS_ALL_FREE,
    ACCESS_EXEMPT_PREFIXES,
    ACCESS_TRIAL_DAYS,
    ACCESS_TRIAL_WARN_SECONDS,
    DEPOSIT_UNLOCKED_STATUSES,
)
from database import get_deposit, get_user_access, upsert_user_access

TS_FMT = "%Y-%m-%d %H:%M:%S"


def _parse_dt(value: str) -> Optional[datetime]:
    try:
        return datetime.strptime(value, TS_FMT) if value else None
    except ValueError:
        return None


def compute_access(
    now: datetime,
    trial_started_at: Optional[datetime],
    deposit_paid: bool,
) -> dict:
    """纯函数：由服务端时间、试用期起点、押金状态计算当前权限。

    边界约定（对齐需求 2/7）：
    - 剩余试用秒数 == 0 即视为试用结束（最后一天到期后立即锁定，跨零点/到期瞬间即失效）。
    - 试用剩余 0 < remaining <= WARN_SECONDS 时置 warn_expiring，供客户端提前提醒。
    - 押金已缴纳（deposit_paid）→ access_granted 恒为 True，与试用期无关。
    - ACCESS_ALL_FREE=true 时关闭收费墙：所有用户一律 access_granted（演示/公测阶段）。
    """
    if ACCESS_ALL_FREE:
        return {
            "in_trial": True,
            "deposit_paid": deposit_paid,
            "access_granted": True,
            "warn_expiring": False,
            "trial_remaining_seconds": 0,
            "trial_end_at": None,
        }
    if trial_started_at is None:
        # 全新用户：尚未确认试用起点（调用方随后用服务端时间落库）
        remaining = ACCESS_TRIAL_DAYS * 86400.0
        in_trial = True
        trial_end = None
    else:
        trial_end = trial_started_at + timedelta(days=ACCESS_TRIAL_DAYS)
        remaining = (trial_end - now).total_seconds()
        in_trial = remaining > 0
    access_granted = in_trial or deposit_paid
    warn_expiring = in_trial and 0 < remaining <= ACCESS_TRIAL_WARN_SECONDS
    return {
        "in_trial": in_trial,
        "deposit_paid": deposit_paid,
        "access_granted": access_granted,
        "warn_expiring": warn_expiring,
        "trial_remaining_seconds": max(int(remaining), 0),
        "trial_end_at": trial_end.strftime(TS_FMT) if trial_end else None,
    }


def resolve_access(user_id: int, now: Optional[datetime] = None) -> dict:
    """确认试用起点（无记录则用服务端时间落库，幂等只写一次）→ 计算并返回权限状态。

    不存在的试用记录不会导致崩溃——全新用户直接按"试用期内"处理并落库。
    """
    now = (now or datetime.now()).replace(microsecond=0)
    row = get_user_access(user_id)
    started = _parse_dt(row["trial_started_at"]) if row else None
    if started is None:
        started = now
        try:
            upsert_user_access(user_id, {"trial_started_at": now.strftime(TS_FMT)})
        except Exception:
            # 落库失败不阻塞请求：按未落库的新用户（试用中）放行，下次再补记
            pass
    deposit = get_deposit(user_id)
    deposit_paid = bool(deposit and deposit.get("status") in DEPOSIT_UNLOCKED_STATUSES)
    state = compute_access(now, started, deposit_paid)
    # 后台人工覆盖：'lock' 强制锁定、'unlock' 强制解锁，空串保持派生规则（仅核对用户本人/deposit）
    if row and row.get("admin_override") == "lock":
        state["access_granted"] = False
    elif row and row.get("admin_override") == "unlock":
        state["access_granted"] = True
        state["in_trial"] = True
        trial_end = started + timedelta(days=36500)  # 覆盖解锁视为长期授权
        state["trial_end_at"] = trial_end.strftime(TS_FMT)
        state["trial_remaining_seconds"] = int((trial_end - now).total_seconds())
    state["admin_override"] = row.get("admin_override", "") if row else ""
    state["user_id"] = user_id
    state["trial_started_at"] = started.strftime(TS_FMT)
    state["server_time"] = now.strftime(TS_FMT)
    return state


async def access_control_middleware(request: Request, call_next: Callable):
    """全局权限校验中间件：非豁免路径 + 已登录用户 → 未解锁则 403（结构化 fail）。

    返回结构：{"detail": {"code": "access_denied", "message": "...", "access": {...}}}
    前端识别 code=access_denied 后展示"试用期已结束 → 缴纳押金"的引导界面。
    """
    path = request.url.path
    if path.startswith(ACCESS_EXEMPT_PREFIXES):
        return await call_next(request)
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return await call_next(request)
    from auth_utils import verify_token
    user_id = verify_token(auth.split(" ", 1)[1].strip())
    if user_id is None:
        return await call_next(request)
    state = resolve_access(user_id)
    if state["access_granted"]:
        return await call_next(request)
    return JSONResponse(
        status_code=403,
        content={
            "detail": {
                "code": "access_denied",
                "message": "免费试用期已结束，缴纳押金即可解锁全部功能",
                "access": state,
            }
        },
    )