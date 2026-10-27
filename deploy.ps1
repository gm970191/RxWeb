# =============================================================================
# deploy.ps1 - Windows 一键发布到 Ubuntu / 宝塔
# =============================================================================
# 请用 PowerShell 7（pwsh），不要用系统自带的 Windows PowerShell 5.1。
# 7.x 默认按 UTF-8 解析脚本，不需要 UTF-8 BOM。
#
# 在项目根目录执行：
#   pwsh -File .\deploy.ps1
#
# 常用参数：
#   -NoBuild        已有 frontend/dist 时跳过构建
#   -DryRun         只打包暂存，不上传
#   -SetupKey       把本机 SSH 公钥装到服务器，以后免密
#   -SkipRestart    只传文件，不重启进程
#   -Reseed         上传后按 seed.py 重写远程 company.db 演示数据
#
# 配置写在 deploy.env（不要提交）。默认发布到：
#   root@47.97.245.103:/www/wwwroot/RxWeb   端口 8001
# =============================================================================

#Requires -Version 7.0

[CmdletBinding()]
param(
    [switch]$NoBuild,
    [switch]$DryRun,
    [switch]$SetupKey,
    [switch]$SkipRestart,
    [switch]$Reseed
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Write-Info {
    param([string]$Message)
    Write-Host ('[info] ' + $Message)
}

function Raise-DeployError {
    param([string]$Message)
    throw ('[error] ' + $Message)
}

function Get-CleanText {
    param([string]$Text)
    if ([string]::IsNullOrEmpty($Text)) { return "" }
    return $Text.Replace("`r", "").Replace("`n", "").Trim()
}

function Quote-BashSingle {
    param([string]$Value)
    $clean = Get-CleanText $Value
    return ("'" + $clean.Replace("'", "'\''") + "'")
}

function Read-DeployEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    Get-Content -Path $Path -Encoding utf8NoBOM | ForEach-Object {
        $line = Get-CleanText $_
        if (-not $line -or $line.StartsWith("#") -or ($line -notmatch "=")) { return }
        $key, $val = $line.Split("=", 2)
        $key = Get-CleanText $key
        $val = (Get-CleanText $val).Trim("'").Trim('"')
        Set-Item -Path "Env:$key" -Value $val
    }
}

Read-DeployEnv (Join-Path $Root "deploy.env")

$HostName = Get-CleanText $(if ($env:DEPLOY_HOST) { $env:DEPLOY_HOST } else { "47.97.245.103" })
$UserName = Get-CleanText $(if ($env:DEPLOY_USER) { $env:DEPLOY_USER } else { "root" })
$RemotePath = Get-CleanText $(if ($env:DEPLOY_PATH) { $env:DEPLOY_PATH } else { "/www/wwwroot/RxWeb" })
$SshPort = Get-CleanText $(if ($env:DEPLOY_SSH_PORT) { $env:DEPLOY_SSH_PORT } else { "22" })
$AppPort = Get-CleanText $(if ($env:APP_PORT) { $env:APP_PORT } else { "8001" })
$Password = Get-CleanText $(if ($env:DEPLOY_PASS) { $env:DEPLOY_PASS } else { "" })
$Remote = "${UserName}@${HostName}"
$SiteUrl = "http://${HostName}:${AppPort}/"

Write-Info ("target  {0}:{1}" -f $Remote, $SshPort)
Write-Info ("path    {0}" -f $RemotePath)
Write-Info ("url     {0}" -f $SiteUrl)

foreach ($cmd in @("ssh", "scp", "tar")) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Raise-DeployError ("找不到命令 {0}。请在 Windows 可选功能里启用 OpenSSH 客户端。" -f $cmd)
    }
}

$script:AskPassFile = $null
$script:UsePassword = $false

function Clear-AskPass {
    if ($script:AskPassFile -and (Test-Path $script:AskPassFile)) {
        Remove-Item -Force $script:AskPassFile -ErrorAction SilentlyContinue
    }
    Remove-Item Env:SSH_ASKPASS -ErrorAction SilentlyContinue
    Remove-Item Env:SSH_ASKPASS_REQUIRE -ErrorAction SilentlyContinue
}

