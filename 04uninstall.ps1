#Requires -Version 5.1
<#
.SYNOPSIS
    Voice2Text - 04 Uninstall / Clean Up
.DESCRIPTION
    Interactively removes the virtual environment, optional model cache,
    user data, and .env configuration file.
.EXAMPLE
    .\04uninstall.ps1
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

function Confirm-Step([string]$question) {
    $ans = (Read-Host "$question [y/N]").Trim()
    return $ans -match '^[Yy]$'
}

try {

    Write-Host "===================================" -ForegroundColor Red
    Write-Host " Voice2Text  04 - Uninstall / Clean" -ForegroundColor Red
    Write-Host "===================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "WARNING: This will permanently delete selected items." -ForegroundColor Yellow
    Write-Host ""

    # ── Step 1: Virtual environment ───────────────────────────────
    Write-Host "[1/4] Remove virtual environment (.venv)" -ForegroundColor Cyan
    if (Test-Path ".venv") {
        if (Confirm-Step "    Delete .venv?") {
            Remove-Item ".venv" -Recurse -Force
            Write-Host "    [OK] .venv removed." -ForegroundColor Green
        } else {
            Write-Host "    [SKIP]" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "    [SKIP] .venv does not exist." -ForegroundColor DarkGray
    }

    # ── Step 2: Hugging Face model cache ──────────────────────────
    Write-Host ""
    Write-Host "[2/4] Remove Hugging Face model cache" -ForegroundColor Cyan
    $hfCachePaths = @(
        "$env:USERPROFILE\.cache\huggingface\hub",
        "$env:HF_HOME\hub"
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

    $qwenDirs = @()
    foreach ($hfCache in $hfCachePaths) {
        $found = Get-ChildItem $hfCache -Directory -ErrorAction SilentlyContinue |
                 Where-Object { $_.Name -match 'Qwen3.ASR|qwen3.asr' }
        $qwenDirs += $found
    }

    if ($qwenDirs.Count -gt 0) {
        Write-Host "    Found Qwen3-ASR cache directories:" -ForegroundColor Yellow
        $qwenDirs | ForEach-Object { Write-Host "      - $($_.FullName)" }
        if (Confirm-Step "    Delete these cache directories (several GB)?") {
            $qwenDirs | ForEach-Object {
                Remove-Item $_.FullName -Recurse -Force
                Write-Host "    [OK] Removed $($_.Name)" -ForegroundColor Green
            }
        } else {
            Write-Host "    [SKIP]" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "    [SKIP] No Qwen3-ASR cache found." -ForegroundColor DarkGray
    }

    # ── Step 3: User data ─────────────────────────────────────────
    Write-Host ""
    Write-Host "[3/4] Remove user data (recordings, history database)" -ForegroundColor Cyan
    if (Test-Path "data") {
        if (Confirm-Step "    Delete data/ directory (recordings + history)?") {
            Remove-Item "data" -Recurse -Force
            Write-Host "    [OK] data/ removed." -ForegroundColor Green
        } else {
            Write-Host "    [SKIP]" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "    [SKIP] data/ does not exist." -ForegroundColor DarkGray
    }

    # ── Step 4: .env configuration ────────────────────────────────
    Write-Host ""
    Write-Host "[4/4] Remove .env configuration file" -ForegroundColor Cyan
    if (Test-Path ".env") {
        if (Confirm-Step "    Delete .env?") {
            Remove-Item ".env" -Force
            Write-Host "    [OK] .env removed." -ForegroundColor Green
        } else {
            Write-Host "    [SKIP]" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "    [SKIP] .env does not exist." -ForegroundColor DarkGray
    }

    Write-Host ""
    Write-Host "===================================" -ForegroundColor Green
    Write-Host " Cleanup complete!" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "[ERROR] $_" -ForegroundColor Red
    $script:ExitCode = 1
}

Invoke-PauseExit
