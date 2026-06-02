# Implementation Status

## Current Phase

Active goal: complete the Long-Horizon Economic Agency in Monopoly and Targeted
Scenario Suite / Micro-Decisions research tracks from the current `plan.md`.

Current focus: complete. The Long-Horizon Economic Agency in Monopoly and Targeted
Scenario Suite / Micro-Decisions research tracks from `plan.md` are implemented,
tested, documented, and usable for research runs. Remaining work is limited to
external research execution inputs such as paid/publication OpenRouter campaign runs
and real human expert label collection.

## Active Goal Progress: Long-Horizon And Micro-Decision Research Tracks

### Completed In Current Goal

- Archived the previous common-infrastructure goal prompt at
  `archives/plan_common_benchmark_infrastructure_2026-06-02.md`.
- Replaced `plan.md` with the current goal prompt focused on:
  - Long-Horizon Economic Agency in Monopoly.
  - Targeted Scenario Suite / Micro-Decisions.
- Preserved the strict no-prompt-change rule. No prompt construction, prompt content,
  retry wording, OpenRouter tool schemas, message roles, or model-facing payloads have
  been intentionally changed in this goal.
- Added first-pass `monopoly-long-v1` research registry contracts:
  - `contracts/schemas/research_registry.schema.json`
  - `contracts/ts/research.ts`
  - `contracts/examples/research_seed_registry.example.json`
  - `contracts/examples/research_model_roster.example.json`
  - `contracts/examples/long_campaign_config.example.json`
- Added versioned fixed seed cohorts:
  - `contracts/research/monopoly_long_v1_seed_registry.json`
  - `smoke`
  - `easy`
  - `normal`
  - `volatile`
  - `auction_heavy`
  - `trade_heavy`
  - `liquidation_heavy`
  - `publication`
- Added versioned model/baseline roster registry:
  - `contracts/research/monopoly_long_v1_model_rosters.json`
  - `smoke`
  - `frontier`
  - `cost_controlled`
  - `baseline_mix`
  - `baseline_field`
- Added first smoke campaign config:
  - `campaigns/monopoly-long-v1-smoke.json`
- Added Python registry loaders and semantic validators:
  - `python/packages/arena/src/monopoly_arena/research_registry.py`
  - validates JSON schema,
  - enforces `prompt_pipeline.status = "unchanged"`,
  - detects duplicate seeds,
  - verifies cohort/roster key consistency,
  - verifies roster actor references,
  - rejects disabled roster actors by default.
- Added campaign matrix planner and execution adapter:
  - `python/packages/arena/src/monopoly_arena/long_campaign.py`
  - expands fixed seeds, repetitions, and seat permutations into deterministic planned
    run rows,
  - supports `configured_order`, `latin_square`, `full`, and `seeded_random`,
  - records stable run ids and resume keys,
  - distinguishes repeated actor ids by roster slot,
  - includes `baseline_strategies` maps for baseline rows,
  - executes runnable cells through `LlmRunner`,
  - resumes only completed cells and refuses to append to incomplete run directories,
  - writes deterministic campaign artifacts under `runs/campaigns/<campaign_id>/`,
  - preserves prompts by leaving all model-facing construction in the existing runner.
- Added deterministic baseline actor selector:
  - `python/packages/arena/src/monopoly_arena/baselines.py`
  - `random_legal`
  - `always_buy`
  - `cash_conservative`
  - `no_trade`
  - `builder`
  - `auction_aggressive`
- Added optional `LlmRunner(..., baseline_strategies={player_id: baseline_id})`
  support so baseline players choose legal structured actions without prompt
  construction, prompt artifacts, or OpenRouter calls.
- Added campaign-level long-horizon reports:
  - `results.jsonl`
  - `results.csv`
  - `run_results.json`
  - `leaderboard.json`
  - `leaderboard.csv`
  - `statistics.json`
  - `baseline_comparison.json`
  - `paper_report.md`
  - `execution_result.json`
- Added campaign statistics for final net worth, rank, win rate, seat effects, seed
  effects, deterministic bootstrap confidence intervals, usage/cost summaries, replay
  verification aggregates, and failure-taxonomy aggregates.
