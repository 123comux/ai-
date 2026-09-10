"""Auth API router: WeChat mini-program login + token issuance."""

import json
import os
import re
import uuid
import urllib.request
import urllib.parse
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel

from config import WECHAT_APPID, WECHAT_SECRET, WECHAT_CODE2SESSION_URL, DEV_MODE, DEV_IMPERSONATE, H5_PHONE_LOGIN
from database import get_user_by_openid, create_user, get_user, update_user_profile, get_connection
from auth_utils import create_token, get_current_user
from fsx import save_avatar

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 头像上传存储目录（main.py 已把 /static 挂载为静态目录）
AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "avatars")
ALLOWED_AVATAR_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# 中国大陆手机号
PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


class WechatLoginRequest(BaseModel):
    code: str
    nickname: str = ""
    avatar: str = ""


class H5LoginRequest(BaseModel):
    phone: str
    nickname: str = ""


class UpdateProfileRequest(BaseModel):
    nickname: str = ""
    avatar: str = ""
    grade: str = ""
    major: str = ""
    target_direction: str = ""


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


def _user_payload(user: dict) -> dict:
    """统一的用户信息返回结构（小程序端 / 网页端登录共用，保证字段一致）。"""
    return {
        "id": user["id"],
        "openid": user["openid"],
        "nickname": user["nickname"],
        "avatar": user["avatar"],
        "grade": user.get("grade", ""),
        "major": user.get("major", ""),
        "target_direction": user.get("target_direction", ""),
    }


@router.post("/wechat-login")
async def wechat_login(body: WechatLoginRequest):
    """Exchange a WeChat login code for a signed token + user profile."""
    if not body.code:
        raise HTTPException(status_code=400, detail="缺少登录 code")
    user = _resolve_user(body.code, body.nickname, body.avatar)
    return {"token": create_token(user["id"]), "user": _user_payload(user)}


@router.post("/h5-login")
async def h5_login(body: H5LoginRequest):
    """网页端（手机浏览器）登录：手机号 ↔ openid=h5_<手机号> 映射后签发同一套 token。

    网页端没有 wx.login，无法使用 code2session；这里用手机号作为身份标识，
    复用同一张 users 表，因此网页端与小程序端共享全部业务数据。

    ⚠️ 安全提示：当前版本不校验短信验证码（等价于"知道手机号即可登录"），仅适合内测。
    上线前必须二选一改造，前端页面结构无需改动：
      1) 本接口补短信验证码（新增发送验证码接口 + 校验）
      2) 换成微信网页授权（公众号 OAuth）后同样签发本站 token
    置 H5_PHONE_LOGIN=false 可一键关闭该入口。
    """
    if not H5_PHONE_LOGIN:
        raise HTTPException(status_code=403, detail="网页端登录未开放，请使用微信小程序")

    # 容忍用户输入里的空格/连字符（如 138-0000-0000）
    phone = re.sub(r"[\s\-]", "", body.phone or "")
    if not PHONE_RE.match(phone):
        raise HTTPException(status_code=400, detail="请输入正确的 11 位手机号")

    openid = f"h5_{phone}"
    user = get_user_by_openid(openid)
    if user is None:
        nickname = (body.nickname or "").strip()[:30] or f"学员{phone[-4:]}"
        user = create_user(openid=openid, nickname=nickname, avatar="")
    return {"token": create_token(user["id"]), "user": _user_payload(user)}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return _user_payload(user)


@router.put("/profile")
async def update_profile(body: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    """更新当前用户资料（昵称/头像 + 学员自填的年级/专业/目标方向）。

    昵称/头像来自微信"头像昵称填写能力"（基础库 2.21.2+）：
    前端用 <button open-type="chooseAvatar"> 获取头像、<input type="nickname"> 获取昵称，
    用户主动选择后再回传本接口落库。生产环境头像需先上传到自有服务器/CDN 再回传 URL。
    """
    nickname = (body.nickname or "").strip()[:30]
    avatar = (body.avatar or "").strip()
    grade = (body.grade or "").strip()[:20]
    major = (body.major or "").strip()[:30]
    target_direction = (body.target_direction or "").strip()[:30]
    update_user_profile(user["id"], nickname, avatar, grade, major, target_direction)
    updated = get_user(user["id"])
    return {
        "ok": True,
        "user": {
            "id": updated["id"],
            "openid": updated["openid"],
            "nickname": updated["nickname"],
            "avatar": updated["avatar"],
            "grade": updated["grade"],
            "major": updated["major"],
            "target_direction": updated["target_direction"],
        },
    }


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """上传头像，返回可持久访问的 URL。

    存储顺序（见 fsx.save_avatar）：
      1. Vercel Blob（配置了 BLOB_READ_WRITE_TOKEN 时）→ 返回绝对 URL；
      2. 本地 static/avatars（自建服务器 / 本地开发）→ 返回 /static/avatars/xxx；
      3. 只读且未配置对象存储（Vercel 未建 Blob Store）→ 503 并给出可操作提示。

    微信 chooseAvatar 返回的是临时路径（会话结束后失效），
    前端需先上传换取永久 URL，再调 PUT /auth/profile 落库。
    """
    ext = os.path.splitext((file.filename or "").lower())[1]
    if ext not in ALLOWED_AVATAR_EXTS:
        raise HTTPException(status_code=400, detail="仅支持 jpg/jpeg/png/webp/gif 图片")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="头像不能超过 2MB")
    fname = f"{user['id']}_{uuid.uuid4().hex}{ext}"
    url = save_avatar(content, fname, file.content_type or "")
    if not url:
        raise HTTPException(
            status_code=503,
            detail="服务端未配置文件存储，暂时无法上传头像：请在 Vercel 项目里创建 Blob Store"
                   "（Storage → Blob，会自动注入 BLOB_READ_WRITE_TOKEN）后重试。")
    return {"ok": True, "avatar_url": url}


# ============ 开发期"模拟切换用户"（仅 DEV_IMPERSONATE=true 时开放，生产务必关闭） ============

@router.get("/dev/config")
async def dev_config():
    """前端探测：是否开放模拟切换用户（开关可见性）。"""
    return {"impersonate_enabled": bool(DEV_IMPERSONATE)}


@router.get("/dev/users")
async def dev_users(user: dict = Depends(get_current_user)):
    """列出后台用户（id/昵称/openid），供设置页开发期切换。"""
    if not DEV_IMPERSONATE:
        raise HTTPException(status_code=404, detail="not found")
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, nickname, openid, created_at FROM users ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return {"users": [dict(r) for r in rows]}


@router.post("/dev/impersonate")
async def dev_impersonate(user_id: int, user: dict = Depends(get_current_user)):
    """以指定用户身份签发 token（模拟切换，便于测试多用户数据隔离）。"""
    if not DEV_IMPERSONATE:
        raise HTTPException(status_code=404, detail="not found")
    target = get_user(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    token = create_token(target["id"])
    return {
        "token": token,
        "user": {
            "id": target["id"],
            "openid": target["openid"],
            "nickname": target["nickname"],
            "avatar": target["avatar"],
            "grade": target.get("grade", ""),
            "major": target.get("major", ""),
            "target_direction": target.get("target_direction", ""),
        },
    }
