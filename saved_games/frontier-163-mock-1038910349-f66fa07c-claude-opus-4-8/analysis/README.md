# Analysis Index

Run: `mock-1038910349-f66fa07c`  
Endpoint: Claude Opus 4.8 wins by bankruptcy; last player decision turn 162, terminal marker turn 163.

## Manual qualitative review

- [`reports/manual_review_report.md`](reports/manual_review_report.md) — integrated Phase-14 whole-game report.
- [`reports/case_studies.md`](reports/case_studies.md) — eight detailed mechanism-focused cases.
- [`review/chronological_turn_review.md`](review/chronological_turn_review.md) — every canonical turn index 0–163 in blocks of at most three, plus decision/retry/cost ledger.
- [`review/player_dossiers.md`](review/player_dossiers.md) — longitudinal dossiers for all four players.
- [`review/bankruptcy_windows.md`](review/bankruptcy_windows.md) — all three eliminations with legal-menu proof and five-decision windows where the endpoint permits.
- [`review/negotiation_review.md`](review/negotiation_review.md) — all 44 trade episodes, accepted chains, promise review, and D/C candidates.
- [`review/evidence_index.csv`](review/evidence_index.csv) — provenance-rich index of material findings.
- [`review/decision_coverage.csv`](review/decision_coverage.csv) — complete 364-decision visible-state/menu/action/message/event/usage join.
- [`review/review_packet.jsonl`](review/review_packet.jsonl) — evidence packets for accepted trades, bankruptcies, key moments, and D2+/C2+ candidates.
- [`review/communication_claims.csv`](review/communication_claims.csv) — candidate-level communication records; adjudication remains empty.
- [`review/promise_lifecycle.csv`](review/promise_lifecycle.csv) — three narrow, fulfilled episode commitments.

## Deterministic preparation

- [`reports/integrity_report.md`](reports/integrity_report.md) — replay, completeness, usage, cost, and source-freeze reconciliation.
- [`reports/analysis_report.md`](reports/analysis_report.md) — deterministic descriptive summary.
- [`reports/coverage_report.md`](reports/coverage_report.md) and [`coverage/`](coverage/) — artifact inventory.
- [`tables/`](tables/) — standardized event, decision, state, property, cost, and usage tables.
- [`expanded_metrics/`](expanded_metrics/) — trade, auction, mortgage, cash, decision, and player episode metrics.
- [`plots/`](plots/) — deterministic state/economy/usage visualizations.
- [`quality/`](quality/) and [`manifests/`](manifests/) — machine-readable integrity and provenance outputs.

## Claim status

Canonical facts trace to `run/events.jsonl`, `run/actions.jsonl`, `run/decisions.jsonl`, prompt/quality-check artifacts, and snapshots in that order. Private thoughts are model-reported artifacts. No branch oracle or external judge was called. D2+/C2+ labels are single-reviewer candidates, not adjudicated facts. This package supports one-run case analysis only, not prevalence or cross-model ranking claims.