- Added long-horizon campaign artifact API/frontend inspection:
  - `GET /campaigns`
  - `GET /campaigns/{campaign_id}`
  - `GET /campaigns/{campaign_id}/artifacts`
  - `GET /campaigns/{campaign_id}/artifacts/{artifact_name}`
  - `/research`
  - `/research/campaigns/<campaign_id>`
- Added focused docs:
  - `docs/long_horizon_campaigns.md`
- Extended contract validation to include:
  - research registry examples,
  - actual long-horizon seed registry,
  - actual long-horizon model roster registry,
  - actual smoke campaign config.
- Added focused tests:
  - `python/packages/arena/tests/test_research_campaign.py`
- Generated the smoke campaign locally with:
  - `uv run python -m monopoly_arena.long_campaign --config campaigns/monopoly-long-v1-smoke.json --runs-dir runs`
  - output under ignored `runs/campaigns/monopoly-long-v1-smoke/`
- Added micro research overlay contract:
  - `contracts/schemas/micro_research.schema.json`
  - `contracts/examples/micro_expert_label_task.example.json`
  - `contracts/examples/micro_expert_label.example.json`
- Added research-only micro suite overlays:
  - `contracts/micro/research_suites/bias-v1.json`
  - `contracts/micro/research_suites/safety-v1.json`
  - `contracts/micro/research_suites/counterfactual-v1.json`
  - `contracts/micro/research_suites/campaign-v1.json`
- Added counterfactual pair registry:
  - `contracts/micro/counterfactual_pairs/counterfactual-v1.json`
- Added targeted campaign registry:
  - `contracts/micro/campaigns/campaign-v1.json`
- Added shared TypeScript contracts for micro research suites, counterfactual pairs,
  campaign definitions, expert label tasks, and expert labels in:
  - `contracts/ts/micro.ts`
- Added Python micro research loaders, validators, static report builder, and human
  review queue generation:
  - `python/packages/microbench/src/monopoly_microbench/research.py`
- Added microbench CLI support:
  - `uv run python -m monopoly_microbench.cli research-report --suite safety-v1 --runs-dir ../runs`
- Added microbench research report joins for existing batch results:
  - scenario/category joined score summaries,
  - counterfactual pair deltas and stability bands,
  - fixture-sequence campaign step coverage and sequence scores,
  - safety report candidate metrics separated from human-reviewed labels.
- Added human expert label import/export infrastructure:
  - `expert_labels.jsonl`
  - `label_summary.json`
  - `uv run python -m monopoly_microbench.cli review-queue --suite safety-v1 --out <path>`
  - `uv run python -m monopoly_microbench.cli validate-labels --labels <path>`
  - labels must validate as `human_review_only: true` and reject LLM label sources.
- Added micro research report artifact API/frontend inspection:
  - `GET /micro/research-reports`
  - `GET /micro/research-reports/{report_id}`
  - `GET /micro/research-reports/{report_id}/artifacts`
  - `GET /micro/research-reports/{report_id}/artifacts/{artifact_name}`
  - `/research`
  - `/research/micro/<report_id>`
- Added focused docs:
  - `docs/micro_research_suites.md`
- Added focused tests for:
  - research suite validation,
  - safety human-review-only queues,
  - counterfactual and campaign references,
  - static report artifact generation.
- Generated a static safety research report locally under ignored
  `runs/micro_batches/micro-research-safety-v1/`.

### In Progress In Current Goal

- None.

### Remaining In Current Goal

- No implementation work remains from `plan.md`.
- `monopoly-long-v1` is executable for repeated campaign runs, but no paid/publication
  LLM publication campaign has been run in this goal because that consumes OpenRouter
  budget and requires a final model roster/budget decision.
- Real human expert labels were not fabricated. The expert-label schema, queue,
  validation, import/export, report joins, and UI artifact inspection exist; actual
  subjective label collection remains an external research operation.
- Multi-turn micro campaigns are implemented as validated fixture-sequence campaign
  reports, which the plan allowed when engine stateful transitions were not available.
  A live stateful micro-campaign runner can be a later extension if the research design
  needs engine-applied transitions between steps.

### Current Goal Blockers

- None for implementation.
- External research inputs still needed for publication-grade results:
  - OpenRouter budget/model approval for large paid campaign runs,
  - real human reviewers for subjective safety/deception labels.

