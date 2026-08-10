#!/bin/sh
# 容器入口：首次启动时初始化并灌入种子数据，之后直接启动 API 服务。
set -e

DATA_DIR=/app/data
DB_PATH="$DATA_DIR/cms.db"

# 确保数据目录存在
mkdir -p "$DATA_DIR/processed"

# 若数据库不存在则初始化（建表 + 从 data/processed/*.json 灌入课程/项目/视频/方向/管理员等）
if [ ! -f "$DB_PATH" ]; then
  echo "[entrypoint] 数据库不存在，开始初始化并灌入种子数据..."
  python -m database
  echo "[entrypoint] 初始化完成。"
else
  echo "[entrypoint] 数据库已存在，跳过初始化。"
fi

# 启动 API（多进程可用 gunicorn 替换；此处用 uvicorn 单进程即可）
exec uvicorn main:app --host 0.0.0.0 --port 8000
