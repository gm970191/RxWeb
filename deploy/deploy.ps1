# =============================================================================
# deploy.ps1 - Windows 一键发布到 Ubuntu / 宝塔
# =============================================================================
# 请用 PowerShell 7（pwsh），不要用系统自带的 Windows PowerShell 5.1。
# 7.x 默认按 UTF-8 解析脚本，不需要 UTF-8 BOM。
#
# 在项目根目录执行（必须指定站点；默认发到调试机）：
#   pwsh -File .\deploy\deploy.ps1 -Site aierde
#   pwsh -File .\deploy\deploy.ps1 -Site aierde -Target prod
#
# 常用参数：
#   -Site           站点目录名，对应 deploy/sites/<站点>/site.env
#   -Target         debug（默认）或 prod。生产地址或端口为空时直接拒绝
#   -NoBuild        已有 frontend/dist 时跳过构建
#   -DryRun         只打包暂存，不上传
#   -SetupKey       把本机 SSH 公钥装到服务器，以后免密
#   -SkipRestart    只传文件，不重启进程
#   -Reseed         上传后按 seed.py 重写远程 company.db 演示数据
#
# 站点地址、目录、端口：deploy/sites/<站点>/site.env
# SSH 口令：deploy/machines.env（不要提交）
# =============================================================================

#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Site,
    [ValidateSet("debug", "prod")]
    [string]$Target = "debug",
    [switch]$NoBuild,
    [switch]$DryRun,
    [switch]$SetupKey,
    [switch]$SkipRestart,
    [switch]$Reseed
)

$ErrorActionPreference = "Stop"
$DeployDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $DeployDir
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

function Get-SeedValue {
    param(
        [string]$Text,
        [string]$Name
    )
    $pattern = '(?m)^' + [regex]::Escape($Name) + '\s*=\s*[''"]([^''"]+)[''"]'
    if ($Text -match $pattern) { return $Matches[1] }
    return ""
}

function Get-EnvValue {
    param([string]$Name)
    $item = Get-Item -Path "Env:$Name" -ErrorAction SilentlyContinue
    if (-not $item) { return "" }
    return Get-CleanText ([string]$item.Value)
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

if ($Site -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]*$') {
    Raise-DeployError "站点名只能使用字母、数字、下划线和连字符"
}

$SiteDir = Join-Path $DeployDir (Join-Path "sites" $Site)
$SiteFile = Join-Path $SiteDir "site.env"
if (-not (Test-Path $SiteFile)) {
    Raise-DeployError ("找不到站点配置 {0}" -f $SiteFile)
}

Read-DeployEnv (Join-Path $DeployDir "machines.env")
Read-DeployEnv $SiteFile
$siteSecret = Join-Path $SiteDir "deploy.env"
if (Test-Path $siteSecret) { Read-DeployEnv $siteSecret }

$prefix = $(if ($Target -eq "prod") { "PROD" } else { "DEBUG" })
$HostName = Get-EnvValue "${prefix}_HOST"
$UserName = Get-EnvValue "${prefix}_USER"
if (-not $UserName) { $UserName = "root" }
$RemotePath = Get-EnvValue "${prefix}_PATH"
$SshPort = Get-EnvValue "${prefix}_SSH_PORT"
if (-not $SshPort) { $SshPort = "22" }
$AppPort = Get-EnvValue "${prefix}_APP_PORT"
$Password = Get-EnvValue "${prefix}_PASS"
if (-not $Password) { $Password = Get-EnvValue "DEPLOY_PASS" }
$SiteTitle = Get-CleanText $(if ($env:SITE_NAME) { $env:SITE_NAME } else { $Site })
$env:VITE_SITE_ID = $(if ($env:SITE_ID) { Get-CleanText $env:SITE_ID } else { $Site })
$env:VITE_SITE_NAME = $SiteTitle

$missing = @()
if (-not $HostName) { $missing += "${prefix}_HOST" }
if (-not $RemotePath) { $missing += "${prefix}_PATH" }
if (-not $AppPort) { $missing += "${prefix}_APP_PORT" }
if ($AppPort -and $AppPort -notmatch '^\d+$') { $missing += "${prefix}_APP_PORT(必须是数字)" }
if ($missing.Count -gt 0) {
    Raise-DeployError ("{0} 的 {1} 还是空的，已停止。请先填写 deploy/sites/{2}/site.env" -f $Target, ($missing -join ", "), $Site)
}

$Remote = "${UserName}@${HostName}"
$SiteUrl = "http://${HostName}:${AppPort}/"

