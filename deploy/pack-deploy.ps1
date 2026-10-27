# Build production zip (backend + frontend/dist only).
#   pwsh -File .\deploy\pack-deploy.ps1

$ErrorActionPreference = "Stop"
$DeployDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $DeployDir
Set-Location $Root

$py = $null
foreach ($name in @("python", "py", "python3")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Source; break }
}
if (-not $py) {
    throw "python not found. Install Python and add it to PATH."
}

& $py (Join-Path $DeployDir "pack-deploy.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
