#!/bin/sh
# 容器入口：适用于任何「一个容器同时提供 H5 + API」的平台
#   - 本地 / 云服务器 / CloudBase / 阿里云函数计算 FC（自定义镜像）
#   - SQLite 模式（默认，本地/单机）：首次启动建表并灌种子
#   - MySQL 模式（云数据库，生产）：**不自动灌种子**，避免覆盖线上已有内容；
#     确需初始化时显式设 SEED_ON_BOOT=true
set -e

DATA_DIR="${DATA_DIR:-/app/data}"
DB_PATH="$DATA_DIR/cms.db"

# 确保数据目录存在。注意：阿里云函数计算 FC 等 Serverless 平台的容器
# 文件系统可能只允许 /tmp 写入，这里即使失败也不能中断启动
# （DB_ENGINE=mysql 时本来就不需要这个目录）。
mkdir -p "$DATA_DIR/processed" 2>/dev/null || \
  echo "[entrypoint] 警告：$DATA_DIR 不可写，已跳过（DB_ENGINE=mysql 下无影响）"

# 监听端口：
#   - 阿里云 FC 会把控制台「监听端口」的值注入 FC_SERVER_PORT，优先采用它，
#     否则会出现「镜像里 PORT=8010、平台健康检查 9000」导致的 PortNotListening
#   - 其它平台用 PORT 覆盖，默认 8010（8000 常被其它服务占用）
if [ -n "${FC_SERVER_PORT:-}" ]; then
  LISTEN_PORT="$FC_SERVER_PORT"
  echo "[entrypoint] 检测到 FC_SERVER_PORT=$FC_SERVER_PORT（函数计算）"
else
  LISTEN_PORT="${PORT:-8010}"
fi

if [ "${DB_ENGINE:-sqlite}" = "mysql" ]; then
  if [ "${SEED_ON_BOOT:-false}" = "true" ]; then
    echo "[entrypoint] DB_ENGINE=mysql + SEED_ON_BOOT=true：对云数据库建表并灌种子..."
    python -m database
  else
    echo "[entrypoint] DB_ENGINE=mysql：使用云数据库，跳过本地初始化（避免覆盖线上数据）"
  fi
elif [ ! -f "$DB_PATH" ]; then
  echo "[entrypoint] 数据库不存在，开始初始化并灌入种子数据..."
  python -m database
  echo "[entrypoint] 初始化完成。"
else
  echo "[entrypoint] 数据库已存在，跳过初始化。"
fi

# 启动 API（多进程可用 gunicorn 替换；此处用 uvicorn 单进程即可）
# 端口需与容器平台配置的「监听端口」一致。
echo "[entrypoint] 启动 uvicorn：${HOST:-0.0.0.0}:${LISTEN_PORT}"
exec uvicorn main:app --host "${HOST:-0.0.0.0}" --port "$LISTEN_PORT"
