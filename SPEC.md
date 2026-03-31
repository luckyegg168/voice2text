# Voice2Text — 語音辨識發送文字系統

## 1. Project Overview

**專案名稱**: Voice2Text  
**類型**: Local AI Speech Recognition Application  
**核心功能**: 將麥克風音訊或音訊檔案即時轉換為文字，支援本地 API server 與 CLI，具備簡繁轉換、熱詞增強、歷史紀錄與翻譯功能  
**目標使用者**: 開發者、需要整合語音轉文字功能的應用程式

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Voice2Text                               │
├─────────────────────────────────────────────────────────────────┤
│  Interface Layer                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐   │
│  │ PySide6  │  │  Typer   │  │  FastAPI Server          │   │
│  │   GUI    │  │   CLI    │  │  (OpenAI-compatible)     │   │
│  └────┬─────┘  └────┬─────┘  └───────────┬──────────────┘   │
│       │              │                      │                   │
│       └──────────────┼──────────────────────┘                   │
│                      ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Service Layer                           │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────┐  │  │
│  │  │ AudioProcessor │  │ Transcription  │  │  Translation │  │  │
│  │  │  (Recording,   │  │   Service     │  │  Service   │  │  │
│  │  │   VAD, 16kHz) │  │  (Qwen3-ASR)  │  │  (LLM API) │  │  │
│  │  └────────────────┘  └────────────────┘  └───────────┘  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────┐  │  │
│  │  │  OpenCC Engine │  │   Hot Words    │  │  History  │  │  │
│  │  │ (簡繁轉換)     │  │   Manager      │  │  Manager  │  │  │
│  │  └────────────────┘  └────────────────┘  └───────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                      │                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Model Layer                             │  │
│  │           Qwen3-ASR-0.6B / 1.7B + Local LLM            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Component | Technology |
|-----------|------------|
| ASR Model | Qwen3-ASR (qwen-asr package) |
| 簡繁轉換 | OpenCC (opencc-python-reimplemented) |
| GUI | PySide6 (Qt for Python) |
| CLI | Typer |
| API Server | FastAPI + Uvicorn |
| API Format | OpenAI-compatible + Native |
| Audio Processing | sounddevice + scipy |
| Translation | Local LLM API (OpenAI-compatible) |
| History Storage | SQLite + 檔案系統 |

---

## 4. Project Structure (Portable App)

```
voice2text/                          # 專案根目錄（可攜帶）
│
├── .venv/                          # Python 虛擬環境（本機隔離）
│   ├── Lib/
│   └── Scripts/
│
├── app/                            # 應用程式碼
│   ├── __init__.py
│   ├── __main__.py                 # 程式進入點
│   │
│   ├── core/                       # 核心商業邏輯（無 GUI/CLI 依賴）
│   │   ├── __init__.py
│   │   ├── config.py               # 設定管理
│   │   ├── constants.py            # 常數定義
│   │   ├── qwen3_asr.py           # Qwen3-ASR 模型封裝
│   │   ├── audio_processor.py      # 音訊處理
│   │   ├── opencc_engine.py        # OpenCC 簡繁轉換
│   │   ├── hot_words.py            # 熱詞管理
│   │   ├── history_manager.py       # 歷史紀錄
│   │   └── translation_service.py   # 翻譯服務
│   │
│   ├── api/                        # FastAPI 網頁服務
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── transcription.py
│   │   │   ├── translation.py
│   │   │   ├── conversion.py
│   │   │   └── history.py
│   │   └── models.py
│   │
│   ├── cli/                        # Typer CLI
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── mic.py
│   │       ├── file.py
│   │       ├── convert.py
│   │       ├── translate.py
│   │       ├── history.py
│   │       ├── hotwords.py
│   │       └── serve.py
│   │
│   └── gui/                        # PySide6 GUI
│       ├── __init__.py
│       ├── app.py
│       ├── main_window.py
│       ├── widgets/
│       │   ├── __init__.py
│       │   ├── transcription_area.py
│       │   ├── control_panel.py
│       │   ├── audio_level_indicator.py
│       │   └── status_bar.py
│       ├── dialogs/
│       │   ├── __init__.py
│       │   ├── settings_dialog.py
│       │   ├── history_dialog.py
│       │   ├── hotwords_dialog.py
│       │   └── translation_dialog.py
│       └── utils/
│           ├── __init__.py
│           ├── signal_bus.py
│           └── theme.py
│
├── data/                           # 執行時期資料（專案內）
│   ├── recordings/                 # 歷史音訊備份
│   ├── hotwords.json              # 熱詞設定檔
│   └── voice2text.db              # SQLite 資料庫
│
├── models/                         # 快取模型（本機儲存）
│   └── .gitkeep                   # HuggingFace cache
│
├── scripts/                        # 腳本（本機使用）
│   ├── setup.ps1                  # Windows 安裝腳本
│   ├── setup.sh                   # Linux/macOS 安裝腳本
│   ├── run-gui.ps1                # Windows 啟動 GUI
│   ├── run-gui.sh                 # Linux/macOS 啟動 GUI
│   └── run-api.ps1                # Windows 啟動 API
│
├── tests/
│   ├── __init__.py
│   ├── core/
│   ├── api/
│   └── gui/
│
├── pyproject.toml
├── .env.example
├── .env                            # 本機設定（自動建立）
├── .gitignore
└── README.md
```