### Current Goal Verification

Passed in the current goal:

- `node contracts/validate-contracts.mjs`
- `uv run pytest packages/arena/tests/test_research_campaign.py -q`
- `uv run pytest packages/arena/tests/test_research_campaign.py -q` after adding
  campaign execution/report artifacts.
- `uv run pytest packages/arena/tests/test_baselines.py -q`
- `uv run pytest packages/arena/tests/test_baselines.py packages/arena/tests/test_research_campaign.py -q`
- `uv run ruff check packages/arena/src/monopoly_arena/research_registry.py packages/arena/src/monopoly_arena/long_campaign.py packages/arena/tests/test_research_campaign.py`
- `uv run ruff check packages/arena/src/monopoly_arena/baselines.py packages/arena/src/monopoly_arena/llm_runner.py packages/arena/tests/test_baselines.py`
- `uv run ruff check packages/arena/src/monopoly_arena/baselines.py packages/arena/src/monopoly_arena/llm_runner.py packages/arena/src/monopoly_arena/long_campaign.py packages/arena/src/monopoly_arena/research_registry.py packages/arena/tests/test_baselines.py packages/arena/tests/test_research_campaign.py`
- `uv run mypy packages/arena/src/monopoly_arena/baselines.py packages/arena/src/monopoly_arena/long_campaign.py packages/arena/src/monopoly_arena/research_registry.py packages/microbench/src/monopoly_microbench/research.py`
- `uv run python -m monopoly_arena.long_campaign --config campaigns/monopoly-long-v1-smoke.json --runs-dir runs`
- `uv run pytest packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_catalog_validates_bias_safety_counterfactual_and_campaign_overlays packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_human_review_queue_is_human_review_only packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_counterfactual_and_campaign_references_are_first_class packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_static_report_writes_paper_facing_artifacts -q`
- `uv run ruff check packages/microbench/src/monopoly_microbench/research.py packages/microbench/src/monopoly_microbench/cli.py packages/microbench/src/monopoly_microbench/__init__.py packages/microbench/src/monopoly_microbench/paths.py packages/microbench/tests/test_catalog_scorer_runner.py`
- `uv run pytest packages/microbench/tests/test_catalog_scorer_runner.py -q` after
  adding result joins and human-label import/export (`20 passed`; pytest cache warning only).
- `uv run ruff check packages/microbench/src/monopoly_microbench/research.py packages/microbench/src/monopoly_microbench/cli.py packages/microbench/src/monopoly_microbench/__init__.py packages/microbench/tests/test_catalog_scorer_runner.py`
- `uv run mypy packages/microbench/src/monopoly_microbench/research.py`
- `uv run pytest apps/api/tests/test_artifact_review_endpoints.py -q` after adding
  campaign and micro research artifact endpoints.
- `uv run ruff check apps/api/src/monopoly_api/main.py apps/api/src/monopoly_api/run_manager.py apps/api/tests/test_artifact_review_endpoints.py`
- `bun run build` after adding `/research` frontend artifact inspection.
- `uv run python -m monopoly_microbench.cli research-report --suite safety-v1 --runs-dir ../runs`
- `pwsh -File scripts/verify.ps1` (`All checks passed.`)
- Browser verification for `/research` on a local Vite dev server at
  `http://127.0.0.1:5174/research` with no console errors.

The focused micro research pytest run emitted a pytest cache permission warning under
`python/packages/microbench/.pytest_cache`, but the tests passed.

## Completed

- Read `AGENTS.md`, `plan.md`, and current implementation before editing.
- Preserved the strict no-prompt-change rule. No prompt construction, prompt content, retry wording, OpenRouter tool schemas, message roles, or model-facing payloads have been intentionally changed.
- Added run-level artifact foundations:
  - `run_config.json`
  - `players.json`
  - `seat_assignment.json`
  - `artifact_manifest.json`
- Added run-level scorecard artifacts:
  - `scorecard.json`
  - `scorecard_players.json`
  - `scorecard_decisions.jsonl`
  - `scorecard_events.jsonl`
- Added run-level OpenRouter usage/cost artifacts from actual response data only:
  - `usage.json`
  - `usage_decisions.jsonl`
  - `usage_attempts.jsonl`
  - `cost_report.json`
