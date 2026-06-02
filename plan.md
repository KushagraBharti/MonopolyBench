# Goal Prompt: Implement The Common MonopolyBench Benchmark Infrastructure

Use this file as the exact goal prompt:

```text
/goal plan.md
Complete this plan fully. Do not stop until every required capability is implemented,
tested, documented, and verified, or until a concrete external blocker is recorded.
Absolutely preserve the prompt pipeline. Do not change how prompts are built, sent,
formatted, worded, tooled, retried, logged as model-facing content, or exposed to the
LLM in any way.
```

This file is intended to be used as the goal-mode prompt for implementing the shared
benchmark infrastructure described in `research_direction.md`. It should steer the
agent to keep working until the common infrastructure is actually complete, tested,
documented, and usable.

The goal is not to change the research framing. The goal is to implement the shared
platform pieces that every research direction needs:

- richer scorecards and metrics,
- batch evaluation infrastructure,
- seeded seat permutations,
- deterministic replay verification from JSON artifacts,
- thorough OpenRouter token and cost accounting,
- a full trace analyzer,
- a failure taxonomy,
- model cards,
- a human review workflow built into replay,
- research-facing micro-decision metadata,
- replay/UI artifact upgrades,
- documentation, schemas, tests, and verification.

## Goal-Mode Operating Contract

The agent working on this goal must treat this file as the source of truth for scope.
Do not stop after a partial implementation. Do not stop after writing only docs. Do not
stop after implementing only backend artifacts. Continue until all acceptance criteria
in this file are either complete or explicitly recorded as blocked by a concrete
external dependency.

At the start of the goal:

1. Read `AGENTS.md`.
2. Read this `plan.md`.
3. Read `research_direction.md`.
4. Inspect the current implementation before editing:
   - `python/packages/engine/src/monopoly_engine/replay.py`
   - `python/packages/telemetry/src/monopoly_telemetry/run_files.py`
   - `python/packages/telemetry/src/monopoly_telemetry/summary.py`
   - `python/packages/arena/src/monopoly_arena/openrouter_client.py`
   - `python/packages/arena/src/monopoly_arena/decision_resolver.py`
   - `python/packages/arena/src/monopoly_arena/llm_runner.py`
   - `python/packages/arena/src/monopoly_arena/batch_run.py`
   - `python/packages/microbench/src/monopoly_microbench/*`
   - `python/apps/api/src/monopoly_api/*`
   - `frontend/src/*`
   - `contracts/schemas/*`
   - `contracts/ts/*`
5. Create or update a local progress file, preferably `implementation_status.md`,
   with a checklist copied from this file. Update it after every completed phase.

During the goal:

- Keep work moving in implementation phases.
- Use the existing architecture rather than inventing a parallel benchmark system.
- Preserve all AGENTS.md invariants: authoritative engine, deterministic replay,
  UI render-only, legal-actions-only LLM control, OpenRouter-only LLM gateway, and
  no silent mutations.
- Prefer deterministic, schema-validated JSON artifacts over ad hoc text files.
- When touching protocol shapes, update JSON Schema, TypeScript types, examples,
  producers, consumers, and tests together.
- After every major phase, run the most relevant tests before continuing.
- Before marking complete, run the final verification checklist near the bottom of
  this file.

The goal is complete only when:

- all required artifacts are produced for normal full-game runs,
- batch runs produce batch-level artifacts and aggregate metrics,
- replay verification is automatic and produces a report,
- seat permutation support is deterministic and persisted,
- OpenRouter token/cost accounting is captured as accurately as the platform allows,
- trace findings and failure tags are generated and visible in replay/review UI,
- model cards are generated from batch/run data,
- human review queues and labels can be created and persisted,
- micro scenario schema expansion is research-facing only and does not affect prompts,
- the UI can inspect replay artifacts without implementing rules,
- docs explain how to run and interpret everything,
- and tests pass.

## Absolute Non-Negotiables

These constraints are stricter than normal engineering preferences because this repo
is a benchmark.

### No Prompt Changes

This is the strictest rule in the goal.

Do not change prompt content, prompt formatting, prompt condition behavior, tool
prompt construction, retry prompt wording, system prompts, user prompt payloads,
message ordering, message roles, message keys, serialized prompt JSON, OpenRouter tool
schemas, tool choice behavior, retry behavior, prompt memory behavior, private thought
requirements, public message requirements, or anything else that changes what the LLM
sees.

The goal agent must assume that the current prompt pipeline has been hand-curated and
is benchmark-critical. Any accidental prompt diff is a regression.

This applies to:

- full-game prompts,
- microbench prompts,
- retry prompts,
- public/private message requirements,
- OpenRouter tool schemas,
- prompt memory behavior,
- prompt artifact content,
- quality-check prompt exports.

The only allowed prompt-adjacent work is better logging of existing prompt artifacts
and metadata that is not sent to the LLM.

Required prompt-preservation tests:

- For existing full-game decision fixtures where prompt construction can be reproduced,
  generated model-facing messages and tools must remain byte-for-byte identical before
  and after this implementation.
- For existing micro scenarios under `live_game`, generated model-facing messages and
  tools must remain byte-for-byte identical before and after adding research metadata.
- Prompt artifact paths, timestamps, and non-model-facing artifact manifests may change.
  Model-facing request payloads may not.
- If a required implementation appears to require prompt changes, stop that part of
  the work and record it as blocked for user approval. Do not make the prompt change.

### No Prompt Condition Framework

Do not implement prompt conditions, prompt ablations, alternate prompt formats, memory
variants, prompt dashboards, or prompt experiments. These require direct user oversight
and are out of scope for this goal.

Existing `prompt_condition: "live_game"` behavior should remain unchanged.

### No Guardrail Condition Framework

Do not implement experimental guardrails, guardrail ablations, hard action blockers,
soft policy interventions, or prompt-based guardrail instructions.

The engine's existing legality constraints remain mandatory. The new human review and
failure taxonomy may label behavior after the fact, but they must not constrain or
coach model behavior during decisions.

### No Heuristic Value Models Exposed To LLMs

Do not build a model-facing value model. Do not add rent EV summaries, asset valuation
hints, opponent threat dashboards, trade advice, auction advice, or any computed
strategic helper into prompts or decision payloads.

For analysis only, it is acceptable to compute:

- descriptive metrics directly from events, actions, decisions, and snapshots,
- simple rule-based trace flags for human review,
- face-value accounting of cash/property/buildings,
- curated microbench rubric outcomes,
- replay-derived deltas.

If an analyzer uses an interpretive label, it must be stored as post-hoc analysis and
must never be fed back into the LLM.

### Microbench Schema Must Be Research-Facing Only

The micro decision suite may gain metadata that helps researchers organize, filter,
review, and analyze scenarios. That metadata must never be included in prompts sent to
models.

The agent must explicitly test that adding micro metadata does not change prompt
request artifacts for existing scenarios under the default `live_game` condition.

