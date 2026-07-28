# Integrity Report: mock-24591-46c1eb90

## Outcome

- Overall deterministic audit: **PASS WITH WARNINGS**
- Blocking integrity failures: **0**
- Standard top-level artifacts: **44/44 present**
- Raw run files frozen: **2598 files, 46718319 bytes**
- Quality-check files frozen: **802 files, 11088697 bytes**
- Artifact-manifest checks: **41 existing entries verified; 0 byte/hash mismatches**
- Planned-but-absent review artifacts in the original manifest: `reviews\review_labels.jsonl, reviews\review_summary.json`

## Replay

- Fresh state replay: **PASSED**
- Fresh artifact replay: **PASSED**
- Events: **2916 original / 2916 replayed**
- State-relevant compared events: **1332 / 1332**
- Actions applied: **396**
- State mismatches: **0**
- Artifact mismatches: **0**
- Missing/extra actions: **0 / 0**
- State canonical SHA-256: `48b670f105e07267b9dc09c7d561322a04f16bf47e97d1d3375e30b66609597f`
- Artifact canonical SHA-256: `7a0dc9c7cad51f475ee796882703ac337e277ffd92a983511351b3d16196dd46`

## Artifact Completeness

- Event rows: **2916**; sequence gaps/duplicates: **0 / 0**
- Decision log rows: **792** = 396 started + 396 resolved
- Applied action rows: **396**
- Call-attempt rows: **401** = 396 initial + 5 retries
- Prompt artifacts: **401 attempts × 5 files = 2005 files**
- Quality-check artifacts: **401 attempts × 2 files = 802 files**
- State snapshots: **551 total; 155 canonical turn snapshots**
- Final summary versus `run/state/turn_0154.json`: cash, bankruptcy, and winner checks pass.

## Model Calls, Retries, Fallbacks, And Cost

- Model-required decisions: **396**
- Call attempts: **401**
- Valid attempts: **396**
- Invalid attempts: **5**
- Retry attempts/decisions: **5 / 5**
- Fallback attempts/decisions: **0 / 0**
- Missing usage rows: **0**
- Input/output/reasoning/total tokens: **1563529 / 479932 / 381579 / 2043461**
- OpenRouter actual cost: **$4.65275495**
- Summary rounded cost: **$4.652755**
- Cost rounding difference: **$0.00000005**
- Reasoning semantics: reasoning tokens are a subset of output tokens and are not added to total again.

## Warnings And Unresolved Provenance

1. The raw run does not record its run-time repository commit. Intake and analysis use commit `e2623b39ebc054283197a1021a60910172f0279d`.
2. Responses are stored as 401 JSON files under `run/prompts/`; there is no separate `run/responses/` directory.
3. There is no `run_manifest.json`; configuration is distributed across the existing run/experiment/player/seat/artifact manifests.
4. Requested provider routes are recorded, and observed providers/models are recoverable from raw decision responses, but there is no `provider_route_summary.csv` or dedicated actual-provider field in call rows.
5. The max-token omission and medium reasoning effort are explicit; the temperature sent/omitted fact is not independently recorded.
6. Per-artifact embedded prompt/response hashes are absent; the freeze manifest supplies full-tree SHA-256 coverage.
7. The original artifact manifest intentionally lists `reviews/review_labels.jsonl` and `reviews/review_summary.json` as absent; no qualitative review was performed.

## Evidence

- `analysis/manifests/source_artifact_hashes.json`
- `analysis/quality/artifact_completeness.json`
- `analysis/quality/replay_verification.json`
- `analysis/quality/call_reconciliation.json`
- `analysis/quality/quality_flags.json`
- `run/artifact_manifest.json`
- `run/replay_report.json`
- `run/usage.json`
- `run/summary.json`

## Deterministic Tooling Defect

The shared standardizer rendered all four USD plots with whole-dollar tick labels. Sub-dollar call/turn plots collapsed to repeated `$0` labels, while cumulative/model plots repeated rounded values. The four PNGs were regenerated only from canonical CSV tables with two-decimal USD ticks. Shared code and raw run evidence were not modified.
