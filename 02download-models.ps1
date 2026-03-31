#Requires -Version 5.1
<#
.SYNOPSIS
    Voice2Text - 02 Download / Verify Models
.DESCRIPTION
    Downloads Qwen3-ASR speech recognition models from Hugging Face Hub
    into the local cache. Requires 01setup.ps1 to have been run first.
.EXAMPLE
    .\02download-models.ps1
#>

Set-StrictMode -Version Latest
$script:ExitCode = 0
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

function Invoke-PauseExit {
    Write-Host ""
    Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
    $null = Read-Host
    exit $script:ExitCode
}

try {

    # ── Verify virtual environment exists ─────────────────────────
    $pythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"
    if (-Not (Test-Path $pythonExe)) {
        throw "Virtual environment not found. Please run 01setup.ps1 first."
    }

    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host " Voice2Text  02 - Download Models" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available models:" -ForegroundColor Yellow
    Write-Host "  1) Qwen/Qwen3-ASR-0.6B  (recommended, ~1.3 GB, faster)"
    Write-Host "  2) Qwen/Qwen3-ASR-1.7B  (higher accuracy, ~3.5 GB)"
    Write-Host "  3) Download both"
    Write-Host ""

    $choice = Read-Host "Select model to download [1/2/3]"
    $choice  = $choice.Trim()

    $models = switch ($choice) {
        "1"     { @("Qwen/Qwen3-ASR-0.6B") }
        "2"     { @("Qwen/Qwen3-ASR-1.7B") }
        "3"     { @("Qwen/Qwen3-ASR-0.6B", "Qwen/Qwen3-ASR-1.7B") }
        default { throw "Invalid selection '$choice'. Please enter 1, 2, or 3." }
    }

    foreach ($model in $models) {
        Write-Host ""
        Write-Host "--- Downloading $model ---" -ForegroundColor Yellow
        Write-Host "    (large file; progress is shown below)"

        $pyCode = @"
import sys
from huggingface_hub import snapshot_download
try:
    path = snapshot_download(repo_id='$model')
    print(f'Download complete: {path}')
except Exception as exc:
    print(f'Download failed: {exc}', file=sys.stderr)
    sys.exit(1)
"@
        & $pythonExe -c $pyCode
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to download $model. Check network connection and Hugging Face access."
        }
        Write-Host "  [OK] $model downloaded successfully." -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "===================================" -ForegroundColor Green
    Write-Host " Model download complete!" -ForegroundColor Green
    Write-Host " Next step: run 03start.ps1" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "[ERROR] $_" -ForegroundColor Red
    $script:ExitCode = 1
}

Invoke-PauseExit
