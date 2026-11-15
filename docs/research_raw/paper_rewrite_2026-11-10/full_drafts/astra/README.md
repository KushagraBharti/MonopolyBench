# Astra's independent complete manuscript

`manuscript.tex` and `manuscript.pdf` are the full independent rewrite. This is one of four competing complete coauthor drafts, not the final integrated paper. Every section was written by Astra before reading the new complete drafts by Sol, Opus or Fable 5.2.

The paper centers bargaining over rival development, executable finance, distress and creditor inheritance. It includes seven distinct contextual incidents, the complete offer-response table, response styles, construction access/resolution, liquidation, longitudinal observations, current literature, all research-question boundaries, and evidence appendices.

Build with TeX Live/LuaLaTeX:

```sh
bash build.sh
```

Optional regeneration/checks use Python with matplotlib, pymupdf and Pillow:

```sh
python build_figures.py
bash build.sh
python verify_document.py
```

The scripts use the shared `../../data/` retained datasets and the original repository files for quote-source checks. They do not run games or the engine. The PDF and LaTeX build itself do not need a model account or network.

Evidence checks are in `qa/verification.json` and `qa/ledger_checks.json`. Rendered-page inspection is recorded in `qa/render_review.md`. Scientific scope and checked-versus-inherited findings are in `evidence_map.md`. Figures, current literature and full-paper objections have separate notes.

The prior draft, original outline and canonical games remain unchanged. No new controlled evaluations, commits or pushes were made.
