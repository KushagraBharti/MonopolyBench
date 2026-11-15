# Verification

Completed on 14 November 2026 for the independent Sol manuscript. Checks are restricted to existing-record arithmetic, source/quotation inspection, document compilation, and PDF rendering. No new evaluation was performed.

The document compiles with `bash build.sh`. It has **23 pages: seven two-column main pages, two reference pages, and fourteen appendix pages**. Main source text is approximately 4,600 whitespace-delimited words, excluding the abstract. Body type is declared 10 pt, with 0.8-inch letter-page margins and a 0.25-inch column gap. No font reduction or compressed-spacing workaround was used. The final PDF author metadata names Kushagra Bharti. The bibliography contains 24 cited primary works; there is no reference-count claim.

`tools/verify.py` rendered all 23 pages and checked all 29 nonempty focal authored-note, provider-reasoning, and assistant-content fields against normalized PDF text. Footer page numbers are excluded from matching across page breaks; exact Unicode is preserved in JSON. All fields match. No LaTeX warnings, undefined references/citations, overfull boxes, missing-character diagnostics, empty pages, or out-of-page text spans remain. All four final contact sheets were inspected, with enlarged inspection of the title page, the complete rubric table, and first full-channel page. The table continuation labels and orphan section/response headings found during layout review were fixed.

The final PDF SHA-256 is `38401dae8ea7adda7f807c5c4ba20931a68bf8fcedbb717130a29eda186ce8a6`. The machine-readable report is `qa/verification.json`; rendered pages and contact sheets are in `qa/`. Source integrity is frozen separately in `release_manifest.json` after completion of support files.

Saved-record checks:

- Direct recount: 50,918 events, 6,989 resolved decisions, 8,679 attempts.
- Every one of 188 entry records rejoined to original first prompts/responses; all resource bounds match the historical ledger.
- Payable partition confirmed as 62/53/16. Continued-financing source-proof premises confirmed as 108/12/9/2, with ownership/evenness and sufficient Q checked at every payable entry.
- Paid-episode arithmetic confirms $51,997 in obligations, 180 mortgages, 89 sales, 67 one-action and 61 multiaction payments.
- All 920 offer response labels rejoined to original applied actions; 113 accepts, 394 counters, 413 rejections; 918 legally acceptable opportunities.
- All 59 entries in the five retained quotation manifests match original file hashes, JSON fields, and specified spans. This checks more retained source quotations than are printed directly in the concise main text.
- All 84 protected historical manuscript files still match the prior final-manuscript manifest.
- Twenty historical artifact/state replay report pairs were read and retain passed status. Artifact reports exclude no event types and sum to 50,918 compared events. No replay was executed.
- Stored executable-audit results retain 56 upper-bound insufficiency certificates, three positive witnesses, and one restricted-menu impossibility result. None was rerun.
- Engine SHA-256 at both collection commits and the current read-only source agrees with `122edf5f16db0c4b8e0bd475ded73bf70a2b08065304d0517b8f8e2c98d63e0d`.

`qa/record_checks.json` and `qa/additional_record_checks.json` retain the arithmetic and source checks. Semantic rubrics, 61/74 reason labels, broad channel-conflict counts, exposure histories, and delivery findings have the inherited/direct distinctions in `evidence_map.md`. No human annotation, new model judge, strategic optimum, or controlled mechanism is supplied by this verification.

A fresh local build under `qa/self_contained_rebuild/` used only copied `manuscript.tex`, `references.bib`, `sections/*.tex`, and `build.sh`. It produced 23 pages with identical extracted text, without repository evidence or the original build directory. `qa/self_contained_build.json` records the result. This establishes a self-contained document build, not an anonymous external repository rebuild or public-release certification.

All work products are confined to this assigned directory. No benchmark source, prompt, saved game, other new author draft, or historical manuscript was edited. No subagent, commit, or push was used.
