# Interview Copilot - uses only this folder's venv and .env
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = Join-Path $Root "..\venv\Scripts\python.exe"
$Pip = Join-Path $Root "..\venv\Scripts\pip.exe"
$MainPy = Join-Path $Root "..\main.py"
$EnvFile = Join-Path $Root ".env"
$EnvExample = Join-Path $Root ".env.example"
$Requirements = Join-Path $Root "requirements.txt"
$InstallMarker = Join-Path $Root "..\venv\.requirements-installed"

if (-not (Test-Path $Python)) {
    Write-Host "Creating interview-copilot venv..."
    python -m venv (Join-Path $Root "..\venv")
}

if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "Created .env - add OPENAI_API_KEY"
}

$NeedsInstall = -not (Test-Path $InstallMarker)
if (-not $NeedsInstall) {
    $NeedsInstall = (Get-Item $Requirements).LastWriteTimeUtc -gt
        (Get-Item $InstallMarker).LastWriteTimeUtc
}
if ($NeedsInstall) {
    Write-Host "Installing project dependencies..."
    & $Pip install -r $Requirements -q --trusted-host pypi.org --trusted-host files.pythonhosted.org
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed."
    }
    New-Item -ItemType File -Path $InstallMarker -Force | Out-Null
}

Write-Host "Interview Copilot"
Write-Host "  Folder: $Root"
Write-Host "  Python: $Python"
Write-Host "  Config: $EnvFile"
Write-Host ""

& $Python $MainPy