function Enable-PasswordAuth {
    if (-not $Password) {
        Raise-DeployError "密钥登录失败，且 deploy.env 里没有 DEPLOY_PASS"
    }
    $ask = Join-Path $env:TEMP ("rxweb-askpass-{0}.cmd" -f [guid]::NewGuid().ToString("n"))
    $esc = $Password.Replace("%", "%%")
    Set-Content -Path $ask -Value "@echo off`r`necho $esc" -Encoding ASCII -NoNewline
    $script:AskPassFile = $ask
    $env:SSH_ASKPASS = $ask
    $env:SSH_ASKPASS_REQUIRE = "force"
    $env:DISPLAY = "localhost:0"
    $script:UsePassword = $true
}

function Get-SshArgs {
    $opts = @(
        "-p", $SshPort,
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ServerAliveInterval=30",
        "-o", "ConnectTimeout=12"
    )
    if ($script:UsePassword) {
        $opts += @(
            "-o", "PreferredAuthentications=password",
            "-o", "PubkeyAuthentication=no",
            "-o", "NumberOfPasswordPrompts=1"
        )
    }
    return $opts
}

function Invoke-Remote {
    param(
        [Parameter(Mandatory = $true)][string]$RemoteCommand,
        [switch]$IgnoreFailure
    )
    # 必须把整条命令当成 ssh 的一个参数。
    # 若写成 ssh host bash -lc $cmd，Windows OpenSSH 会拼成：
    #   bash -lc mkdir -p ...
    # 于是 bash -c 只执行 mkdir，后面的路径全丢，报 missing operand。
    $cmd = Get-CleanText $RemoteCommand
    $sshArgs = (Get-SshArgs) + @("-o", "RequestTTY=no", $Remote, "--", $cmd)
    if ($IgnoreFailure) {
        & ssh @sshArgs 1>$null 2>$null
    } else {
        & ssh @sshArgs
    }
    if (-not $IgnoreFailure -and $LASTEXITCODE -ne 0) {
        Raise-DeployError ("远程命令失败 (exit {0}): {1}" -f $LASTEXITCODE, $cmd)
    }
    return $LASTEXITCODE
}

