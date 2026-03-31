#Requires -Version 5.1
<#
.SYNOPSIS
    Voice2Text - 01 Environment Setup
.DESCRIPTION
    Creates virtual environment, installs dependencies, creates data directories,
    and generates a default .env configuration file.
    Run this script once before using the application.
.EXAMPLE
    .\01setup.ps1
#>

Set-StrictMode -Version Latest
$script:ExitCode = 0
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# ------------------------------------------------------------------
# Helper: always pause before closing so the window stays readable
# ------------------------------------------------------------------
function Invoke-PauseExit {
    Write-Host ""
    Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
    $null = Read-Host
    exit $script:ExitCode
}

# ------------------------------------------------------------------
# Helper: print a section header
# ------------------------------------------------------------------
function Write-Step([string]$msg) {
    Write-Host ""
    Write-Host ">>> $msg" -ForegroundColor Yellow
}

# ------------------------------------------------------------------
# Main logic wrapped in try/catch so exceptions stay visible
# ------------------------------------------------------------------
try {

    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host " Voice2Text  01 - Environment Setup" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan

    # ── Python version check ──────────────────────────────────────
    Write-Step "Checking Python installation..."
    $pyCmd = $null
    foreach ($candidate in @("python", "python3", "py")) {
        try {
            $ver = & $candidate --version 2>&1
            if ($ver -match "Python 3\.(\d+)" -and [int]$Matches[1] -ge 10) {
                $pyCmd = $candidate
                Write-Host "  [OK] Found $ver" -ForegroundColor Green
                break
            }
        } catch { }
    }
    if (-not $pyCmd) {
        throw "Python 3.10 or newer not found. Please install from https://python.org and re-run."
    }

    # ── Create virtual environment ────────────────────────────────
    Write-Step "Setting up virtual environment..."
    if (-Not (Test-Path ".venv")) {
        Write-Host "  Creating .venv ..."
        & $pyCmd -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }
        Write-Host "  [OK] Virtual environment created." -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] .venv already exists." -ForegroundColor DarkGray
    }

    $pipExe    = Join-Path $ScriptDir ".venv\Scripts\pip.exe"
    $pythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"

    # ── Upgrade pip ───────────────────────────────────────────────
    Write-Step "Upgrading pip..."
    & $pythonExe -m pip install --upgrade pip --quiet
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
    Write-Host "  [OK] pip upgraded." -ForegroundColor Green

    # ── Install project dependencies ──────────────────────────────
    Write-Step "Installing project dependencies (pyproject.toml)..."
    Write-Host "  This may take several minutes on first run."
    & $pipExe install -e ".[all]"
    if ($LASTEXITCODE -ne 0) { throw "Package installation failed. Check pyproject.toml and network connection." }
    Write-Host "  [OK] Dependencies installed." -ForegroundColor Green

    # ── Create data directories ───────────────────────────────────
    Write-Step "Creating data directories..."
    foreach ($dir in @("data", "data\recordings")) {
        $full = Join-Path $ScriptDir $dir
        if (-Not (Test-Path $full)) {
            New-Item -ItemType Directory -Path $full | Out-Null
            Write-Host "  [OK] Created $dir" -ForegroundColor Green
        } else {
            Write-Host "  [SKIP] $dir already exists." -ForegroundColor DarkGray
        }
    }

    # ── Generate default .env ─────────────────────────────────────
    Write-Step "Generating .env configuration..."
    $envPath = Join-Path $ScriptDir ".env"
    if (-Not (Test-Path $envPath)) {
        $envContent = @"
# Voice2Text Configuration - Edit as needed

# ASR Model
DEFAULT_MODEL=Qwen/Qwen3-ASR-0.6B
DEVICE=cuda
DTYPE=float16

# Audio
SAMPLE_RATE=16000
CHANNELS=1
VAD_ENABLED=true

# Translation API (Ollama default)
TRANSLATION_API_URL=http://localhost:11434/v1/chat/completions
TRANSLATION_API_KEY=
TRANSLATION_MODEL=llama3.2

# Storage
DATA_DIR=./data
RECORDINGS_DIR=./data/recordings
DATABASE_URL=sqlite+aiosqlite:///./data/voice2text.db
MAX_HISTORY_ITEMS=1000

# OpenCC
OPENCC_MODE=s2t
HOTWORDS_FILE=./data/hotwords.json
"@
        $envContent | Set-Content $envPath -Encoding UTF8
        Write-Host "  [OK] Created .env (edit it to customize settings)" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] .env already exists." -ForegroundColor DarkGray
    }

    Write-Host ""
    Write-Host "===================================" -ForegroundColor Green
    Write-Host " Setup complete!" -ForegroundColor Green
    Write-Host " Next step: run 02download-models.ps1" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "[ERROR] $_" -ForegroundColor Red
    $script:ExitCode = 1
}

Invoke-PauseExit
