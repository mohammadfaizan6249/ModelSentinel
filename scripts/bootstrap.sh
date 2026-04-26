#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Installing frontend dependencies..."
cd "$ROOT_DIR"
npm install

echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Installing backend dependencies..."
./.venv/bin/pip install ./services/api

echo
echo "Bootstrap complete."
echo "Run the API with: make run-api"
echo "Run the frontend with: npm run dev:web"
echo "Run all checks with: ./scripts/check_all.sh"
