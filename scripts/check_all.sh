#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Missing virtual environment at $ROOT_DIR/.venv"
  echo "Create it with: python3 -m venv .venv"
  exit 1
fi

echo "Running backend unit tests..."
PYTHONPATH="$ROOT_DIR:$ROOT_DIR/services/api" "$VENV_PYTHON" -m unittest discover -s "$ROOT_DIR/tests" -p "test_*.py" -v

echo "Running frontend lint..."
npm --prefix "$ROOT_DIR" --workspace apps/web run lint

echo "Running frontend production build..."
npm --prefix "$ROOT_DIR" run build:web

echo "Running monitoring snapshot CLI..."
PYTHONPATH="$ROOT_DIR" "$VENV_PYTHON" -B "$ROOT_DIR/services/monitoring/jobs/drift_snapshot.py"
