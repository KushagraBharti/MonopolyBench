#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/Library/TeX/texbin:$PATH"
export SOURCE_DATE_EPOCH=1794614400
export FORCE_SOURCE_DATE=1
mkdir -p qa
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex >qa/build_stdout.txt 2>&1
cp build/manuscript.pdf manuscript.pdf
if [[ "${1:-}" == "--verify" ]]; then
  PAPER_PYTHON="${PAPER_PYTHON:-python3}"
  "$PAPER_PYTHON" tools/verify_document.py
fi
