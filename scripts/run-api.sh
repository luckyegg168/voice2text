#!/bin/bash
# Voice2Text - Run API Server (Unix)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "錯誤：找不到虛擬環境 (.venv)"
    echo "請先執行 bash scripts/setup.sh"
    exit 1
fi

# 讀取 .env 並設定環境變數
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# 設定環境變數
export HF_HOME="$PROJECT_ROOT/models/.hf_cache"
export TRANSFORMERS_CACHE="$PROJECT_ROOT/models/.transformers_cache"
export PYTHONPATH="$PROJECT_ROOT"

PORT="${API_PORT:-8000}"
HOST="${API_HOST:-0.0.0.0}"

echo "啟動 Voice2Text API Server..."
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  URL:  http://$HOST:$PORT/docs"
echo ""

# 啟動 API
source .venv/bin/activate
uvicorn app.api.main:app --host "$HOST" --port "$PORT" --reload
