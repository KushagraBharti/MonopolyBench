#!/usr/bin/env bash
# Build the manuscript PDF. Figures and generated TeX are checked in; regenerate them with
#   OPUS_CACHE=<scratch dir> python tools/corpus.py && python tools/offers.py && ... (see BUILD.md)
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/Library/TeX/texbin:$PATH"
export SOURCE_DATE_EPOCH=1794355200
export FORCE_SOURCE_DATE=1
latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=build manuscript.tex
cp build/manuscript.pdf manuscript.pdf
