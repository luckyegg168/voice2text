#Requires -Version 5.1
<#
.SYNOPSIS
    Voice2Text - 03 Start Application
.DESCRIPTION
    Launches the GUI desktop app, the REST API server, or both.
    Requires 01setup.ps1 to have been run first.
.EXAMPLE
    .\03start.ps1
#>

Set-StrictMode -Version Latest
$script:ExitCode = 0
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

function Invoke-PauseExit {
    param([switch]$OnError)
    if ($OnError) {
        Write-Host ""
        Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
        $null = Read-Host
    }
    exit $script:ExitCode
}

try {

    # ── Verify virtual environment ────────────────────────────────
    $pythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"
    if (-Not (Test-Path $pythonExe)) {
        throw "Virtual environment not found. Please run 01setup.ps1 first."
    }

    # ── Load .env environment variables ──────────────────────────
    $envPath = Join-Path $ScriptDir ".env"
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*?)\s*$') {
                $key = $Matches[1].Trim()
                $val = $Matches[2].Trim()
                if ($key) { [System.Environment]::SetEnvironmentVariable($key, $val, "Process") }
            }
        }
    }

    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host " Voice2Text  03 - Start Application" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Launch options:" -ForegroundColor Yellow
    Write-Host "  1) GUI  - Graphical desktop app (default)"
    Write-Host "  2) API  - REST API server  (http://localhost:8000/docs)"
    Write-Host "  3) Both - GUI + API server in separate windows"
    Write-Host ""

    $choice = (Read-Host "Select option [1/2/3] (default: 1)").Trim()
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }

    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "Starting GUI..." -ForegroundColor Green
            & $pythonExe -m app.gui
            $script:ExitCode = $LASTEXITCODE
            # GUI exited - pause so user can read any error output
            Invoke-PauseExit -OnError
        }
        "2" {
            Write-Host ""
            Write-Host "Starting API server..." -ForegroundColor Green
            Write-Host "  Swagger docs: http://localhost:8000/docs"
            Write-Host "  Press Ctrl+C to stop."
            Write-Host ""
            & $pythonExe -m app.api
            $script:ExitCode = $LASTEXITCODE
            Invoke-PauseExit -OnError
        }
        "3" {
            Write-Host ""
            Write-Host "Starting API server in a new window..." -ForegroundColor Green
            $apiArgs = "-NoExit -ExecutionPolicy Bypass -Command `"Set-Location '$ScriptDir'; & '$pythonExe' -m app.api`""
            Start-Process powershell.exe -ArgumentList $apiArgs

            Write-Host "Starting GUI..." -ForegroundColor Green
            & $pythonExe -m app.gui
            $script:ExitCode = $LASTEXITCODE
            Invoke-PauseExit -OnError
        }
        default {
            throw "Invalid option '$choice'. Please enter 1, 2, or 3."
        }
    }

} catch {
    Write-Host ""
    Write-Host "[ERROR] $_" -ForegroundColor Red
    $script:ExitCode = 1
    Write-Host ""
    Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
    $null = Read-Host
    exit $script:ExitCode
}
