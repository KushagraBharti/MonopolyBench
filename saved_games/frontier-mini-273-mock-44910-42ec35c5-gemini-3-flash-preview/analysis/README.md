# Saved-game analysis

This folder contains the completed deterministic and exhaustive qualitative
analysis of legacy run `mock-44910-42ec35c5`. The frozen source commit recorded
by the package is `fa773791718e3b5d8ff18448e2ad3fa42b375259`.
Canonical evidence remains in `../run/` and `../quality_check/`; both directories
are read-only inputs and retain their frozen byte trees.

## Authoritative domains and deterministic facts

- Playable turns are zero-based `0..272` (273 turns). Turn index 273 is a
  terminal-only `GAME_ENDED` marker and has no decision/action.
- State replay passes 1,942/1,942 state-relevant events.
- Full artifact replay passes 4,102/4,102 events.
- There are 540 resolved decisions/actions, 549 attempts, 9 retry decisions,
  9 invalid attempts, zero fallbacks, and zero attempts missing provider usage.
- Attempt cost sums exactly to Decimal `4.24475240`; aggregate JSON renders
  `4.244752400000001`, a documented `1E-15` floating-point serialization delta.
- Frozen source trees are `run/`
  `25524577aa9ec7754151d9997627cec1280bf0255293085d59670bb617477f50`
  and `quality_check/`
  `ff2e7c006d723b85936e530b13b779b55922a3082fd32ac97ccf32457e6663d1`.

## Qualitative outputs

The review uses 91 contiguous blocks of exactly three turns, with all 540
resolved decisions covered exactly once. Start with:

- `review/chronological_turn_review.md` for the complete chronology.
- `review/decision_coverage.csv`, `review/evidence_index.csv`, and
  `review/review_packet.jsonl` for machine-readable joins.
- `review/player_dossiers.md`, `review/bankruptcy_windows.md`, and
  `review/negotiation_review.md` for focused interpretation.
- `review/communication_claims.csv` and `review/promise_lifecycle.csv` for
  bounded communication labels.
- `reports/manual_review_report.md` and `reports/case_studies.md` for synthesis.

Deterministic tables are indexes, not substitutes for raw evidence. All labels are
downstream: public/private divergence alone is not deception, mutual exchange
alone is not collusion, and counterfactuals are bounded by the legal actions
actually offered.

## Validation

From this saved-game directory run:

```powershell
python analysis/tools/validate_package.py
python analysis/tools/validate_qualitative_review.py
```

The qualitative validator checks turn continuity, decision/action bijection,
attempt and retry reconciliation, the three bankruptcy windows, citation
resolution, case-study fields, parseability, PNG integrity, frozen source trees,
generated manifests, deterministic replay facts, and exact ZIP parity.
Historical analysis and prior ZIPs remain under
`../../archive/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/`.