### OpenRouter Only

All model calls remain routed through OpenRouter. Do not add direct OpenAI, Anthropic,
Google, xAI, Meta, or other vendor clients. Do not add direct vendor tokenizer
dependencies in this goal. Actual usage, native token counts, and cost must come from
OpenRouter response/generation data whenever available.

## External Implementation Notes

The implementation should use current OpenRouter capabilities rather than guessing.
Research notes to apply:

- OpenRouter usage accounting docs: https://openrouter.ai/docs/use-cases/usage-accounting
- OpenRouter generation endpoint docs: https://openrouter.ai/docs/api-reference/get-a-generation
- OpenRouter models endpoint docs: https://openrouter.ai/docs/api/api-reference/models/get-models
- OpenRouter credits endpoint docs: https://openrouter.ai/docs/api-reference/get-credits
- OpenRouter model routing/provider docs: https://openrouter.ai/docs/features/provider-routing

Practical implications:

- Preserve the `usage` object returned by chat completions when present.
- Preserve OpenRouter request IDs and generation IDs.
- If final cost or native token counts are absent from the chat completion response,
  query the generation endpoint when possible and backfill usage accounting.
- Snapshot model pricing from the OpenRouter models endpoint at batch start and store
  it with the run/batch artifacts, because model prices can change.
- Use OpenRouter native token counts and generation metadata as the official accounting
  source.
- Record actual and preflight-estimated accounting fields separately when estimates are
  needed for budgets.

## Resolved User Defaults

These defaults have already been decided and should not be re-asked unless the user
explicitly reopens them.

- `plan.md` is the exact goal prompt.
- Default live OpenRouter batch budget: `$50`.
- Budget policy: stop immediately when the budget is exceeded or cannot safely cover
  the next planned run. Do not start another game once the stop condition is met.
- Default seat permutation mode: `latin_square`, because it is the most research-useful
  default under realistic cost limits. `full` is allowed for small/carefully budgeted
  experiments, and `seeded_random` is allowed when explicitly configured.
- Replay every completed full game by default, including casual UI runs and batch
  runs.
- Store replay JSON artifacts freely. Artifact volume is acceptable for now.
- Replay should be backed by JSON artifacts that allow stepping through the full game
  event by event, plus flags for major events so the UI can jump directly to them.
- Replay UI should resemble the main game UI, but with better navigation.
- Private thoughts should be easy to view in replay/review inspector panes because
  human review depends on them. They should not be rendered as public chat.
- Replay UI must include skip modes:
  - important decisions only,
  - trace findings only,
  - failures only,
  - negotiations/trades only,
  - auctions only,
  - bankruptcies/cash collapses only,
  - model decisions only,
  - manual full event stepping.
- Replay and human review should be combined into one workflow/view when practical.
- Subjective behavioral labels must be human-reviewed only. Do not add LLM classifiers
  for deception, collusion, false claims, kingmaking, spite, strategy drift, or similar
  categories.
- Cost and token accounting should rely on official OpenRouter actual usage data,
  native token counts, generation metadata, and OpenRouter model pricing snapshots.
  Do not add local tokenizer dependencies as part of this goal.
- Markdown model cards should link to private-thought artifacts rather than quote
  private-thought excerpts by default. JSON artifacts should still store the full
  private thoughts for review and replay.
- The existing 130 micro scenarios are enough for the first implementation. The first
  goal implementation should review all existing scenarios one by one, improve
  research-facing metadata/rubrics/review fields where useful, and avoid a large
  scenario expansion unless an obvious gap is discovered.
- Existing micro-decision suites may be bulk-updated with research-only metadata and
  additional scenario coverage, but no model-facing prompt content or prompt generation
  behavior may change.
- Do not change existing micro scenario `decision_point` payloads or other fields that
  are sent to the LLM unless the user explicitly approves that prompt-facing change.
- Batch artifacts should live under `runs/batches/<batch_id>/` so ordinary non-batch
  runs remain easy to browse under `runs/<run_id>/`.
- Default live OpenRouter batch concurrency is `1` simultaneous run/request stream.
  This is a concurrency default, not a scheduled daily-run cadence.
- Define an aggregate full-game score now. The primary score should be based on final
  net worth and winning/bankrupting opponents, while still preserving all raw metrics.
- Scoreboard UI should expose a score matrix, not only one fixed rank:
  - net-worth ranking,
  - winner/completion ranking,
  - speed ranking based on how quickly opponents are bankrupted,
  - reliability/cost-adjusted ranking,
  - and a combined experimental ranking that can be changed later.

Reviewer identity clarification:

- A reviewer identity is just the value stored with a human review label so later
  analysis can tell who created a label or whether multiple reviewers agreed.
- Use a simple optional string field named `reviewer_id`.
- No authentication system is required for this goal.
- If no reviewer id is provided, default to `local_reviewer`.
- The UI should allow changing the reviewer id in review settings.

# Implementation Scope

The rest of this file is the implementation checklist.

## 1. Standardized Run Scorecard

Every full game should produce a scorecard that is substantially richer than
`winner_player_id`. The scorecard should be deterministic, derived from artifacts, and
stored in machine-readable files.

### Files And Modules To Extend

Likely touch points:

- `python/packages/telemetry/src/monopoly_telemetry/summary.py`
- `python/packages/telemetry/src/monopoly_telemetry/run_files.py`
- `python/packages/telemetry/tests/*`
- `python/packages/engine/src/monopoly_engine/models.py`
- `contracts/schemas/*` if new stable artifact shapes are added
- `contracts/ts/*` if frontend consumes the new shapes
- `python/apps/api/src/monopoly_api/*`
- `frontend/src/pages/*`
- `frontend/src/components/*`

### Required Artifacts

For every full-game run, produce:

- `summary.json`: backward-compatible high-level summary plus new scorecard fields.
- `scorecard.json`: complete run scorecard.
- `scorecard_players.json`: per-player scorecard rows.
- `scorecard_decisions.jsonl`: per-decision metric rows.
- `scorecard_events.jsonl`: event-derived metric rows where useful.
- `artifact_manifest.json`: paths, schema versions, hashes, creation time, run id.

If adding all files at once is too much, `scorecard.json` and `scorecard_players.json`
are required first, but the final goal is not complete until the per-decision and
manifest artifacts exist.

### Core Outcome Metrics

Compute and store per run:

- run id,
- schema version,
- engine rules version if available,
- contract schema version if available,
- scoring version,
- seed,
- max turns,
- start timestamp counter settings,
- max trade exchanges,
- max auction actions,
- player count,
- game completion status,
- game end reason,
- winner player id,
- winner model id,
- final turn index,
- total event count,
- total decision count,
- total applied action count,
- total rent paid,
- total rent collected,
- total tax paid,
- total auction volume,
- total trade count,
- total property transfer count,
- total bankruptcies,
- total houses built,
- total hotels built,
- total houses sold,
- total hotels sold,
- total mortgages,
- total unmortgages.

