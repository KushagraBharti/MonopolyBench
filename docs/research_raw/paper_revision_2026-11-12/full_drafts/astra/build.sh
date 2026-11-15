#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export SOURCE_DATE_EPOCH=1794441600
export FORCE_SOURCE_DATE=1
export PATH="/Library/TeX/texbin:$PATH"
PAPER_PYTHON="${PAPER_PYTHON:-python3}"
"$PAPER_PYTHON" tools/check_finance.py > qa/finance_output.txt
"$PAPER_PYTHON" tools/check_offer_forms.py > qa/forms_output.txt
"$PAPER_PYTHON" tools/analyze.py > qa/analysis_output.txt
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex
cp build/manuscript.pdf manuscript.pdf
