#!/usr/bin/env bash
# =============================================================================
# Voice2Text - 01 Environment Setup
# Creates virtual environment, installs dependencies, creates data directories,
# and generates a default .env configuration file.
# Usage: bash 01setup.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; GRAY='\033[0;90m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}  [OK] $*${RESET}"; }
skip() { echo -e "${GRAY}  [SKIP] $*${RESET}"; }
step() { echo -e "\n${YELLOW}>>> $*${RESET}"; }
err()  { echo -e "${RED}[ERROR] $*${RESET}" >&2; }

exit_handler() {
    local code=$?
    if [ $code -ne 0 ]; then
        echo ""
        err "Setup failed (exit code $code). See messages above."
    fi
    echo ""
    read -r -p "Press Enter to exit..." || true
}
trap exit_handler EXIT

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e "${CYAN}===================================${RESET}"
echo -e "${CYAN} Voice2Text  01 - Environment Setup${RESET}"
echo -e "${CYAN}===================================${RESET}"

# ── Python version check ──────────────────────────────────────────────────────
step "Checking Python installation..."
PY_CMD=""
for candidate in python3 python python3.12 python3.11 python3.10; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" --version 2>&1 | grep -oP 'Python \K[0-9]+\.[0-9]+' || true)
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "${major:-0}" -ge 3 ] && [ "${minor:-0}" -ge 10 ]; then
            PY_CMD="$candidate"
            ok "Found $candidate ($("$candidate" --version 2>&1))"
            break
        fi
    fi
done
if [ -z "$PY_CMD" ]; then
    err "Python 3.10 or newer not found."
    echo "  Install from https://python.org or via your system package manager."
    exit 1
fi

# ── Create virtual environment ────────────────────────────────────────────────
step "Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    echo "  Creating .venv ..."
    "$PY_CMD" -m venv .venv
    ok "Virtual environment created."
else
    skip ".venv already exists."
fi

PIP_EXE=".venv/bin/pip"
PYTHON_EXE=".venv/bin/python"

# ── Upgrade pip ───────────────────────────────────────────────────────────────
step "Upgrading pip..."
"$PYTHON_EXE" -m pip install --upgrade pip --quiet
ok "pip upgraded."

# ── Install project dependencies ──────────────────────────────────────────────
step "Installing project dependencies (pyproject.toml)..."
echo "  This may take several minutes on first run."
"$PIP_EXE" install -e ".[all]"
ok "Dependencies installed."

# ── Create data directories ───────────────────────────────────────────────────
step "Creating data directories..."
for dir in "data" "data/recordings"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        ok "Created $dir"
    else
        skip "$dir already exists."
    fi
done

# ── Generate default .env ─────────────────────────────────────────────────────
step "Generating .env configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Voice2Text Configuration - Edit as needed

# ASR Model
DEFAULT_MODEL=Qwen/Qwen3-ASR-0.6B
DEVICE=cuda
DTYPE=float16

# Audio
SAMPLE_RATE=16000
CHANNELS=1
VAD_ENABLED=true

# Translation API (Ollama default)
TRANSLATION_API_URL=http://localhost:11434/v1/chat/completions
TRANSLATION_API_KEY=
TRANSLATION_MODEL=llama3.2

# Storage
DATA_DIR=./data
RECORDINGS_DIR=./data/recordings
DATABASE_URL=sqlite+aiosqlite:///./data/voice2text.db
MAX_HISTORY_ITEMS=1000

# OpenCC
OPENCC_MODE=s2t
HOTWORDS_FILE=./data/hotwords.json
EOF
    ok "Created .env (edit it to customize settings)"
else
    skip ".env already exists."
fi

echo ""
echo -e "${GREEN}===================================${RESET}"
echo -e "${GREEN} Setup complete!${RESET}"
echo -e "${CYAN} Next step: run ./02download-models.sh${RESET}"
echo -e "${GREEN}===================================${RESET}"
