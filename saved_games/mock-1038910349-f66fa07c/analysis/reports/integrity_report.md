# Integrity and Reconciliation Report: mock-1038910349-f66fa07c

## Scope

Deterministic descriptive audit only. No chronological whole-game review, bankruptcy-window interpretation, negotiation review, deception/collusion labeling, or case-study construction was performed.

## Freeze and provenance

- Intake source commit: `e2623b39ebc054283197a1021a60910172f0279d`.
- Run evidence: `2425` files, `38488781` bytes, canonical POSIX-path tree SHA-256 `12d8808f309045fff61a15fdde6da9ad7090b82320b967f7e18869e6c78b8c93`; pre/post-move PowerShell digest `111acf898cecfc7a747d87890a72e64cb291563f745a4a091903565d655e5d8a`.
- Quality-check evidence: `742` files, `8044597` bytes, tree SHA-256 `9f7eea64df1ee3c3cbe3764d96fc66172bf7ac093908b78673b9da533096efb6` (identical under both path separator formats).
- Full per-file SHA-256 inventory: `analysis/manifests/source_artifact_hashes.json`.
- Run-time artifact checksums: `run/artifact_manifest.json`; all `41` declared-present entries match.
- Configuration: `run/run_config.json`, `run/experiment_manifest.json`, `run/players.json`, `run/seat_assignment.json`, and `run/pricing_snapshot.json`.

## Completeness

Overall status: **WARNING**.

- Standardizer top-level contract: `44/44` present; missing `0`; extra top-level artifacts `0`.
- Events: `2694`; actions: `364`; resolved decisions: `364`; call attempts: `371`.
- State snapshots: `528` total, `164` canonical end-of-turn snapshots covering turns `0..163`.
- Prompt artifacts: `1855` files (`371` complete five-file attempt sets).
- Quality-check artifacts: `742` files (`371` request/response pairs).
- Final snapshot agrees with summary for player cash and bankruptcy status; winner `Claude Opus 4.8`, endpoint `BANKRUPTCY`, turn `163`.

Warnings are metadata/shape gaps rather than missing canonical state/action evidence: no separate `responses/`, `run_manifest.json`, `provider_route_summary.csv`, raw `metric_definitions.json`, or `token_report.json`; no raw source-commit/ruleset hash. Substitutes and exact evidence paths are recorded in `analysis/quality/artifact_completeness.json`. Review labels are absent by design and qualitative review was prohibited.

## Replay

- Aggregate replay: **PASSED**, `2694` original and `2694` replayed events.
- State replay: **PASSED**, `1238` compared state-relevant events, zero mismatches.
- Artifact replay: **PASSED**, `2694` compared full-stream events, zero mismatches.
- Actions: `364`; missing actions `0`; extra actions `0`; decision-ID mismatch `false`.
- The existing reports and a separate read-only in-memory verifier both pass. Exact report payloads and command metadata are in `analysis/quality/replay_verification.json`.

## Call, retry, fallback, usage, and cost reconciliation

- Resolved decisions: `364`.
- Attempts: `371` = `364` initial + `7` corrective retries.
- Decisions needing retry: `7/364`; first-pass valid: `357/364` (98.0769%).
- Invalid attempts: `7/371` attempts.
- Fallbacks: `0/364` decisions.
- Missing usage: `0/371` attempts.
- OpenRouter actual cost: `$12.062756050000` across `371` attempts; discrepancy versus `usage.json` and `cost_report.json`: `$0.000000000000`.
- Tokens: input `1609023`, output `275129`, total `1884152`, reasoning `202283`, cached `39424`.

Reasoning tokens are preserved as a subset of completion/output tokens and are not double-counted into total tokens. Native per-call token fields are null, so aggregate native zeros mean “unreported,” not measured zero. Requested routes and fallback policy are in the run configuration; actual providers are recoverable from raw decision responses. Full model denominators, sums, rates, raw semantics, and unresolved metadata discrepancies are in `analysis/quality/call_reconciliation.json`.

## Deterministic generated outputs

- Standard tables, plots, reports, coverage inventory, manifest, and share zip under `analysis/` and the saved-game root.
- Expanded metrics in `analysis/expanded_metrics/`: 4 players, 2,694 events, 364 actions, 364 resolved decisions, 44 trade episodes, 4 auction episodes, 16 mortgage episodes, 64 cash-reason rows, 88 trade-player rows, and 16 auction-player rows.
- No semantic or oracle-gated metric was fabricated; their status remains explicit in `analysis/expanded_metrics/semantic_metric_status.json`.
- Visual inspection exposed a standardizer formatting bug: `money_formatter` rounds every dollar-axis tick to a whole dollar, producing duplicate labels for sub-dollar ranges. The four cost plots in this package were deterministically regenerated from the standard CSV tables with cent-level tick labels; shared analysis code was not changed.
