# Windows 部署与运行

适合：在自己的 Windows 电脑上先把官网跑起来。云服务器请看 [08_Ubuntu部署与运行.md](./08_Ubuntu部署与运行.md)。

## 1. 安装两个软件

### Python 3

1. 打开 https://www.python.org/downloads/ 下载 Windows 安装包
2. 安装界面 **必须勾选** `Add python.exe to PATH`
3. 新开一个 PowerShell，输入：

```powershell
python --version
```

能看到 `Python 3.x.x` 即可。

### Node.js

1. 打开 https://nodejs.org/ 下载 LTS 版本
2. 安装完成后新开 PowerShell：

```powershell
node --version
npm --version
```

两个命令都有版本号即可。

## 2. 拿到项目代码

若你已经有 `D:\Projects\RxWeb` 文件夹，跳过。否则把整个项目拷到一个不含中文空格最好的路径，例如 `D:\Projects\RxWeb`。

## 3. 一键启动（和 Ubuntu 测试机相同：一个 8001 端口）

在项目根目录打开 PowerShell：

```powershell
cd D:\Projects\RxWeb
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

第一次会：创建 `.venv` → 安装 Python 包 → 没有 `company.db` 就写入演示数据 → `npm install` / `npm run build` → 启动网站。

浏览器打开：**http://127.0.0.1:8001**

当前窗口不要关。要停止：在这个窗口按 `Ctrl+C`。

### 后台运行（关掉 PowerShell 也继续）

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1 -Daemon
```

停止 / 查看状态：

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1 -Stop
powershell -ExecutionPolicy Bypass -File .\start.ps1 -Status
```

后台日志在 `logs\rxweb.log`。

### 改端口

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1 -Port 8001
```

## 4. 开发模式（改代码立刻刷新）

这是「两个进程、两个端口」，和上面的一键 8001 **不是同一套**。不要和 `start.ps1` 同时跑（都会占用 8001）。

推荐一条命令（后台 18001 + 前台 8001）：

```powershell
cd D:\Projects\RxWeb
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

浏览器打开：**http://127.0.0.1:8001**。Vite 会把 `/api` 转到 `18001`。

停止：当前窗口 `Ctrl+C` 停前台；再执行 `.\start-dev.ps1 -Stop` 停后台。

也可以手动开两个终端：

**终端 1 — 后端（18001）：**

```powershell
cd D:\Projects\RxWeb
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
..\.venv\Scripts\uvicorn.exe app.main:app --reload --port 18001
```

**终端 2 — 前端（8001）：**

```powershell
cd D:\Projects\RxWeb\frontend
npm install
npm run dev
```

开发时代理配置在 `frontend/vite.config.js`，目标必须是 `http://127.0.0.1:18001`。

改完后要上传到 Ubuntu 测试机：先 `pack-deploy.ps1` 打包，再按 [08_Ubuntu部署与运行.md](./08_Ubuntu部署与运行.md) 覆盖并重启。测试机只开 **8001**，不必开 18001。

新手若只想「先看到和服务器一样的网站」，用第 3 节的 `start.ps1` 即可。

## 5. 常见问题

**提示无法运行脚本 / ExecutionPolicy**

使用文档里的 `powershell -ExecutionPolicy Bypass -File .\start.ps1`，不要直接双击。

**python 不是内部或外部命令**

安装 Python 时没勾选 PATH。重装并勾选，或把 Python 安装目录加到系统环境变量 Path。

**中文乱码、字符串缺少终止符**

旧版 `pack-deploy.ps1` 曾因编码导致 PowerShell 5.1 解析失败。请使用仓库里现在这份英文提示的 `pack-deploy.ps1`。`start.ps1` 已尽量避免在关键字符串里使用会破坏解析的字符。

**页面只有 API 的 JSON，没有官网**

说明 `frontend\dist` 不存在或构建失败。看窗口里 `npm run build` 是否报错。

**端口被占用**

换端口：`.\start.ps1 -Port 8002`，或结束占用 8001 的程序。若刚跑过 `start-dev.ps1`，先 `.\start-dev.ps1 -Stop`。