function Test-SshKeyLogin {
    $probe = @(
        "-p", $SshPort,
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=8",
        "-o", "StrictHostKeyChecking=accept-new",
        $Remote, "true"
    )
    & ssh @probe 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

try {
    if (-not $DryRun) {
        if (Test-SshKeyLogin) {
            Write-Info "SSH 密钥登录成功"
        } else {
            Enable-PasswordAuth
            Write-Info "使用密码登录（建议随后执行 -SetupKey 改为免密）"
        }
    }

    if ($SetupKey) {
        $sshDir = Join-Path $env:USERPROFILE ".ssh"
        if (-not (Test-Path $sshDir)) {
            New-Item -ItemType Directory -Path $sshDir | Out-Null
        }
        $key = Join-Path $sshDir "id_ed25519"
        $pub = "$key.pub"
        if (-not (Test-Path $pub)) {
            Write-Info ("生成本机 SSH 密钥: {0}" -f $key)
            & ssh-keygen -t ed25519 -N "" -f $key
            if ($LASTEXITCODE -ne 0) { Raise-DeployError "ssh-keygen 失败" }
        }
        $pubText = Get-CleanText (Get-Content -Raw $pub)
        Write-Info ("安装公钥到 {0}:~/.ssh/authorized_keys" -f $Remote)
        $install = ('mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && grep -qxF {0} ~/.ssh/authorized_keys || echo {0} >> ~/.ssh/authorized_keys' -f (Quote-BashSingle $pubText))
        Invoke-Remote $install
        Write-Info "完成。之后可把 deploy.env 里的 DEPLOY_PASS 删掉。"
        return
    }

    $distIndex = Join-Path $Root "frontend\dist\index.html"
    if ($NoBuild) {
        if (-not (Test-Path $distIndex)) {
            Raise-DeployError "-NoBuild 但找不到 frontend/dist/index.html"
        }
        Write-Info "跳过构建，使用已有 frontend/dist"
    } else {
        if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
            Raise-DeployError "找不到 npm。请安装 Node.js，或带 -NoBuild 使用已有 dist"
        }
        Write-Info "构建前端 ..."
        Push-Location (Join-Path $Root "frontend")
        try {
            if (-not (Test-Path "node_modules")) {
                & npm install
                if ($LASTEXITCODE -ne 0) { Raise-DeployError "npm install 失败" }
            }
            & npm run build
            if ($LASTEXITCODE -ne 0) { Raise-DeployError "npm run build 失败" }
        } finally {
            Pop-Location
        }
        if (-not (Test-Path $distIndex)) {
            Raise-DeployError "构建后仍没有 frontend/dist/index.html"
        }
    }

    $stage = Join-Path $env:TEMP ("rxweb-stage-" + [guid]::NewGuid().ToString("n"))
    New-Item -ItemType Directory -Path (Join-Path $stage "backend") | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $stage "frontend\dist") | Out-Null
    Copy-Item (Join-Path $Root "start.sh") (Join-Path $stage "start.sh")
    $service = Join-Path $Root "rxweb.service"
    if (Test-Path $service) {
        Copy-Item $service (Join-Path $stage "rxweb.service")
    }

    $backendSrc = Join-Path $Root "backend"
    Get-ChildItem $backendSrc -Recurse -File | Where-Object {
        $_.FullName -notmatch '\\venv\\' -and
        $_.FullName -notmatch '\\__pycache__\\' -and
        $_.Extension -ne ".pyc" -and
        $_.Extension -ne ".db"
    } | ForEach-Object {
        $rel = $_.FullName.Substring($backendSrc.Length).TrimStart("\", "/")
        $dest = Join-Path (Join-Path $stage "backend") $rel
        $destDir = Split-Path $dest -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir | Out-Null
        }
        Copy-Item $_.FullName $dest
    }
    Copy-Item -Recurse -Force (Join-Path $Root "frontend\dist\*") (Join-Path $stage "frontend\dist\")
    $runtimeEnv = Join-Path $Root "runtime.env"
    if (Test-Path $runtimeEnv) {
        Copy-Item $runtimeEnv (Join-Path $stage "runtime.env")
        Write-Info "将一并上传 runtime.env（SMTP 等运行配置）"
    }

    Write-Info "将上传: start.sh, backend/, frontend/dist/"
    Write-Info "不会上传: node_modules, .git, venv, company.db, 源码 src/"

    if ($DryRun) {
        Write-Host ('[dry-run] 暂存目录: ' + $stage)
        Get-ChildItem $stage -Recurse -File | ForEach-Object {
            Write-Host ("  " + $_.FullName.Substring($stage.Length))
        }
        Write-Host '[dry-run] 未连接服务器，退出'
        Remove-Item -Recurse -Force $stage
        return
    }

    $tarball = Join-Path $env:TEMP ("rxweb-deploy-" + [guid]::NewGuid().ToString("n") + ".tgz")
    Write-Info "打包暂存目录 ..."
    & tar -czf $tarball -C $stage .
    if ($LASTEXITCODE -ne 0) { Raise-DeployError "tar 打包失败" }

    $remoteTar = "/tmp/rxweb-deploy.tgz"
    Write-Info "上传压缩包 ..."
    $scpArgs = @(
        "-P", $SshPort,
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=12"
    )
    if ($script:UsePassword) {
        $scpArgs += @(
            "-o", "PreferredAuthentications=password",
            "-o", "PubkeyAuthentication=no",
            "-o", "NumberOfPasswordPrompts=1"
        )
    }
    $scpArgs += @($tarball, "${Remote}:${remoteTar}")
    & scp @scpArgs
    if ($LASTEXITCODE -ne 0) { Raise-DeployError "scp 上传失败" }

    Write-Info "远程解压（不覆盖 company.db / .venv / logs）..."
    $extract = @(
        ("mkdir -p {0} {1} {2}" -f (Quote-BashSingle $RemotePath), (Quote-BashSingle "$RemotePath/backend"), (Quote-BashSingle "$RemotePath/frontend"))
        ("rm -rf {0}" -f (Quote-BashSingle "$RemotePath/frontend/dist"))
        ("tar -xzf {0} -C {1}" -f (Quote-BashSingle $remoteTar), (Quote-BashSingle $RemotePath))
        ("rm -f {0}" -f (Quote-BashSingle $remoteTar))
        ('sed -i ''s/\r$//'' {0}' -f (Quote-BashSingle "$RemotePath/start.sh"))
        ("chmod +x {0}" -f (Quote-BashSingle "$RemotePath/start.sh"))
        ('if [ -f {0} ]; then sed -i ''s/\r$//'' {0}; chmod 600 {0}; fi' -f (Quote-BashSingle "$RemotePath/runtime.env"))
    ) -join " && "
    Invoke-Remote $extract

    if ($SkipRestart) {
        Write-Info ("已跳过重启。文件已上传到 {0}" -f $RemotePath)
        return
    }

    Write-Info "检查远程 Python ..."
    $ensurePy = 'command -v python3 >/dev/null 2>&1 || (export DEBIAN_FRONTEND=noninteractive; apt-get update -y && apt-get install -y python3 python3-venv python3-pip)'
    Invoke-Remote $ensurePy

    if ($Reseed) {
        Write-Info "按 seed.py 重写远程演示数据（会覆盖 company.db 中的产品和新闻）..."
        $seedCmd = ('cd {0} && python3 backend/seed.py' -f (Quote-BashSingle $RemotePath))
        Invoke-Remote $seedCmd
    }

    Write-Info "重启服务 ..."
    $startSh = Quote-BashSingle "$RemotePath/start.sh"
    $restart = ('bash {0} --stop >/dev/null 2>&1 || true; bash {0} --daemon' -f $startSh)
    Invoke-Remote $restart

    Write-Info ("检查防火墙是否放行 {0} ..." -f $AppPort)
    $openFw = ('command -v ufw >/dev/null 2>&1 && ufw allow {0}/tcp || true' -f $AppPort)
    Invoke-Remote $openFw

    Write-Info "等待进程起来 ..."
    $healthPy = "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${AppPort}/', timeout=3).read(32)"
    $healthCmd = ('python3 -c {0}' -f (Quote-BashSingle $healthPy))
    $healthy = $false
    for ($i = 0; $i -lt 10; $i++) {
        $code = Invoke-Remote -RemoteCommand $healthCmd -IgnoreFailure
        if ($code -eq 0) {
            $healthy = $true
            break
        }
        Start-Sleep -Seconds 1
    }

    if (-not $healthy) {
        Write-Host '[error] 健康检查失败。最近日志：'
        try {
            Invoke-Remote ('tail -n 40 {0} 2>/dev/null || echo no-log' -f (Quote-BashSingle "$RemotePath/logs/rxweb.log"))
        } catch {}
        Raise-DeployError ("部署后网站没有响应 {0}" -f $SiteUrl)
    }

    Write-Host ('[done] 部署完成  ' + $SiteUrl)
    try { Invoke-Remote ('bash {0} --status' -f (Quote-BashSingle "$RemotePath/start.sh")) } catch {}
}
finally {
    Clear-AskPass
    if ($stage -and (Test-Path $stage)) {
        Remove-Item -Recurse -Force $stage -ErrorAction SilentlyContinue
    }
    if ($tarball -and (Test-Path $tarball)) {
        Remove-Item -Force $tarball -ErrorAction SilentlyContinue
    }
}