Compute and store per player:

- player id,
- player display name,
- model id,
- model display name,
- seat index,
- final rank,
- winner boolean,
- final cash,
- final property face value,
- final building value estimate if available,
- final mortgage liability estimate,
- final net worth estimate,
- final liquid net worth estimate,
- bankruptcy status,
- bankruptcy turn,
- bankruptcy creditor type,
- bankruptcy creditor player id if applicable,
- turns played,
- turns survived,
- opponents bankrupted,
- final property count,
- final mortgage count,
- final unmortgaged property count,
- final complete color group count,
- final developed monopoly count,
- final railroad count,
- final utility count,
- houses owned,
- hotels owned,
- rent collected,
- rent paid,
- net rent flow,
- taxes paid,
- jail entries,
- jail turns,
- get-out-of-jail cards used,
- properties bought directly,
- properties won by auction,
- properties acquired by trade,
- properties lost by trade,
- properties lost by bankruptcy,
- auction bids placed,
- auctions won,
- auctions dropped,
- trades proposed,
- trades received,
- trades accepted,
- trades rejected,
- counters made,
- public messages sent,
- private thoughts recorded,
- invalid attempts,
- retries used,
- fallbacks used,
- average decision latency,
- total input tokens,
- total output tokens,
- total reasoning tokens if available,
- total cached tokens if available,
- total cost,
- cost per decision,
- cost per turn survived,
- cost per net-worth point.

### Strategic And Economic Descriptive Metrics

These must be post-hoc descriptive metrics. They must not add strategic advice to
prompts.

Track:

- cash buffer after each optional action,
- lowest cash reached,
- average cash at turn end,
- number of times a player ended a turn with negative cash pressure resolved,
- number of times legal build was available and the chosen action was `end_turn`,
- number of times legal mortgage/unmortgage was available and the player ended turn,
- number of build actions while cash after action was below configured descriptive
  thresholds,
- number of unmortgage actions while low on cash,
- number of mortgage actions on complete color groups,
- number of house-to-hotel conversions,
- number of conversions when bank house inventory changed materially,
- number of direct purchases declined by starting auction,
- number of direct purchases made while cash below descriptive thresholds,
- number of direct purchases declined while cash above descriptive thresholds,
- auction bids above property list price,
- auction bids above 150 percent of list price,
- auction wins below list price,
- auction exits while having enough cash to continue,
- trade offers that complete a monopoly for self,
- trade offers that complete a monopoly for opponent,
- accepted trades that complete a monopoly for self,
- accepted trades that complete a monopoly for opponent,
- accepted trades with positive/negative face-value cash-property delta,
- accepted trades that transfer get-out-of-jail cards,
- rejected trades that would have completed a monopoly for self,
- bankruptcy after recent high-spend optional action,
- liquidation actions by type,
- liquidation failures or fallback events.

Important: do not label these as "optimal" or "suboptimal" unless the label comes from
a curated micro scenario rubric or a human review. Use neutral names such as
`legal_build_available_then_end_turn`, `auction_bid_above_list_price`, and
`trade_completed_opponent_monopoly`.

### Aggregate Full-Game Score

Define a primary full-game score now, but keep all raw metrics available.

Primary score:

- `primary_score = final_net_worth_estimate`

Research interpretation:

- models are trying to maximize final net worth,
- winning the game and bankrupting opponents are still critical outcome metrics,
- bankrupting opponents should be reported directly through `winner`, `final_rank`,
  `opponents_bankrupted`, `bankruptcy_rate`, and `turns_survived`,
- scoreboards should sort primarily by win/game completion when the game reaches a
  natural winner, and by `primary_score` for max-turn or unfinished games,
- batch leaderboards should expose both win-oriented rankings and net-worth-oriented
  rankings so the scoring formula is transparent.

Score matrix:

- `net_worth_score`: final net worth estimate.
- `winner_score`: winner/completion status and final rank.
- `speed_score`: rewards ending the game quickly by bankrupting all opponents in fewer
  turns.
- `bankruptcy_pressure_score`: opponents bankrupted and bankruptcy cascade impact.
- `survival_score`: turns survived and bankruptcy avoidance.
- `reliability_score`: valid first-response rate, retry rate, fallback rate, and replay
  pass status.
- `cost_adjusted_score`: score per OpenRouter cost unit.

The first combined score can be experimental and versioned, but the UI must show the
component scores separately. This lets the scoreboard evolve later without losing the
raw research signal.

Tie-breakers for per-game ranking:

1. winner status,
2. final net worth estimate,
3. final liquid net worth estimate,
4. opponents bankrupted,
5. turns survived,
6. final cash.

Do not bury raw net worth behind a complicated opaque composite. If a composite score
is later added, it must be stored separately and documented with a versioned scoring
spec.

### Reliability Metrics

Track per run, per player, and per model:

- total LLM decisions,
- total automated decisions if any,
- invalid first attempts,
- retry count,
- retry success count,
- retry failure count,
- fallback count,
- fallback reasons,
- schema failures,
- malformed JSON/tool arguments,
- missing tool call,
- multiple tool calls,
- unknown tool/action,
- illegal action attempt,
- rules-invalid action attempt,
- missing required public message,
- missing required private thought,
- OpenRouter HTTP status distribution,
- OpenRouter error type distribution,
- network error count,
- no API key count,
- average latency,
- p50 latency,
- p90 latency,
- p95 latency,
- p99 latency,
- max latency,
- timeout count if distinguishable.

### Behavioral And Review-Oriented Metrics

These are flags for analysis and human review, not final truth unless reviewed.

Track:

- public/private mismatch candidate count,
- false factual claim candidate count,
- deception candidate count,
- collusion candidate count,
- kingmaking candidate count,
- spite-play candidate count,
- coercive threat candidate count,
- revenge-language candidate count,
- repetitive/no-progress candidate count,
- strategy-drift candidate count,
- human-reviewed true positive count by label,
- human-reviewed false positive count by label,
- unreviewed candidate count by label.

Candidate labels should be conservative. Human review labels should be stored
separately and should supersede candidate labels for paper-ready claims.

### Acceptance Criteria

This section is complete only when:

- scorecard artifacts are written for full-game runs,
- scorecards are generated from logs rather than live mutable objects,
- existing summaries remain backward compatible,
- per-player, per-model, and per-run metrics are present,
- unit tests cover scorecard generation from synthetic logs,
- tests cover missing/partial artifact behavior,
- and frontend/API can load scorecards without implementing game rules.

## 2. Batch Evaluation Harness

Research claims require controlled repeated runs. The current batch runner is a useful
start, but the benchmark needs a full batch protocol.

### Files And Modules To Extend

Likely touch points:

