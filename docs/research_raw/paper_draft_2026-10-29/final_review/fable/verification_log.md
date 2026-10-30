# Fable verification log (2026-10-29, final integration review)

Sources read at their 15:35 state: manuscript.tex, preamble.tex, sections/*.tex, references.bib, references_source.bib, build/manuscript.log, build_output.log, manuscript.pdf (33 pages, all rendered at 80 dpi into contact sheets plus 200 dpi crops of pages 3, 12, 13, 27, 29). Renders are under render/.

index games found: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

## Cohort table (Table 7) cross-checks

- data/t01_cohort.json: 20/20 rows match seed, rotation, turns, winner and winner seat.
- saved_games game-index.csv files (12-game collection = G1-12; 8-game collection = G13-20, keyed on collection_game): 20/20 rows match on every column the index provides (turns and git SHA for all; seed, winner model and fingerprint for G13-20). Mismatches: none.
- The 12-game index carries no seed or winner column, so seeds and winners for G1-12 rest on data/t01_cohort.json (hash recorded in figure_manifest.json) and on the phase-3 exhibits cited in coauthors/fable/evidence_map.md.

## Other checks

- Redemption and trade-interest rounding recomputed over all sixteen board prices from contracts/data/board.json: redemption engine value exceeds the exact ceiling for principals 50, 90, 100, 110, 200; trade interest is exact for all.
- Taxes: contracts/data/board.json tax_amounts {4: 200, 38: 100}.
- Cited keys: 32 used, all present in references.bib; references_source.bib sha256 equals the frozen phase-3 library; diff to references.bib removes only `note` fields.
- Final LuaLaTeX pass (build/manuscript.log): no Warning, Overfull or Underfull lines; no '??' in extracted text.
