#!/usr/bin/env bash
# Rebuild checks, figures and the PDF for the Fable 5.2 full draft. No engine or model execution.
set -euo pipefail
cd "$(dirname "$0")"
REPO="$(cd ../../../../.. && pwd)"
python3 tools/census_decisions.py > qa/census_decisions.log
python3 tools/retab_offers.py   > qa/retab_offers.log
python3 tools/retab_economy.py  > qa/retab_economy.log
python3 tools/retab_distress.py > qa/retab_distress.log
python3 tools/retab_conflicts.py > qa/retab_conflicts.log
python3 tools/build_quotes.py   > qa/build_quotes.log
python3 tools/make_tables.py    > qa/make_tables.log
"$REPO/python/.venv/bin/python" tools/make_figures.py > qa/make_figures.log
export SOURCE_DATE_EPOCH=1794268800
export FORCE_SOURCE_DATE=1
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex
cp build/manuscript.pdf manuscript.pdf
"$REPO/python/.venv/bin/python" tools/check_manuscript.py > qa/check_manuscript.log