- `batches/batch.example.json`
- `python/packages/arena/src/monopoly_arena/batch_run.py`
- `python/packages/microbench/src/monopoly_microbench/runner.py`
- `python/packages/telemetry/src/monopoly_telemetry/*`
- `python/apps/api/src/monopoly_api/*`
- `contracts/schemas/*`
- `contracts/ts/*`
- `frontend/src/pages/*`
- `frontend/src/components/*`

### Batch Types

Support at minimum:

- `full_game`: repeated full Monopoly games.
- `micro_suite`: runs micro-decision scenarios.
- `mixed`: optional wrapper that can include full-game and micro-suite jobs in one
  batch manifest.

Do not implement prompt ablation, guardrail ablation, or orchestrator ablation in this
goal.

### Batch Config

Create or formalize a batch config schema. It should include:

- `schema_version`,
- `batch_id`,
- `batch_type`,
- `description`,
- `created_by`,
- `created_at`,
- `seed_manifest`,
- `seeds`,
- `matches`,
- `models`,
- `players`,
- `seat_permutation`,
- `max_turns`,
- `max_trade_exchanges`,
- `max_auction_actions`,
- `runs_dir`,
- `batch_artifact_dir` defaulting to `runs/batches/<batch_id>/`,
- `concurrency` defaulting to `1`,
- `rate_limit`,
- `cost_budget` defaulting to `50.00`,
- `cost_budget_unit` using OpenRouter's reported cost unit, expected to be USD-style
  account credits unless OpenRouter exposes a more specific unit,
- `budget_policy` defaulting to `stop_immediately`,
- `token_budget`,
- `continue_on_failure`,
- `replay_after_run`,
- `build_scorecard_after_run`,
- `build_trace_after_run`,
- `build_failure_taxonomy_after_run`,
- `write_model_cards`,
- `micro_suite_id`,
- `micro_scenario_ids`,
- `metadata`.

### Batch Artifacts

Every batch should write:

- `runs/batches/<batch_id>/batch_config.json`,
- `runs/batches/<batch_id>/batch_manifest.json`,
- `runs/batches/<batch_id>/model_config.json`,
- `runs/batches/<batch_id>/model_pricing_snapshot.json`,
- `runs/batches/<batch_id>/seed_manifest.json`,
- `runs/batches/<batch_id>/seat_manifest.json`,
- `runs/batches/<batch_id>/run_index.json`,
- `runs/batches/<batch_id>/run_index.jsonl`,
- `runs/batches/<batch_id>/results.jsonl`,
- `runs/batches/<batch_id>/leaderboard.json`,
- `runs/batches/<batch_id>/scorecard_summary.json`,
- `runs/batches/<batch_id>/category_breakdown.json`,
- `runs/batches/<batch_id>/statistical_summary.json`,
- `runs/batches/<batch_id>/replay_report.json`,
- `runs/batches/<batch_id>/trace_summary.json`,
- `runs/batches/<batch_id>/failure_summary.json`,
- `runs/batches/<batch_id>/cost_report.json`,
- `runs/batches/<batch_id>/token_report.json`,
- `runs/batches/<batch_id>/budget_report.json`,
- `runs/batches/<batch_id>/review_queue.jsonl`,
- `runs/batches/<batch_id>/artifact_manifest.json`.

The batch should not be considered complete if it only writes `index.jsonl`.

### Batch Features

Implement:

- deterministic run id generation,
- resume behavior that does not duplicate completed run ids,
- per-run status tracking,
- failed-run tracking,
- batch-level progress artifacts,
- concurrency control,
- cost budget preflight and stop-immediately budget behavior,
- token budget preflight and stop-immediately budget behavior,
- per-model and per-seat aggregates,
- confidence intervals where enough samples exist,
- rank distributions,
- win-rate distributions,
- invalid/retry/fallback distributions,
- latency distributions,
- cost distributions,
- replay pass/fail distributions,
- failure-taxonomy distributions,
- links/paths to each run's replay artifacts.

### Leaderboard Requirements

The leaderboard should include:

- model id,
- display name,
- number of runs,
- number of seats played,
- seeds covered,
- win rate,
- average rank,
- median rank,
- average final net worth,
- median final net worth,
- average primary full-game score,
- median primary full-game score,
- bankruptcy rate,
- average turns survived,
- win-oriented rank,
- net-worth-oriented rank,
- microbench average if batch includes micro runs,
- retry rate,
- fallback rate,
- invalid first-attempt rate,
- total tokens,
- total cost,
- cost per completed game,
- cost per win,
- cost-adjusted score,
- replay pass rate,
- reviewed failure counts.

### Acceptance Criteria

This section is complete only when:

- a documented batch config can run full-game batches,
- a documented batch config can run micro-suite batches,
- run-level and batch-level artifacts are written,
- partial failures are represented without corrupting completed results,
- batch resume works,
- batch outputs include cost, token, replay, trace, failure, and scorecard summaries,
- and tests cover successful batches, failed batches, and resume behavior.

## 3. Seat Permutation Support

Monopoly seating order matters. Models must not always occupy the same player id or
turn order.

### Core Design

Separate:

- stable model identity,
- player display identity,
- engine player id,
- seat index,
- turn order,
- batch run id.

The same model should be able to appear as `p1`, `p2`, `p3`, and `p4` across a balanced
set of runs.

### Permutation Modes

Support:

- `none`: preserve configured order.
- `full`: run all seat permutations for the selected models when feasible.
- `latin_square`: balanced subset suitable for larger model pools or cost limits.
- `seeded_random`: deterministic random shuffle per game.

For `seeded_random`, the shuffle must be derived from:

- batch id,
- batch seed,
- game seed,
- match index,
- model ids,
- configured permutation salt.

Do not use wall-clock randomness for seat assignment.

### Seat Artifacts

Write:

- `seat_manifest.json` at batch level,
- `seat_assignment.json` per run,
- seat fields in `run_config.json`,
- seat fields in `scorecard_players.json`,
- seat fields in `leaderboard.json`,
- seat fields in model cards.

Each run should record:

- model id,
- model display name,
- engine player id,
- player name,
- seat index,
- turn order,
- permutation id,
- permutation mode,
- permutation seed material,
- permutation digest.

### Acceptance Criteria

This section is complete only when:

- seat permutation works for full-game batches,
- the same model can rotate through all seats,
- replay uses the same stored seat assignment,
- metrics can be grouped by seat and by model,
- tests prove deterministic shuffling,
- tests prove player/model identities are not conflated.

## 4. Deterministic Replay Verification

Replay should be an automatic benchmark proof, not an optional developer check.

### Current Foundation

The repo already has:

- `python/packages/engine/src/monopoly_engine/replay.py`
- `actions.jsonl`
- `events.jsonl`
- per-turn snapshots
- replay tests in the API/engine area.

Extend this instead of replacing it.

### Required Run Artifacts

Every replayable run should write:

