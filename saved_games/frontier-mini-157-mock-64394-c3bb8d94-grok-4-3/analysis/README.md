# Analysis package

Run `mock-64394-c3bb8d94` is a 157-turn bankruptcy game won by Grok 4.3. This directory contains deterministic quantitative outputs and an exhaustive manual qualitative review. Canonical evidence remains under `../run/` and `../quality_check/`; the review does not modify those artifacts.

## Qualitative review

- `review/chronological_turn_review.md` — every turn 0–157 in blocks of at most three turns, plus complete action, decision, attempt, and snapshot reconciliation.
- `review/player_dossiers.md` — evolving dossiers for all four players.
- `review/bankruptcy_windows.md` — GPT, Claude, and Gemini bankruptcy windows with legal-menu adjudication.
- `review/negotiation_review.md` — all 44 trade episodes (7 accepted, 37 rejected).
- `review/evidence_index.csv` — structured finding-to-source map.
- `review/review_packet.jsonl` — machine-readable mechanism packets with fact/reasoning/interpretation/uncertainty separation.
- `review/promise_lifecycle.csv` — lifecycle of finality, blocker, capability, and survival claims.
- `review/communication_claims.csv` — claim-level canonical adjudication and high-bar deception review.
- `reports/case_studies.md` — eight detailed mechanism case studies.
- `reports/manual_review_report.md` — substantial synthesis of acquisition, negotiation, reliability, development, bankruptcy, and labeling evidence.

## Deterministic quantitative outputs

- `tables/` — standardized event, action, state, usage, cost, and aggregate tables.
- `expanded_metrics/` — episode, liquidity, bankruptcy, negotiation, and replay-derived metrics.
- `plots/` — standard visualizations, including four cost plots reviewed for cent-level readability.
- `reports/analysis_report.md` — generated quantitative overview.
- `reports/coverage_report.md` — generated artifact coverage summary.
- `reports/integrity_report.md` — generated integrity summary.
- `reports/verification_log.md` — exact prior deterministic verification commands and results.
- `manifest/` — source and generated artifact hashes, tool/config provenance, and package manifests.
- `tools/` — package-local deterministic verification and plot-regeneration helpers.

## Interpretation rules

Canonical facts come from events/actions/decisions/snapshots. Model text is reported reasoning, not automatically fact. Reviewer interpretation is labeled separately, and unsupported counterfactual value claims are avoided. “Avoidable bankruptcy” means the immediate legal menu contained a solvent sequence; “forced” means the terminal legal menu did not. No deception or collusion label is assigned without evidence of material falsity, contrary knowledge, strategic benefit, and no better non-deceptive explanation.

This is one run. The outputs support mechanism analysis and exact evidence retrieval, not prevalence estimates, rankings, or population-level claims.
