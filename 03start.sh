#!/usr/bin/env bash
# =============================================================================
# Voice2Text - 03 Start Application
# Launches the GUI desktop app, REST API server, or both.
# Requires 01setup.sh to have been run first.
# Usage: bash 03start.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; RESET='\033[0m'

err() { echo -e "${RED}[ERROR] $*${RESET}" >&2; }

exit_handler() {
    local code=$?
    if [ $code -ne 0 ]; then
        echo ""
        err "Exited with code $code."
        echo ""
        read -r -p "Press Enter to exit..." || true
    fi
}
trap exit_handler EXIT

# ── Verify venv ───────────────────────────────────────────────────────────────
PYTHON_EXE=".venv/bin/python"
if [ ! -f "$PYTHON_EXE" ]; then
    err "Virtual environment not found. Please run 01setup.sh first."
    exit 1
fi

# ── Load .env ─────────────────────────────────────────────────────────────────
if [ -f ".env" ]; then
    set -o allexport
    # shellcheck disable=SC1091
    source <(grep -E '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=' .env | sed 's/^[[:space:]]*//')
    set +o allexport
fi

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e "${CYAN}===================================${RESET}"
echo -e "${CYAN} Voice2Text  03 - Start Application${RESET}"
echo -e "${CYAN}===================================${RESET}"
echo ""
echo -e "${YELLOW}Launch options:${RESET}"
echo "  1) GUI  - Graphical desktop app (default)"
echo "  2) API  - REST API server  (http://localhost:8000/docs)"
echo "  3) Both - GUI + API server in background"
echo ""
read -r -p "Select option [1/2/3] (default: 1): " choice
choice="${choice//[[:space:]]/}"
[ -z "$choice" ] && choice="1"

case "$choice" in
    1)
        echo -e "\n${GREEN}Starting GUI...${RESET}"
        "$PYTHON_EXE" -m app.gui
        ;;
    2)
        echo -e "\n${GREEN}Starting API server...${RESET}"
        echo "  Swagger docs: http://localhost:8000/docs"
        echo "  Press Ctrl+C to stop."
        echo ""
        "$PYTHON_EXE" -m app.api
        ;;
    3)
        echo -e "\n${GREEN}Starting API server in background...${RESET}"
        "$PYTHON_EXE" -m app.api &
        API_PID=$!
        echo "  API server PID: $API_PID"
        echo "  Swagger docs:   http://localhost:8000/docs"
        sleep 1
        echo -e "${GREEN}Starting GUI...${RESET}"
        "$PYTHON_EXE" -m app.gui
        # When GUI exits, stop API server
        echo "  Stopping API server (PID $API_PID)..."
        kill "$API_PID" 2>/dev/null || true
        ;;
    *)
        err "Invalid option '$choice'. Please enter 1, 2, or 3."
        exit 1
        ;;
esac
