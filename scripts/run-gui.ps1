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

# 確認 PySide6 已安裝
$pyside6Check = & .\.venv\Scripts\python.exe -c "import PySide6" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "錯誤：PySide6 未安裝，請重新執行 .\scripts\setup.ps1" -ForegroundColor Red
    exit 1
}

# 設定環境變數（HuggingFace / Transformers cache 到專案內，避免污染使用者目錄）
$env:HF_HOME = "$ProjectRoot\models\.hf_cache"
$env:TRANSFORMERS_CACHE = "$ProjectRoot\models\.transformers_cache"
$env:PYTHONPATH = "$ProjectRoot"

Write-Host "啟動 Voice2Text GUI..." -ForegroundColor Cyan

# 啟動 GUI（exit code 傳回呼叫端）
& .\.venv\Scripts\python.exe -m app.gui
exit $LASTEXITCODE
