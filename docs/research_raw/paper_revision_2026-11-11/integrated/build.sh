#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export SOURCE_DATE_EPOCH=1794355200
export FORCE_SOURCE_DATE=1
export PATH="/Library/TeX/texbin:$PATH"
"${PAPER_PYTHON:-python3}" tools/build_integration.py > build_data.log
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex
cp build/manuscript.pdf manuscript.pdf
