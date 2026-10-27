# =============================================================================
# RxWeb Windows 启动脚本
# =============================================================================
# 这个文件是给 Windows 用的。双击不会自动跑完所有步骤，请用 PowerShell 执行。
#
# 【第一次使用前】请先安装：
#   1. Python 3.10 或更高：https://www.python.org/downloads/
#      安装时务必勾选 "Add python.exe to PATH"
#   2. Node.js（带 npm）：https://nodejs.org/
#
# 【怎么运行】在项目根目录（有 start.ps1 的那个文件夹）打开 PowerShell：
#   powershell -ExecutionPolicy Bypass -File .\start.ps1
#
# 【常用参数】
#   .\start.ps1                  前台运行，关闭窗口即停止
#   .\start.ps1 -Daemon          后台运行（关掉 PowerShell 也继续）
#   .\start.ps1 -Stop            停止后台进程
#   .\start.ps1 -Status          查看是否在运行
#   .\start.ps1 -Rebuild         强制重装 Python 依赖并重新构建前端
#   .\start.ps1 -Port 8001       指定端口，默认 8001
#
# 启动成功后浏览器打开：http://127.0.0.1:8001
# 本机热更新请用 start-dev.ps1，浏览器也是 8001。不要和本脚本同时跑。
# =============================================================================

# param 必须写在脚本最前面（注释块之后也可以，但要在其他命令之前）
# 它用来接收你在命令行里传入的开关和参数
param(
    [switch]$Daemon,     # 加了这个就是后台运行
    [switch]$Rebuild,    # 强制重装依赖、重建前端
    [switch]$Stop,       # 停止后台进程
    [switch]$Status,     # 只查看状态，不启动
    [switch]$Help,       # 显示帮助
    [int]$Port = 8001,   # 网站端口，默认 8001（页面和 /api 同一个端口）
    [string]$Site = "ruixue"
)

# 出错立刻停下来，避免后面步骤在错误状态下继续跑
$ErrorActionPreference = "Stop"

# -----------------------------------------------------------------------------
# 路径说明（务必读懂这几行）
# -----------------------------------------------------------------------------
# $PSScriptRoot = 本脚本所在目录，也就是项目根目录 RxWeb\
# 虚拟环境放在根目录 .venv\ ，不要用 backend\venv（那是旧的 Windows 环境）
# 前端源码在 frontend\ ，构建结果在 frontend\dist\
# 后端代码在 backend\ ，启动时工作目录必须是 backend\ ，uvicorn 才能找到 app.main
# -----------------------------------------------------------------------------
$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$VenvUvicorn = Join-Path $Venv "Scripts\uvicorn.exe"
$FrontendDir = Join-Path $Root "frontend"
$BackendDir = Join-Path $Root "backend"
$DistIndex = Join-Path $FrontendDir "dist\index.html"
$DbFile = Join-Path $Root "company.db"
$LogDir = Join-Path $Root "logs"
$PidFile = Join-Path $Root "rxweb.pid"
$LogFile = Join-Path $LogDir "rxweb.log"

# 监听地址 0.0.0.0 表示本机所有网卡都能访问（局域网其他电脑也能打开）
# 注意：PowerShell 里 $Host 是保留名，所以这里用 $BindHost
$BindHost = "0.0.0.0"

function Show-Help {
    Write-Host "RxWeb Windows start script"
    Write-Host "  .\start.ps1              foreground (Ctrl+C to stop)"
    Write-Host "  .\start.ps1 -Daemon      background"
    Write-Host "  .\start.ps1 -Stop        stop background process"
    Write-Host "  .\start.ps1 -Status      show status"
    Write-Host "  .\start.ps1 -Rebuild     reinstall deps and rebuild frontend"
    Write-Host "  .\start.ps1 -Port 8001   bind port (default 8001)"
}

function Test-RxWebRunning {
    # pid 文件里存的是后台进程的进程号
    # 文件在、进程也还活着，才算真正在运行
    if (-not (Test-Path $PidFile)) { return $false }
    $procId = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if (-not $procId) { return $false }
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    return [bool]$proc
}

if ($Help) {
    Show-Help
    exit 0
}

if ($Stop) {
    if (Test-RxWebRunning) {
        $procId = Get-Content $PidFile | Select-Object -First 1
        Write-Host "[info] stopping pid=$procId ..."
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "[info] stopped"
    } else {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "[info] not running"
    }
    exit 0
}

