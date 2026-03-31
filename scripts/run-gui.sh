#!/bin/bash
# Voice2Text - Run GUI (Unix)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "錯誤：找不到虛擬環境 (.venv)"
    echo "請先執行 bash scripts/setup.sh"
    exit 1
fi

# 設定環境變數
export HF_HOME="$PROJECT_ROOT/models/.hf_cache"
export TRANSFORMERS_CACHE="$PROJECT_ROOT/models/.transformers_cache"
export PYTHONPATH="$PROJECT_ROOT"

echo "啟動 Voice2Text GUI..."

# 啟動 GUI
source .venv/bin/activate
python -m app.gui
