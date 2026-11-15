# Integrated manuscript — finalization in progress

This package integrates all four independent complete manuscripts under the November 14 finalization brief. Astra, Sol, Opus and Fable 5.2 have been compared, and the fresh Sol 6.1 adversarial review has been applied. The candidate now awaits complete core-team cross-review and final release checks. Material choices are recorded in the parent `INTEGRATION_DECISIONS.md`.

## Build the document

```sh
bash build.sh
```

The default build uses only the shipped static LaTeX, bibliography, figures and generated text. It requires LuaLaTeX, latexmk, BibTeX and the TeX Gyre/Latin Modern fonts. It does not require the saved-game archive, execute analysis, or make network requests. The result is `manuscript.pdf`.

## Recheck the original records

These optional commands require a complete MonopolyBench checkout, including the canonical `saved_games` paths in `data/game_map.json` and historical research inputs. They read stored records and perform arithmetic; they never import or execute the rules engine, run a policy, search state space, replay a game, or call a model.

```sh
python3 tools/refresh_records.py
python3 tools/prepare.py
python3 tools/check_sources.py
python3 tools/check_integrated_additions.py
python3 tools/check_stated_totals.py
```

`refresh_records.py`, adopted from Sol's independent revision, re-extracts all 188 first responses, recomputes resource sums and the 108/12/9/2 proof-premise partition, and checks corpus totals. `prepare.py` separately verifies the retained complete first-response record and produces the full sixteen-case text supplement without altering its wording. `check_sources.py` verifies all retained quotation spans and all 920 offer/action joins, and reads the stored audit/replay reports without executing them.

The bargaining classifications and bootstrap results come from the preserved November 12 analysis. The complete arithmetic scripts are at `docs/research_raw/paper_revision_2026-11-12/integrated/tools/`; their stored inputs and output tables remain included here. Do not run those scripts in the protected historical folder when preserving its byte hashes. The release distinguishes rebuilding a document, checking original records and collecting new evidence.

`check_integrated_additions.py` checks the thirty building-owning debtors whose initially listed mortgages suffice against their original action records, and verifies three additional G7 quotations and the recipient's receipt of the public counteroffer. It does not evaluate a strategy.

`check_stated_totals.py` reproduces the supplemental numeric-presence count on unpayable debts. Matching contexts, field hashes and the definition are shipped in `data/stated_totals_check.json`. The check does not score whole-response accuracy.

## Verify and inspect the PDF

```sh
python3 -m venv /tmp/monopoly-paper-env
/tmp/monopoly-paper-env/bin/pip install pymupdf pillow
PAPER_PYTHON=/tmp/monopoly-paper-env/bin/python bash build.sh --verify
```

Verification requires the repository archive. It checks original source hashes, the focal fields and displayed quotes in the PDF, the protected historical manuscript, document warnings and text boundaries. It renders pages and contact sheets under `qa/` for visual inspection. Render intermediates are not part of the scientific corpus.

This is a named preprint by Kushagra Bharti, with AI assistance disclosed separately. No affiliation, submission or acceptance is asserted. The standing instruction against new evaluations remains in force.
