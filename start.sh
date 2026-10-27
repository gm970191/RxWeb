#!/usr/bin/env bash
# =============================================================================
# RxWeb Ubuntu / 宝塔 启动脚本
# =============================================================================
# 这个文件只能在 Linux（Ubuntu、宝塔面板那台云服务器）上用。
# Windows 请改用 start.ps1。
#
# 【第一次使用前】在服务器执行：
#   apt update
#   apt install -y python3 python3-venv python3-pip unzip
#   # 如果压缩包里没有 frontend/dist，还要安装 Node.js（宝塔 -> 软件商店）
#
# 【单独启动命令】（zip 解压到 /www/wwwroot/RxWeb 之后）
#   bash /www/wwwroot/RxWeb/start.sh --daemon
#
# 【以后更新】Windows 重新 pack-deploy 后，上传 zip，在服务器执行：
#   bash /www/wwwroot/RxWeb/start.sh --stop
#   unzip -o /www/wwwroot/RxWeb-deploy.zip -d /www/wwwroot/RxWeb
#   sed -i 's/\r$//' /www/wwwroot/RxWeb/start.sh
#   bash /www/wwwroot/RxWeb/start.sh --daemon
# 不会重装系统、不会重建 venv（已存在则跳过）、不会覆盖 company.db（包里没有库）。
#
# 【常用参数】
#   bash start.sh                 前台运行，Ctrl+C 停止；关掉 SSH 也会停
#   bash start.sh --daemon        后台运行，关掉 SSH 也继续（生产常用）
#   bash start.sh --stop          停止后台进程
#   bash start.sh --status        查看是否在运行
#   bash start.sh --rebuild       强制重装依赖并重新构建前端
#
# 页面和 /api 使用同一个端口。未设置 PORT 时默认 8001（瑞学调试机）。
# 服务器上的实际端口以 runtime.env 里的 PORT 为准。
# 宝塔防火墙 / 云服务器安全组要放行该端口。
#
# 【Windows 上传后必做】脚本可能带 Windows 换行符 \r，Linux 会报错。先执行：
#   sed -i 's/\r$//' /www/wwwroot/RxWeb/start.sh
# =============================================================================

# set -e ：任何命令失败就立刻退出，避免带着错误继续跑
# set -u ：用了未定义变量就报错
# set -o pipefail ：管道中只要有一步失败，整段算失败
set -euo pipefail

# -----------------------------------------------------------------------------
# 路径说明
# -----------------------------------------------------------------------------
# $0 是脚本自己的路径。dirname 取出它所在目录，再 pwd 转成绝对路径。
# 这样你在任何目录执行 bash /www/wwwroot/RxWeb/start.sh 都能找到项目根。
# 虚拟环境放项目根目录 .venv/ ，这是 Linux 专用的，不要用 Windows 带来的 backend/venv。
# -----------------------------------------------------------------------------
ROOT="$(cd "$(dirname "$0")" && pwd)"
# 调试机/生产机的 SMTP 等配置放 runtime.env，不进代码仓库
if [[ -f "$ROOT/runtime.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/runtime.env"
  set +a
fi
PORT="${PORT:-8001}"          # 没设置环境变量 PORT 时，默认 8001（官网 + /api）
HOST="${HOST:-0.0.0.0}"       # 0.0.0.0 = 监听所有网卡，外网才能访问
VENV="$ROOT/.venv"
FRONTEND_DIR="$ROOT/frontend"
BACKEND_DIR="$ROOT/backend"
DIST_INDEX="$FRONTEND_DIR/dist/index.html"
LOG_DIR="$ROOT/logs"
PID_FILE="$ROOT/rxweb.pid"    # 后台进程号存在这里，--stop / --status 会读它
LOG_FILE="$LOG_DIR/rxweb.log"
REBUILD=0
DAEMON=0
ACTION="start"

# 逐个解析你在命令行传入的参数
for arg in "$@"; do
  case "$arg" in
    --rebuild|-r) REBUILD=1 ;;
    --daemon|-d) DAEMON=1 ;;
    --stop) ACTION="stop" ;;
    --status) ACTION="status" ;;
    --help|-h)
      echo "Usage: $0 [--daemon] [--rebuild] [--stop] [--status]"
      echo "  default port 8001, listen 0.0.0.0"
      echo "  PORT=8001 HOST=0.0.0.0 $0 --daemon"
      exit 0
      ;;
    *)
      echo "[error] unknown arg: $arg"
      echo "use --help"
      exit 1
      ;;
  esac
done

# 判断后台进程是否还活着
# kill -0 PID 不会真的杀掉进程，只检查这个 PID 是否存在
is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

if [[ "$ACTION" == "stop" ]]; then
  if is_running; then
    pid="$(cat "$PID_FILE")"
    echo "[info] stopping pid=$pid ..."
    kill "$pid" 2>/dev/null || true
    for _ in 1 2 3 4 5; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.4
    done
    # 5 次还没退出，就强制杀掉
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    echo "[info] stopped"
  else
    rm -f "$PID_FILE"
    echo "[info] not running"
  fi
  exit 0
