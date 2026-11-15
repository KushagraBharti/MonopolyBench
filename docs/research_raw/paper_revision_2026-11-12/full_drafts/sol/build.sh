#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v lualatex >/dev/null 2>&1; then export PATH="/Library/TeX/texbin:$PATH"; fi
PAPER_PYTHON="${PAPER_PYTHON:-python3}"
mkdir -p build qa
"$PAPER_PYTHON" tools/analyze.py > qa/analysis_output.txt
latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=build manuscript.tex > qa/build_output.txt 2>&1
cp build/manuscript.pdf manuscript.pdf
"$PAPER_PYTHON" tools/verify.py
