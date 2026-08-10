# ============================================================
# AI 教学服务平台 —— 后端 API 运行时镜像（精简，不含训练依赖）
# 构建：docker build -f backend/Dockerfile -t ai-teach-backend .
# 运行：docker run -d -p 8000:8000 --env-file backend/.env -v ai-teach-data:/app/data ai-teach-backend
# ============================================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEV_MODE=false

WORKDIR /app

# 先装依赖，充分利用镜像层缓存
COPY backend/requirements-runtime.txt /app/requirements-runtime.txt
RUN pip install --no-cache-dir -r requirements-runtime.txt

# 复制后端代码（含 data/processed 种子数据与配置）
COPY backend/ /app/

# 赋予入口脚本可执行权限
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