- `run_config.json`,
- `players.json`,
- `seat_assignment.json`,
- `actions.jsonl`,
- `events.jsonl`,
- `decisions.jsonl`,
- `state/*.json`,
- `replay_events.jsonl` or an equivalent generated replay output,
- `replay_steps.jsonl` with one step per replayable event/decision transition,
- `replay_flags.jsonl` with major events and jump targets,
- `replay_navigation.json` with indexes for turns, decisions, failures, trace findings,
  negotiations, auctions, bankruptcies, and cash-collapse events,
- `replay_report.json`,
- `replay_diff.json` when mismatch occurs,
- `event_hashes.json`,
- `artifact_manifest.json`.

`run_config.json` must include enough information to reconstruct the engine:

- seed,
- run id,
- players,
- max turns,
- start timestamp counter,
- timestamp step,
- max trade exchanges,
- max auction actions,
- engine version if available,
- schema version,
- seat assignment,
- applied action count.

### Replay Report

`replay_report.json` should answer:

- was replay attempted,
- replay status,
- replay started at,
- replay finished at,
- original event count,
- replay event count,
- original canonical hash,
- replay canonical hash,
- first mismatch index,
- first mismatch original event,
- first mismatch replay event,
- missing actions,
- extra actions,
- decision id mismatch,
- schema validation status,
- events schema validation status,
- actions schema validation status,
- snapshots schema validation status,
- canonicalization rules used,
- run config used,
- replay duration.

### Batch Replay

For batches:

- run replay after each completed full game if `replay_after_run` is true,
- default `replay_after_run` to true for every full-game batch,
- aggregate pass/fail in `batch/replay_report.json`,
- include replay pass rate in leaderboard,
- fail final verification if benchmark-worthy runs cannot replay.

For non-batch full-game runs:

- replay verification should run by default after game completion,
- replay reports should be written even for casual UI runs,
- failures should be visible in the replay/review UI.

### Replay UI

The replay UI should consume artifacts and allow:

- selecting a run,
- stepping through events,
- jumping to turn,
- jumping to decision,
- jumping to failure/trace flags,
- skipping to important decisions only,
- skipping to failures only,
- skipping to trace findings only,
- skipping to negotiations/trades only,
- skipping to auctions only,
- skipping to bankruptcies/cash collapses only,
- hiding routine events when fast review mode is enabled,
- viewing board state from snapshots,
- viewing decisions/actions/prompts/responses for the selected decision,
- viewing public messages and private thoughts,
- viewing replay verification status,
- viewing event diffs when replay failed.

The UI must not infer rules. It should render from artifacts only.

### Acceptance Criteria

This section is complete only when:

- full-game runs write sufficient replay config,
- replay verification runs automatically,
- passing replay produces matching canonical hashes,
- failing replay produces useful diffs,
- batch replay aggregation exists,
- API/frontend can load replay reports,
- tests cover pass and mismatch cases.

## 5. OpenRouter Cost And Token Accounting

Long-horizon benchmarks can be expensive. Cost and token accounting must be explicit,
auditable, and as accurate as OpenRouter allows.

### Accuracy Principles

Use this hierarchy:

1. Actual OpenRouter usage and generation accounting.
2. OpenRouter generation endpoint backfill.
3. OpenRouter model pricing snapshot plus observed native token counts.
4. Conservative budget preflight estimates from historical OpenRouter data and pricing
   snapshots only.

Never mix actual and estimated values without labeling them.

### OpenRouter Data To Capture

For every attempt, capture:

- request id,
- generation id if available,
- OpenRouter model id requested,
- OpenRouter model id returned,
- provider route if available,
- provider name if available,
- status code,
- finish reason,
- usage object,
- prompt tokens,
- completion tokens,
- total tokens,
- native prompt tokens,
- native completion tokens,
- native total tokens,
- reasoning tokens when available,
- cached input tokens when available,
- cache write tokens when available,
- cache read tokens when available,
- cost from response when available,
- total cost from generation endpoint when available,
- prompt cost,
- completion cost,
- reasoning cost if separable,
- cache read/write cost if separable,
- latency ms,
- retry index,
- fallback status,
- error type.

For every model at batch start, capture a pricing snapshot from OpenRouter's models
endpoint:

- model id,
- canonical model id,
- name,
- created date if available,
- context length,
- architecture fields,
- pricing prompt,
- pricing completion,
- pricing request,
- pricing image,
- pricing web search,
- pricing internal reasoning,
- tokenizer metadata if available,
- supported parameters,
- provider routing metadata if available,
- snapshot timestamp.

For every batch, capture:

- credit balance before batch if OpenRouter credits endpoint is available,
- credit balance after batch if available,
- total actual cost,
- total estimated cost,
- total unknown cost,
- total actual tokens,
- total estimated tokens,
- cost by model,
- cost by run,
- cost by player,
- cost by decision type,
- cost by retry/fallback,
- cost by micro category if applicable.

### Tokenizers And Estimates

Do not add local tokenizer dependencies in this goal.

Rely on OpenRouter's actual usage accounting:

- chat completion `usage` objects,
- native token counts,
- generation endpoint metadata,
- pricing data from the OpenRouter models endpoint.

If OpenRouter usage data is missing:

- store actual token/cost fields as `null`,
- store `accounting_status: "missing_openrouter_usage"`,
- store the OpenRouter request id/generation id needed for later audit,
- do not invent final benchmark token counts from a local tokenizer.

For budget preflight, use only:

- already-known historical OpenRouter costs from prior runs,
- OpenRouter pricing snapshots,
- configured conservative per-decision estimates.

Any preflight estimate must be labeled as an estimate and must not be used as the
final benchmark accounting if OpenRouter actuals are available.

### Required Artifacts

Per run:

- `usage.json`,
- `usage_decisions.jsonl`,
- `usage_attempts.jsonl`,
- `pricing_snapshot.json`,
- `cost_report.json`.

Per batch:

- `model_pricing_snapshot.json`,
- `usage_summary.json`,
- `cost_report.json`,
- `token_report.json`,
- `budget_report.json`.

### Integration Points

Extend:

- `OpenRouterResult` to preserve normalized usage/accounting fields.
- `OpenRouterClient` to optionally query generation details after completion.
- `DecisionResolutionAttempt` logs to include normalized usage fields.
- `summary.py` to aggregate usage accurately.
- batch runner to snapshot model pricing and credits.
- model cards to include cost/tokens.
- UI cost dashboard to display run/batch accounting.

### Acceptance Criteria

This section is complete only when:

- every OpenRouter attempt preserves raw and normalized usage data,
- actual and estimated token/cost fields are distinct,
- batch-level pricing snapshots are stored,
- cost reports aggregate by run, model, player, and decision type,
- missing usage data is represented explicitly,
- tests cover usage aggregation and missing/partial usage,
- no local tokenizer dependencies are added,
- no direct vendor API calls are introduced.

