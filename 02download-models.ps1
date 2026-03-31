#Requires -Version 5.1
<#
.SYNOPSIS
  Voice2Text — 02 下載 / 驗證模型
.DESCRIPTION
  從 Hugging Face Hub 下載 Qwen3-ASR 模型到本機快取
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

$pythonExe = ".venv\Scripts\python.exe"
if (-Not (Test-Path $pythonExe)) {
    Write-Host "✘ 找不到虛擬環境，請先執行 01setup.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Voice2Text  02 — 下載模型" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "可用模型：" -ForegroundColor Yellow
Write-Host "  1) Qwen/Qwen3-ASR-0.6B  （推薦，~1.3 GB）"
Write-Host "  2) Qwen/Qwen3-ASR-1.7B  （較精確，~3.5 GB）"
Write-Host "  3) 全部下載"
Write-Host ""

$choice = Read-Host "請選擇要下載的模型 [1/2/3]"

$models = @()
switch ($choice) {
    "1" { $models = @("Qwen/Qwen3-ASR-0.6B") }
    "2" { $models = @("Qwen/Qwen3-ASR-1.7B") }
    "3" { $models = @("Qwen/Qwen3-ASR-0.6B", "Qwen/Qwen3-ASR-1.7B") }
    default {
        Write-Host "✘ 無效選項，退出。" -ForegroundColor Red
        exit 1
    }
}

foreach ($model in $models) {
    Write-Host "`n下載 $model …" -ForegroundColor Yellow
    & $pythonExe -c @"
from huggingface_hub import snapshot_download
import sys
try:
    path = snapshot_download(repo_id='$model')
    print(f'✔ 下載完成：{path}')
except Exception as e:
    print(f'✘ 下載失敗：{e}', file=sys.stderr)
    sys.exit(1)
"@
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✘ 下載 $model 失敗，請確認網路連線和 Hugging Face 存取權限。" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " 模型下載完成！" -ForegroundColor Green
Write-Host " 下一步：執行 03start.ps1 啟動應用程式" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
