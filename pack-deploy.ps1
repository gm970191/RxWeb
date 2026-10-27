# Build production zip (backend + frontend/dist only).
#   powershell -ExecutionPolicy Bypass -File .\pack-deploy.ps1
#   python .\pack-deploy.py

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$py = $null
foreach ($name in @("python", "py", "python3")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Source; break }
}
if (-not $py) {
    throw "python not found. Install Python and add it to PATH."
}

& $py (Join-Path $Root "pack-deploy.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
