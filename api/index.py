"""Vercel Python Serverless 入口：把 backend/ 下那套 FastAPI app 原样暴露出去。

不需要为 Serverless 单独写一份后端：这里只做三件事
    1. 把 backend/ 加入 sys.path，复用本地开发用的同一个 app（backend/main.py）；
    2. 兼容 Vercel 两种 rewrite 行为（见下），保证路由一定能命中；
    3. 补一个 Serverless 友好的默认环境变量。

关于路径兼容（踩坑点，实测结论）：
    实测发现 Vercel 只把「精确的 /api」路由到本函数，`/api/courses` 这类子路径
    会直接被边缘节点 404（响应头里没有 hkg1，说明函数根本没执行），
    rewrite `/api/:path*` → `/api/index/api/:path*` 并不能把子路径送进来。
    与其猜 Vercel 的 rewrite 语义，不如让调用方把真实路径显式传进来：

        x-original-path:  /api/courses        ← 反向代理（如 Cloudflare Pages Function）写入
        x-original-query: limit=10&page=2     ← 不含问号

    本中间件看到该头就把 ASGI 的 path / query_string 还原成真实请求，
    于是函数停在固定入口 `/api/index`，业务路由却完全正常。

    兼容保留：若没有该头，仍按老逻辑剥掉 `/api/index` 前缀，
    这样直接从 Vercel 访问 `/api/index/xxx` 的旧行为不变。
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

# 反向代理用来告知真实路径的请求头（见模块 docstring）
_H_PATH = b"x-original-path"
_H_QUERY = b"x-original-query"


class _PathCompat:
    """ASGI 中间件：还原真实请求路径。

    1) 有 x-original-path（Cloudflare 等反代写入）→ 直接采用，最可靠；
    2) 否则剥掉 Vercel 函数路径前缀 /api/index（兼容直连 Vercel 的老行为）。
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            headers = scope.get("headers") or []
            incoming = dict(headers)
            override = incoming.get(_H_PATH)

            real = None
            query = None
            if override:
                real = override.decode("utf-8", "replace") or "/"
                if not real.startswith("/"):
                    real = "/" + real
                query = incoming.get(_H_QUERY) or b""
            else:
                path = scope.get("path") or "/"
                if path.startswith(_FUNCTION_PREFIX):
                    real = path[len(_FUNCTION_PREFIX):] or "/"
                    if not real.startswith("/"):
                        real = "/" + real

            if real is not None:
                scope = dict(scope)
                scope["path"] = real
                scope["raw_path"] = real.encode("utf-8")
                if query is not None:
                    scope["query_string"] = query
                if override:
                    # 内部约定头不外传给业务代码
                    scope["headers"] = [(k, v) for k, v in headers if k not in (_H_PATH, _H_QUERY)]

        await self.app(scope, receive, send)


app = _PathCompat(_app)

# Vercel 的 Python runtime 也认 `handler`；指向同一个 ASGI app 以防两种约定都用
handler = app
