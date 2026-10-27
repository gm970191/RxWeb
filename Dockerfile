# =============================================================================
# RxWeb Dockerfile（给完全新手看的说明）
# =============================================================================
# Docker 是什么：把“操作系统 + Python + Node 构建工具 + 我们的网站”打包进一个
# 叫“镜像”的盒子。别人只要安装了 Docker，就能用同一套命令把网站跑起来，
# 不用在 Windows / Ubuntu 上分别装 Python、Node。
#
# 镜像 vs 容器：
#   镜像 = 做好的安装包（只读）
#   容器 = 用镜像跑起来的一个正在运行的进程
#
# 本文件采用“多阶段构建”：
#   第 1 阶段（frontend-build）：用 Node 把 Vue 编译成静态文件 frontend/dist
#   第 2 阶段（运行阶段）：只保留 Python，把编译好的页面拷进来，体积更小
#
# 常用命令见 docs/09_Docker部署与运行.md
# =============================================================================

# ---------- 第 1 阶段：编译前端 ----------
# node:20-bookworm-slim = 官方 Node 20，基于 Debian，体积较小
FROM node:20-bookworm-slim AS frontend-build

# 容器里的工作目录，后面的 COPY / RUN 都相对这里
WORKDIR /src/frontend

# 先只拷 package.json 和 lock 文件，再 npm ci
# 这样依赖没变时，Docker 能复用这一层缓存，第二次构建会快很多
COPY frontend/package.json frontend/package-lock.json ./

# npm ci = 严格按照 lock 文件安装，适合构建，比 npm install 更可复现
RUN npm ci

# 再拷前端其余源码（src、index.html、vite.config.js 等）
COPY frontend/ ./

# 编译结果会出现在 /src/frontend/dist
RUN npm run build


# ---------- 第 2 阶段：运行后端 + 已编译的前端 ----------
FROM python:3.12-slim-bookworm

# 容器内项目根目录约定为 /app
# backend/app/main.py 里：
#   数据库路径 = /app/company.db
#   前端 dist  = /app/frontend/dist
WORKDIR /app

# 禁止 Python 写 .pyc，并让 print 立刻输出到 docker logs（不缓冲）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 先拷依赖清单，再 pip install，同样是为了利用 Docker 缓存
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 拷贝后端源码（含 seed.py，用来生成演示数据库）
COPY backend/ /app/backend/

# 从第 1 阶段把编译好的官网页面拷过来（运行镜像里不需要 Node）
COPY --from=frontend-build /src/frontend/dist /app/frontend/dist

# 启动时检查数据库、再拉起 uvicorn 的小脚本
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# 声明容器对外的端口（真正映射到宿主机要在 docker run -p 里写）
EXPOSE 8001

# 容器启动时执行入口脚本（里面会再 exec uvicorn）
ENTRYPOINT ["/app/docker-entrypoint.sh"]
