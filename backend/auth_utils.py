"""Auth utilities: HMAC-signed login tokens + FastAPI dependencies.

Dependency-free (stdlib hmac/hashlib) so it runs in any environment.
Token format: "<user_id>.<exp_ts>.<hmac_hex>" — verifiable without a DB lookup.
"""

import hmac
import hashlib
import time
from typing import Optional

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import JWT_SECRET, TOKEN_EXPIRE_DAYS
from database import get_user

security = HTTPBearer(auto_error=False)


def _sign(payload: str) -> str:
    return hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_token(user_id: int) -> str:
    """Create a signed login token for the given user id."""
    exp = int(time.time()) + TOKEN_EXPIRE_DAYS * 86400
    payload = f"{user_id}.{exp}"
    return f"{payload}.{_sign(payload)}"


def verify_token(token: str) -> Optional[int]:
    """Return user_id if the token is valid & unexpired, else None."""
    if not token or token.count(".") != 2:
        return None
    head, exp_s, sig = token.split(".")
    payload = f"{head}.{exp_s}"
    expected = _sign(payload)
    # constant-time compare
    if not hmac.compare_digest(expected, sig):
        return None
    try:
        exp = int(exp_s)
    except ValueError:
        return None
    if exp < int(time.time()):
        return None
    try:
        return int(head)
    except ValueError:
        return None


def _extract_token(creds: Optional[HTTPAuthorizationCredentials]) -> Optional[str]:
    if creds and creds.credentials:
        return creds.credentials
    return None


async def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """FastAPI dependency: require a valid token, return the user dict (raises 401)."""
    token = _extract_token(creds)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或登录态已失效")
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录态无效，请重新登录")
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


async def get_optional_user(request: Request) -> Optional[dict]:
    """Return the user if a valid Bearer token is present, else None.

    Used by progress routers so they can record per-user progress when logged in
    while staying backward-compatible (global JSON fallback) when not authenticated.
    """
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    user_id = verify_token(token)
    if user_id is None:
        return None
    return get_user(user_id)