Write-Info ("site    {0}  {1}" -f $Site, $SiteTitle)
Write-Info ("target  {0}  {1}:{2}" -f $Target, $Remote, $SshPort)
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
        Raise-DeployError "密钥登录失败，且 deploy/machines.env 里没有对应环境的口令"
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
        Write-Info "完成。之后可把 deploy/machines.env 里的口令删掉。"
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
        Write-Info ("构建前端（站点 {0}）..." -f $env:VITE_SITE_ID)
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
    $startSrc = Join-Path $Root "start.sh"
    $startText = [System.IO.File]::ReadAllText($startSrc)
    if ($startText -notmatch '@RXWEB_APP_PORT@') {
        Raise-DeployError "start.sh 缺少端口占位符 @RXWEB_APP_PORT@"
    }
    $startText = $startText.Replace('@RXWEB_APP_PORT@', $AppPort)
    $startUtf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText((Join-Path $stage "start.sh"), $startText, $startUtf8)

    $backendSrc = Join-Path $Root "backend"
    Get-ChildItem $backendSrc -Recurse -File | Where-Object {
        $_.FullName -notmatch '\\venv\\' -and
        $_.FullName -notmatch '\\__pycache__\\' -and
        $_.FullName -notmatch '\\seed_data\\' -and
        $_.Name -ne "site_seed.py" -and
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
    $seedSrc = Join-Path $SiteDir "seed_data.py"
    if (-not (Test-Path $seedSrc)) {
        Raise-DeployError ("找不到该站点的种子数据 {0}" -f $seedSrc)
    }
    $seedText = Get-Content -Raw -Encoding utf8 $seedSrc
    $siteIdPattern = 'SITE_ID\s*=\s*[''"]' + [regex]::Escape($env:VITE_SITE_ID) + '[''"]'
    if ($seedText -notmatch $siteIdPattern) {
        Raise-DeployError ("种子文件的 SITE_ID 不是 {0}" -f $env:VITE_SITE_ID)
    }
    Copy-Item $seedSrc (Join-Path $stage "backend\site_seed.py")
    Write-Info ("只上传该站点的种子数据 {0}" -f $seedSrc)
    Copy-Item -Recurse -Force (Join-Path $Root "frontend\dist\*") (Join-Path $stage "frontend\dist\")
    $runtimeLines = New-Object System.Collections.Generic.List[string]
    $runtimeSrc = Join-Path $SiteDir "runtime.env"
    if (Test-Path $runtimeSrc) {
        Get-Content -Path $runtimeSrc -Encoding utf8 | ForEach-Object {
            $line = Get-CleanText $_
            if (-not $line) { return }
            if ($line.StartsWith("PORT=") -or $line.StartsWith("PUBLIC_BASE_URL=") -or $line.StartsWith("SITE_ID=") -or $line.StartsWith("SITE_NAME=") -or $line.StartsWith("RXWEB_ADMIN_EMAIL=") -or $line.StartsWith("RXWEB_USER_EMAIL=")) { return }
            $runtimeLines.Add($line)
        }
        Write-Info "将一并上传该站点 runtime.env（SMTP 等），并按本次目标写入端口"
    } else {
        Write-Info "该站点没有 runtime.env，只写入端口和 PUBLIC_BASE_URL"
    }
    $runtimeBody = New-Object System.Collections.Generic.List[string]
    $runtimeBody.Add("PORT=$AppPort")
    $runtimeBody.Add("PUBLIC_BASE_URL=http://${HostName}:${AppPort}")
    $runtimeBody.Add("SITE_ID=$($env:VITE_SITE_ID)")
    $runtimeBody.Add("SITE_NAME=$(Quote-BashSingle $SiteTitle)")
    $adminEmail = Get-SeedValue $seedText "admin_email"
    $userEmail = Get-SeedValue $seedText "user_email"
    if (-not $adminEmail -or -not $userEmail) {
        Raise-DeployError "种子文件缺少 admin_email 或 user_email"
    }
    $runtimeBody.Add("RXWEB_ADMIN_EMAIL=$adminEmail")
    $runtimeBody.Add("RXWEB_USER_EMAIL=$userEmail")
    foreach ($line in $runtimeLines) { $runtimeBody.Add($line) }
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllLines((Join-Path $stage "runtime.env"), $runtimeBody, $utf8)

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

    $remoteTar = "/tmp/rxweb-deploy-$Site.tgz"
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
        ("rm -rf {0} {1} {2}" -f (Quote-BashSingle "$RemotePath/frontend/dist"), (Quote-BashSingle "$RemotePath/backend/seed_data"), (Quote-BashSingle "$RemotePath/backend/app/__pycache__"))
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
        $seedCmd = ('cd {0} && SITE_ID={1} python3 backend/seed.py' -f (Quote-BashSingle $RemotePath), (Quote-BashSingle $env:VITE_SITE_ID))
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
