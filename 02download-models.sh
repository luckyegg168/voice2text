#!/usr/bin/env bash
# =============================================================================
# Voice2Text - 02 Download / Verify Models
# Downloads Qwen3-ASR speech recognition models from Hugging Face Hub.
# Requires 01setup.sh to have been run first.
# Usage: bash 02download-models.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}  [OK] $*${RESET}"; }
err()  { echo -e "${RED}[ERROR] $*${RESET}" >&2; }

exit_handler() {
    local code=$?
    if [ $code -ne 0 ]; then
        echo ""
        err "Download failed (exit code $code). See messages above."
    fi
    echo ""
    read -r -p "Press Enter to exit..." || true
}
trap exit_handler EXIT

# ── Verify venv ───────────────────────────────────────────────────────────────
PYTHON_EXE=".venv/bin/python"
if [ ! -f "$PYTHON_EXE" ]; then
    err "Virtual environment not found. Please run 01setup.sh first."
    exit 1
fi

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e "${CYAN}===================================${RESET}"
echo -e "${CYAN} Voice2Text  02 - Download Models${RESET}"
echo -e "${CYAN}===================================${RESET}"
echo ""
echo -e "${YELLOW}Available models:${RESET}"
echo "  1) Qwen/Qwen3-ASR-0.6B  (recommended, ~1.3 GB, faster)"
echo "  2) Qwen/Qwen3-ASR-1.7B  (higher accuracy, ~3.5 GB)"
echo "  3) Download both"
echo ""
read -r -p "Select model to download [1/2/3]: " choice
choice="${choice//[[:space:]]/}"

case "$choice" in
    1) models=("Qwen/Qwen3-ASR-0.6B") ;;
    2) models=("Qwen/Qwen3-ASR-1.7B") ;;
    3) models=("Qwen/Qwen3-ASR-0.6B" "Qwen/Qwen3-ASR-1.7B") ;;
    *) err "Invalid selection '$choice'. Please enter 1, 2, or 3."; exit 1 ;;
esac

for model in "${models[@]}"; do
    echo ""
    echo -e "${YELLOW}--- Downloading $model ---${RESET}"
    echo "    (large file; progress shown below)"
    "$PYTHON_EXE" - << PYEOF
import sys
from huggingface_hub import snapshot_download
try:
    path = snapshot_download(repo_id="$model")
    print(f"Download complete: {path}")
except Exception as exc:
    print(f"Download failed: {exc}", file=sys.stderr)
    sys.exit(1)
PYEOF
    ok "$model downloaded successfully."
done

echo ""
echo -e "${GREEN}===================================${RESET}"
echo -e "${GREEN} Model download complete!${RESET}"
echo -e "${CYAN} Next step: run ./03start.sh${RESET}"
echo -e "${GREEN}===================================${RESET}"
