"""Auth API router: WeChat mini-program login + token issuance."""

import json
import urllib.request
import urllib.parse
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from config import WECHAT_APPID, WECHAT_SECRET, WECHAT_CODE2SESSION_URL, DEV_MODE
from database import get_user_by_openid, create_user, get_user
from auth_utils import create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class WechatLoginRequest(BaseModel):
    code: str
    nickname: str = ""
    avatar: str = ""


def _code2session(code: str) -> dict:
    """Call WeChat jscode2session. Returns dict with openid/session_key/unionid or errcode."""
    params = urllib.parse.urlencode({
        "appid": WECHAT_APPID,
        "secret": WECHAT_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    })
    url = f"{WECHAT_CODE2SESSION_URL}?{params}"
    with urllib.request.urlopen(url, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _resolve_user(code: str, nickname: str, avatar: str) -> dict:
    """Resolve (create or fetch) the user for a login code.

    In DEV_MODE (or when AppID/Secret are not configured) any code is accepted
    and mapped to a deterministic dev openid, so the app is fully usable locally.
    """
    if DEV_MODE or not WECHAT_APPID or not WECHAT_SECRET:
        openid = f"dev_{code}"
        user = get_user_by_openid(openid)
        if user is None:
            user = create_user(
                openid=openid,
                nickname=nickname or f"体验用户_{code[-4:]}",
                avatar=avatar or "",
            )
        return user

    # Real WeChat login
    wx = _code2session(code)
    if "errcode" in wx and wx["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"微信登录失败: {wx.get('errmsg', 'unknown')}",
        )
    openid = wx.get("openid")
    if not openid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="微信未返回 openid")
    unionid = wx.get("unionid", "")
    user = get_user_by_openid(openid)
    if user is None:
        user = create_user(
            openid=openid,
            unionid=unionid,
            nickname=nickname or "微信用户",
            avatar=avatar or "",
        )
    return user


@router.post("/wechat-login")
async def wechat_login(body: WechatLoginRequest):
    """Exchange a WeChat login code for a signed token + user profile."""
    if not body.code:
        raise HTTPException(status_code=400, detail="缺少登录 code")
    user = _resolve_user(body.code, body.nickname, body.avatar)
    token = create_token(user["id"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "openid": user["openid"],
            "nickname": user["nickname"],
            "avatar": user["avatar"],
        },
    }


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return {
        "id": user["id"],
        "openid": user["openid"],
        "nickname": user["nickname"],
        "avatar": user["avatar"],
    }
