#!/usr/bin/env bash
# ==============================================================================
# Run the AI Email Security Detector locally (Linux / macOS)
# ==============================================================================
# Usage:
#   chmod +x run-local.sh
#   ./run-local.sh
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"

# ── 1. Create virtual environment if it doesn't exist ─────────────────────────
if [ ! -f "$PYTHON_BIN" ]; then
  echo "[INFO] Creating virtual environment at $VENV_DIR ..."
  python3 -m venv "$VENV_DIR"
fi

# ── 2. Install / update dependencies ─────────────────────────────────────────
echo "[INFO] Installing dependencies ..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r requirements.txt

# ── 3. Start the Flask development server ─────────────────────────────────────
echo ""
echo "[INFO] Starting Email Security Detector on http://127.0.0.1:5000"
echo "[INFO] Press Ctrl+C to stop."
echo ""

export FLASK_APP=src.wsgi:application
export FLASK_ENV=development
# WARNING: the fallback key below is only safe for local development.
# Set the SECRET_KEY environment variable before running this script in any
# shared or production environment.
export SECRET_KEY="${SECRET_KEY:-dev-secret-key-32-characters!!}"

"$VENV_DIR/bin/flask" run --host=127.0.0.1 --port=5000
