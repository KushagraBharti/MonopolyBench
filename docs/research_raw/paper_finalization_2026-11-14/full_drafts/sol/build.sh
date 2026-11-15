#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/Library/TeX/texbin:$PATH"
export SOURCE_DATE_EPOCH=1794614400
export FORCE_SOURCE_DATE=1
mkdir -p build qa
latexmk -lualatex -outdir=build -interaction=nonstopmode -halt-on-error manuscript.tex > qa/build_output.txt 2>&1
cp build/manuscript.pdf manuscript.pdf