if ($Status) {
    if (Test-RxWebRunning) {
        $procId = Get-Content $PidFile | Select-Object -First 1
        Write-Host "[info] running pid=$procId  http://${BindHost}:${Port}"
        exit 0
    }
    Write-Host "[info] not running"
    exit 1
}

Set-Location $Root

if (Test-RxWebRunning) {
    $procId = Get-Content $PidFile | Select-Object -First 1
    Write-Host "[error] already running pid=$procId . Stop first: .\start.ps1 -Stop"
    exit 1
}

# -----------------------------------------------------------------------------
# 1) 检查 Python
# Windows 上命令一般是 python，不是 python3
# -----------------------------------------------------------------------------
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[error] python not found. Install Python 3 and tick 'Add python.exe to PATH'."
    exit 1
}

# -----------------------------------------------------------------------------
# 2) 创建虚拟环境
# 虚拟环境 = 项目自己的 Python 依赖隔离目录，避免污染系统 Python
# -----------------------------------------------------------------------------
if (-not (Test-Path $VenvPython)) {
    Write-Host "[info] creating venv: $Venv"
    python -m venv $Venv
    $Rebuild = $true
}

# -----------------------------------------------------------------------------
# 3) 安装后端依赖（fastapi / uvicorn 等）
# 依赖清单在 backend\requirements.txt
# -----------------------------------------------------------------------------
if ($Rebuild -or -not (Test-Path $VenvUvicorn)) {
    Write-Host "[info] installing backend requirements..."
    & $VenvPython -m pip install -U pip
    & $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt")
}

# -----------------------------------------------------------------------------
# 4) 准备 SQLite 数据库 company.db
# 没有这个文件时，用 seed.py 写入演示数据（产品、新闻、下载）
# -----------------------------------------------------------------------------
if (-not (Test-Path $DbFile)) {
    Write-Host "[info] company.db missing, seeding demo data for site $Site..."
    Push-Location $BackendDir
    $env:SITE_ID = $Site
    & $VenvPython "seed.py"
    Pop-Location
}

# -----------------------------------------------------------------------------
# 5) 构建前端
# Vue 源码不能直接给浏览器用，要用 Vite 编译成 frontend\dist\
# FastAPI 会把 dist 和 API 挂在同一个 8001 端口
# -----------------------------------------------------------------------------
$needBuild = $false
if ($Rebuild) { $needBuild = $true }
elseif (-not (Test-Path $DistIndex)) { $needBuild = $true }

if ($needBuild) {
    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npmCmd) {
        Write-Host "[error] npm not found. Install Node.js, or copy frontend\dist from another machine."
        exit 1
    }
    Write-Host "[info] building frontend for site $Site..."
    $env:VITE_SITE_ID = $Site
    Push-Location $FrontendDir
    if (-not (Test-Path "node_modules")) {
        npm install
        if ($LASTEXITCODE -ne 0) { Pop-Location; throw "npm install failed" }
    }
    npm run build
    if ($LASTEXITCODE -ne 0) { Pop-Location; throw "npm run build failed" }
    Pop-Location
} else {
    Write-Host "[info] frontend\dist exists, skip build (use -Rebuild to force)"
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

Write-Host "[info] starting http://${BindHost}:${Port}"

# -----------------------------------------------------------------------------
# 6) 启动 uvicorn
# 必须在 backend 目录下执行：app.main:app 表示 backend\app\main.py 里的 app 对象
# -----------------------------------------------------------------------------
if ($Daemon) {
    # Start-Process 会新开一个进程，当前窗口可以关掉
    $proc = Start-Process -FilePath $VenvUvicorn `
        -ArgumentList "app.main:app","--host",$BindHost,"--port","$Port" `
        -WorkingDirectory $BackendDir `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError $LogFile `
        -WindowStyle Hidden `
        -PassThru
    Set-Content -Path $PidFile -Value $proc.Id
    Start-Sleep -Milliseconds 800
    if (Test-RxWebRunning) {
        Write-Host "[info] started in background pid=$($proc.Id)"
        Write-Host "[info] log: $LogFile"
        Write-Host "[info] stop: .\start.ps1 -Stop"
    } else {
        Write-Host "[error] start failed, see log: $LogFile"
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        exit 1
    }
} else {
    # 前台运行：日志直接打在当前窗口，按 Ctrl+C 停止
    Set-Location $BackendDir
    & $VenvUvicorn app.main:app --host $BindHost --port $Port
}