---

## 5. Functionality Specification

### 5.1 Core Features

#### 5.1.1 Audio Processing
- [x] 從麥克風即時錄音
- [x] 支援 WAV 檔案輸入
- [x] 自動轉換為 16kHz, mono, float32
- [x] VAD (Voice Activity Detection) 去除靜音
- [x] 即時進度回調

#### 5.1.2 Speech Recognition
- [x] 使用 Qwen3-ASR-0.6B 或 1.7B
- [x] 自動語言偵測
- [x] 支援 30 種語言 + 22 種中文方言
- [x] 模型快取（避免重複載入）
- [x] 記憶體管理（LRU eviction）

#### 5.1.3 OpenCC 簡繁轉換
- [x] 支援 簡→繁、繁→簡 轉換
- [x] 多種轉換模式（預設、歌詞、姓氏等）
- [x] GUI 一鍵切換
- [x] CLI 參數支援
- [x] 轉換模式：
  - `s2t` - 簡體→繁體
  - `t2s` - 繁體→簡體
  - `s2tw` - 簡體→臺灣正體
  - `tw2s` - 臺灣正體→簡體
  - `s2hk` - 簡體→香港繁體
  - `hk2s` - 香港繁體→簡體

#### 5.1.4 熱詞功能 (Hot Words)
- [x] 熱詞清單管理（新增、編輯、刪除）
- [x] 支援多組熱詞群組
- [x] 熱詞權重調整（boost factor）
- [x] 自動套用熱詞到轉寫結果
- [x] 熱詞檔案格式：
  ```json
  {
    "groups": [
      {
        "name": "技術術語",
        "words": [
          {"text": "Qwen3-ASR", "weight": 2.0},
          {"text": "PySide6", "weight": 2.0}
        ]
      }
    ]
  }
  ```

#### 5.1.5 歷史紀錄
- [x] 自動儲存每次轉寫結果
- [x] 音訊檔案備份（WAV 格式）
- [x] SQLite 資料庫儲存中繼資料
- [x] 歷史紀錄欄位：
  - `id` - 唯一識別碼
  - `text` - 轉寫文字
  - `language` - 偵測語言
  - `model` - 使用模型
  - `audio_path` - 音訊檔案路徑
  - `duration` - 音訊長度（秒）
  - `translated_text` - 翻譯文字（可選）
  - `created_at` - 建立時間
- [x] GUI 歷史面板（對話框）
- [x] 支援搜尋、篩選、刪除
- [x] 一鍵回填歷史文字到編輯區

#### 5.1.6 翻譯功能
- [x] 支援本地 LLM API URL
- [x] OpenAI-compatible API 格式
- [x] 支援多語言翻譯
- [x] GUI 翻譯按鈕 + 目標語言選擇
- [x] CLI 翻譯參數
- [x] 翻譯結果可儲存到歷史紀錄
- [x] API 設定：
  ```env
  TRANSLATION_API_URL=http://localhost:11434/v1/chat/completions
  TRANSLATION_API_KEY=optional-key
  TRANSLATION_MODEL=llama3.2
  ```

#### 5.1.7 PySide6 GUI

**主視窗**：
- [x] 即時錄音按鈕（Push-to-Talk）
- [x] 音訊檔案拖放
- [x] 即時文字顯示
- [x] 模型選擇（0.6B / 1.7B）
- [x] 語言下拉選單
- [x] 複製文字到剪貼簿
- [x] 儲存文字到檔案
- [x] 狀態列（模型狀態、記憶體用量）
- [x] **設定按鈕 → 開啟設定對話框**

