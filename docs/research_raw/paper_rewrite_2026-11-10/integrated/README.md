# Integrated manuscript

This manuscript integrates the complete independent papers and whole-paper reviews by Astra, Sol, Opus and Fable 5.2. The final revision foregrounds strategic bargaining, financing, development and creditor inheritance, with eight contextual transcript incidents. Detailed response conditions and verification scope are retained in the appendix and evidence archive. All three final reviews have been adjudicated; no further review round is pending.

- Read `manuscript.pdf`; edit `manuscript.tex` and the native `sections/*.tex` files.
- `integration_decisions.md` records editorial choices and review dispositions.
- `evidence_map.md` separates performed source checks from inherited analyses.
- `qa/document_checks.json` records the exact PDF hash, original quote checks, frozen-file checks and document diagnostics. It does not certify the scientific interpretation.
- `tools/build_exhibits.py` reconstructs two figures and three native table row sets from retained ledgers. It does not run a game or import the engine.

## Build

LuaLaTeX and latexmk are required. Figure generation and document checks use Python with Matplotlib, Pillow and PyMuPDF.

```sh
python tools/build_exhibits.py
python tools/check_retained_tables.py
python tools/check_opus_followup.py
python tools/check_fable_followup.py
python tools/prepare_quote_labels.py
bash build.sh
python tools/verify_document.py
```

On the current Mac, add `/Library/TeX/texbin` to `PATH`. The already provisioned Python environment is `/tmp/monopoly-astra-rewrite-venv/bin/python`; it is a local convenience, not a portable dependency specification. Generated TeX files are checked in alongside the figures so a document-only build does not require Python. `build.sh` fixes the source date and places auxiliary files in `build/`.

The parent rewrite package and the repository are needed for original-source verification. The PDF itself is standalone. The source manifests identify copied inputs and retained original paths rather than implying all raw games are bundled into this small directory.

## Scope

The manuscript contains eight main incidents: G2, G15, G7, G19, G20, G12, G13 and G18. Three controls remain in the appendix. Quotation text is unchanged from source-checked definitions; twenty-five metadata labels distinguish complete fields from excerpts, with the exact transformation verified. Thirty-eight displayed cards contain forty checked original spans. Every motivating question is mapped to available evidence and constructs still unmeasured. The main bargaining table separates opening and later offers, and a second table compares counter content with non-completing exchanges. Appendix tables show static financing budgets for nine windows and exploratory cash-to-list-price ratios.

No games, engine continuations, synthetic evaluations or model evaluation calls were performed for this integration. The original outline, literature review, prior manuscripts, four independent drafts, canonical games, prompts and engine remain unchanged. No commit or push was made for this revision. The source date does not imply that the new integrated manuscript is part of the earlier public checkpoint.
