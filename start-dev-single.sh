#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$ROOT_DIR/SentinelVault"
ML_DIR="$ROOT_DIR/crypto-ml"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not installed."
  exit 1
fi

cleanup() {
  if [[ -n "${ML_PID:-}" ]] && kill -0 "$ML_PID" >/dev/null 2>&1; then
    kill "$ML_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

cd "$ML_DIR"
PORT=8000 python3 fastapi_server.py &
ML_PID=$!

echo "Crypto ML API started with PID $ML_PID"

cd "$APP_DIR"
npm run dev
