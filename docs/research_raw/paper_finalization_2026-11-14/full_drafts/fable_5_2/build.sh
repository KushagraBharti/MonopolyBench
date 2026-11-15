#!/usr/bin/env bash
# Rebuild every table, quotation, figure and supplement file from the saved games,
# compile the manuscript and verify the PDF.
#
# Reads stored JSON and JSONL only. Does not import the rules engine, replay a game,
# run a policy or call a model.
set -euo pipefail
cd "$(dirname "$0")"
PAPER_PYTHON="${PAPER_PYTHON:-python3}"
export PATH="/Library/TeX/texbin:$PATH"
export SOURCE_DATE_EPOCH=1794614400
export FORCE_SOURCE_DATE=1
mkdir -p qa build data sections assets supplement
(
  cd tools
  for step in 01_episodes 02_finance 03_stated_totals 04_corpus 05_bargaining 06_quotes 07_tables; do
    "$PAPER_PYTHON" "$step.py" > "../qa/$step.txt"
  done
)
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex > qa/build_output.txt 2>&1
cp build/manuscript.pdf manuscript.pdf
(cd tools && "$PAPER_PYTHON" 08_verify.py)