- Added run-level deterministic replay verification artifacts:
  - `replay_report.json`
  - `replay_steps.jsonl`
  - `replay_flags.jsonl`
  - `replay_navigation.json`
- Added first-pass trace/failure/review artifacts:
  - `trace_findings.jsonl`
  - `trace_summary.json`
  - `failure_findings.jsonl`
  - `failure_summary.json`
  - `review_queue.jsonl`
- Added versioned failure taxonomy:
  - `contracts/taxonomy/failure_taxonomy.json`
- Added read-only OpenRouter metadata helpers for:
  - models/pricing snapshot lookup,
  - credits lookup,
  - generation lookup.
- Added batch artifact directory layout under `runs/batches/<batch_id>/`.
- Batch configs now normalize and persist `max_turns`; batch run ids include `max_turns` so deterministic progression settings are part of the run identity.
- Added deterministic batch seat permutation support:
  - `latin_square`
  - `full`
  - `seeded_random`
  - `configured_order`
- Added batch-level artifacts:
  - `batch_config.json`
  - `batch_manifest.json`
  - `model_config.json`
  - `model_pricing_snapshot.json`
  - `seed_manifest.json`
  - `seat_manifest.json`
  - `run_index.json`
  - `run_index.jsonl`
  - `results.jsonl`
  - `leaderboard.json`
  - `scorecard_summary.json`
  - `category_breakdown.json`
  - `statistical_summary.json`
  - `replay_report.json`
  - `trace_summary.json`
  - `failure_summary.json`
  - `cost_report.json`
  - `token_report.json`
  - `budget_report.json`
  - `review_queue.jsonl`
  - `artifact_manifest.json`
- Added batch-level model cards under `runs/batches/<batch_id>/model_cards/`:
  - `<safe_model_id>.json`
  - `<safe_model_id>.md`
- Model cards are derived from batch/run artifacts and markdown cards link to replay/review artifacts instead of quoting private-thought excerpts.
- Added run-level review label persistence:
  - `reviews/review_labels.jsonl`
  - `reviews/review_summary.json`
- Added full-game API endpoints for stored artifacts and human review:
  - `GET /runs/{run_id}/artifacts`
  - `GET /runs/{run_id}/artifacts/{artifact_name}`
  - `GET /runs/{run_id}/review/queue`
  - `GET /runs/{run_id}/review/labels`
  - `POST /runs/{run_id}/review/labels`
  - `GET /runs/{run_id}/review/summary`
- Added batch API endpoints for stored batch artifacts and model cards:
  - `GET /batches`
  - `GET /batches/{batch_id}`
  - `GET /batches/{batch_id}/artifacts`
  - `GET /batches/{batch_id}/artifacts/{artifact_name}`
  - `GET /batches/{batch_id}/model_cards/{card_id}`
- Added stored snapshot API endpoints for replay board rendering:
  - `GET /runs/{run_id}/snapshots`
  - `GET /runs/{run_id}/snapshots/{snapshot_name}`
- Added frontend artifact client helpers for run artifacts, replay artifacts, review labels, batch artifacts, snapshots, and model cards.
- Added first-pass replay/review UI:
  - `/runs/{run_id}/replay`
  - `/runs/{run_id}/review`
  - board rendered from stored snapshots,
  - event timeline,
  - skip modes for important, trace, failures, trades, auctions, bankruptcies, and model events,
  - trace/failure finding lists,
  - decision artifact inspector,
  - human review label form.
- Added first-pass batch dashboard UI:
  - `/batches`
  - `/batches/{batch_id}`
  - leaderboard table,
  - cost/token/replay/failure/trace summaries,
  - artifact inventory,
  - model-card JSON/Markdown viewer.
- Updated `batches/batch.example.json` with the decided batch defaults:
  - `$50` budget,
  - concurrency `1`,
  - `latin_square` seat permutation,
  - `max_turns` `200`,
  - resume enabled,
  - replay/scorecard/trace/failure enabled.
- Updated `README.md` with first-pass documentation for:
  - full-game run artifacts,
  - full-game batch artifacts,
  - deterministic seat permutations,
  - replay verification,
  - OpenRouter usage/cost accounting,
  - failure taxonomy and trace analysis,
  - human review workflow,
  - artifact API endpoints,
  - the strict no-prompt-change constraint.
