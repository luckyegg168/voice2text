#Requires -Version 5.1
<#
.SYNOPSIS
  Voice2Text — 04 解除安裝 / 清理
.DESCRIPTION
  移除虛擬環境及可選的模型快取和使用者資料
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host "=====================================" -ForegroundColor Red
Write-Host " Voice2Text  04 — 解除安裝 / 清理" -ForegroundColor Red
Write-Host "=====================================" -ForegroundColor Red
Write-Host ""

# ── 1. 移除虛擬環境（必要項目）────────────────────────────────────────
$confirm = Read-Host "確定要移除虛擬環境 .venv？[y/N]"
if ($confirm -match "^[Yy]$") {
    if (Test-Path ".venv") {
        Remove-Item ".venv" -Recurse -Force
        Write-Host "✔ 已移除 .venv" -ForegroundColor Green
    } else {
        Write-Host "：.venv 不存在，跳過" -ForegroundColor DarkGray
    }
} else {
    Write-Host "跳過移除 .venv。" -ForegroundColor Yellow
}

# ── 2. 移除 Hugging Face 模型快取（可選）──────────────────────────────
Write-Host ""
$hfCache = "$env:USERPROFILE\.cache\huggingface\hub"
if (Test-Path $hfCache) {
    Write-Host "找到 HuggingFace 快取目錄：$hfCache" -ForegroundColor Yellow
    $confirm2 = Read-Host "確定要刪除模型快取（約數 GB）？[y/N]"
    if ($confirm2 -match "^[Yy]$") {
        # 只刪除 Qwen3-ASR 相關目錄
        Get-ChildItem $hfCache -Directory | Where-Object { $_.Name -like "*Qwen3-ASR*" } | ForEach-Object {
            Remove-Item $_.FullName -Recurse -Force
            Write-Host "✔ 已移除 $($_.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "跳過刪除模型快取。" -ForegroundColor Yellow
    }
} else {
    Write-Host "未找到 HuggingFace 快取，跳過。" -ForegroundColor DarkGray
}

# ── 3. 移除使用者資料（可選）─────────────────────────────────────────
Write-Host ""
if (Test-Path "data") {
    $confirm3 = Read-Host "確定要刪除 data/ 目錄（歷史紀錄、錄音）？[y/N]"
    if ($confirm3 -match "^[Yy]$") {
        Remove-Item "data" -Recurse -Force
        Write-Host "✔ 已刪除 data/" -ForegroundColor Green
    } else {
        Write-Host "跳過刪除 data/。" -ForegroundColor Yellow
    }
}

# ── 4. 移除 .env（可選）──────────────────────────────────────────────
Write-Host ""
if (Test-Path ".env") {
    $confirm4 = Read-Host "確定要刪除 .env 設定檔？[y/N]"
    if ($confirm4 -match "^[Yy]$") {
        Remove-Item ".env" -Force
        Write-Host "✔ 已刪除 .env" -ForegroundColor Green
    } else {
        Write-Host "跳過刪除 .env。" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " 清理完成！" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
