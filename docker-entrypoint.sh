#!/bin/sh
# =============================================================================
# Docker 容器入口脚本
# =============================================================================
# Dockerfile 的 ENTRYPOINT 会执行本文件。
# 容器每次启动都会走这里，顺序是：
#   1. 若还没有数据库文件，就用 seed.py 写入演示数据
#   2. 用 uvicorn 启动网站（必须前台运行：容器主进程退出 = 容器退出）
#
# 为什么必须 cd 到 /app/backend ？
#   uvicorn app.main:app 要从 backend 目录导入 app 包。
# =============================================================================

set -eu

# 没设置 RXWEB_DB 时，用镜像里的默认路径 /app/company.db
RXWEB_DB="${RXWEB_DB:-/app/company.db}"
export RXWEB_DB

# 若指向 /data/company.db 这类路径，先确保目录存在
mkdir -p "$(dirname "$RXWEB_DB")"

cd /app/backend

# -s = 文件存在并且大小大于 0
if [ ! -s "$RXWEB_DB" ]; then
  echo "[info] database missing, seeding demo data -> $RXWEB_DB"
  python seed.py
fi

echo "[info] starting http://0.0.0.0:8001"
# exec：让 uvicorn 成为 PID 1，docker stop 才能正确结束进程
exec uvicorn app.main:app --host 0.0.0.0 --port 8001
