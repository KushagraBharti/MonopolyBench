# Handoff: Opus xhigh final whole-paper review

**Target:** `integrated/manuscript.pdf` (SHA-256 `f0312183…ed8a1`). The 78-entry pin matched before and after the review.

## Verdict

The integrated paper states a coherent, worthwhile and well-bounded result. The positive center holds:

- Fourteen of sixteen collateral-dependent debts are paid.
- In thirteen of those, the first text names the released collateral or gives a budget that includes it; one is tentative.
- Both failures leave that collateral out.

Every number I recomputed reproduces: bargaining tables, debt partition, necessity rows, refusals, tool choice and replay. Every incident continuation I traced matches the records.

No structural rewrite is warranted. About eleven sentences need correction.

## Corrections, in priority order (full text in `replacement_prose.tex`)

1. **OFR-01 (major), R1.** Say that the release dependency is the standard Monopoly rule and that liquidation states list no values. Successful texts apply familiar rules and board values to unlisted deeds; they do not discover a dependency.
2. **OFR-04 (moderate), R10.** G18: at the d431 renewal, Opus's returned text already says buying Pacific "might just prolong p1's survival". At d438 it rejects Sol's packages because paying "mainly just extends the game". The concern predates the deterioration. Do not claim insincerity.
3. **OFR-02 (moderate), R3.** In the introduction, the cash-bid "other direction" holds only when pooled. Within recipients the gaps run from −0.2 to +8.5.
4. **OFR-03 (moderate), R5.** Give the no-Grok block values (27.5, 45.5, 6.0, −23.5, 11.1) and their neither-cell sizes (10, 11, 8, 4, 3).
5. **OFR-05 (moderate), R2.** The provider-returned texts may be condensed: Opus returns 59–105 words against 220–429 reasoning tokens, and Gemini also returns an encrypted block.
6. **OFR-07 (moderate), R7–R8.** In G15 and G2, add each holder's earlier blocking policy before the third-party warning. This corrects my own OPX-10.
7. **Minor.**
   - OFR-06 / R4: the abstract's population wording, and "document" instead of "establish".
   - OFR-08 / R11: the conclusion's "sensitive to".
   - OFR-09 / R6: the G5 first reasoning block.
   - OFR-10 / R9: the G13 note wording and Opus's d251 solvency remark.
   - OFR-11: an optional related-work check.

New quotations are exact. Their offsets and field hashes are in `extracted_spans.json`. The integrator should add manifest-backed macros for them.

## Files

- `initial_position.md`
- `review.md`
- `findings.json`
- `replacement_prose.tex` and `build/replacement_prose.pdf`
- `verification.md`
- Scripts and their JSON outputs
- `pin_check_before.txt` and `pin_check_after.txt`

## Not done, and why

- No new evaluation of any kind.
- No edits outside this folder.
- No other final reviewer's folder opened.
- The integration's eight incidents and the user's no-new-evaluations rule are preserved.
- Human byline and venue remain for the project owner; I invented neither.
- The OFR-11 reference was not verified.

I am stopping here.