## 6. Full Trace Analyzer

A leaderboard says who won. A trace analyzer should help explain how and why.

### Core Principle

The trace analyzer is post-hoc. It reads artifacts and writes analysis artifacts. It
must not alter engine behavior, legal actions, prompts, or model decisions.

### Inputs

The analyzer should consume:

- `events.jsonl`,
- `actions.jsonl`,
- `decisions.jsonl`,
- `state/*.json`,
- `scorecard.json`,
- `scorecard_players.json`,
- `usage_attempts.jsonl`,
- human review labels if present,
- micro results if linked.

### Required Outputs

Per run:

- `trace_findings.jsonl`,
- `trace_summary.json`,
- `timeline.json`,
- `decision_index.json`,
- `turn_index.json`,
- `player_timelines.json`,
- `negotiation_threads.jsonl`,
- `auction_threads.jsonl`,
- `asset_flow.jsonl`,
- `cash_flow.jsonl`,
- `behavioral_flags.jsonl`,
- `review_queue.jsonl`.

Per batch:

- `trace_summary.json`,
- `top_findings.jsonl`,
- `model_trace_breakdown.json`,
- `failure_trace_breakdown.json`,
- `review_queue.jsonl`.

### Trace Finding Shape

Each trace finding should include:

- `schema_version`,
- `run_id`,
- `finding_id`,
- `finding_type`,
- `severity`,
- `confidence`,
- `status`,
- `turn_index`,
- `decision_id`,
- `player_id`,
- `model_id`,
- `event_seq_start`,
- `event_seq_end`,
- `supporting_event_ids`,
- `supporting_action_ids` if available,
- `supporting_decision_ids`,
- `snapshot_path`,
- `summary`,
- `details`,
- `derived_metrics`,
- `human_review_required`,
- `human_review_status`,
- `tags`.

### Finding Categories

Implement deterministic/post-hoc detectors for:

- decisive rent payments,
- bankruptcy cascade,
- major cash swing,
- major net-worth swing,
- property monopoly completed,
- opponent monopoly completed,
- trade accepted,
- trade rejected,
- trade countered,
- trade completed own monopoly,
- trade completed opponent monopoly,
- auction won,
- auction over list price,
- auction far over list price,
- auction below list price,
- repeated auction bids by same player,
- direct purchase declined,
- property bought while low cash,
- build action,
- build while low cash,
- house shortage created,
- house shortage relieved,
- hotel conversion,
- mortgage action,
- unmortgage action,
- liquidation sequence,
- bankruptcy declaration,
- fallback action,
- retry success,
- retry failure,
- repeated fallback window,
- public/private mismatch candidate,
- false factual claim candidate,
- deception/collusion candidate,
- kingmaking candidate,
- spite-play candidate.

For subjective categories, write candidates and route them to human review. Do not make
paper claims from unreviewed subjective candidates.

### Negotiation Threading

Build negotiation thread artifacts that group:

- proposal decision,
- public message,
- private thought,
- proposed offer/request,
- response decision,
- response public message,
- response private thought,
- accept/reject/counter action,
- resulting property transfers,
- resulting cash changes,
- monopoly completion effects,
- downstream rent/build events within a configurable window.

### Replay UI Integration

The replay UI should show:

- a timeline lane for trace findings,
- a filterable finding list,
- severity filters,
- model/player filters,
- jump-to-decision,
- jump-to-event,
- supporting events/actions,
- side-by-side public/private text,
- review status,
- reviewer labels and notes.

### Acceptance Criteria

This section is complete only when:

- trace analyzer CLI/API can analyze an existing run,
- full-game runs can generate trace artifacts automatically,
- batch runs aggregate trace findings,
- replay UI exposes trace findings,
- subjective findings are marked as review candidates,
- tests cover representative trace detectors.

## 7. Failure Taxonomy

The benchmark needs stable failure labels for debugging, model cards, and research
analysis.

### Taxonomy Artifact

Create a versioned taxonomy spec, for example:

- `contracts/taxonomy/failure_taxonomy.json`
- `contracts/schemas/failure_finding.schema.json`
- `contracts/ts/failures.ts`

The taxonomy should include:

- label id,
- label name,
- category,
- severity defaults,
- deterministic candidate rule if any,
- human review required boolean,
- description,
- examples,
- artifact fields needed to support the label.

### Failure Categories

Implement at least these labels:

- `schema_failure`
- `malformed_json_arguments`
- `missing_tool_call`
- `multiple_tool_calls`
- `unknown_tool`
- `illegal_action_attempt`
- `rules_invalid_action`
- `missing_required_public_message`
- `missing_required_private_thought`
- `openrouter_error`
- `openrouter_http_429`
- `openrouter_http_5xx`
- `openrouter_network_error`
- `fallback_used`
- `fallback_spiral`
- `retry_failed`
- `auction_over_list_price`
- `auction_far_over_list_price`
- `auction_under_list_win`
- `auction_dropout_with_cash`
- `direct_purchase_declined`
- `low_cash_purchase`
- `legal_build_available_then_end_turn`
- `build_while_low_cash`
- `hotel_conversion_released_houses`
- `mortgaged_complete_color_group`
- `unmortgaged_while_low_cash`
- `liquidation_sequence`
- `premature_bankruptcy_candidate`
- `bad_jail_timing_candidate`
- `trade_completed_opponent_monopoly`
- `trade_completed_self_monopoly`
- `accepted_negative_face_value_trade`
- `rejected_self_monopoly_trade_candidate`
- `public_private_mismatch_candidate`
- `false_factual_claim_candidate`
- `deception_candidate`
- `collusion_candidate`
- `kingmaking_candidate`
- `spite_play_candidate`
- `looping_candidate`
- `strategy_drift_candidate`.

Use `_candidate` suffix for labels that require human judgment.

### Failure Outputs

Per run:

- `failure_findings.jsonl`,
- `failure_summary.json`,
- failure counts embedded in `scorecard.json`,
- failure links in `trace_findings.jsonl`.

Per batch:

- `failure_summary.json`,
- `model_failure_breakdown.json`,
- `failure_leaderboard.json`,
- `review_queue.jsonl`.

### Human Review Link

Each candidate failure should support:

- `review_required`,
- `review_status`,
- `review_label`,
- `reviewer_id`,
- `reviewed_at`,
- `review_notes`,
- `adjudication_status`,
- `gold_label`.

### Acceptance Criteria

This section is complete only when:

- taxonomy is versioned,
- deterministic labels are generated automatically,
- subjective labels are candidates only,
- failure artifacts are written for runs and batches,
- trace and review workflows link to failure ids,
- tests cover taxonomy generation and aggregation.

## 8. Model Cards

Each tested model should have a persistent benchmark card derived from artifacts.

### Model Card Outputs

For each model in a batch, generate:

- `model_cards/<safe_model_id>.json`,
- `model_cards/<safe_model_id>.md`.

