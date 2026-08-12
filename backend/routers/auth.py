"""Auth API router: WeChat mini-program login + token issuance."""

import json
import os
import uuid
import urllib.request
import urllib.parse
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel

from config import WECHAT_APPID, WECHAT_SECRET, WECHAT_CODE2SESSION_URL, DEV_MODE
from database import get_user_by_openid, create_user, get_user, update_user_profile
from auth_utils import create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 上传头像存储目录（main.py 已把 /static 挂载为静态目录）
AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "avatars")
ALLOWED_AVATAR_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class WechatLoginRequest(BaseModel):
    code: str
    nickname: str = ""
    avatar: str = ""


class UpdateProfileRequest(BaseModel):
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


@router.put("/profile")
async def update_profile(body: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    """更新当前用户资料（昵称/头像）。

    昵称/头像来自微信"头像昵称填写能力"（基础库 2.21.2+）：
    前端用 <button open-type="chooseAvatar"> 获取头像、<input type="nickname"> 获取昵称，
    用户主动选择后再回传本接口落库。生产环境头像需先上传到自有服务器/CDN 再回传 URL。
    """
    nickname = (body.nickname or "").strip()[:30]
    avatar = (body.avatar or "").strip()
    update_user_profile(user["id"], nickname, avatar)
    updated = get_user(user["id"])
    return {
        "ok": True,
        "user": {
            "id": updated["id"],
            "openid": updated["openid"],
            "nickname": updated["nickname"],
            "avatar": updated["avatar"],
        },
    }


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """上传头像文件到本地 static 目录，返回可持久访问的相对 URL。

    微信 chooseAvatar 返回的是临时路径（会话结束后失效），
    前端需先上传换取永久 URL，再调 PUT /auth/profile 落库。
    生产环境应改为上传到云存储/CDN。
    """
    ext = os.path.splitext((file.filename or "").lower())[1]
    if ext not in ALLOWED_AVATAR_EXTS:
        raise HTTPException(status_code=400, detail="仅支持 jpg/jpeg/png/webp/gif 图片")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="头像不能超过 2MB")
    os.makedirs(AVATAR_DIR, exist_ok=True)
    fname = f"{user['id']}_{uuid.uuid4().hex}{ext}"
    with open(os.path.join(AVATAR_DIR, fname), "wb") as f:
        f.write(content)
    return {"ok": True, "avatar_url": f"/static/avatars/{fname}"}
