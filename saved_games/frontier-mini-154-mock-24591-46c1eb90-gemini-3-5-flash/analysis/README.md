# Analysis Index

Run `mock-24591-46c1eb90` is a 154-turn bankruptcy-endpoint case study won by Gemini 3.5 Flash. Deterministic reports remain unchanged; the files below add downstream qualitative review.

## Manual review

- `reports/manual_review_report.md` — polished whole-game synthesis, integrity/claim boundary, mechanism findings, and limitations.
- `review/chronological_turn_review.md` — every turn index and every applied decision in blocks of no more than three turns.
- `review/player_dossiers.md` — longitudinal plans, portfolios, liquidity, relationships, adaptation, failures, and outcomes for all four players.
- `review/bankruptcy_windows.md` — every elimination window, causal lead-up, immediate legal survival analysis, and oracle limits.
- `review/negotiation_review.md` — canonical proposal/counter/accept/reject chains with terms, leverage, and externalities.
- `reports/case_studies.md` — detailed mechanism case studies with legal menus, economics, messages, effects, alternatives, and single-run caveats.

## Structured review artifacts

- `review/evidence_index.csv` — one resolved citation row per applied decision.
- `review/review_packet.jsonl` — joined visible state, legal menu, selected action, messages, emitted effects, attempts, usage, and source paths.
- `review/promise_lifecycle.csv` — reviewed commitments and lifecycle status.
- `review/communication_claims.csv` — evidence-linked factual/behavioral claim coding with conservative D/C labels.

## Deterministic artifacts

The existing `tables/`, `plots/`, `expanded_metrics/`, `quality/`, `coverage/`, and standard reports are the frozen deterministic analysis surface. `reports/analysis_report.md` remains the standardizer-produced overview; `reports/manual_review_report.md` is the qualitative Phase-14-style supplement.

All findings are single-run observations or reviewed cases. They are not model rankings or prevalence estimates. Private thoughts are model-reported rationale artifacts, not direct evidence of intent. Exact regret, trade surplus, and counterfactual bankruptcy claims require a declared oracle or branch runner.
