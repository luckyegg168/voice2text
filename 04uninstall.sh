#!/usr/bin/env bash
# =============================================================================
# Voice2Text - 04 Uninstall / Clean Up
# Interactively removes the virtual environment, optional model cache,
# user data, and .env configuration file.
# Usage: bash 04uninstall.sh
# =============================================================================

set -uo pipefail   # Note: no -e so we can handle errors manually

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; GRAY='\033[0;90m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}    [OK] $*${RESET}"; }
skip() { echo -e "${GRAY}    [SKIP] $*${RESET}"; }
warn() { echo -e "${YELLOW}$*${RESET}"; }

exit_handler() {
    echo ""
    read -r -p "Press Enter to exit..." || true
}
trap exit_handler EXIT

confirm() {
    local prompt="$1"
    read -r -p "    $prompt [y/N]: " ans
    [[ "${ans,,}" == "y" ]]
}

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e "${RED}===================================${RESET}"
echo -e "${RED} Voice2Text  04 - Uninstall / Clean${RESET}"
echo -e "${RED}===================================${RESET}"
echo ""
warn "WARNING: This will permanently delete selected items."
echo ""

# ── Step 1: Virtual environment ───────────────────────────────────────────────
echo -e "${CYAN}[1/4] Remove virtual environment (.venv)${RESET}"
if [ -d ".venv" ]; then
    if confirm "Delete .venv?"; then
        rm -rf .venv
        ok ".venv removed."
    else
        skip ""
    fi
else
    skip ".venv does not exist."
fi

# ── Step 2: Hugging Face model cache ──────────────────────────────────────────
echo ""
echo -e "${CYAN}[2/4] Remove Hugging Face model cache${RESET}"
HF_CACHE_DIR="${HF_HOME:-$HOME/.cache/huggingface}/hub"
QWEN_DIRS=()
if [ -d "$HF_CACHE_DIR" ]; then
    while IFS= read -r -d '' d; do
        QWEN_DIRS+=("$d")
    done < <(find "$HF_CACHE_DIR" -maxdepth 1 -type d -iname '*qwen3*asr*' -print0 2>/dev/null || true)
fi
if [ ${#QWEN_DIRS[@]} -gt 0 ]; then
    echo "    Found Qwen3-ASR cache:"
    for d in "${QWEN_DIRS[@]}"; do echo "      $d"; done
    if confirm "Delete these directories (several GB)?"; then
        for d in "${QWEN_DIRS[@]}"; do
            rm -rf "$d"
            ok "Removed $(basename "$d")"
        done
    else
        skip ""
    fi
else
    skip "No Qwen3-ASR cache found."
fi

# ── Step 3: User data ─────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[3/4] Remove user data (recordings, history database)${RESET}"
if [ -d "data" ]; then
    if confirm "Delete data/ directory (recordings + history)?"; then
        rm -rf data
        ok "data/ removed."
    else
        skip ""
    fi
else
    skip "data/ does not exist."
fi

# ── Step 4: .env configuration ────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[4/4] Remove .env configuration file${RESET}"
if [ -f ".env" ]; then
    if confirm "Delete .env?"; then
        rm -f .env
        ok ".env removed."
    else
        skip ""
    fi
else
    skip ".env does not exist."
fi

echo ""
echo -e "${GREEN}===================================${RESET}"
echo -e "${GREEN} Cleanup complete!${RESET}"
echo -e "${GREEN}===================================${RESET}"
