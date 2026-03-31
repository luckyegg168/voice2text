#Requires -Version 5.1
<#
.SYNOPSIS
  Voice2Text — 03 啟動應用程式
.DESCRIPTION
  選擇啟動 GUI 介面、REST API 伺服器或兩者同時執行
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
Write-Host " Voice2Text  03 — 啟動應用程式" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "啟動選項：" -ForegroundColor Yellow
Write-Host "  1) GUI  — 圖形化介面（桌面應用）"
Write-Host "  2) API  — REST API 伺服器"
Write-Host "  3) 全部 — GUI + API 伺服器（各開一個視窗）"
Write-Host ""

$choice = Read-Host "請選擇 [1/2/3]（預設 1）"
if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }

switch ($choice) {
    "1" {
        Write-Host "`n啟動 GUI …" -ForegroundColor Green
        & $pythonExe -m app.gui
    }
    "2" {
        Write-Host "`n啟動 API 伺服器 …" -ForegroundColor Green
        & $pythonExe -m app.api
    }
    "3" {
        Write-Host "`n同時啟動 GUI 和 API 伺服器 …" -ForegroundColor Green
        Start-Process -FilePath $pythonExe -ArgumentList "-m app.api" -WindowStyle Normal
        & $pythonExe -m app.gui
    }
    default {
        Write-Host "✘ 無效選項，退出。" -ForegroundColor Red
        exit 1
    }
}
