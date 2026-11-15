#!/usr/bin/env bash
# Re-run every check of the Fable 5.2 cross-review and rebuild the replacement prose.
# Reads saved records and the four frozen drafts. Runs no game, engine, replay or model call.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PY:-python3}"
for s in c1_cash_by_cell c2_refusal_to_sale c3_defensive_contrast c3b_offer_type c3c_swap_table c3d_dedup \
         c3e_grok_conflict_openings c4_seller_conversion c5_debt_census c6_distress_populations \
         c7_landings_and_misc c8_spot_checks c9_cash_sensitivity c10_quote_sources build_quotes c11_prose_facts build_findings; do
  echo "== $s"; "$PY" "tools/$s.py" > "build/$s.out" 2>&1 || { tail -5 "build/$s.out"; exit 1; }
  tail -1 "build/$s.out"
done
export PATH="/Library/TeX/texbin:$PATH" SOURCE_DATE_EPOCH=1794355200 FORCE_SOURCE_DATE=1
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build replacement_prose.tex > build/pass1.log 2>&1
lualatex -interaction=nonstopmode -halt-on-error -output-directory=build replacement_prose.tex > build/pass2.log 2>&1
cp build/replacement_prose.pdf replacement_prose.pdf
if grep -q -i "overfull\|undefined\|missing character" build/replacement_prose.log; then echo "LaTeX diagnostics present"; exit 1; fi
grep "Output written" build/replacement_prose.log
