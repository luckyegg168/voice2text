# Voice2Text - Run API Server (Windows PowerShell)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# 檢查虛擬環境
if (-not (Test-Path ".venv")) {
    Write-Host "錯誤：找不到虛擬環境 (.venv)" -ForegroundColor Red
    Write-Host "請先執行 .\scripts\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# 讀取 .env 中的設定
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            if (-not [string]::IsNullOrEmpty($name) -and $name -notmatch "^#") {
                Set-Item -Path "env:$name" -Value $value
            }
        }
    }
}

# 設定環境變數
$env:HF_HOME = "$ProjectRoot\models\.hf_cache"
$env:TRANSFORMERS_CACHE = "$ProjectRoot\models\.transformers_cache"
$env:PYTHONPATH = "$ProjectRoot"

$port = if ($env:API_PORT) { $env:API_PORT } else { "8000" }
$host = if ($env:API_HOST) { $env:API_HOST } else { "0.0.0.0" }

Write-Host "啟動 Voice2Text API Server..." -ForegroundColor Cyan
Write-Host "  Host: $host" -ForegroundColor White
Write-Host "  Port: $port" -ForegroundColor White
Write-Host "  URL:  http://$host`:$port/docs" -ForegroundColor White
Write-Host ""

# 啟動 API
& .\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host $host --port $port --reload
