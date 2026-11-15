#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/Library/TeX/texbin:$PATH"
export SOURCE_DATE_EPOCH=1794355200
mkdir -p build
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build manuscript.tex > qa/latex_pass1.txt
bibtex build/manuscript > qa/bibtex.txt
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build manuscript.tex > qa/latex_pass2.txt
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build manuscript.tex > qa/latex_pass3.txt
cp build/manuscript.pdf manuscript.pdf
