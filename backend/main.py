"""
FastAPI Backend for AI Talent Training Mini-Program.

Provides APIs for:
- Knowledge base search (from FineWeb-Edu, QVAC Genesis, StudyChat)
- AI ability assessment
- Courses, projects, and learning paths

Usage:
    pip install -r backend/requirements.txt
    python -m backend.data_pipeline.download   # Download datasets
    python -m backend.data_pipeline.preprocess  # Process into knowledge base
    uvicorn backend.main:app --reload           # Start API server
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from config import CORS_ORIGINS, CORS_ORIGIN_REGEX, HOST, PORT
from routers import access, knowledge, assessment, courses, projects, learning_paths, ai, user_data, videos, content, admin, admin_panel, mine_data, auth, deposit, community, homework, pay
from database import init_db

app = FastAPI(
    title="AI Talent Training API",
    description="Backend API for the AI Talent Training Mini-Program. "
                "Powered by FineWeb-Edu, QVAC Genesis, and StudyChat datasets.",
    version="1.0.0",
)

# 中间件注册顺序（Starlette 为"后注册者最外层"）：先把 log/权限 中间件注册好，
# CORS **最后**注册 → 位于最外层，即使权限中间件短路返回 403，出站仍会补 CORS 头，H5 端才能读到错误体。
# Debug: log Origin header of all requests
@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin", "NONE")
    logging.info(f"Request: {request.method} {request.url.path} Origin={origin}")
    response = await call_next(request)
    return response

# 功能使用权限校验：5 天免费试用 → 逾期未缴押金则 403（豁免路径见 config.ACCESS_EXEMPT_PREFIXES）
from services.access_service import access_control_middleware
app.middleware("http")(access_control_middleware)

# CORS（最外层，须最后注册）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(access.router)
app.include_router(knowledge.router)
app.include_router(assessment.router)
app.include_router(courses.router)
app.include_router(projects.router)
app.include_router(learning_paths.router)
app.include_router(ai.router)
app.include_router(user_data.router)
app.include_router(videos.router)
app.include_router(content.router)
app.include_router(homework.admin_router)  # 需在 admin.router 之前：/api/admin/homework/* 不能被通用 /{table}/{item_id} 抢走
app.include_router(deposit.admin_router)   # 同：/api/admin/deposit/* 需在 admin.router 之前注册
app.include_router(admin.router)
app.include_router(admin_panel.router)
app.include_router(mine_data.router)
app.include_router(auth.router)
app.include_router(deposit.router)
app.include_router(community.router)
app.include_router(homework.router)
app.include_router(pay.router)

# 静态文件（上传的头像等），生产环境应改由云存储/CDN 提供
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
try:  # Serverless（Vercel）部署目录只读；目录随代码打包，创建失败可忽略
    os.makedirs(os.path.join(STATIC_DIR, "avatars"), exist_ok=True)
except Exception:
    pass
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Ensure DB tables (incl. users / deposit) exist on startup.
init_db()


@app.get("/")
async def root():
    return {
        "name": "AI Talent Training API",
        "version": "1.0.0",
        "datasets": ["FineWeb-Edu", "QVAC Genesis", "StudyChat"],
        "endpoints": {
            "knowledge": "/api/knowledge/",
            "assessment": "/api/assessment/",
            "courses": "/api/courses/",
            "projects": "/api/projects/",
            "learning_paths": "/api/learning-paths/",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


def _warmup_models():
    """后台预热本地 AI 模型（不阻塞启动）。AI_WARMUP=false 可关闭。"""
    if os.getenv("AI_WARMUP", "true").lower() in ("0", "false", "no", "off"):
        return
    try:
        from services import assessment_ai_service, tutor_service
        for name, fn in (("assessment", assessment_ai_service.warm_up),
                         ("tutor", tutor_service.warm_up)):
            try:
                ok = fn()
                logging.info(f"[warmup] {name} model loaded: {ok}")
            except Exception as e:
                logging.info(f"[warmup] {name} model skipped: {e}")
    except Exception as e:
        logging.info(f"[warmup] services unavailable: {e}")


@app.on_event("startup")
async def _startup_warmup():
    """启动后后台线程预热本地模型，首个 AI 请求不再等待冷加载。

    Serverless（Vercel）上不用预热：实例随请求起停，线程会被冻结/回收，白耗启动时间。
    """
    if os.getenv("VERCEL"):
        logging.info("[warmup] Serverless 环境，跳过模型预热（线上主路径走智谱/DeepSeek API）")
        return
    import threading
    threading.Thread(target=_warmup_models, daemon=True).start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)