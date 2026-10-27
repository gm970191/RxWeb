# =============================================================================
# RxWeb Windows 本机开发启动（前后端分开两个端口）
# =============================================================================
# 调试机不用本脚本。调试机每个网站只有一个端口，页面和接口在一起。
#
# 本脚本只给 Windows 本机改代码时用。浏览器打开 http://127.0.0.1:8001 。
# 18001 是本机 FastAPI 的接口端口，不是网站端口。Vite 把 /api 转到这个端口。
#
# 【怎么运行】在项目根目录打开 PowerShell：
#   powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
#
# 【常用参数】
#   .\start-dev.ps1           前台跑 Vite；后端在后台 --reload
#   .\start-dev.ps1 -Stop     停止开发用的后端进程
#   .\start-dev.ps1 -Status   查看后端是否在跑
# =============================================================================

param(
    [switch]$Stop,
    [switch]$Status,
    [switch]$Help,
    [int]$FrontendPort = 8001,
    [int]$BackendPort = 18001,
    [string]$Site = "ruixue"
)

$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$VenvUvicorn = Join-Path $Venv "Scripts\uvicorn.exe"
$FrontendDir = Join-Path $Root "frontend"
$BackendDir = Join-Path $Root "backend"
if ($Site -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]*$') {
    Write-Host "[error] 站点名只能使用字母、数字、下划线和连字符"
    exit 1
}
$DataDir = Join-Path $Root (Join-Path "data" $Site)
$DbFile = Join-Path $DataDir "company.db"
$env:SITE_ID = $Site
$env:RXWEB_DB = $DbFile
$env:RXWEB_DEV_API_PORT = "$BackendPort"
$LogDir = Join-Path $Root "logs"
$PidFile = Join-Path $Root "rxweb-dev-backend.pid"
$LogFile = Join-Path $LogDir "rxweb-dev-backend.log"

function Show-Help {
    Write-Host "RxWeb Windows local dev"
    Write-Host "  open http://127.0.0.1:$FrontendPort"
    Write-Host "  .\start-dev.ps1         start backend + vite"
    Write-Host "  .\start-dev.ps1 -Stop   stop backend"
    Write-Host "  .\start-dev.ps1 -Status show backend status"
}

function Test-DevBackendRunning {
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
    if (Test-DevBackendRunning) {
        $procId = Get-Content $PidFile | Select-Object -First 1
        Write-Host "[info] stopping backend pid=$procId ..."
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "[info] backend stopped"
    } else {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "[info] backend not running"
    }
    exit 0
}

if ($Status) {
    if (Test-DevBackendRunning) {
        $procId = Get-Content $PidFile | Select-Object -First 1
        Write-Host "[info] backend running pid=$procId"
        exit 0
    }
    Write-Host "[info] backend not running"
    exit 1
}

Set-Location $Root

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[error] python not found. Install Python 3 and tick 'Add python.exe to PATH'."
    exit 1
}

$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Write-Host "[error] npm not found. Install Node.js."
    exit 1
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "[info] creating venv: $Venv"
    python -m venv $Venv
}

if (-not (Test-Path $VenvUvicorn)) {
    Write-Host "[info] installing backend requirements..."
    & $VenvPython -m pip install -U pip
    & $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt")
}

if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}
if (-not (Test-Path $DbFile)) {
    Write-Host "[info] seeding demo data for site $Site -> $DbFile"
    Push-Location $BackendDir
    & $VenvPython "seed.py"
    Pop-Location
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

if (Test-DevBackendRunning) {
    $procId = Get-Content $PidFile | Select-Object -First 1
    Write-Host "[info] backend already running pid=$procId"
} else {
    Write-Host "[info] starting backend"
    $proc = Start-Process -FilePath $VenvUvicorn `
        -ArgumentList "app.main:app","--reload","--host","127.0.0.1","--port","$BackendPort" `
        -WorkingDirectory $BackendDir `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError $LogFile `
        -WindowStyle Hidden `
        -PassThru
    Set-Content -Path $PidFile -Value $proc.Id
    Start-Sleep -Milliseconds 800
    if (-not (Test-DevBackendRunning)) {
        Write-Host "[error] backend start failed, see log: $LogFile"
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        exit 1
    }
    Write-Host "[info] backend pid=$($proc.Id)  log: $LogFile"
}

$env:VITE_SITE_ID = $Site
Write-Host "[info] starting frontend http://127.0.0.1:${FrontendPort} site=$Site"
Write-Host "[info] open browser: http://127.0.0.1:${FrontendPort}"
Write-Host "[info] stop vite: Ctrl+C ; stop backend: .\start-dev.ps1 -Stop"

Push-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    npm install
    if ($LASTEXITCODE -ne 0) { Pop-Location; throw "npm install failed" }
}
npm run dev -- --port $FrontendPort --strictPort --host
Pop-Location