- Added research-only metadata schema support for micro scenarios:
  - `research_metadata.schema_version = "micro_research_metadata_v1"`
  - `research_metadata.visibility = "research_only_never_prompt"`
  - review status/priority,
  - target capability and target behavior,
  - strategic tension,
  - expected failure modes,
  - taxonomy tags,
  - optional counterfactual pair metadata,
  - paper section,
  - researcher notes,
  - source claims and URLs,
  - prompt immutability marker.
- Added first-pass research metadata to all 130 `micro-v1` scenarios without changing any `decision_point` payload. A before/after SHA-256 check over every `decision_point` reported zero mismatches.
- Added micro scenario summary exposure for `research_metadata` so API/UI can filter/display research-facing annotations without touching model-facing prompt payloads.
- Added micro UI metadata surfacing:
  - scenario search includes target capabilities and expected failure modes,
  - scenario cards show target capability,
  - detail brief shows target capability, review priority, and explicit `research_only_never_prompt` visibility.
- Added tests proving:
  - every micro scenario has complete research-only metadata,
  - mutating `research_metadata` does not change `system_prompt`, `user_payload`, `user_content`, or `messages`.
- Added consolidated benchmark artifact schemas and examples:
  - `contracts/schemas/benchmark_artifact.schema.json`
  - `contracts/examples/artifact_manifest.example.json`
  - `contracts/examples/batch_config.example.json`
  - `contracts/examples/model_card.example.json`
  - `contracts/examples/replay_step.example.json`
  - `contracts/examples/review_label.example.json`
  - `contracts/examples/trace_finding.example.json`
- Added shared TypeScript artifact contracts in `contracts/ts/artifacts.ts` and updated the frontend artifact client to consume those shared types.
- Added tests for batch resume and `continue_on_failure` behavior.
- Added budget preflight using known historical OpenRouter actuals only:
  - uses the maximum observed prior run cost as the next-run estimate,
  - stops before starting another run if remaining budget cannot cover that estimate,
  - records unavailable preflight status instead of guessing when no prior actual cost exists.
- Added OpenRouter generation endpoint usage backfill:
  - queries `get_generation(generation_id)` when chat response accounting is incomplete and the client supports it,
  - backfills official prompt/completion/native/reasoning/cached token and cost fields into post-hoc artifacts,
  - records accounting source per attempt,
  - does not change prompt requests, tools, retry behavior, or model-facing payloads.
- Updated README schema/versioning notes, batch defaults, and micro metadata documentation.

## In Progress

- None.

## Remaining

- None for the common infrastructure goal. Additional UI polish, richer charts, and future prompt/guardrail condition work are deliberately outside this goal unless explicitly approved later.

## Blockers

- None currently.

## Verification

Final full-suite pass:

- `pwsh -File scripts/verify.ps1`
  - contracts validated,
  - Python ruff passed,
  - Python mypy passed,
  - engine tests passed (`51 passed`),
  - API tests passed (`69 passed`),
  - arena tests passed (`10 passed`),
  - telemetry tests passed (`7 passed`),
  - frontend lint passed,
  - frontend production build passed.

Previously passed before the current batch edits:

- `uv run pytest packages/telemetry/tests -q`
- `uv run pytest apps/api/tests/test_replay_runner.py::test_replay_matches_event_stream_with_trade apps/api/tests/test_llm_runner.py::test_static_run_artifacts_are_written_without_system_prompt_text apps/api/tests/test_batch_runner.py::test_batch_runner_writes_index_and_summaries -q`
- `uv run ruff check packages/telemetry/src packages/telemetry/tests apps/api/tests/test_replay_runner.py packages/arena/src/monopoly_arena/llm_runner.py packages/arena/src/monopoly_arena/replay_verification.py`
- `node contracts/validate-contracts.mjs`

Passed after the current batch/model-card edits:

