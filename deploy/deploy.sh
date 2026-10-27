#!/usr/bin/env bash
# =============================================================================
# deploy.sh — 从本机一键发布到 Ubuntu / 宝塔
# =============================================================================
# 比「只 rsync 两段目录」更稳的地方：
#   1. 本机先构建 frontend/dist，服务器不必装 Node
#   2. 不上传、不覆盖 company.db（服务器上的新闻/产品数据会保留）
#   3. 不上传 node_modules、.git、venv（Windows 的 venv 在 Linux 上不能用）
#   4. 同步后自动 stop / daemon，并做一次健康检查
#   5. 密码写在 deploy.env，不写进脚本
#
# 用法（在项目根目录）：
#   bash deploy/deploy.sh --site aierde
#   bash deploy/deploy.sh --site aierde --target prod
#   bash deploy/deploy.sh --site aierde --no-build
#   bash deploy/deploy.sh --site aierde --dry-run
#   bash deploy/deploy.sh --site aierde --setup-key
#   bash deploy/deploy.sh --site aierde --skip-restart
#
# 站点地址、目录、端口：deploy/sites/<站点>/site.env
# SSH 口令：deploy/machines.env（不要提交）
# 生产地址或端口为空时直接拒绝，不会连接服务器。
# =============================================================================

set -euo pipefail

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DEPLOY_DIR/.." && pwd)"
cd "$ROOT"

NO_BUILD=0
DRY_RUN=0
SETUP_KEY=0
SKIP_RESTART=0
SITE=""
TARGET="debug"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --site)
      SITE="${2:-}"
      shift 2
      ;;
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --no-build) NO_BUILD=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --setup-key) SETUP_KEY=1; shift ;;
    --skip-restart) SKIP_RESTART=1; shift ;;
    --help|-h)
      sed -n '2,24p' "$0"
      exit 0
      ;;
    *)
      echo "[error] unknown arg: $1  (use --help)"
      exit 1
      ;;
  esac
done

if [[ -z "$SITE" ]]; then
  echo "[error] 请指定站点，例如: bash deploy/deploy.sh --site aierde"
  exit 1