**設定對話框（獨立頁面）**：
- [x] **模型設定**：預設模型、Device、dtype
- [x] **音訊設定**：取樣率、聲道、VAD 開關
- [x] **翻譯 API 設定**：API URL、API Key、模型名稱
- [x] **簡繁轉換設定**：預設轉換模式
- [x] **歷史紀錄設定**：儲存路徑、最大筆數
- [x] **外觀設定**：主題語言（UI 使用中文/英文）

**歷史紀錄對話框**：
- [x] 搜尋列
- [x] 日期篩選
- [x] 歷史列表（文字預覽、時間、模型）
- [x] 操作：播放音訊、複製文字、刪除
- [x] 雙擊回填文字到主視窗

**熱詞設定對話框**：
- [x] 群組列表（左側）
- [x] 熱詞編輯（右側）
- [x] 新增/刪除群組
- [x] 新增/編輯/刪除熱詞
- [x] 權重滑桿

**翻譯對話框**：
- [x] 來源文字（當前文字）
- [x] 目標語言選擇
- [x] 翻譯結果顯示
- [x] 複製/儲存按鈕

#### 5.1.8 Typer CLI
```bash
# 麥克風錄音轉寫
voice2text mic --language Chinese --model Qwen/Qwen3-ASR-0.6B

# 音訊檔案轉寫
voice2text file --audio path/to/audio.wav --language auto

# 簡繁轉換
voice2text convert --mode s2t --input "简体字"
voice2text convert --mode t2s --input "繁體字"

# 翻譯
voice2text translate --text "Hello world" --target-lang Chinese
voice2text translate --input-file output.txt --target-lang zh

# 歷史紀錄
voice2text history list
voice2text history search "關鍵字"
voice2text history delete --id 123

# 熱詞管理
voice2text hotwords add --group tech --word "PySide6" --weight 2.0
voice2text hotwords list
voice2text hotwords remove --group tech --word "PySide6"

# 設定管理
voice2text config list
voice2text config set DEFAULT_MODEL Qwen/Qwen3-ASR-1.7B
voice2text config set TRANSLATION_API_URL http://localhost:11434/v1

# 啟動 API server
voice2text serve --port 8000 --host 0.0.0.0
```

#### 5.1.9 FastAPI Server

**OpenAI-compatible endpoint**:
```http
POST /v1/audio/transcriptions
Content-Type: multipart/form-data

file: (binary)
model: Qwen/Qwen3-ASR-0.6B
language: (optional)
```

**Native endpoint**:
```http
POST /asr
Content-Type: application/json

{
  "audio": "base64 encoded WAV",
  "model": "Qwen/Qwen3-ASR-0.6B",
  "language": "auto"
}
```

**Translation endpoint**:
```http
POST /translate
Content-Type: application/json

{
  "text": "Hello world",
  "target_language": "Chinese",
  "source_language": "English"
}
```

### 5.2 Data Flow

```
Microphone → sounddevice → np.ndarray (16kHz mono)
                                     ↓
                              VAD Filter
                                     ↓
                          Qwen3-ASR Model
                                     ↓
                              Transcription
                                     ↓
              ┌──────────────────────┼──────────────────────┐
              ▼                     ▼                      ▼
         OpenCC Engine         Hot Words            Translation
         (簡繁轉換)             Manager               Service
              │                     │                      │
              └──────────────────────┼──────────────────────┘
                                     ▼
                              History Manager
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                                 ▼
              SQLite DB                        audio_files/
```

---

## 6. UI Design (PySide6)

### 6.1 Main Window Layout

```
┌────────────────────────────────────────────────────────────────┐
│  Voice2Text  [⚙ 設定]                                   [─][□][×]│
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Model: [Qwen/Qwen3-ASR-0.6B ▼]  Lang: [Auto ▼]        │  │
│  │ 熱詞: [技術術語 ▼]                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │              Transcription Text Area                      │  │
│  │              (Editable, Scrollable)                       │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │ 🎤 Record           │  │ 🔊 Translate: [中文 ▼] [→]    │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📁 Open   💾 Save   📋 Copy   🔄 簡繁   🗑️ Clear     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ═══════════════════════════════════════════════════════ │  │
│  │ (Audio Level Indicator)                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Status: Ready | Model: 0.6B | Memory: 2.1GB | VAD: ON  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [📜 歷史] [🏷️ 熱詞]                                         │
└────────────────────────────────────────────────────────────────┘
```

