# Astra complete independent finalization draft

The main text is seven two-column pages, followed by references and a complete supplement. `manuscript.pdf` is the reading copy. This is a named preprint draft, not a submitted conference paper. Human author: Kushagra Bharti, as recorded in the repository's CITATION.cff. AI assistance is disclosed separately.

From this directory, run:

```sh
python3 -m venv /tmp/monopoly-paper-env
/tmp/monopoly-paper-env/bin/pip install pymupdf pillow
PAPER_PYTHON=/tmp/monopoly-paper-env/bin/python bash build.sh
```

LuaLaTeX, latexmk, BibTeX, TeX Gyre Pagella/Heros and Latin Modern Mono are required. The script adds the macOS TeX Live path if available; other installations must expose the commands on PATH. The tested document environment used PyMuPDF 2.1 and Pillow 13.0.0. The package is repository-contained: run it within a complete MonopolyBench checkout with the `saved_games` archive and earlier research packages. It does not download or run games.

The build checks all 188 initial financing responses against raw decision records, regenerates all available text channels for the sixteen necessary-collateral episodes, compiles the paper, checks 20 quoted spans and 29 initial fields in the PDF, checks the protected 84-file November 12 manifest, and renders all pages under `qa/`. The source contains no engine import or model request. The render files are local QA artifacts, not additional research data.

The source-linked offer ledger, tables and resampling outputs are preserved from `docs/research_raw/paper_revision_2026-11-12/integrated/`. Its `tools/analyze.py`, `check_offer_forms.py`, `check_finance.py`, `integrate_checks.py` and `final_checks.py` document their arithmetic and generation. These are retained analyses, not freshly collected evidence. Their historical inputs and hashes are included in `data/`; the `game_map.json` resolves G1–G20 to canonical saved runs. This draft's own read-only generator is `tools/prepare.py`. Do not run earlier build commands in protected historical folders if preserving their byte hashes.

The historical three payment witnesses, G7 menu search, construction checks and two replay modes are reported from their stored results. No engine, policy, solver, replay or model evaluation was run for this draft. The 131-entry continuation argument is mathematical source reasoning, not an executed baseline score.

`evidence_map.md` gives claim provenance. `changes_and_dissent.md` records editorial judgments. `verification.md` records build and rendering checks. The draft remains separate from the forthcoming integrated release.