fi
if [[ ! "$SITE" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  echo "[error] 站点名只能使用字母、数字、下划线和连字符"
  exit 1
fi
if [[ "$TARGET" != "debug" && "$TARGET" != "prod" ]]; then
  echo "[error] --target 只能是 debug 或 prod"
  exit 1
fi

# -----------------------------------------------------------------------------
# 读取 deploy.env（KEY=VALUE，支持引号，忽略注释和空行）
# -----------------------------------------------------------------------------
load_env() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "$line" || "$line" == \#* ]] && continue
    [[ "$line" == *=* ]] || continue
    local key="${line%%=*}"
    local val="${line#*=}"
    key="${key%"${key##*[![:space:]]}"}"
    key="${key#"${key%%[![:space:]]*}"}"
    val="${val#"${val%%[![:space:]]*}"}"
    val="${val%"${val##*[![:space:]]}"}"
    val="${val#\"}"
    val="${val%\"}"
    val="${val#\'}"
    val="${val%\'}"
    export "$key=$val"
  done < "$file"
}

SITE_DIR="$DEPLOY_DIR/sites/$SITE"
if [[ ! -f "$SITE_DIR/site.env" ]]; then
  echo "[error] 找不到站点配置 $SITE_DIR/site.env"
  exit 1
fi

load_env "$DEPLOY_DIR/machines.env"
load_env "$SITE_DIR/site.env"
load_env "$SITE_DIR/deploy.env"

if [[ "$TARGET" == "prod" ]]; then
  DEPLOY_HOST="${PROD_HOST:-}"
  DEPLOY_USER="${PROD_USER:-root}"
  DEPLOY_PATH="${PROD_PATH:-}"
  DEPLOY_SSH_PORT="${PROD_SSH_PORT:-22}"
  APP_PORT="${PROD_APP_PORT:-}"
  DEPLOY_PASS="${PROD_PASS:-${DEPLOY_PASS:-}}"
else
  DEPLOY_HOST="${DEBUG_HOST:-}"
  DEPLOY_USER="${DEBUG_USER:-root}"
  DEPLOY_PATH="${DEBUG_PATH:-}"
  DEPLOY_SSH_PORT="${DEBUG_SSH_PORT:-22}"
  APP_PORT="${DEBUG_APP_PORT:-}"
  DEPLOY_PASS="${DEBUG_PASS:-${DEPLOY_PASS:-}}"
fi

missing=""
[[ -z "$DEPLOY_HOST" ]] && missing="${missing} ${TARGET} host"
[[ -z "$DEPLOY_PATH" ]] && missing="${missing} ${TARGET} path"
[[ -z "$APP_PORT" ]] && missing="${missing} ${TARGET} port"
if [[ -n "$missing" ]]; then
  echo "[error] ${TARGET} 配置还是空的:${missing}"
  echo "        请先填写 deploy/sites/${SITE}/site.env。本次不会连接服务器。"
  exit 1
fi

REMOTE="${DEPLOY_USER}@${DEPLOY_HOST}"
SITE_URL="http://${DEPLOY_HOST}:${APP_PORT}/"

echo "[info] site    ${SITE}  ${SITE_NAME:-}"
echo "[info] target  ${TARGET}  ${REMOTE}:${DEPLOY_SSH_PORT}"
echo "[info] path    ${DEPLOY_PATH}"
echo "[info] url     ${SITE_URL}"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[error] 找不到命令: $1"
    exit 1
  }
}

need_cmd ssh
need_cmd tar

# -----------------------------------------------------------------------------
# SSH / rsync 包装：优先密钥；否则用密码（sshpass 或 SSH_ASKPASS）
# -----------------------------------------------------------------------------
ASKPASS_FILE=""
cleanup() {
  if [[ -n "$ASKPASS_FILE" && -f "$ASKPASS_FILE" ]]; then
    rm -f "$ASKPASS_FILE"
  fi
  if [[ -n "${SSH_CONTROL_PATH:-}" && -S "${SSH_CONTROL_PATH}" ]]; then
    ssh -o ControlPath="$SSH_CONTROL_PATH" -O exit "$REMOTE" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

SSH_BASE=(
  -p "$DEPLOY_SSH_PORT"
  -o StrictHostKeyChecking=accept-new
  -o ServerAliveInterval=30
  -o ConnectTimeout=12
)

SSH_PREFIX=()
RSYNC_RSH="ssh -p ${DEPLOY_SSH_PORT} -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30"

if [[ "$DRY_RUN" -eq 0 ]]; then
  if ssh "${SSH_BASE[@]}" -o BatchMode=yes -o ConnectTimeout=8 "$REMOTE" "true" >/dev/null 2>&1; then
    echo "[info] SSH 密钥登录成功"
  else
    if [[ -z "$DEPLOY_PASS" ]]; then
      echo "[error] 密钥登录失败，且 deploy/machines.env 里没有对应环境的口令"
      echo "        请填写口令，或先执行: bash deploy/deploy.sh --site ${SITE} --setup-key"
      exit 1
    fi
    if command -v sshpass >/dev/null 2>&1; then
      export SSHPASS="$DEPLOY_PASS"
      SSH_PREFIX=(sshpass -e)
      RSYNC_RSH="sshpass -e ssh -p ${DEPLOY_SSH_PORT} -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no"
      SSH_BASE+=(-o PreferredAuthentications=password -o PubkeyAuthentication=no)
      echo "[info] 使用 sshpass 密码登录"
    else
      ASKPASS_FILE="$(mktemp)"
      umask 077
      printf '#!/usr/bin/env bash\nprintf "%%s\\n" %q\n' "$DEPLOY_PASS" > "$ASKPASS_FILE"
      chmod 700 "$ASKPASS_FILE"
      export SSH_ASKPASS="$ASKPASS_FILE"
      export SSH_ASKPASS_REQUIRE=force
      export DISPLAY="${DISPLAY:-:0}"
      SSH_BASE+=(-o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1)
      RSYNC_RSH="ssh -p ${DEPLOY_SSH_PORT} -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1"
      echo "[info] 使用 SSH_ASKPASS 密码登录（建议安装 sshpass 或改用 --setup-key）"
    fi
  fi
fi

ssh_run() {
  "${SSH_PREFIX[@]}" ssh "${SSH_BASE[@]}" "$REMOTE" "$@"
}

# -----------------------------------------------------------------------------
# 把本机公钥写入服务器 authorized_keys
# -----------------------------------------------------------------------------
if [[ "$SETUP_KEY" -eq 1 ]]; then
  mkdir -p "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  local_key="$HOME/.ssh/id_ed25519"
  if [[ ! -f "${local_key}.pub" ]]; then
    echo "[info] 生成本机 SSH 密钥: $local_key"
    ssh-keygen -t ed25519 -N "" -f "$local_key"
  fi
  echo "[info] 安装公钥到 ${REMOTE}:~/.ssh/authorized_keys"
  pub="$(cat "${local_key}.pub")"
  ssh_run "mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && grep -qxF '$pub' ~/.ssh/authorized_keys || echo '$pub' >> ~/.ssh/authorized_keys"
  echo "[info] 完成。之后可把 deploy/machines.env 里的口令删掉。"
  exit 0
fi

# -----------------------------------------------------------------------------
# 本机构建前端
# -----------------------------------------------------------------------------
DIST_INDEX="$ROOT/frontend/dist/index.html"
if [[ "$NO_BUILD" -eq 1 ]]; then
  if [[ ! -f "$DIST_INDEX" ]]; then
    echo "[error] --no-build 但找不到 frontend/dist/index.html，请先构建"
    exit 1
  fi
  echo "[info] 跳过构建，使用已有 frontend/dist"
else
  need_cmd npm
  echo "[info] 构建前端 ..."
  if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
    (cd "$ROOT/frontend" && npm install)
  fi
  (cd "$ROOT/frontend" && npm run build)
  [[ -f "$DIST_INDEX" ]] || { echo "[error] 构建后仍没有 frontend/dist/index.html"; exit 1; }
fi

# -----------------------------------------------------------------------------
# 准备要上传的文件：start.sh、backend、frontend/dist、按本次目标生成的 runtime.env
# -----------------------------------------------------------------------------
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"; cleanup' EXIT

mkdir -p "$STAGE/backend" "$STAGE/frontend/dist"
cp "$ROOT/start.sh" "$STAGE/start.sh"

# 端口和对外地址按本次目标写入，避免调试机站点误听 8001。
{
  echo "PORT=${APP_PORT}"
  echo "PUBLIC_BASE_URL=http://${DEPLOY_HOST}:${APP_PORT}"
  if [[ -f "$SITE_DIR/runtime.env" ]]; then
    grep -Ev '^[[:space:]]*(PORT|PUBLIC_BASE_URL)=' "$SITE_DIR/runtime.env" || true
  fi
} > "$STAGE/runtime.env"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude='venv/' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache/' \
    --exclude='*.db' \
    "$ROOT/backend/" "$STAGE/backend/"
  rsync -a --delete "$ROOT/frontend/dist/" "$STAGE/frontend/dist/"
else
  tar -C "$ROOT/backend" \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='*.db' \
    -cf - . | tar -C "$STAGE/backend" -xf -
  tar -C "$ROOT/frontend/dist" -cf - . | tar -C "$STAGE/frontend/dist" -xf -
fi

echo "[info] 将上传: start.sh, backend/, frontend/dist/"
echo "[info] 不会上传: node_modules, .git, venv, company.db, 源码 src/"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] 暂存目录文件："
  (cd "$STAGE" && find . -type f | sort)
  echo "[dry-run] 未连接服务器，退出"
  exit 0
fi

# -----------------------------------------------------------------------------
# 上传：有 rsync 用增量；否则 tar 管道（Git Bash / 无 rsync 时）
# -----------------------------------------------------------------------------
echo "[info] 确保远程目录存在 ..."
ssh_run "mkdir -p '$DEPLOY_PATH' '$DEPLOY_PATH/backend' '$DEPLOY_PATH/frontend'"

if command -v rsync >/dev/null 2>&1; then
  echo "[info] rsync 同步 ..."
  rsync -az --delete -e "$RSYNC_RSH" \
    "$STAGE/start.sh" "$REMOTE:$DEPLOY_PATH/start.sh"
  rsync -az -e "$RSYNC_RSH" \
    "$STAGE/runtime.env" "$REMOTE:$DEPLOY_PATH/runtime.env"
  rsync -az --delete \
    --exclude='venv/' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.db' \
    -e "$RSYNC_RSH" \
    "$STAGE/backend/" "$REMOTE:$DEPLOY_PATH/backend/"
  rsync -az --delete -e "$RSYNC_RSH" \
    "$STAGE/frontend/dist/" "$REMOTE:$DEPLOY_PATH/frontend/dist/"
else
  echo "[info] 本机没有 rsync，改用 tar + ssh ..."
  tar -C "$STAGE" -czf - . | ssh_run "tar -xzf - -C '$DEPLOY_PATH'"
fi

# -----------------------------------------------------------------------------
# 远程：修换行符、停旧进程、启动
# 注意：绝不会去动 company.db / .venv / logs
# -----------------------------------------------------------------------------
echo "[info] 修复 start.sh 换行符 ..."
ssh_run "sed -i 's/\r$//' '$DEPLOY_PATH/start.sh' '$DEPLOY_PATH/runtime.env' && chmod +x '$DEPLOY_PATH/start.sh' && chmod 600 '$DEPLOY_PATH/runtime.env'"

if [[ "$SKIP_RESTART" -eq 1 ]]; then
  echo "[info] 已跳过重启。文件已上传到 $DEPLOY_PATH"
  exit 0
fi

echo "[info] 检查远程 Python ..."
ssh_run "command -v python3 >/dev/null || (export DEBIAN_FRONTEND=noninteractive && apt-get update -y && apt-get install -y python3 python3-venv python3-pip)"

echo "[info] 重启服务 ..."
ssh_run "bash '$DEPLOY_PATH/start.sh' --stop >/dev/null 2>&1 || true; bash '$DEPLOY_PATH/start.sh' --daemon"

echo "[info] 检查防火墙是否放行 ${APP_PORT} ..."
ssh_run "command -v ufw >/dev/null 2>&1 && ufw allow ${APP_PORT}/tcp || true"

echo "[info] 等待进程起来 ..."
health_py="import urllib.request; urllib.request.urlopen('http://127.0.0.1:${APP_PORT}/', timeout=3).read(32)"
ok=0
for i in 1 2 3 4 5 6 7 8 9 10; do
  if ssh_run "python3 -c \"$health_py\"" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 1
done

if [[ "$ok" -ne 1 ]]; then
  echo "[error] 健康检查失败。最近日志："
  ssh_run "tail -n 40 '$DEPLOY_PATH/logs/rxweb.log' 2>/dev/null || echo '(没有日志文件)'"
  exit 1
fi

echo "[done] 部署完成  $SITE_URL"
ssh_run "bash '$DEPLOY_PATH/start.sh' --status" || true
