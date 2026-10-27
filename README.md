# 瑞学软件有限公司 (RxWeb) 官方网站

公司官网：企业形象、产品、新闻、下载与联系我们。前端 Vue 3，后端 FastAPI，数据库 SQLite。测试 / 生产环境用 **同一个 8001 端口** 同时提供页面和 `/api` 接口。本机热更新开发时，前台仍是 8001，后台单独占用 18001。

## 新手从这里开始

请按顺序阅读 `docs` 目录（从零讲解，含每一步命令）：

1. [从零开始](./docs/00_从零开始.md) — 项目是什么、端口/虚拟环境/Docker 等词是什么意思
2. [项目文件组成与功能](./docs/05_项目文件组成与功能.md) — 每个文件干什么、哪些不要上传
3. [打包方法](./docs/06_打包方法.md) — 如何打 `RxWeb-deploy.zip`
4. 按环境动手：
   - [Windows 部署与运行](./docs/07_Windows部署与运行.md) → `start.ps1` / `start-dev.ps1`
   - [Ubuntu / 宝塔 部署与运行](./docs/08_Ubuntu部署与运行.md) → `start.sh`
   - [Docker 部署与运行](./docs/09_Docker部署与运行.md) → `Dockerfile` + `docker-compose.yml`

设计文档（架构、表结构、接口、前端规划）：[01](./docs/01_System_Architecture.md) · [02](./docs/02_Database_Design.md) · [03](./docs/03_API_Endpoints.md) · [04](./docs/04_Frontend_Design.md)

## 最快三条命令

Windows 本机：

```powershell
cd D:\Projects\RxWeb
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

浏览器打开 http://127.0.0.1:8001

本机改代码立刻刷新（前台 8001 + 后台 18001）：

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

Ubuntu（zip 已解压到 `/www/wwwroot/RxWeb`）：

```bash
sed -i 's/\r$//' /www/wwwroot/RxWeb/start.sh
bash /www/wwwroot/RxWeb/start.sh --daemon
```

浏览器打开 `http://服务器IP:8001`。测试机不必开放 18001。

Docker（项目根目录）：

```bash
docker compose up --build -d
```

## 技术栈

- 前端：Vue 3、Vite、Vue Router、Pinia、Element Plus
- 后端：Python 3、FastAPI、Uvicorn
- 数据库：SQLite（`company.db`）

根目录的 `requirements.txt` 是历史 Flask 清单，**不要用它安装依赖**。后端请使用 `backend/requirements.txt`。

## 初始账号

首次启动或写入种子数据后，可用下面两个账号登录（登录页不展示）：

| 角色 | 邮箱 | 密码 | 说明 |
| :--- | :--- | :--- | :--- |
| 管理员 | `admin@rxweb.com` | `rxweb123` | 进入后台，管理新闻、产品、留言和操作日志 |
| 普通用户 | `user@rxweb.com` | `user123` | 查看自己提交的留言和回复 |

也可在登录页自行注册普通用户。后台地址：`/admin`（未登录会跳到登录页）。

## 忽略清单

`.gitignore` 会忽略 `node_modules`、虚拟环境、日志、`frontend/dist`、本地 zip 等。Windows 的 `backend/venv` 不能拿到 Linux 上使用。
