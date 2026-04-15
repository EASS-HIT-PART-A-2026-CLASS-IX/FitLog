#!/usr/bin/env bash
# FitLog EX3 demo launcher
# Usage: bash scripts/demo.sh
set -euo pipefail

echo "Starting FitLog demo..."
echo ""
echo "Make sure both services are running in separate terminals:"
echo "  Terminal 1:  uv run uvicorn app.main:app --reload"
echo "  Terminal 2:  uv run streamlit run frontend/app.py"
echo ""
read -rp "Press Enter when the API is ready... "

uv run python scripts/demo.py