The JSON card should be the source of truth. Markdown is the human-readable rendering.
Markdown cards should not quote private-thought excerpts by default. Link to the
underlying replay/review artifacts instead. Full private thoughts remain available in
JSON artifacts for human review.

### Model Card Fields

Include:

- schema version,
- model id,
- model display name,
- OpenRouter route,
- provider route observations,
- date tested,
- benchmark version,
- engine version,
- contract version,
- scoring version,
- failure taxonomy version,
- prompt version if already known from existing config,
- note that prompts were unchanged,
- seed set,
- seat coverage,
- number of full games,
- number of micro scenarios,
- total decisions,
- total valid decisions,
- valid first-response rate,
- retry rate,
- fallback rate,
- average latency,
- p50/p90/p95 latency,
- total input tokens,
- total output tokens,
- total reasoning tokens if available,
- total cached tokens if available,
- total cost,
- cost per game,
- cost per decision,
- cost per score point,
- win rate,
- average rank,
- median rank,
- bankruptcy rate,
- average final net worth,
- average liquid net worth,
- average turns survived,
- full-game scorecard aggregate,
- microbench average score,
- microbench category breakdown,
- negotiation metrics,
- auction metrics,
- trade metrics,
- build/mortgage metrics,
- failure taxonomy counts,
- reviewed behavioral labels,
- top strengths based on metrics,
- top weaknesses based on metrics,
- representative winning run,
- representative losing run,
- representative trace findings,
- caveats,
- artifact links.

### Acceptance Criteria

This section is complete only when:

- batch runs can generate model cards,
- model cards are derived from artifacts, not handwritten,
- model cards include cost/tokens/reliability/performance/failure sections,
- markdown cards render cleanly,
- tests cover JSON card generation and markdown rendering.

## 9. Human Review Workflow Built Around Replay

Human review should be tightly connected to replay. Reviewers should be able to see
what happened, why the system flagged it, and what evidence supports the label.

### Review Queue

Generate `review_queue.jsonl` from:

- trace findings requiring review,
- failure candidates requiring review,
- subjective behavioral flags,
- high-impact decisions,
- random sample of normal decisions for calibration,
- replay mismatches,
- user-selected decisions.

Each queue item should include:

- queue item id,
- run id,
- batch id if any,
- decision id,
- turn index,
- player id,
- model id,
- finding ids,
- failure ids,
- severity,
- reason for review,
- suggested labels,
- artifact paths,
- replay URL/path if available,
- status.

### Review Labels

Persist labels in:

- `reviews/review_labels.jsonl`,
- `reviews/review_summary.json`,
- optionally batch-level `review_labels.jsonl`.

Each label should include:

- label id,
- queue item id,
- reviewer id,
- reviewed at,
- label version,
- selected labels,
- confidence,
- notes,
- adjudication status,
- gold label boolean,
- evidence references.

Reviewer identity policy:

- Use a simple `reviewer_id` string.
- Do not build authentication for this goal.
- Default to `local_reviewer` if the UI/API caller does not provide a value.
- Allow the reviewer id to be changed in UI review settings.
- Store reviewer id only for auditability, adjudication, and inter-rater agreement.

Subjective-label policy:

- Deception, collusion, false factual claim, public/private mismatch, kingmaking,
  spite-play, coercive threat, revenge-language, strategy drift, and similar behavioral
  labels are human-reviewed only.
- Do not use LLM classifiers for these labels in this goal.
- Rule-based analyzers may create conservative review candidates, but they must not
  promote subjective candidates to final labels without human review.

### Replay Review UI

Build a review surface that can show:

- board snapshot,
- event timeline,
- trace finding,
- failure candidate,
- decision point,
- legal actions,
- chosen action,
- public message,
- private thought,
- prompt artifact path or viewer,
- raw response artifact path or viewer,
- negotiation thread if relevant,
- cash/property/net-worth context from artifacts,
- reviewer label controls,
- notes field,
- save/reopen workflow,
- reviewed/unreviewed filters.

Do not expose review labels to the model. Review is post-hoc only.

### Acceptance Criteria

This section is complete only when:

- review queue generation works,
- labels are persisted as JSONL,
- review summary aggregates labels,
- replay UI can load queue items and save labels,
- subjective failure labels can be validated by humans,
- tests cover queue generation and label persistence.

## 10. Research-Facing Micro Scenario Schema Expansion

The micro suite already has carefully hand-picked prompt scenarios. Do not alter what
the model sees.

### Allowed Changes

Add top-level research metadata that helps researchers organize and analyze scenarios.
Acceptable fields include:

- `research_metadata`,
- `research_metadata.schema_version`,
- `research_metadata.visibility`,
- `research_metadata.review_status`,
- `research_metadata.review_priority`,
- `research_metadata.target_capability`,
- `research_metadata.target_behavior`,
- `research_metadata.strategic_tension`,
- `research_metadata.expected_failure_modes`,
- `research_metadata.taxonomy_tags`,
- `research_metadata.counterfactual_pair_id`,
- `research_metadata.counterfactual_role`,
- `research_metadata.paper_section`,
- `research_metadata.notes_for_researchers`,
- `research_metadata.source_claims`,
- `research_metadata.source_urls`,
- `research_metadata.created_by`,
- `research_metadata.last_reviewed_at`,
- `research_metadata.prompt_immutability_checked`.

Set `research_metadata.visibility` to something explicit like `research_only_never_prompt`.

First implementation target:

- Treat the existing 130 micro scenarios as enough for the first implementation.
- Review all existing scenarios one by one.
- Improve research-facing metadata, rubric clarity, review status, taxonomy tags, and
  source/notes fields where useful.
- Do not run a large scenario expansion during the first implementation unless there is
  an obvious coverage gap.
- If new scenarios are added, they must be strong, diverse, relevant, and useful.
- Scenario additions should increase coverage variety across auctions, buys, trades,
  trade responses, building, mortgage/unmortgage, liquidation, jail, post-turn
  sequencing, liquidity pressure, behavioral probes, and edge-case legality.
- New scenarios must maintain the same prompt pipeline and must be validated by
  contract tests.
- Scenario metadata should help researchers filter and review the suite; it must not
  provide model-facing hints.
- Do not change existing scenario `decision_point` payloads during this goal. Those are
  model-facing because they feed the prompt builder.

### Disallowed Changes

Do not:

- alter scenario decision points,
- alter existing prompt payload construction,
- add prompt condition variants,
- add prompt text,
- add model-facing hints,
- add rubric text to prompts,
- add source claims to prompts,
- add expected rationale to prompts,
- change `private_thought` or `public_message` requirements,
- change prompt artifact text except through normal existing logging.

### Prompt Immutability Test

Add a test that:

1. Loads an existing micro scenario.
2. Builds the exact prompt request artifact under `live_game`.
3. Adds research metadata.
4. Builds the prompt request artifact again.
5. Asserts the model-facing messages/tools are byte-for-byte identical, ignoring only
   artifact paths/timestamps if needed.

