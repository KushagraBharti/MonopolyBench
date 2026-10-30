#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Fixed document date; compiler/font versions must also match for byte equality.
export SOURCE_DATE_EPOCH=1793232000
export FORCE_SOURCE_DATE=1
latexmk -lualatex -interaction=nonstopmode -halt-on-error paper_outline.tex
latexmk -lualatex -interaction=nonstopmode -halt-on-error figures_and_tables.tex
cp build/paper_outline.pdf paper_outline.pdf
cp build/figures_and_tables.pdf figures_and_tables.pdf
