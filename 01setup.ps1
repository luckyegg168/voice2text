#Requires -Version 5.1
<#
.SYNOPSIS
  Voice2Text — 01 初始化環境
.DESCRIPTION
  建立虛擬環境、安裝依賴套件、建立資料目錄、產生預設 .env
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Voice2Text  01 — 初始化環境" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 進入專案目錄
Set-Location $ScriptDir

# ── Python 版本檢查 ────────────────────────────────────────────────────
$python = "python"
try {
    $ver = & $python --version 2>&1
    Write-Host "✔ 找到 Python：$ver" -ForegroundColor Green
} catch {
    Write-Host "✘ 找不到 python，請先安裝 Python 3.10+。" -ForegroundColor Red
    exit 1
}

# ── 建立虛擬環境 ──────────────────────────────────────────────────────
if (-Not (Test-Path ".venv")) {
    Write-Host "`n建立虛擬環境 .venv …" -ForegroundColor Yellow
    & $python -m venv .venv
    Write-Host "✔ 虛擬環境建立完成" -ForegroundColor Green
} else {
    Write-Host "✔ 虛擬環境已存在，跳過" -ForegroundColor Green
}

# ── 啟動虛擬環境並安裝套件 ────────────────────────────────────────────
$pip = ".venv\Scripts\pip.exe"
$pythonExe = ".venv\Scripts\python.exe"

Write-Host "`n升級 pip …" -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade pip --quiet

Write-Host "`n安裝依賴套件（pyproject.toml）…" -ForegroundColor Yellow
& $pip install -e ".[all]" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "✘ 安裝失敗，請檢查 pyproject.toml 或網路連線。" -ForegroundColor Red
    exit 1
}
Write-Host "✔ 套件安裝完成" -ForegroundColor Green

# ── 建立資料目錄 ─────────────────────────────────────────────────────
$dirs = @("data", "data\recordings")
foreach ($d in $dirs) {
    if (-Not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d | Out-Null
        Write-Host "✔ 建立目錄 $d" -ForegroundColor Green
    }
}

# ── 產生預設 .env ────────────────────────────────────────────────────
if (-Not (Test-Path ".env")) {
    Write-Host "`n建立預設 .env …" -ForegroundColor Yellow
    @"
# Voice2Text 設定檔 — 依需求修改

DEFAULT_MODEL=Qwen/Qwen3-ASR-0.6B
DEVICE=cuda
DTYPE=float16

SAMPLE_RATE=16000
CHANNELS=1
VAD_ENABLED=true

# 翻譯 API（Ollama 預設）
TRANSLATION_API_URL=http://localhost:11434/v1/chat/completions
TRANSLATION_API_KEY=
TRANSLATION_MODEL=llama3.2

DATA_DIR=./data
RECORDINGS_DIR=./data/recordings
DATABASE_URL=sqlite+aiosqlite:///./data/voice2text.db
MAX_HISTORY_ITEMS=1000

OPENCC_MODE=s2t
HOTWORDS_FILE=./data/hotwords.json
"@ | Set-Content ".env" -Encoding UTF8
    Write-Host "✔ 已建立 .env（請依需求修改）" -ForegroundColor Green
} else {
    Write-Host "✔ .env 已存在，跳過" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " 初始化完成！" -ForegroundColor Green
Write-Host " 下一步：執行 02download-models.ps1" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
