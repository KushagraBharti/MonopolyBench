#!/usr/bin/env bash
# Regenerate every number, table, figure and quotation insert from stored records.
# Reads saved games and earlier ledgers only; runs no engine, replay, game or model call.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PAPER_PYTHON:-/tmp/monopoly-astra-rewrite-venv/bin/python}"
"$PY" offers_analysis.py
"$PY" finance_analysis.py
"$PY" provenance_checks.py
"$PY" quotes.py
"$PY" tables.py
"$PY" figures.py
