#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m venv .venv
"$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

cat <<'EOF'
Setup complete.

Run the application with:
  ./run_glkvmapp.sh

If Qt reports that the "xcb" platform plugin could not be initialized,
install the Ubuntu runtime package:
  sudo apt install libxcb-cursor0
EOF
