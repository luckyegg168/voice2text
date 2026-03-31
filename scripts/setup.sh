#!/bin/bash
# Voice2Text Portable App Setup Script (Linux/macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "======================================"
echo " Voice2Text - Setup (Unix)"
echo "======================================"
echo ""

# 檢查 Python
echo "[1/5] 檢查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    if [[ $PYTHON_VERSION =~ Python\ 3\.(10|11|12|13) ]]; then
        echo "  OK ($PYTHON_VERSION)"
    else
        echo "  ERROR: 需要 Python 3.10-3.13"
        exit 1
    fi
else
    echo "  ERROR: 未找到 Python"
    echo "  請從 python.org 安裝或使用系統套件管理器"
    exit 1
fi

# 建立虛擬環境
echo "[2/5] 建立虛擬環境 (.venv)..."
if [ -d ".venv" ]; then
    echo "  已存在，跳過"
else
    python3 -m venv .venv
fi

# 啟動虛擬環境並升級 pip
echo "[3/5] 升級 pip..."
source .venv/bin/activate
pip install --upgrade pip --quiet

# 安裝依賴
echo "[4/5] 安裝依賴套件..."
pip install -e ".[dev]" --quiet

# 建立必要目錄
echo "[5/5] 建立資料目錄..."
for dir in data data/recordings models; do
    mkdir -p "$dir"
done

# 複製 .env.example 到 .env
if [ ! -f ".env" ]; then
    echo ""
    echo "複製 .env.example 到 .env..."
    cp .env.example .env
fi

echo ""
echo "======================================"
echo " 安裝完成！"
echo "======================================"
echo ""
echo "啟動方式：" 
echo "  GUI:  bash scripts/run-gui.sh"
echo "  API:  bash scripts/run-api.sh"
echo "  CLI:  source .venv/bin/activate && python -m app.cli"
echo ""