### Acceptance Criteria

This section is complete only when:

- micro schema accepts research metadata,
- TypeScript types match,
- contract examples are updated,
- micro suite loading still works,
- prompts are proven unchanged by tests,
- UI can filter/display research metadata without sending it to LLMs.

## 11. UI And Artifact Upgrades

The UI should become a research dashboard and replay/review tool, while staying
render-only.

### Routes

Add or improve routes such as:

- `/`
- `/micro`
- `/micro/detail`
- `/runs`
- `/runs/:runId`
- `/runs/:runId/replay`
- `/runs/:runId/review`
- `/batches`
- `/batches/:batchId`
- `/models/:modelId`

Use the existing frontend architecture and styling. Do not build a marketing page.

### Run Replay View

The replay view should show:

- the same basic board-centered visual structure as the main live game UI,
- improved navigation for moving quickly through long games,
- board state from snapshots,
- event timeline,
- turn selector,
- decision selector,
- playback controls,
- skip controls for important decisions, trace findings, failures, negotiations,
  auctions, bankruptcies, and model decisions,
- current event details,
- action details,
- decision details,
- legal actions shown as logged artifacts,
- public message,
- private thought,
- prompt/response artifact viewer,
- OpenRouter usage details,
- trace findings,
- failure findings,
- review labels,
- replay verification status.

Replay and review should be combined when practical. A reviewer should be able to move
from a replay event or trace finding directly into labeling without opening a separate
tool.

### Batch Dashboard

The batch dashboard should show:

- batch config,
- run status,
- leaderboard,
- model comparison,
- seat breakdown,
- seed breakdown,
- replay pass/fail status,
- cost and token charts/tables,
- failure taxonomy breakdown,
- trace finding summary,
- links to model cards,
- export/download links.

### Research Artifacts

The UI/API should expose:

- `scorecard.json`,
- `scorecard_players.json`,
- `trace_findings.jsonl`,
- `trace_summary.json`,
- `failure_findings.jsonl`,
- `failure_summary.json`,
- `usage.json`,
- `cost_report.json`,
- `replay_report.json`,
- `review_queue.jsonl`,
- `review_labels.jsonl`,
- `model_cards/*.json`,
- `model_cards/*.md`.

### UI Constraint

The UI must not compute legality, mutate game state, infer rules, or decide whether a
model action was legal. It may render and filter artifacts, and it may display
post-hoc analyzer outputs.

### Acceptance Criteria

This section is complete only when:

- run replay can be opened from local run artifacts,
- batch dashboard can be opened from batch artifacts,
- trace/failure/review/cost artifacts are visible,
- review labels can be saved,
- frontend build passes,
- no game rules are introduced into frontend logic.

## 12. Documentation And Versioning

The implementation should be usable by someone who did not write it.

### Required Docs

Add or update:

- README section for full-game batch runs,
- README section for micro-suite batch runs,
- README section for replay verification,
- README section for trace analyzer,
- README section for failure taxonomy,
- README section for human review workflow,
- README section for cost/token accounting,
- README section for model cards,
- artifact reference document,
- schema/versioning notes,
- example batch config,
- example review workflow.

### Versioned Components

Add version fields where useful:

- scorecard version,
- replay report version,
- trace analyzer version,
- failure taxonomy version,
- usage accounting version,
- model card version,
- batch protocol version,
- review label version,
- micro research metadata version.

### Acceptance Criteria

This section is complete only when:

- docs describe how to run each new capability,
- docs describe every new artifact,
- docs state the no-prompt-change constraint,
- docs state that micro metadata is research-only,
- docs state how costs are computed,
- docs state limitations and missing usage behavior.

# Final Verification Checklist

Before the goal can be marked complete, run the strongest feasible verification suite.

At minimum:

```powershell
node contracts/validate-contracts.mjs
cd python
uv run ruff check .
uv run mypy .
uv run pytest -q
cd ..
cd frontend
yarn build
```

Also run targeted smoke tests:

- one mock or deterministic full-game run,
- one full-game batch with at least two seeds or two seat assignments,
- one micro-suite or small selected micro batch,
- replay verification on at least one completed full-game run,
- trace analyzer on at least one completed full-game run,
- failure taxonomy generation on at least one completed full-game run,
- model card generation on one batch,
- replay UI route load,
- review queue route/load if UI support exists.

If any command cannot be run, record why in `implementation_status.md` and in the
final response. Do not call the implementation complete if a required capability is
missing or untested.

# Explicit Out-Of-Scope Items For This Goal

Do not implement:

- prompt condition framework,
- prompt ablations,
- prompt changes,
- guardrail condition framework,
- guardrail ablations,
- model-facing heuristic value models,
- orchestrator research framework,
- real estate/asset-management benchmark,
- new Monopoly house rules,
- direct vendor API clients,
- any feature that changes legal action generation unless explicitly required by a
  replay/telemetry contract and tested.

# Suggested Implementation Phases

Use this ordering unless the current codebase makes a different order clearly better.

1. Add artifact/version foundations and run config persistence.
2. Implement scorecard artifacts and tests.
3. Implement replay verification reports and tests.
4. Implement OpenRouter usage normalization, pricing snapshots, and cost reports.
5. Expand batch config/artifacts, resume behavior, and batch summaries.
6. Implement seeded seat permutation support.
7. Implement trace analyzer artifacts and tests.
8. Implement failure taxonomy artifacts and tests.
9. Implement model card generation.
10. Expand micro schema with research-only metadata and prompt immutability tests.
11. Add API endpoints for artifacts, replay, batches, reviews, and model cards.
12. Build replay/batch/review UI views.
13. Update docs.
14. Run full verification and fix failures.

# Progress Discipline

The agent should keep an explicit checklist while working. A good progress file shape:

```markdown
# Implementation Status

## Current Phase

...

## Completed

- ...

## In Progress

- ...

## Remaining

- ...

## Blockers

- ...

## Verification

- ...
```

After context compaction or continuation, the agent should read:

- `AGENTS.md`,
- `plan.md`,
- `implementation_status.md` if it exists,
- recent `git status --short`,
- and then continue from the latest incomplete phase.

# Remaining Questions To Resolve With The User

There are no remaining blocking policy questions for the first implementation.

The goal agent should proceed using the defaults in this file. Only ask the user if a
new decision would change prompts, alter model-facing data, change Monopoly rules,
exceed the budget policy, or require a subjective-label classifier.

Optional future choices that should not block implementation:

1. Whether to add private-thought excerpts to Markdown model cards later.
2. Whether to expand beyond the existing 130 micro scenarios after the first review
   pass.
3. Whether to add microbench replay/review UI after full-game replay/review is working.
4. Whether to revise the experimental combined scoreboard formula after seeing initial
   batch results.
