#!/usr/bin/env bash
# Rebuild the cross-review checks, the quotation macros and the replacement-prose PDF.
# Reads stored records only. Runs no engine, replay, game or model query.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PAPER_PYTHON:-/tmp/monopoly-astra-rewrite-venv/bin/python}"
export PATH="/Library/TeX/texbin:$PATH"
if [[ "${1:-}" != "--tex-only" ]]; then
  ( cd tools
    "$PY" -B check_debts.py            > ../data/check_debts_output.txt
    "$PY" -B check_request_values.py   > ../data/check_request_values_output.txt
    "$PY" -B check_offers.py           > ../data/check_offers_output.txt
    "$PY" -B check_response_conflicts.py > ../data/check_response_conflicts_output.txt
    "$PY" -B check_economy.py          > ../data/check_economy_output.txt
    "$PY" -B build_quotes.py           > ../data/build_quotes_output.txt )
fi
mkdir -p build
latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=build replacement_prose.tex > build/latexmk_stdout.txt 2>&1
cp build/replacement_prose.pdf replacement_prose.pdf
( cd tools && "$PY" -B verify_replacement.py 2>/dev/null | tee ../data/verify_replacement_output.txt )
( cd tools && "$PY" -B write_findings.py )
