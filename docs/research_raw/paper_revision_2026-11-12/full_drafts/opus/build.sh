#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export SOURCE_DATE_EPOCH=1794441600
export FORCE_SOURCE_DATE=1
export PATH="/Library/TeX/texbin:$PATH"
if [ "${SKIP_ANALYSIS:-0}" != "1" ]; then bash analysis/run_all.sh > build_analysis.log; fi
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex > build_latex.log 2>&1 || { tail -40 build_latex.log; exit 1; }
cp build/manuscript.pdf manuscript.pdf
