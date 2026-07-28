# Analysis Index

Run: `mock-2413970733-53b199c1`  
Endpoint: 172 turns, bankruptcy, Gemini 3.1 Pro Preview winner.

This directory contains two complementary layers. The standardized deterministic layer preserves replay, accounting, tables, plots, and integrity checks. The qualitative layer adds a complete human review without altering canonical run, quality-check, or archived recovery evidence.

## Integrated qualitative reports

- [Manual qualitative review](reports/manual_review_report.md) — publication-oriented synthesis, chronological key moments, every-player assessment, negotiation/communication findings, bankruptcy mechanisms, limitations.
- [Mechanism-focused case studies](reports/case_studies.md) — seven deeply sourced cases with pre-state economics, legal menus, messages/rationales, effects, bounded alternatives, and research significance.

## Exhaustive review records

- [Chronological turn review](review/chronological_turn_review.md) — every playable turn 0–171 in blocks of at most three, all 613 decisions, canonical event chronology, snapshots, and block-specific synthesis.
- [Player dossiers](review/player_dossiers.md) — live-plan reconstruction and final assessment for all four players.
- [Bankruptcy windows](review/bankruptcy_windows.md) — five-before/five-after windows where structurally available, legal liquidation accounting, and avoidability classifications.
- [Negotiation review](review/negotiation_review.md) — every proposal, counter, acceptance, rejection, repetition, and material negotiation message across 133 episodes.
- [Evidence index](review/evidence_index.csv) — path/ID/sequence inventory for canonical evidence plus explicitly labeled pre-resume provenance.
- [Decision review packet](review/review_packet.jsonl) — one joined record per resolved decision: visible pre-state, legal menu, action, messages, rationale, effects, retries/fallbacks, usage/cost, and sources.
- [Promise lifecycle](review/promise_lifecycle.csv) — reviewed commitments from formation through fulfillment, breach, supersession, or game end.
- [Communication claims](review/communication_claims.csv) — evidence-linked D/C candidate review with confidence, caveats, and alternative explanations.
- [Qualitative validation record](quality/qualitative_review_validation.json) — machine-readable coverage, reconciliation, citation, provenance, replay, and archive-contract checks.

## Deterministic and integrity reports

- [Standardized analysis report](reports/analysis_report.md)
- [Integrity and replay report](reports/integrity_report.md)
- [Coverage report](reports/coverage_report.md)
- [Data dictionary](reports/data_dictionary.md)
- [Expanded metrics report](expanded_metrics/expanded_metrics_report.md)

Deterministic tables are under `tables/` and `expanded_metrics/`; plots are under `plots/`; replay/completeness records are under `quality/`; source and analysis manifests are under `manifests/`.

## Provenance boundary

`run/` is canonical. `archive/evidence/mock-2413970733-53b199c1-pre-resume/` is supporting recovery evidence only. The duplicated `decision_started` marker for `...dec-000242` at the resume boundary is not a duplicated resolution or action. Source hash manifests may describe original CRLF bytes while repository blobs are LF-normalized; that provenance distinction is not treated as semantic or replay failure.
