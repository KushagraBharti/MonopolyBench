# MonopolyBench Artifact Reference

This document is the stable reference for benchmark artifacts written under `runs/`.
Artifacts are post-run research outputs. They must not change prompt construction, prompt text, tool schemas, retry content, or anything else visible to the model.

## Full Game Runs

Each full game writes to `runs/<run_id>/`.

Core replay artifacts:
- `events.jsonl`: canonical event stream emitted by the authoritative engine.
- `actions.jsonl`: applied actions plus decision metadata, sufficient for deterministic replay when available.
- `state_replay_report.json`: engine-state replay status over state-relevant events. This intentionally excludes LLM observation events and normalizes global event sequencing fields so it answers whether the game-state trajectory replayed.
- `artifact_replay_report.json`: strict full event-stream replay status. This includes LLM request/response/message/thought events and catches artifact metadata drift, fallback metadata drift, missing observation events, and other research-log mismatches.
- `replay_report.json`: aggregate replay status with `state_status` and `artifact_status`. A run may be `state_passed_artifact_failed` when game state replayed but strict artifact metadata did not.
- `replay_diff.json`: compact mismatch/error summary for failed replays.
- `event_hashes.json`: stream hashes and per-event canonical hashes.
- `replay_steps.jsonl`: ordered replay steps for UI playback.
- `replay_flags.jsonl`: important replay markers.
- `replay_navigation.json`: skip targets for important decisions/events.

Score and accounting artifacts:
- `scorecard.json`: run-level and player-level metrics.
- `scorecard_players.json`: player score rows.
- `scorecard_decisions.jsonl`: per-decision score rows.
- `scorecard_events.jsonl`: per-event score rows.
- `usage.json`: OpenRouter-reported usage only.
- `usage_decisions.jsonl`: per-decision usage.
- `usage_attempts.jsonl`: per-attempt usage.
- `cost_report.json`: actual OpenRouter cost rollup.
- `pricing_snapshot.json`: OpenRouter model metadata snapshot when available.

Trace, failure, and review artifacts:
- `trace_findings.jsonl`: deterministic trace findings and human-review candidates.
- `failure_findings.jsonl`: failure taxonomy findings.
- `trace_summary.json`: trace finding counts.
- `failure_summary.json`: failure finding counts.
- `timeline.json`: ordered event/decision timeline with finding links.
- `decision_index.json`: decision lookup surface.
- `turn_index.json`: per-turn event/decision/finding counts.
- `player_timelines.json`: per-player timeline grouping.
- `negotiation_threads.jsonl`: trade thread groupings.
- `auction_threads.jsonl`: auction thread groupings.
- `asset_flow.jsonl`: property, mortgage, and building flow rows.
- `cash_flow.jsonl`: cash and rent flow rows.
- `behavioral_flags.jsonl`: subjective human-review candidates.
- `review_queue.jsonl`: human review queue.
- `review_labels.jsonl`: human-provided labels only.
- `review_summary.json`: rollup of human review labels.

Static metadata:
- `run_config.json`: seed, engine settings, replay policy, and prompt immutability note.
- `players.json`: player/model configuration metadata.
- `seat_assignment.json`: seat order and permutation metadata.
- `artifact_manifest.json`: file existence, byte counts, and hashes.
- `state/turn_*.json`: authoritative snapshots.
- `prompts/`: prompt/response logs for audit only.

## Batch Runs

Each batch writes to `runs/batches/<batch_id>/`.

Batch control and manifests:
- `batch_config.json`: normalized batch config.
- `batch_manifest.json`: run list and model-card links.
- `artifact_manifest.json`: batch artifact list.
- `model_config.json`: tested model metadata without system prompt text.
- `model_pricing_snapshot.json`: OpenRouter metadata snapshot.
- `seed_manifest.json`: seed assignments.
- `seat_manifest.json`: seat permutation assignments and seed material.
- `run_index.json` and `run_index.jsonl`: run/component index.

Batch scoring and statistics:
- `results.jsonl`: compact result rows.
- `leaderboard.json`: model rankings, rank distributions, and score modes.
- `scorecard_summary.json`: scorecard rollup.
- `category_breakdown.json`: event or micro-category rollup.
- `statistical_summary.json`: descriptive statistics and confidence intervals.

Batch replay, failure, review, and accounting:
- `replay_report.json`: batch replay pass-rate summary, including aggregate, state, and artifact status counts.
- `trace_summary.json`: trace finding rollup.
- `failure_summary.json`: failure finding rollup.
- `model_failure_breakdown.json`: failures by model.
- `failure_leaderboard.json`: model ranking by fewest failures.
- `top_findings.jsonl`: highest-priority trace/failure findings.
- `model_trace_breakdown.json`: traces by model.
- `failure_trace_breakdown.json`: combined failure/trace rollup.
- `review_queue.jsonl`: aggregate human review queue.
- `cost_report.json`: batch actual cost rollup.
- `token_report.json`: batch actual token rollup.
- `usage_summary.json`: combined actual cost/token summary.
- `budget_report.json`: cost and token budget status/preflight.

Model cards:
- `model_cards/<safe_model_id>.json`: structured card.
- `model_cards/<safe_model_id>.md`: markdown card without private-thought excerpts.

## Batch Types

`full_game` runs deterministic Monopoly games through the normal LLM arena.

`micro_suite` runs research-facing micro-decision scenarios through the existing microbench runner. Scenario research metadata remains research-only and must never be inserted into prompts.

`mixed` is a parent batch that can launch full-game and micro-suite components and writes a parent `run_index.jsonl` that points to each component batch.

## Non-Negotiable Prompt Boundary

Artifact generation is downstream of decisions. Agents must not change prompt construction, prompt content, message order, tool schema construction, retry wording, or model-facing prompt conditions while working on artifacts, metrics, replay, UI, contracts, or batch orchestration.
