"""Vercel Python Serverless 入口：把 backend/ 下那套 FastAPI app 原样暴露出去。

不需要为 Serverless 单独写一份后端：这里只做三件事
    1. 把 backend/ 加入 sys.path，复用本地开发用的同一个 app（backend/main.py）；
    2. 兼容 Vercel 两种 rewrite 行为（见下），保证路由一定能命中；
    3. 补一个 Serverless 友好的默认环境变量。

关于路径兼容（踩坑点，已按「两种行为都能跑」实现）：
    vercel.json 里把 `/api/:path*` 之类 rewrite 到本函数，Vercel 传给 ASGI 的
    `scope["path"]` 可能是「原始路径」也可能是「rewrite 目标路径」。
    因此 vercel.json 的目标统一写成 `/api/index/<原始路径>`，
    这里再把前缀 `/api/index` 剥掉：
        /api/courses                  → 原样使用（已经是原始路径）
        /api/index/api/courses        → 剥前缀 → /api/courses
    两种情况都能正确命中 FastAPI 路由，不依赖 Vercel 的未文档化细节。
"""

import os
import sys

BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

# Serverless 环境：实例随请求起停，跳过本地模型预热（线上主路径走智谱/DeepSeek API）
os.environ.setdefault("AI_WARMUP", "false")

from main import app as _app  # noqa: E402

_FUNCTION_PREFIX = "/api/index"


class _PathCompat:
    """ASGI 中间件：剥掉 Vercel 函数路径前缀，还原真实请求路径。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path") or "/"
            if path.startswith(_FUNCTION_PREFIX):
                real = path[len(_FUNCTION_PREFIX):] or "/"
                if not real.startswith("/"):
                    real = "/" + real
                scope = dict(scope)
                scope["path"] = real
                if scope.get("raw_path"):
                    scope["raw_path"] = real.encode("utf-8")
        await self.app(scope, receive, send)


app = _PathCompat(_app)

# Vercel 的 Python runtime 也认 `handler`；指向同一个 ASGI app 以防两种约定都用
handler = app
