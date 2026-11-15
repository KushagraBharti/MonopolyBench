#!/usr/bin/env bash
# Rebuild every generated input and the PDF from the saved games.
# Reads saved records only. No game, engine run, replay or model call is made.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-/tmp/monopoly-astra-rewrite-venv/bin/python}"
export PATH="/Library/TeX/texbin:$PATH"
export SOURCE_DATE_EPOCH=1794441600
export FORCE_SOURCE_DATE=1
if [ "${1:-}" != "--tex-only" ]; then
  ( cd analysis
    "$PY" b1_offers.py >/dev/null       # offer ledger, full tables, strata, sensitivity
    "$PY" b2_debt.py >/dev/null         # debt episodes, tiers, sixteen cases, first texts
    "$PY" b3_conditions.py >/dev/null   # prompts, refusals, usage, request settings
    "$PY" b4_provenance.py >/dev/null   # game map, commits, stored replay reports
    "$PY" b5_incidents.py >/dev/null    # asserted facts for the eight incidents
    "$PY" build_quotes.py >/dev/null    # quotations and the sixteen readings
    "$PY" build_prompt_listing.py >/dev/null
    "$PY" build_tables.py               # facts.tex and tables.tex
    "$PY" make_figures.py )
fi
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex >/dev/null
cp build/manuscript.pdf manuscript.pdf
if [ "${1:-}" != "--tex-only" ]; then
  ( cd analysis && "$PY" -W ignore verify_document.py && "$PY" -W ignore render_pages.py && "$PY" write_manifest.py )
fi
