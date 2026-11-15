# Independent Sol whole-paper package

Start with `manuscript.pdf`. Native source is `manuscript.tex`, with authored sections in `sections/`, exact inherited quote definitions, and `references.bib`. This is a complete independent manuscript, not a section contribution. No other new author draft was read.

The central claim concerns LLM attention to competitors' future options, with mixed evidence for coherent valuation. Three figures show same-deed asks, all trade-group ownership/exposure histories, and first-creditor pre-estate ranks. Eight main incidents retain exact source spans.

## Build

From this directory, on the available machine:

```bash
/tmp/monopoly-astra-rewrite-venv/bin/python analyze_records.py
/tmp/monopoly-astra-rewrite-venv/bin/python make_tables.py
bash build.sh
/tmp/monopoly-astra-rewrite-venv/bin/python verify_document.py
```

Python needs Matplotlib, PyMuPDF, and Pillow. LuaLaTeX and BibTeX are found under `/Library/TeX/texbin`; TeX Gyre Pagella/Heros and Latin Modern fonts are used. The script prepends the TeX binary directory and runs LuaLaTeX/BibTeX/LaTeX/LaTeX. The PDF and generated figures are included, so reading requires no build.

Arithmetic scripts require the original repository at its current relative directory layout, including all twenty saved research games, prior reconstructed offer/flow/episode ledgers, and the original board data. Exact quote verification requires the original sources named in the copied manifests. `data/source_hashes.json` fixes numerical inputs; `data/copied_sources.json` fixes copied quote definitions/manifests. No engine package is imported or executed. A standalone archival copy must preserve those sources or include them under the same documented relative layout.

## Reports

- `initial_position.md`: pre-analysis independent position.
- `evidence_map.md`: fresh arithmetic versus inherited witnesses/codes.
- `literature_inspiration.md`: exact primary readings and supported citation uses.
- `findings_and_limits.md`: new results, dissent and feedback dispositions.
- `qa/document_checks.json`: quote/PDF/source checks.
- `qa/public_delivery_checks.json`: complete-message exposure checks; G12 has no later delivery.
- `qa/render/`: every page at 1.5x resolution and contact sheets.
- `handoff.md`: completion and remaining cross-review work.

All writes in this assignment are confined to this Sol directory. No game, prompt, engine, prior source, shared revision file, branch, commit, or push was changed. The package's numerical recomputation is an existing-record analysis, not an evaluation run.
