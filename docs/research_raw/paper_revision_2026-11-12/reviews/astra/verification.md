# Astra review verification

- Read all four manuscript roots and active main/appendix sections, including the sixteen first-decision fields and peer handoffs/evidence maps. All four independent papers were frozen before this comparison.
- Earlier in this review, inspected all seventeen Astra PDF pages as contact sheets and full-size finance/bargaining/conduct pages. Did not rebuild frozen peer PDFs.
- New `check_cross_review.py` reads all twenty original `decisions.jsonl` files. It joins first resolved actions to the 188 debt ledger rows, reproduces 50/56 and 3/131, checks no first-action fallbacks, recounts recovery-note provenance and the narrow content-name mismatch screen, and preserves G15 d168–175.
- Read the Fable numerical-check implementation and all sixteen `b6_readings.json` rows. The two incorrect maximum claims are marked equal to an incomplete subtotal; this is why the 14/15 scalar agreement is not used as a semantic accuracy rate.
- Read all displayed main offer counts and both exact-block-resampling implementations. Astra and Sol reproduce the same 3,125-draw intact-block distributions. Opus's two-stage algorithm is a different target, not a numerical contradiction.
- All 234 entries in `four_draft_manifest.json` passed after the checks.
- No engine, replay, synthetic test, baseline, rollout, provider call or new game was run. All new writes are in `reviews/astra/`.
- Historical payment witnesses, menu search, semantic labels and replay executions are inherited evidence. This review adds no human validation or independent empirical sample.
