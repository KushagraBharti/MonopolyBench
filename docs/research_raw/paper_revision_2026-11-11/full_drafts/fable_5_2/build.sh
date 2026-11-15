#!/usr/bin/env bash
# Rebuild every generated input and the PDF. No game, engine or model call is made.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-/tmp/monopoly-astra-rewrite-venv/bin/python}"
export PATH="/Library/TeX/texbin:$PATH"
export SOURCE_DATE_EPOCH=1794355200
export FORCE_SOURCE_DATE=1
if [ "${1:-}" != "--tex-only" ]; then
  ( cd analysis
    "$PY" state_track.py >/dev/null
    "$PY" a1_conditions.py >/dev/null
    "$PY" a2_offer_ledger.py >/dev/null
    "$PY" a3_groups.py >/dev/null
    "$PY" a4_debt.py >/dev/null
    "$PY" a5_estates.py >/dev/null
    "$PY" a6_bargaining.py >/dev/null
    "$PY" a7_conversion.py >/dev/null
    "$PY" a8_estates_flows.py >/dev/null
    "$PY" a9_incident_checks.py >/dev/null
    "$PY" build_quotes.py >/dev/null
    "$PY" build_prompt_listing.py >/dev/null
    "$PY" build_tables.py
    "$PY" make_figures.py )
fi
latexmk -lualatex -interaction=nonstopmode -halt-on-error manuscript.tex
cp build/manuscript.pdf manuscript.pdf
if [ "${1:-}" != "--tex-only" ]; then
  ( cd analysis && "$PY" -W ignore verify_document.py >/dev/null && "$PY" -W ignore render_pages.py && "$PY" write_manifest.py )
fi