- `uv run pytest apps/api/tests/test_batch_runner.py::test_batch_runner_writes_index_and_summaries -q`
- `uv run pytest apps/api/tests/test_llm_runner.py::test_static_run_artifacts_are_written_without_system_prompt_text -q`
- `uv run ruff check packages/arena/src/monopoly_arena/batch_artifacts.py packages/arena/src/monopoly_arena/batch_run.py packages/arena/src/monopoly_arena/llm_runner.py packages/arena/src/monopoly_arena/openrouter_client.py apps/api/tests/test_batch_runner.py`
- `node contracts/validate-contracts.mjs`
- `uv run pytest packages/telemetry/tests -q`
- `uv run pytest apps/api/tests/test_replay_runner.py::test_replay_matches_event_stream_with_trade apps/api/tests/test_batch_runner.py::test_batch_runner_writes_index_and_summaries apps/api/tests/test_llm_runner.py::test_static_run_artifacts_are_written_without_system_prompt_text -q`
- `uv run pytest apps/api/tests/test_artifact_review_endpoints.py -q`
- `uv run ruff check apps/api/src/monopoly_api/main.py apps/api/src/monopoly_api/run_manager.py apps/api/tests/test_artifact_review_endpoints.py packages/telemetry/src/monopoly_telemetry/review.py packages/telemetry/src/monopoly_telemetry/run_files.py packages/telemetry/src/monopoly_telemetry/__init__.py`
- `uv run pytest apps/api/tests/test_artifact_review_endpoints.py -q` after adding batch artifact/model-card endpoints
- `uv run ruff check apps/api/src/monopoly_api/main.py apps/api/src/monopoly_api/run_manager.py apps/api/tests/test_artifact_review_endpoints.py` after adding batch artifact/model-card endpoints
- `uv run pytest apps/api/tests/test_artifact_review_endpoints.py -q` after adding snapshot endpoints
- `uv run ruff check apps/api/src/monopoly_api/main.py apps/api/src/monopoly_api/run_manager.py apps/api/tests/test_artifact_review_endpoints.py packages/telemetry/src/monopoly_telemetry/review.py packages/telemetry/src/monopoly_telemetry/run_files.py` after adding snapshot endpoints
- `bun run build` for the frontend after adding replay/review and batch dashboard routes.
- Browser route check against temporary dev server:
  - `http://127.0.0.1:5173/batches`
  - `http://127.0.0.1:5173/runs/mock-run/replay`
- `node contracts/validate-contracts.mjs` after adding micro research metadata to all 130 scenarios.
- `uv run pytest packages/microbench/tests/test_catalog_scorer_runner.py::test_catalog_validates_full_micro_v1 packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_v1_research_metadata_is_complete_and_research_only packages/microbench/tests/test_catalog_scorer_runner.py::test_live_game_prompt_matches_normal_game_prompt packages/microbench/tests/test_catalog_scorer_runner.py::test_research_metadata_does_not_change_prompt_bundle -q`
- `uv run ruff check packages/microbench/src/monopoly_microbench/catalog.py packages/microbench/tests/test_catalog_scorer_runner.py`
- `bun run build` after adding micro metadata UI/types.
- `uv run pytest apps/api/tests/test_batch_runner.py -q` after adding `max_turns`, resume, and failed-batch coverage.
- `uv run ruff check packages/arena/src/monopoly_arena/batch_artifacts.py packages/arena/src/monopoly_arena/batch_run.py apps/api/tests/test_batch_runner.py`
- `node contracts/validate-contracts.mjs` after adding benchmark artifact schemas/examples.
- `bun run build` after moving artifact UI types into shared contracts.
- `uv run pytest apps/api/tests/test_batch_runner.py -q` after adding historical-cost budget preflight.
- `uv run ruff check packages/arena/src/monopoly_arena/batch_artifacts.py packages/arena/src/monopoly_arena/batch_run.py apps/api/tests/test_batch_runner.py` after adding historical-cost budget preflight.
- `node contracts/validate-contracts.mjs` after adding `budget_policy` to batch artifact contracts.
- `uv run pytest apps/api/tests/test_llm_runner.py::test_generation_endpoint_backfills_usage_artifacts -q`
- `uv run ruff check packages/arena/src/monopoly_arena/decision_resolver.py packages/telemetry/src/monopoly_telemetry/usage.py apps/api/tests/test_llm_runner.py`

`yarn build` could not be run because `yarn` is not installed in this shell, and `corepack` is also unavailable. The build was verified with the repo's existing Bun setup instead.
