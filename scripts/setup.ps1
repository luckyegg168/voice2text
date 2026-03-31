# Voice2Text Portable App Setup Script (Windows PowerShell)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Voice2Text - Setup (Windows)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Python
Write-Host "[1/5] 檢查 Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(10|11|12|13)") {
        Write-Host " OK ($pythonVersion)" -ForegroundColor Green
    } else {
        Write-Host " ERROR: 需要 Python 3.10-3.13" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host " ERROR: 未找到 Python" -ForegroundColor Red
    Write-Host " 請從 https://python.org 安裝 Python" -ForegroundColor Yellow
    exit 1
}

# 建立虛擬環境
Write-Host "[2/5] 建立虛擬環境 (.venv)..." -NoNewline
if (Test-Path ".venv") {
    Write-Host " 已存在，跳過" -ForegroundColor Yellow
} else {
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " ERROR" -ForegroundColor Red
        exit 1
    }
}

# 啟動虛擬環境並升級 pip
Write-Host "[3/5] 升級 pip..." -NoNewline
& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
Write-Host " OK" -ForegroundColor Green

# 安裝依賴
Write-Host "[4/5] 安裝依賴套件..."
$pipOutput = & .\.venv\Scripts\python.exe -m pip install -e ".[dev]" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "  ERROR: pip install 失敗" -ForegroundColor Red
    $pipOutput | Where-Object { $_ -match 'ERROR|error|Error' } | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Red
    }
    exit 1
}

# 建立必要目錄
Write-Host "[5/5] 建立資料目錄..." -NoNewline
$dirs = @("data", "data/recordings", "models")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}
Write-Host " OK" -ForegroundColor Green

# 複製 .env.example 到 .env
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "複製 .env.example 到 .env..." -NoNewline
    Copy-Item ".env.example" ".env"
    Write-Host " OK" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host " 安裝完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "啟動方式：" -ForegroundColor Cyan
Write-Host "  GUI:  .\scripts\run-gui.ps1" -ForegroundColor White
Write-Host "  API:  .\scripts\run-api.ps1" -ForegroundColor White
Write-Host "  CLI:  .\.venv\Scripts\python.exe -m app.cli" -ForegroundColor White
Write-Host ""