### 6.2 Settings Dialog (獨立頁面)

```
┌─────────────────────────────────────────────────────────────────┐
│  設定                                                    [×]    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │  模型設定   │  音訊設定   │ API 設定   │  外觀設定   │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ [模型設定] Tab 內容：                                     │  │
│  │                                                           │  │
│  │  預設模型：[Qwen/Qwen3-ASR-0.6B        ▼]               │  │
│  │                                                           │  │
│  │  設備：    [CUDA ▼]                                       │  │
│  │                                                           │  │
│  │  精度：    [Float16 ▼]                                    │  │
│  │                                                           │  │
│  │  ══════════════════════════════════════════════════════  │  │
│  │                                                           │  │
│  │  熱詞預設群組：[技術術語 ▼] [+ 新增群組]                  │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│              [取消]                           [儲存]              │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 History Dialog

```
┌─────────────────────────────────────────────────────┐
│  📜 歷史紀錄                                 [×]    │
├─────────────────────────────────────────────────────┤
│ 🔍 [搜尋...]                    日期：[全部 ▼]    │
├─────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────┐ │
│ │ 2024-01-15 14:30:00                           │ │
│ │ "今天天氣很好..."                               │ │
│ │ 語言：中文 | 模型：0.6B | 長度：5.2s          │ │
│ │ [▶ 播放] [📋 複製] [🔄 翻譯] [🗑️ 刪除]       │ │
│ └─────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 2024-01-15 14:25:00                           │ │
│ │ "PySide6 是 Qt 的 Python 綁定..."              │ │
│ │ [▶ 播放] [📋 複製] [🔄 翻譯] [🗑️ 刪除]       │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│  下一頁: [◀] 第 1 頁 / 共 10 頁 [▶]              │
└─────────────────────────────────────────────────────┘
```

### 6.4 Color Palette

| Element | Color |
|---------|-------|
| Primary | #0078D4 (Microsoft Blue) |
| Secondary | #F5F5F5 (Light Gray) |
| Accent | #107C10 (Green - Recording) |
| Text | #1A1A1A (Near Black) |
| Background | #FFFFFF (White) |
| Error | #D13438 (Red) |
| Warning | #FFB900 (Amber) |
| Translation | #8764B8 (Purple) |
| Settings | #717171 (Gray) |

### 6.5 Typography

| Element | Font | Size |
|---------|------|------|
| Title | Segoe UI | 16pt Bold |
| Body | Segoe UI | 10pt |
| Button | Segoe UI | 10pt |
| Status | Segoe UI | 9pt |
| History | Segoe UI | 9pt |

---

## 7. API Specification

### 7.1 OpenAI-compatible Endpoint

**POST** `/v1/audio/transcriptions`

Request (multipart/form-data):
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | binary | Yes | Audio file (WAV, MP3, etc.) |
| model | string | Yes | Model ID |
| language | string | No | Language code |

Response:
```json
{
  "text": "Transcribed text here",
  "language": "Chinese",
  "duration": 5.23
}
```

### 7.2 Native Endpoint

**POST** `/asr`

Request (application/json):
```json
{
  "audio": "base64_encoded_wav",
  "model": "Qwen/Qwen3-ASR-0.6B",
  "language": "auto",
  "return_time_stamps": false,
  "hotwords_group": "technical"
}
```

Response:
```json
{
  "text": "Transcribed text here",
  "language": "Chinese",
  "chunks": [
    {
      "text": "Transcribed text",
      "start": 0.0,
      "end": 5.23
    }
  ]
}
```

### 7.3 Translation Endpoint

**POST** `/translate`

Request (application/json):
```json
{
  "text": "Hello world, how are you?",
  "target_language": "Chinese",
  "source_language": "English"
}
```

Response:
```json
{
  "text": "你好世界，你好嗎？",
  "source_language": "English",
  "target_language": "Chinese",
  "model": "llama3.2"
}
```

### 7.4 Conversion Endpoint

**POST** `/convert`

Request (application/json):
```json
{
  "text": "简体字",
  "mode": "s2t"
}
```

Response:
```json
{
  "text": "簡體字",
  "mode": "s2t"
}
```

### 7.5 History Endpoints

**GET** `/history`

Query params: `?search=&limit=50&offset=0`

Response:
```json
{
  "items": [
    {
      "id": 1,
      "text": "今天天氣很好",
      "language": "Chinese",
      "model": "Qwen/Qwen3-ASR-0.6B",
      "audio_path": "/data/recordings/20240115_143000.wav",
      "duration": 5.23,
      "translated_text": null,
      "created_at": "2024-01-15T14:30:00"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

**GET** `/history/{id}`

**DELETE** `/history/{id}`

### 7.6 Health Check

**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "Qwen/Qwen3-ASR-0.6B",
  "translation_api": "connected"
}
```

---

## 8. Configuration (.env) — 全部使用專案內路徑

```env
# ============================================
# Voice2Text Portable App 設定檔
# 所有路徑都相對於專案根目錄
# ============================================

# Model Settings
DEFAULT_MODEL=Qwen/Qwen3-ASR-0.6B
DEVICE=cuda
DTYPE=float16

# Audio Settings
SAMPLE_RATE=16000
CHANNELS=1
VAD_ENABLED=true

# Translation API (OpenAI-compatible)
TRANSLATION_API_URL=http://localhost:11434/v1/chat/completions
TRANSLATION_API_KEY=
TRANSLATION_MODEL=llama3.2

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# History Storage（專案內路徑）
DATA_DIR=./data
RECORDINGS_DIR=./data/recordings
DATABASE_URL=sqlite+aiosqlite:///./data/voice2text.db
MAX_HISTORY_ITEMS=1000

# OpenCC
OPENCC_MODE=s2t

# Hot Words
HOTWORDS_FILE=./data/hotwords.json
DEFAULT_HOTWORDS_GROUP=default

# GUI Settings
GUI_LANGUAGE=zh-TW

# HF Cache（模型快取目錄，設在專案內）
HF_HOME=./models/.hf_cache
TRANSFORMERS_CACHE=./models/.transformers_cache
```

---

## 9. Portable App Setup（可攜帶式設定）

### 9.1 設計原則

1. **虛擬環境隔離**：使用 `.venv/` 本機 Python 環境
2. **資料存在專案內**：`./data/` 目錄儲存所有執行時期資料
3. **模型快取本地化**：`./models/` 目錄儲存 HuggingFace 模型
4. **零系統污染**：不寫入系統目錄，可任意移動專案資料夾

### 9.2 安裝腳本

**Windows (PowerShell)**：
```powershell
.\scripts\setup.ps1
```

**Linux/macOS (Bash)**：
```bash
bash scripts/setup.sh
```

### 9.3 啟動方式

| 模式 | Windows | Linux/macOS |
|------|---------|--------------|
| GUI | `.\scripts\run-gui.ps1` | `bash scripts/run-gui.sh` |
| API Server | `.\scripts\run-api.ps1` | `bash scripts/run-api.sh` |
| CLI | `.venv\Scripts\python -m app.cli` | `.venv/bin/python -m app.cli` |

### 9.4 目錄結構說明

| 目錄 | 用途 |
|------|------|
| `.venv/` | Python 虛擬環境（由 setup 腳本建立） |
| `data/` | SQLite DB、錄音檔、熱詞設定 |
| `models/` | HuggingFace 模型快取（.hf_cache、.transformers_cache） |
| `scripts/` | 安裝與啟動腳本 |

### 9.5 環境變數

所有設定透過 `.env` 檔案管理。首次執行時自動從 `.env.example` 複製。

### 9.6 跨平台支援

| 平台 | 測試狀態 |
|------|----------|
| Windows 10+ | ✅ |
| macOS 12+ | ✅ |
| Ubuntu 20.04+ | ✅ |

---

## 10. Dependencies

```toml
[project]
dependencies = [
    "qwen-asr>=0.1.0",
    "sounddevice>=0.4.0",
    "scipy>=1.11.0",
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
    "PySide6>=6.5.0",
    "typer>=0.9.0",
    "python-multipart>=0.0.6",
    "python-dotenv>=1.0.0",
    "opencc-python-reimplemented>=0.1.7",
    "aiosqlite>=0.19.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
]
```

---

## 11. Database Schema

### Table: transcriptions

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | 唯一識別碼 |
| text | TEXT NOT NULL | 轉寫文字 |
| language | VARCHAR(50) | 偵測語言 |
| model | VARCHAR(100) | 使用模型 |
| audio_path | VARCHAR(500) | 音訊檔案路徑 |
| duration | FLOAT | 音訊長度（秒） |
| translated_text | TEXT | 翻譯文字 |
| created_at | DATETIME | 建立時間 |

### Table: hotwords_groups

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | 唯一識別碼 |
| name | VARCHAR(100) | 群組名稱 |
| created_at | DATETIME | 建立時間 |

### Table: hotwords

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | 唯一識別碼 |
| group_id | INTEGER FK | 所屬群組 |
| word | VARCHAR(200) | 熱詞 |
| weight | FLOAT | 權重（預設 1.0） |

---

## 12. Code Modularity

### 11.1 Core Module (`app/core/`)

核心商業邏輯，完全獨立，無任何 GUI 或 CLI 依賴。

```python
# 範例：音訊處理
from app.core.audio_processor import AudioProcessor
processor = AudioProcessor(sample_rate=16000, channels=1)
audio_data = processor.record(duration=5.0)
text = processor.process_file("audio.wav")

# 範例：歷史管理
from app.core.history_manager import HistoryManager
history = HistoryManager(db_path="./data/voice2text.db")
await history.add(text="hello", language="English")
items = await history.search("hello")
```

### 11.2 Service Interface Pattern

所有核心服務透過抽象介面提供，確保可測試性：

```python
from abc import ABC, abstractmethod

class ITranscriptionService(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes, language: str) -> str: ...

class ITranslationService(ABC):
    @abstractmethod
    async def translate(self, text: str, target: str, source: str) -> str: ...

class IConversionService(ABC):
    @abstractmethod
    def convert(self, text: str, mode: str) -> str: ...
```

### 11.3 Signal Bus (跨元件通訊)

GUI 內使用 Signal Bus 進行元件間解耦：

```python
from app.gui.utils.signal_bus import signal_bus

# 發送信號
signal_bus.transcription_completed.emit(text="hello")
signal_bus.model_loaded.emit(model_name="0.6B")

# 接收信號
signal_bus.transcription_completed.connect(self.on_transcription)
```

### 11.4 Dependency Injection

使用工廠模式注入依賴：

```python
from app.core import AudioProcessor, HistoryManager, OpenCCEngine

class ServiceFactory:
    def __init__(self, config: Config):
        self.config = config
        self._audio_processor = None
        self._history_manager = None

    @property
    def audio_processor(self) -> AudioProcessor:
        if self._audio_processor is None:
            self._audio_processor = AudioProcessor(
                sample_rate=self.config.SAMPLE_RATE,
                channels=self.config.CHANNELS,
            )
        return self._audio_processor

    def create_transcription_service(self) -> TranscriptionService:
        return TranscriptionService(
            model=self._get_model(),
            hotwords=self._get_hotwords(),
        )
```

---

## 13. Acceptance Criteria

### 12.1 Functional
- [ ] GUI 可從麥克風錄音並即時顯示文字
- [ ] GUI 可開啟音訊檔案並轉寫
- [ ] CLI `mic` 命令可錄音並輸出文字
- [ ] CLI `file` 命令可轉寫音訊檔案
- [ ] API server 可啟動並處理請求
- [ ] OpenAI-compatible endpoint 可用 OpenAI SDK 呼叫
- [ ] 模型可在 CUDA 或 CPU 上執行
- [ ] **簡繁轉換功能正常運作**
- [ ] **熱詞可正確套用到轉寫結果**
- [ ] **歷史紀錄可正確儲存與讀取**
- [ ] **翻譯功能可透過本地 LLM API 運作**
- [ ] **設定對話框可獨立運作，設定可保存**
- [ ] **程式碼模組化，各模組可獨立測試**

### 12.2 Non-functional
- [ ] 首次轉寫延遲 < 3 秒（使用快取模型）
- [ ] GUI 响应性良好（不阻塞 UI thread）
- [ ] 支援 Windows 10+ / macOS 12+ / Ubuntu 20.04+

### 12.3 Error Handling
- [ ] 麥克風無權限時顯示清楚錯誤訊息
- [ ] 模型載入失敗時有 fallback 機制
- [ ] API 請求格式錯誤時回傳 422
- [ ] 翻譯 API 連線失敗時顯示錯誤訊息
- [ ] 歷史紀錄載入失敗時顯示錯誤

---

## 14. Future Enhancements

- [ ] 即時串流辨識（WebSocket）
- [ ] 說話者分離（Diarization）
- [ ] 語音活動偵測（VAD）整合
- [ ] 快捷鍵支援
- [ ] 雲端同步歷史紀錄
- [ ] 多語言翻譯同時輸出
