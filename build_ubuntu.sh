#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m pip install --user pyinstaller
python3 -m PyInstaller --onefile --windowed --name JsonConverter ./json_converter.py

echo "Built: ./dist/JsonConverter"
