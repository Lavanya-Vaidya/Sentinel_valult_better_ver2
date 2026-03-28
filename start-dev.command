#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$ROOT_DIR/SentinelVault"
ML_DIR="$ROOT_DIR/crypto-ml"

if ! command -v osascript >/dev/null 2>&1; then
  echo "osascript is required to open Terminal tabs automatically."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not installed."
  exit 1
fi

osascript <<EOF
tell application "Terminal"
  activate
  do script "cd \"$ML_DIR\" && PORT=8000 python3 fastapi_server.py"
  do script "cd \"$APP_DIR\" && npm run dev"
end tell
EOF

echo "Starting Crypto ML API and SentinelVault in Terminal."
