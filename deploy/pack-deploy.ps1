# Build one site's production zip (backend + that site's seed + frontend/dist).
#   pwsh -File .\deploy\pack-deploy.ps1 --site aierde

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

& $py (Join-Path $DeployDir "pack-deploy.py") @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
