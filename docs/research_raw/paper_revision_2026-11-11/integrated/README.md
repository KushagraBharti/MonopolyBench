# Integrated scientific revision

Open [manuscript.pdf](manuscript.pdf). Native source: [manuscript.tex](manuscript.tex).

This is the integrated revision after four independent whole-paper drafts. Astra, Opus and Fable 5.2's all-four cross-reviews have been incorporated. Sol's current whole-paper cross-review remains pending. This is not final approval or a claim of conference readiness.

The paper centers on how the completion contrast differs between swaps and cash bids, how cash conditions bargaining, and how agents execute financing across changing legal options. It contains eight contextual incidents, including successful correction and payment, three figures, and a complete research-question coverage table. Detailed response conditions and historical audit information are retained in appendices.

## Rebuild

Requirements: Python with matplotlib; LuaLaTeX and latexmk. Verification additionally uses PyMuPDF and Pillow. Run from this directory:

```sh
bash build.sh
python3 tools/verify_document.py
python3 tools/check_unlocked_collateral.py
python3 tools/check_offer_forms.py
```

Set `PAPER_PYTHON` to select a Python environment. The local build used `/tmp/monopoly-astra-rewrite-venv/bin/python`. The original repository records must be present for quotation and source verification. Building figures and tables reads owned data copies, while four newly selected quotation fields are verified against their original records. No command here runs the engine, a game, a model evaluation or a new counterfactual trajectory.

## Verification of this revision

- 24 pages; 19 displayed quotation cards in eight incidents.
- No overfull boxes, missing glyphs, unresolved references/citations or LaTeX warnings.
- All displayed quotations match original field spans and occur in extracted PDF text.
- No out-of-page text, PDF Launch actions or blank pages.
- 666 protected-file hashes checked, including the four frozen drafts and earlier preserved sources.
- All 24 pages inspected in contact sheets; the new main table, bargaining figure and payment transcript also inspected at full-page size.
- The offer-form split, cash strata and concession subset are recomputed by `tools/build_integration.py`.
- `tools/check_offer_forms.py` independently reproduces the split, conflict-exclusion sensitivity, changed cash terms in fourteen histories, mortgage-status comparison and G20 payment from the earlier ledger and original records.
- All nineteen newly unlocked-collateral episodes and 33 mortgage actions are checked directly against original first/current menus and applied actions by `tools/check_unlocked_collateral.py`.

See `qa/verification.json`, `data/integration_checks.json`, `qa/unlocked_collateral_check.json`, `qa/fable_cross_review_reproduction.json`, `evidence_map.md`, and `integration_decisions.md`. Historical legal-payment witnesses and previous engine replays are inherited evidence, not new executions.

No canonical artifact, prompt, engine, old outline or frozen independent draft was changed. No commit, push or publication was made.
