#!/usr/bin/env bash
# Rebuild the Opus finalization draft from saved records. No engine, replay,
# policy, search or model call is made by any step.
set -euo pipefail
cd "$(dirname "$0")"
export SOURCE_DATE_EPOCH=1794441600
export FORCE_SOURCE_DATE=1
export PYTHONDONTWRITEBYTECODE=1
PY="${PAPER_PYTHON:-python3}"
mkdir -p qa data sections build
"$PY" tools/finance.py      > qa/finance_output.txt
"$PY" tools/channels.py     > qa/channels_output.txt
"$PY" tools/named_actions.py > qa/named_actions_output.txt
"$PY" tools/bargaining.py   > qa/bargaining_output.txt
"$PY" tools/provenance.py   > qa/provenance_output.txt
"$PY" tools/conditions.py   > qa/conditions_output.txt
"$PY" tools/tables.py       > qa/tables_output.txt
"$PY" tools/quotes.py       > qa/quotes_output.txt
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex > qa/latex_output.txt 2>&1 || { tail -40 qa/latex_output.txt; exit 1; }
cp build/manuscript.pdf manuscript.pdf
"$PY" tools/verify.py | tee qa/verify_output.txt
