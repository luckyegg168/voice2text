# Voice2Text - Run GUI (Windows PowerShell)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# 檢查虛擬環境
if (-not (Test-Path ".venv")) {
    Write-Host "錯誤：找不到虛擬環境 (.venv)" -ForegroundColor Red
    Write-Host "請先執行 .\scripts\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# 設定環境變數（ HuggingFace cache 到專案內）
$env:HF_HOME = "$ProjectRoot\models\.hf_cache"
$env:TRANSFORMERS_CACHE = "$ProjectRoot\models\.transformers_cache"
$env:PYTHONPATH = "$ProjectRoot"

Write-Host "啟動 Voice2Text GUI..." -ForegroundColor Cyan

# 啟動 GUI
& .\.venv\Scripts\python.exe -m app.gui
