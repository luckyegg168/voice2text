# Voice2Text — 語音辨識轉文字工具

> 本地執行的語音辨識工具，基於 Qwen3-ASR，支援繁簡中文轉換與 LLM 翻譯。

## 功能特色

- **語音辨識**：Qwen3-ASR 0.6B / 1.7B 模型，支援普通話、台語等多語言
- **即時錄音**：麥克風錄音轉文字，含音量 VU 表視覺化
- **繁簡轉換**：OpenCC 引擎，支援多種轉換模式
- **本地翻譯**：串接本地 LLM（Ollama）進行多語言翻譯
- **歷史記錄**：aiosqlite 儲存所有辨識結果
- **熱詞管理**：自訂詞彙提升辨識準確度

## 介面

| 模式 | 說明 |
|------|------|
| GUI | PySide6 深色現代化介面 |
| CLI | Typer 命令列工具 |
| API | FastAPI REST 服務 |

## 快速開始

### 環境設定

```powershell
# Windows
.\scripts\setup.ps1
.\scripts\run-gui.ps1
```

```bash
# Linux / macOS
bash scripts/setup.sh
bash scripts/run-gui.sh
```

### 手動安裝

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 啟動方式

```bash
# GUI 介面
python -m app.gui

# CLI 工具
voice2text --help
voice2text mic             # 麥克風錄音
voice2text file audio.wav  # 辨識檔案

# REST API
python -m app.api
# 或
voice2text serve
```

## 鍵盤快捷鍵（GUI）

| 快捷鍵 | 功能 |
|--------|------|
| `Ctrl+R` | 開始／停止錄音 |
| `Ctrl+O` | 開啟音訊檔 |
| `Ctrl+S` | 儲存文字 |
| `Ctrl+Shift+C` | 複製文字 |
| `Ctrl+H` | 歷史記錄 |
| `Ctrl+,` | 偏好設定 |
| `Ctrl+Q` | 結束程式 |
| `Esc` | 停止錄音 |

## 專案結構

```
voice2text/
├── app/
│   ├── api/          # FastAPI REST API
│   ├── cli/          # Typer CLI 命令
│   ├── core/         # 核心邏輯（ASR、轉換、翻譯、歷史）
│   └── gui/          # PySide6 GUI 介面
├── data/
│   └── recordings/   # 錄音暫存
├── scripts/          # 安裝與啟動腳本
└── tests/            # 測試套件
```

## 系統需求

- Python 3.10 – 3.13
- CUDA GPU（建議，可純 CPU 執行但較慢）
- 麥克風（錄音功能）
- Ollama（翻譯功能，可選）

## 依賴套件

| 套件 | 用途 |
|------|------|
| `qwen-asr` | Qwen3-ASR 語音辨識 |
| `PySide6` | Qt GUI 框架 |
| `FastAPI` | REST API |
| `Typer` | CLI 框架 |
| `opencc-python-reimplemented` | 繁簡中文轉換 |
| `aiosqlite` | 非同步 SQLite 歷史記錄 |
| `sounddevice` | 音訊錄製 |
| `httpx` | HTTP 客戶端（翻譯服務） |

## 授權

MIT License
