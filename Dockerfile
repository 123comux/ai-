# ============================================================
# 单容器部署：一个进程同时提供 H5 网页 + FastAPI 接口
#
# 适用：腾讯云 CloudBase 云托管、阿里云函数计算 FC（容器）、Sealos、Zeabur、
#       任意支持 Dockerfile 的平台，或你自己的服务器。
# 不需要 Vercel：前端与接口同源，无需 rewrite、无需跨域配置。
#
# 构建（仓库根目录）：
#     docker build -t aishixi .
# 运行：
#     docker run -d -p 8010:8010 --env-file backend/.env aishixi
# 环境变量（必须）：DB_ENGINE=mysql / DB_HOST / DB_PORT / DB_USER / DB_PASSWORD /
#                  DB_NAME / DB_SSL_REQUIRED=true / JWT_SECRET / DEV_MODE=false
# ============================================================

# ---------- 阶段 1：构建 H5 前端 ----------
FROM node:20-slim AS web
WORKDIR /web
# .npmrc 里有 legacy-peer-deps=true（Taro 4.1.9 与 webpack 5.78 的 peer 冲突）
COPY package.json package-lock.json .npmrc ./
RUN npm install --legacy-peer-deps --no-audit --no-fund
COPY . .
# 构建 h5 并把 backend/static（封面/banner）拷进 dist-h5/static
RUN npm run build:vercel

# ---------- 阶段 2：Python 运行时 ----------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEV_MODE=false \
    SERVE_H5=1 \
    AI_WARMUP=false \
    PORT=8010

WORKDIR /app

# 依赖单独一层，改代码不用重装依赖
COPY backend/requirements-runtime.txt /app/requirements-runtime.txt
RUN pip install --no-cache-dir -r /app/requirements-runtime.txt

# 后端代码（含 data/processed 种子 JSON 与 static 资源）
COPY backend/ /app/

# 前端产物放到 /dist-h5：main.py 里 H5_DIR = <backend>/../dist-h5
COPY --from=web /web/dist-h5 /dist-h5

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8010
ENTRYPOINT ["/app/docker-entrypoint.sh"]
