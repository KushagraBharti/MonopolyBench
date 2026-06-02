# Implementation Status

## Current Phase

Completed common MonopolyBench benchmark infrastructure from `plan.md`.

Current focus: none. The common infrastructure goal implementation is complete and verified.

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
