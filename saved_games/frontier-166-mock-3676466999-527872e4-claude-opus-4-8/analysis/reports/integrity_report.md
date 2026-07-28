# Integrity and Reconciliation Report: mock-3676466999-527872e4

## Outcome

- Overall quality gate: `pass_with_warnings`
- Canonical package: `saved_games/frontier-166-mock-3676466999-527872e4-claude-opus-4-8/run/`
- Quality-check package: `saved_games/frontier-166-mock-3676466999-527872e4-claude-opus-4-8/quality_check/`
- Source commit: ``
- Run inventory: `3208` files, `56428160` bytes, SHA-256 inventory `889feaee6327954b2b57ec43a9f2b9f2a4beed0ad997521ea5ac6e02618a3e9f`
- Quality-check inventory: `1004` files, `13079696` bytes, SHA-256 inventory `fcd58f014be861e237cf5d02fcbc8ca5a2e0e0f091e66dac7e39465a6f6d3e0d`

## Completeness

- Expected top-level run artifacts: `44`; present: `44`; missing: `0`; extra: `0`.
- Events: `3341` with contiguous sequence `0..3340`.
- Unique decisions/actions: `488/488`.
- Attempts: `502`; prompt artifact sets: `502`; quality-check request/response pairs: `502`.
- State snapshots: `656` total, including `167` canonical turn snapshots from `turn_0000.json` through `turn_0166.json`.
- All JSON/JSONL files parse. Summary and final snapshot agree on cash, bankruptcy flags, the sole survivor, and the bankruptcy endpoint.

Warning: `decisions.jsonl` contains two `decision_started` rows for `mock-3676466999-527872e4-dec-000030`. The later start timestamp matches its single resolution. The decision still has exactly one resolution, one action, and one reconciled usage-decision chain.

## Replay

- Fresh replay command exit code: `0`.
- Applied actions: `488`.
- State replay: `passed`; `1389` state-relevant events compared; hash `31cde82e2618be4a97d058a52defbe5811c35aa42fa3676ba6f73a8a7fda9062`.
- Artifact replay: `passed`; `3341` full-stream events compared; hash `1f2e66f7b91c9fe98d38121bf5e5d75a9ec9209d0a33c1231c0d2c5db1ac7853`.
- First mismatch: `null`; missing/extra actions: `0/0`; missing/extra events: `0/0`.

## Calls, Retries, and Cost

- Decision denominator: `488`.
- Attempt denominator: `502` (`488` initial + `14` corrective retries).
- First-pass valid: `474/488` (`97.131148%`).
- Invalid initial attempts: `14/502` attempts (`2.788845%`): `7` malformed and `7` illogical.
- Corrective recovery: `14/14` (`100%`).
- Fallbacks: `0/488` decisions.
- Missing usage: `0/502` attempts.
- Total input/output/reasoning/total tokens: `2251735` / `539118` / `454092` / `2790853`.
- Total actual OpenRouter cost: `$21.91408585`.
- Token semantics: every row satisfies `total = input + output`; reasoning tokens are a reported subset of output and are not added again.
- Raw embedded response usage matches all normalized attempt fields and aggregate totals exactly.

Observed provider attempts: `Anthropic` 88, `Google AI Studio` 119, `OpenAI` 214, `xAI` 81.

Warning: OpenRouter generation-endpoint enrichment did not resolve (`501` HTTP 404 responses and one error without a status code). This does not create usage missingness because the raw chat-completion response supplied complete usage and cost fields.

## Plot Quality Check

- Visually inspected `cost_by_turn.png`, `cost_per_call.png`, `cumulative_cost_by_call.png`, and `cost_by_model.png`.
- The first two were affected by the standardizer's whole-dollar formatter and showed repeated labels at sub-dollar scale.
- Regenerated only `cost_by_turn.png` from `analysis/tables/per_turn_usage_total.csv` and `cost_per_call.png` from `analysis/tables/per_call_usage.csv`, using two-decimal dollar ticks.
- `cumulative_cost_by_call.png` and `cost_by_model.png` were legible at their multi-dollar scales and were left unchanged.
- Shared standardizer code and raw evidence were not modified.

## Generated Outputs

- Standard tables: `26`.
- Standard plots: `23`.
- Expanded metrics: `{'players': 4, 'events': 3341, 'actions': 488, 'resolved_decisions': 488, 'trade_episodes': 107, 'auction_episodes': 1, 'mortgage_episodes': 29, 'cash_reason_rows': 55, 'trade_player_episode_rows': 214, 'auction_player_episode_rows': 4}`.
- Replay, completeness, reconciliation, source-hash, quality-flag, and verification-command records are under `analysis/quality/` and `analysis/manifests/`.
- The share zip is regenerated from the final `analysis/` folder after these records are written.

## Scope Boundary

This task performed deterministic integrity, replay, usage, cost, and metric processing only. It did not perform chronological whole-game review, bankruptcy-window analysis, negotiation review, deception/collusion labeling, promise adjudication, or case-study construction. Manual-review artifacts therefore remain explicitly absent/unreviewed.
