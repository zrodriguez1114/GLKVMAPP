#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${QT_QPA_PLATFORM:-}" ]]; then
  if [[ "${XDG_SESSION_TYPE:-}" == "wayland" ]]; then
    export QT_QPA_PLATFORM=wayland
  fi
fi

exec "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/GLKVMAPP.py"