fi

if [[ "$ACTION" == "status" ]]; then
  if is_running; then
    pid="$(cat "$PID_FILE")"
    echo "[info] running pid=$pid  http://${HOST}:${PORT}"
    exit 0
  fi
  echo "[info] not running"
  exit 1
fi

cd "$ROOT"

if is_running; then
  pid="$(cat "$PID_FILE")"
  echo "[error] already running pid=$pid . Stop first: bash $ROOT/start.sh --stop"
  exit 1
fi

# -----------------------------------------------------------------------------
# 1) 检查 python3
# Ubuntu 上命令是 python3，不是 python
# -----------------------------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "[error] python3 not found. Install:"
  echo "  apt install -y python3 python3-venv python3-pip"
  exit 1
fi

# -----------------------------------------------------------------------------
# 2) 创建 Linux 虚拟环境（项目自己的 Python 依赖，不污染系统）
# -----------------------------------------------------------------------------
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "[info] creating venv: $VENV"
  python3 -m venv "$VENV"
fi

# -----------------------------------------------------------------------------
# 3) 安装后端依赖
# -----------------------------------------------------------------------------
if [[ "$REBUILD" -eq 1 ]] || [[ ! -x "$VENV/bin/uvicorn" ]]; then
  echo "[info] installing backend requirements..."
  "$VENV/bin/pip" install -U pip
  "$VENV/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

# -----------------------------------------------------------------------------
# 4) 没有数据库就写入演示数据
# seed.py 内部用相对路径 ../company.db，所以必须先 cd 到 backend/
# -----------------------------------------------------------------------------
if [[ ! -f "$ROOT/company.db" ]]; then
  echo "[info] company.db missing, seeding demo data..."
  (cd "$BACKEND_DIR" && "$VENV/bin/python" seed.py)
fi

# -----------------------------------------------------------------------------
# 5) 前端：有 frontend/dist 就直接用，不要在服务器上再 npm build
# 创建 venv 不会再强制重建前端（那会误伤「只带了 dist、没带源码」的压缩包）
# -----------------------------------------------------------------------------
PACKAGE_JSON="$FRONTEND_DIR/package.json"
if [[ -f "$DIST_INDEX" ]] && [[ "$REBUILD" -ne 1 ]]; then
  echo "[info] frontend/dist exists, skip build (use --rebuild to force)"
elif [[ -f "$DIST_INDEX" ]] && [[ "$REBUILD" -eq 1 ]] && [[ ! -f "$PACKAGE_JSON" ]]; then
  echo "[warn] --rebuild ignored: no frontend/package.json, keep existing dist"
elif [[ -f "$PACKAGE_JSON" ]]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "[error] npm not found, cannot build frontend."
    echo "  Install Node.js, or pack frontend/dist on Windows and upload again."
    exit 1
  fi
  echo "[info] building frontend..."
  cd "$FRONTEND_DIR"
  if [[ ! -d node_modules ]]; then
    npm install
  fi
  npm run build
  cd "$ROOT"
else
  echo "[error] missing frontend/dist and frontend/package.json"
  echo "  Re-pack on Windows with deploy/pack-deploy.ps1, then unzip again."
  echo "  Check: ls -la $FRONTEND_DIR $FRONTEND_DIR/dist"
  exit 1
fi

if [[ ! -f "$DIST_INDEX" ]]; then
  echo "[error] frontend/dist/index.html still missing after build"
  exit 1
fi

mkdir -p "$LOG_DIR"

echo "[info] starting http://${HOST}:${PORT}"
cd "$BACKEND_DIR"

# -----------------------------------------------------------------------------
# 6) 启动 uvicorn
# app.main:app = backend/app/main.py 文件里的 FastAPI 实例 app
# 同一个 8001 端口既提供 /api/* 接口，也提供官网页面
# -----------------------------------------------------------------------------
if [[ "$DAEMON" -eq 1 ]]; then
  # nohup = 忽略挂断信号，SSH 断开后进程还在
  # & = 放到后台
  # >> 日志文件  2>&1 = 标准错误也写进同一份日志
  nohup "$VENV/bin/uvicorn" app.main:app --host "$HOST" --port "$PORT" \
    >>"$LOG_FILE" 2>&1 &
  echo $! >"$PID_FILE"   # $! 是刚刚后台进程的 PID
  sleep 0.8
  if is_running; then
    echo "[info] started in background pid=$(cat "$PID_FILE")"
    echo "[info] log: $LOG_FILE"
    echo "[info] stop: bash $ROOT/start.sh --stop"
  else
    echo "[error] start failed, see log: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
  fi
else
  # exec 用 uvicorn 替换当前 bash 进程，Ctrl+C 会直接停服务
  exec "$VENV/bin/uvicorn" app.main:app --host "$HOST" --port "$PORT"
fi
