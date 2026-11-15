# Opus independent draft, 12 November 2026

Open `manuscript.pdf` (29 pages: main text pp. 1–19, references pp. 19–20, appendices pp. 21–29). Source: `manuscript.tex` and `sections/`.

## Rebuild

Requirements: Python 3 with matplotlib and PyMuPDF (the local build used `/tmp/monopoly-astra-rewrite-venv/bin/python`; set `PAPER_PYTHON` to choose another), LuaLaTeX and latexmk, and the repository's saved games and research folders present.

```sh
bash build.sh                                   # analysis + figures + tables + quotes + PDF (~40 s)
SKIP_ANALYSIS=1 bash build.sh                   # PDF only, from existing data/ and sections/generated/
/tmp/monopoly-astra-rewrite-venv/bin/python qa/verify_document.py   # quotations and numbers in the PDF
python3 qa/wordcount.py                         # approximate main-text prose words
```

`analysis/run_all.sh` runs, in order: `offers_analysis.py`, `finance_analysis.py`, `provenance_checks.py`, `quotes.py`, `tables.py`, `figures.py`. Each reads stored records only, writes JSON to `data/` with the SHA-256 of every input, and stops on a failed assertion. No script imports the engine or arena, replays a game, runs a policy or contacts a provider. `git show` is used read-only to inspect source at the two run commits.

## Files

- `initial_position.md`: position written before drafting.
- `evidence_map.md`: every claim, its source and whether it was checked or inherited; literature reading scope.
- `findings_and_limits.md`: findings by evidence level, limits, dissent.
- `handoff.md`: status for cross-review and open decisions.
- `data/`: analysis outputs, the 16 first-decision texts and their single-reader classification, the quotation manifest with receipts and outcome checks, copied prompt texts.
- `sections/generated/`: tables and quotation macros produced by the scripts. Do not edit by hand.
- `assets/`: the two figures (PDF and PNG).
- `qa/`: verification script and output, word counter, contact sheets, extracted text.
- `*_inherited.bib`: byte copies of the 11 November bibliography; `opus_additions.bib`: three new entries.
