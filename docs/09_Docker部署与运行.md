# Docker 部署与运行

适合：不想在系统里单独折腾 Python / Node 版本。Windows、macOS、Ubuntu 只要安装了 Docker，命令几乎一样。默认网站端口 **8001**。

先读 [00_从零开始.md](./00_从零开始.md) 里「镜像 vs 容器」那两句。

## 1. 安装 Docker

- Windows：安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)，安装后重启，托盘图标显示 Running。
- Ubuntu 服务器：按 Docker 官方文档安装 Docker Engine，并安装 Compose 插件（`docker compose version` 能出版本号）。

验证：

```bash
docker version
docker compose version
```

## 2. 相关文件各自干什么

| 文件 | 作用 |
|------|------|
| `Dockerfile` | 分两阶段：用 Node 编译 Vue，再用 Python 镜像只保留运行所需文件 |
| `.dockerignore` | 构建时排除 `venv`、`node_modules` 等，加快构建、避免把 Windows 环境打进 Linux 镜像 |
| `docker-entrypoint.sh` | 容器启动：没有数据库就执行 `seed.py`，然后前台启动 uvicorn |
| `docker-compose.yml` | 端口映射 `8001:8001`，数据库放到数据卷 `/data` |

你平时最常用的是 **compose 那一条命令**。

## 3. 推荐：compose 一键启动

在**项目根目录**（和 `Dockerfile` 同一层）执行：

```bash
docker compose up --build -d
```

含义：

- `--build`：按 Dockerfile 重新构建镜像（改过代码就要加）
- `-d`：后台运行

浏览器：**http://127.0.0.1:8001**  
（在云服务器上则是 `http://公网IP:8001`，同样要放行安全组 8001）

查看状态 / 日志 / 停止：

```bash
docker compose ps
docker compose logs -f
docker compose down
```

`down` 默认**不会删除**名为 `rxweb-data` 的数据卷，新闻等数据还在。若要连数据一起删：

```bash
docker compose down -v
```

## 4. 不用 compose 时的等价命令

构建：

```bash
docker build -t rxweb:latest .
```

运行（数据库仍建议挂到命名卷）：

```bash
docker volume create rxweb-data
docker run -d --name rxweb -p 8001:8001 -e RXWEB_DB=/data/company.db -v rxweb-data:/data rxweb:latest
```

停止并删除容器（数据卷还在）：

```bash
docker stop rxweb
docker rm rxweb
```

## 5. 环境变量 `RXWEB_DB`

后端默认读项目根目录的 `company.db`。在容器里把数据库放到数据卷目录更安全：

```text
RXWEB_DB=/data/company.db
```

`docker-compose.yml` 已经写好。不要把 Docker 卷直接挂载到「一个文件路径」上，容易变成目录，SQLite 会失败。

## 6. 把镜像拷到没有 Dockerfile 的服务器

在已构建成功的电脑：

```bash
docker save rxweb:latest -o rxweb-image.tar
```

上传 tar 后：

```bash
docker load -i rxweb-image.tar
docker run -d --name rxweb -p 8001:8001 -e RXWEB_DB=/data/company.db -v rxweb-data:/data rxweb:latest
```

## 7. 常见问题

**构建很慢 / npm 失败**

需要能访问 npm 源。可配置镜像后再 `docker compose up --build`。

**端口被占用**

改 `docker-compose.yml` 里 `ports` 左边的数字，例如 `"8002:8001"`，浏览器改用 8002。右边 `8001` 是容器内部端口，不要改。

**改了代码网页没变**

必须重新构建：`docker compose up --build -d`。只 `up -d` 不会把新源码编进旧镜像。

**Windows 下报文件共享 / WSL 问题**

确认 Docker Desktop 已启动，项目放在它允许访问的磁盘路径。
