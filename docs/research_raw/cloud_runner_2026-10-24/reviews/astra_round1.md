# MonopolyBench cloud execution plan, independent review round 1

Prepared on 24 October 2026 from `/Users/kushagra/CS-Projects/MonopolyBench` at commit `c370c87c`. This is an investigation and implementation plan. No repository files were changed, no tests or generators were run, and no authenticated or paid provider calls were made. Public model catalog and pricing GET requests were used. The user's uncommitted roadmap and research files remain authoritative.

## Recommendation

Deploy one persistent Linux server with the built React frontend, the FastAPI API, a small job supervisor, SQLite, and up to five independent Python game processes. Keep active files on its persistent disk and copy immutable execution records and artifacts to a private Cloudflare R2 bucket during each run. Use R2 for complete downloads and long-term retention. Start with an 8 GB server because final analysis loads whole logs into memory. Measure actual memory before choosing a smaller machine.

My first choice is a Hetzner CX33 in Europe if it is available at the published price. Its base monthly price is $9.99 or EUR 8.49 before tax and IPv4. Allow about $13 to $16 per month for the server, backups, an IPv4 address if needed, and a modest domain allowance. R2 should cost almost nothing at the first campaign's scale. Availability and the final invoice need checking. My managed fallback is one Fly Machine with 4 GB RAM and a persistent volume, initially about $28 to $32 monthly in a low-cost region, with all five game processes inside that machine. Railway is reasonable when deployment convenience matters more than a fixed bill. A dedicated Postgres service is unnecessary at this scale.

The prerequisite is durable execution, not a larger database. Five tabs currently control one game. A new start stops the previous game. Existing recovery works at a clean recorded boundary, but it does not cover arbitrary process crashes. The cloud release needs a durable job ledger, one writer per run, crash-safe persistence, restart reconciliation, and shared spending controls.

The four requested models exist. All expose low, medium, and high effort. Use a shared `medium` setting by default, subject to the approved campaign. It is a common request setting, not equal reasoning compute. The user's GPT-6.1 Sol price differs from today's catalog. The requested $10/$50 prices imply about $29 per game using the five historical frontier games as templates. Today's standard OpenAI route price of $2/$10 lowers that estimate to about $11.41. These are workload projections, not quotes for the new models' behavior.

A four-hour finish cannot be guaranteed. Six of the eight saved games span about 1.28 to 3.95 hours between first request and last response. Two span 8.93 and 15.49 hours. A cloud host removes laptop sleep as a failure source, but cannot guarantee provider latency or a bankruptcy outcome before a fixed time.

## Scope and authority

The roadmap requires a tested new campaign contract before execution and preserves the old fail-closed gates. See `research_direction.md:25`, `research_direction.md:34`, `docs/two_paper_plan.md:155`, and `docs/two_paper_plan.md:177`. The present instruction expressly forbids spending during this round. The later product should make an exact roster, execution window, spending ceiling, and campaign contract reviewable before paid launch. General intent to fund games is not an approved unlimited campaign budget.

This plan treats reasoning selection and the requested model/provider roster as requested configuration work. It does not authorize new prompt text, memory behavior, tool schemas, corrective retry wording, fallback policy, sampling controls, or output-token caps. Any such proposal needs a separate explicit decision and a versioned experimental amendment. Operational metadata stays out of model inputs.

`implementation_status.md:8` describes an older implementation milestone as complete. It does not establish that the new research roadmap, cloud execution, or arbitrary crash recovery is complete. The eight E0 games remain exploratory evidence. The 48-game, two-roster design in `docs/two_paper_plan.md:136` is provisional. The current request supplies one four-model roster, not a second roster or approval for 48 paid games.

## Current launch and execution paths

| Path | What the code does | Evidence |
| --- | --- | --- |
| Live API | `POST /run/start` builds four players, chooses a seed once when absent, and calls the global manager. Defaults are 200 turns, 20 trade exchanges, and 200 auction actions. | `python/apps/api/src/monopoly_api/main.py:63`, `main.py:107`, `main.py:133` |
| API manager | Holds one runner, one asyncio task, one snapshot, one decision index, and one set of WebSocket subscribers in memory. A different start cancels the active run. | `python/apps/api/src/monopoly_api/run_manager.py:30`, `run_manager.py:73`, `run_manager.py:195`, `run_manager.py:225` |
| Headless CLI | `python -m monopoly_arena.run` uses `asyncio.run`, initializes files, and awaits one `LlmRunner`. It supports an explicit run ID and output root. Its default turn cap is 20. | `python/packages/arena/src/monopoly_arena/run.py:46`, `run.py:98` |
| Batch CLI | `python -m monopoly_arena.batch_run` expands seeds and seat assignments, snapshots metadata, then awaits one game at a time. `concurrency` is recorded but this loop is sequential. | `python/packages/arena/src/monopoly_arena/batch_run.py:28`, `batch_run.py:114`, `batch_run.py:161`, `batch_run.py:777` |
| Campaign CLI | `python -m monopoly_arena.long_campaign` validates registered rosters/seeds, creates a complete matrix, runs preflight and credit gates, and executes fixed rows sequentially. | `python/packages/arena/src/monopoly_arena/long_campaign.py:60`, `long_campaign.py:127`, `long_campaign.py:181`, `long_campaign.py:2588` |
| Microbench | Uses the shared resolver for a frozen scenario. It is separate from full games and should not become a shortcut around cloud spending authorization. | `python/packages/microbench/src/monopoly_microbench/runner.py:40`, `runner.py:83` |

`LlmRunner` creates its own engine, player map, prompt memory, resolver, pause event, and applied-decision set. It advances the engine synchronously to a decision, awaits OpenRouter, validates, applies the chosen action, writes records, and yields events. See `python/packages/arena/src/monopoly_arena/llm_runner.py:48`, `llm_runner.py:300`, and `llm_runner.py:331`.

The current API task keeps running when a WebSocket disconnects. Disconnect only unsubscribes the viewer in `python/apps/api/src/monopoly_api/main.py:487`. That already separates a browser session from game lifetime while the server process stays alive. It does not survive laptop sleep when the server runs on that laptop, or an API process restart.

### Five games in one process

The reusable runner can plausibly support five independent instances in one asyncio loop. This is a code-level assessment, not a load-test result. The shipped API, batch runner, and campaign runner do not expose that behavior today.

- OpenRouter uses `httpx.AsyncClient`, asynchronous POSTs, and asynchronous retry sleeps. It is not a blocking requests client. See `python/packages/arena/src/monopoly_arena/openrouter_client.py:25`, `openrouter_client.py:105`.
- Each engine has a private `DeterministicRng`, state, deck order, event sequence, and pending decision. The RNG uses an instance of `random.Random(seed)`. See `python/packages/engine/src/monopoly_engine/engine.py:65` and `rng.py:10`.
- Prompt memory is per runner. There is no shared game RNG in the inspected path. Environment variables and default configuration files are process-wide, so per-run settings must be resolved before launch rather than changed in the environment during execution.
- File serialization, engine work, summary construction, replay verification, scorecards, and trace analysis are synchronous. Several read whole JSONL files into Python objects. They can block other games and the API in one event loop. Under ordinary GIL-enabled CPython, threads also do not provide parallel execution for this Python work. Separate processes do, although actual CPU demand still needs measurement. See `llm_runner.py:235`, `python/packages/telemetry/src/monopoly_telemetry/summary.py:14`, and `python/packages/arena/src/monopoly_arena/replay_verification.py:73`.
- The API decision index retains resolved entries, including large prompt/response structures, in memory. See `python/apps/api/src/monopoly_api/decision_index.py:42` and `decision_index.py:69`.
- Browser sends are awaited in the runner's event path without an explicit send timeout. A slow viewer can delay progress. See `python/apps/api/src/monopoly_api/run_manager.py:181` and `run_manager.py:210`.
- File paths isolate runs only when IDs are unique. There is no cross-process claim or writer lock. The API's ID hash excludes reasoning and provider settings. The CLI hash also excludes its turn cap. See `run_manager.py:243` and `python/packages/arena/src/monopoly_arena/run.py:17`.

Five subprocesses remove event-loop coupling and contain worker failures. They also keep CPU-heavy finalization away from the API. Five separate API deployments would be an emergency workaround, but would duplicate configuration, authentication, budgets, exports, and campaign logic. I do not recommend it as the finished design.

## Recovery today and the missing guarantees

There is a real recovery path. `POST /run/recover` reads the original configuration, events, actions, and decisions. It rebuilds player prompts from logged system messages, constructs a new runner, replays actions from the seed, compares the full canonical event stream, and rebuilds prompt memory. See `python/apps/api/src/monopoly_api/main.py:138`, `run_manager.py:105`, `run_manager.py:978`, and `python/packages/arena/src/monopoly_arena/llm_runner.py:141`.

The existing unit test verifies a clean prefix that ends at a pending decision. It does not inject a crash between each write or resume a paid request in flight. See `python/apps/api/tests/test_llm_runner.py:41` and `test_run_manager_idempotency.py:160`.

The following gaps matter for unattended execution.

1. Applying an action, appending `actions.jsonl`, appending the resolved decision, and emitting each event are separate operations. A crash can leave an action without all its events or a response without an applied action. Strict replay then rejects the prefix. See `llm_runner.py:335` through `llm_runner.py:370`.
2. JSONL appends do not fsync and JSON files use direct `write_text`. There is no transaction across files or durable commit marker. The recovery JSONL reader silently skips malformed lines, which is inappropriate for a strong recovery validator. See `python/packages/telemetry/src/monopoly_telemetry/writer_jsonl.py:8`, `run_files.py:90`, and `python/apps/api/src/monopoly_api/run_manager.py:960`.
3. A provider response can be paid for but lost before persistence. No local transaction can make an external provider request exactly once. The current retry policy can also resend a timed-out request. This must be accounted for as an uncertain call, not assumed free or silently erased.
4. Recovery needs a system prompt observed for every non-baseline player. A very early crash can leave a player without any recoverable prompt. Freeze the complete resolved player configuration before the first paid call, including prompts in protected artifacts.
5. The runner reconstructs from actions and seed. Snapshots do not contain RNG state, deck state, pending payments, and all private engine control state. Do not implement resume by loading the latest `state/turn_*.json`. See `python/packages/engine/src/monopoly_engine/models.py:166` and `engine.py:65`.
6. The API rejects recovery whenever `summary.json` exists, yet the runner writes the summary before usage, replay, traces, and the final manifest. A crash during finalization needs a separate idempotent finalization job. See `run_manager.py:114` and `llm_runner.py:249`.
7. The campaign runner only skips completed cells. It refuses an incomplete nonempty run directory. Its `resume` option is not mid-game recovery. See `python/packages/arena/src/monopoly_arena/long_campaign.py:760`.
8. There is no startup job scan, lease, heartbeat, deployment drain, worker ownership record, or automatic recovery coordinator. A new Uvicorn process creates an empty manager.
9. There is no persisted in-flight resolver state that guarantees reuse of a saved response, preservation of attempt numbers, and preservation of corrective retry wording after a crash.

The cloud contract should promise exactly-once application of committed engine actions and explicit accounting for uncertain external requests. It should not promise identical future LLM generations after an unrecorded provider response is lost.

## Complete artifact inventory

The default write root is `runs/<run_id>/`. The raw wire-text root is `quality_check/<run_id>/`, computed as `runs_dir.parent / "quality_check" / run_id`. Mount the parent data directory, not just `runs`, or these raw files can remain ephemeral. See `python/packages/telemetry/src/monopoly_telemetry/run_files.py:214`.

### During initialization and play

| Files | Frequency and writer |
| --- | --- |
| `run_config.json`, `players.json`, `seat_assignment.json` | Once at fresh runner construction, `python/packages/arena/src/monopoly_arena/llm_runner.py:442`. |
| `events.jsonl` | One append per emitted engine event, `python/packages/telemetry/src/monopoly_telemetry/run_files.py:68`. Public messages and private thoughts are also recorded in the event/decision records. |
| `actions.jsonl` | One append per applied decision, `llm_runner.py:340` and `run_files.py:116`. |
| `decisions.jsonl` | Requested/resolved records with prompts, response attempts, validation, retry/fallback metadata, and applied event references, `python/packages/arena/src/monopoly_arena/decision_resolver.py:424` and `llm_runner.py:351`. Count resolved decisions, not all lines, when estimating game length. |
| `state/turn_0000.json` and later canonical turn files | At initialization, decision requests, turn ends, and game end. First file for a turn is preserved. Different later snapshots get decision/snapshot variant names. See `run_files.py:71` and `llm_runner.py:227`. |
| `prompts/<decision-and-attempt>_system.txt` | Per provider attempt, when available. |
| `prompts/<decision-and-attempt>_user.json` | Per provider attempt, when available. |
| `prompts/<decision-and-attempt>_tools.json` | Per provider attempt, when available. |
| `prompts/<decision-and-attempt>_response.json` | Per provider attempt, including raw provider response content. |
| `prompts/<decision-and-attempt>_parsed.json` | Per provider attempt, parsed calls, validation, selected action and resolution data. These five files are written by `run_files.py:119` and `run_files.py:154`, called by `decision_resolver.py:117`. |
| `quality_check/<run_id>/<decision-and-attempt>_request.txt` and `_response.txt` | Serialized wire payload and response text, `run_files.py:187`, `decision_resolver.py:240`, and `decision_resolver.py:313`. Missing responses remain missing rather than invented. |

The filename helpers preserve attempt indexes and have a compact fallback for long decision IDs. Do not rename them during export. A successful ordinary attempt generally adds five prompt files and two quality files, plus log rows and snapshots. Automated baseline decisions legitimately have no paid provider attempts.

### On normal game completion

The ordered finalization calls are in `python/packages/arena/src/monopoly_arena/llm_runner.py:235` through `llm_runner.py:263`.

| Writer | Files |
| --- | --- |
| `run_files.py:90`, `summary.py:14` | `summary.json`. |
| `python/packages/telemetry/src/monopoly_telemetry/usage.py:20` | `usage.json`, `usage_decisions.jsonl`, `usage_attempts.jsonl`, `cost_report.json`. These rollups are currently generated after the game, not a live hard spending ledger. |
| `llm_runner.py:274` | `pricing_snapshot.json`, currently obtained at the end of a standalone run. |
| `python/packages/telemetry/src/monopoly_telemetry/experiment.py:144` | `experiment_manifest.json`, `review_cost_aggregate.json`, `review_cost_calls.jsonl`. |
| `python/packages/telemetry/src/monopoly_telemetry/scorecard.py:39` | `scorecard.json`, `scorecard_players.json`, `scorecard_decisions.jsonl`, `scorecard_events.jsonl`. |
| `python/packages/arena/src/monopoly_arena/replay_verification.py:52` | `state_replay_report.json`, `artifact_replay_report.json`, `replay_report.json`, `replay_diff.json`, `event_hashes.json`, `replay_steps.jsonl`, `replay_flags.jsonl`, `replay_navigation.json`. |
| `python/packages/telemetry/src/monopoly_telemetry/analysis.py:16` | `trace_findings.jsonl`, `trace_summary.json`, `failure_findings.jsonl`, `failure_summary.json`, `timeline.json`, `decision_index.json`, `turn_index.json`, `player_timelines.json`, `negotiation_threads.jsonl`, `auction_threads.jsonl`, `asset_flow.jsonl`, `cash_flow.jsonl`, `behavioral_flags.jsonl`, `review_queue.jsonl`. |
| `run_files.py:204` | `artifact_manifest.json`. Its known-file list is at `run_files.py:298`. It hashes selected top-level files but does not recursively inventory `prompts/`, `state/`, or the sibling quality directory. |
| Review endpoints, `python/apps/api/src/monopoly_api/run_manager.py:389` | `review_queue.jsonl`, `reviews/review_labels.jsonl`, `reviews/review_summary.json` when humans add review data. The artifact reference's shorthand root review paths differ from these actual nested paths. |
| Campaign billing guard, `long_campaign.py:907` | `billing_policy_violation.json` on a routing or billing violation. Preserve it on failed runs. |

`model_cards/` is a declared `RunFiles` location. Routine per-model cards are batch outputs, not a guarantee that every standalone run writes that directory. Empty or unavailable files should be identified in a manifest rather than silently manufactured.

### Saved-game and later analysis layout

Existing saved games use `<saved-game>/run/`, `<saved-game>/quality_check/`, `<saved-game>/analysis/`, and `saved_game_manifest.json`. Some also contain archives, review materials, `.gitattributes`, and analysis ZIPs. Preserve these when importing historical games.

`scripts/standardize_saved_games.py:580` builds the standard analysis. It writes the following groups.

- `analysis/tables/` contains `run_summary.csv`, `players.csv`, `model_usage.csv`, `per_call_usage.csv`, `per_turn_usage_by_player.csv`, `per_turn_usage_total.csv`, `decisions.csv`, `decision_type_counts.csv`, `actions.csv`, `events.csv`, `event_counts.csv`, `events_by_turn.csv`, `state_by_turn_player.csv`, `property_holdings_by_turn.csv`, `bank_inventory_by_turn.csv`, `trace_findings.csv`, `failure_findings.csv`, `review_queue.csv`, `cash_flow.csv`, `asset_flow.csv`, `auction_threads.csv`, `negotiation_threads.csv`, `top_costliest_calls.csv`, `top_slowest_calls.csv`, `top_output_token_calls.csv`, and `top_reasoning_token_calls.csv`. The writing map is at `standardize_saved_games.py:744`.
- `analysis/coverage/` contains `artifact_presence.csv`, `file_inventory.csv`, and `file_inventory_summary.csv`, written at `standardize_saved_games.py:797`.
- `analysis/plots/` contains `cash_by_turn.png`, `net_worth_estimate_by_turn.png`, `property_value_by_turn.png`, `building_value_by_turn.png`, `mortgage_liability_by_turn.png`, `property_count_by_turn.png`, `houses_by_turn.png`, `hotels_by_turn.png`, `bank_inventory_by_turn.png`, `cost_by_turn.png`, `tokens_by_turn.png`, `calls_by_turn.png`, `cost_by_model.png`, `calls_by_model.png`, `reasoning_tokens_by_model.png`, `total_tokens_by_model.png`, `cumulative_cost_by_call.png`, `cost_per_call.png`, `latency_per_call.png`, `reasoning_tokens_per_call.png`, `output_tokens_per_call.png`, `event_counts.png`, and `decision_type_counts.png`. Plots depend on the relevant source data being present. See `standardize_saved_games.py:854`.
- `analysis/reports/` receives `analysis_report.md`, `coverage_report.md`, and `data_dictionary.md`, written at `standardize_saved_games.py:1037`, `:1065`, and `:1097`.
- `analysis/expanded_metrics/` receives `summary.json`, `semantic_metric_status.json`, `player_metrics.csv`, `trade_episodes.csv`, `trade_player_episodes.csv`, `auction_episodes.csv`, `auction_player_episodes.csv`, `mortgage_episodes.csv`, `cash_ledger.csv`, `cash_reason_metrics.csv`, `decision_metrics.csv`, `metric_definitions.md`, and `expanded_metrics_report.md`. See `python/packages/telemetry/src/monopoly_telemetry/expanded_metrics.py:15` and `:96`.
- `analysis/manifest.json` and `saved_game_manifest.json` describe the package. `standardize_saved_games.py:1121` makes an analysis-only ZIP. That ZIP excludes the raw run and quality trees. It is not the complete export the user requested.
- Optional negotiation analysis writes `negotiation_offers.csv`, `negotiation_tactics.csv`, `negotiation_episodes.csv`, `model_tactic_frequency.csv`, `model_run_tactic_frequency.csv`, `model_negotiation_summary.csv`, `negotiation_tactic_codebook.json`, and `manifest.json`. See `scripts/analyze_negotiation_tactics.py:778`.
- Existing historical games also contain manual or separately generated `analysis/review/`, `analysis/quality/`, and `analysis/manifests/` files. These are not all emitted by the normal game runner. Examples include chronological reviews, promise lifecycle tables, case studies, source hashes, and call reconciliation. Cloud exports must recursively preserve these files without pretending the ordinary finalizer creates human review.

Batch outputs remain under `runs/batches/<batch_id>/`; campaign outputs remain under `runs/campaigns/<campaign_id>/`. Include their configs, seed/seat/run matrices, execution order, preflight and credit snapshots, planned-cell ledger, results, budget report, replay aggregates, model cards, tables and paper report in a campaign export. See `docs/artifact_reference.md:59`, `python/packages/arena/src/monopoly_arena/batch_artifacts.py`, and `long_campaign.py:262`. Do not duplicate all campaign data into every game directory. Export a campaign package with its member games and relative links.

## Measured storage, game length, and cost

I measured actual file byte lengths, recursive file counts, and `du -sk` allocation. Units below are MiB, with 1 MiB equal to 1,048,576 bytes. Core means the saved game's `run/` plus `quality_check/`. Saved allocation includes analysis, ZIPs, and any nested history. R172 has a nested archive, so its total is not a normal raw-game requirement.

| Game label and run ID | Turns | Decisions / attempts | Core MiB | Core files | Saved allocated MiB / files | Recorded cost | Request span hours |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| R115, `mock-321229807-87ca99d7` | 115 | 366 / 377 | 47.62 | 3,163 | 62.51 / 3,253 | $14.61 | 1.96 |
| R163, `mock-1038910349-f66fa07c` | 163 | 364 / 371 | 44.33 | 3,167 | 58.43 / 3,259 | $12.06 | 1.39 |
| R166, `mock-3676466999-527872e4` | 166 | 488 / 502 | 66.21 | 4,212 | 86.00 / 4,304 | $21.91 | 15.49 |
| R172, `mock-2413970733-53b199c1` | 172 | 613 / 631 | 79.30 | 5,246 | 167.22 / 7,406 | $24.60 | 8.93 |
| R191, `mock-83265-81ed4937` | 191 | 583 / 604 | 78.07 | 5,043 | 115.14 / 5,146 | $27.71 | 3.95 |
| Mini154, `mock-24591-46c1eb90` | 154 | 396 / 401 | 55.08 | 3,400 | 73.73 / 3,490 | $4.65 | 1.34 |
| Mini157, `mock-64394-c3bb8d94` | 157 | 346 / 355 | 48.69 | 3,029 | 62.02 / 3,128 | $4.04 | 1.28 |
| Mini273, `mock-44910-42ec35c5` | 273 | 540 / 549 | 75.50 | 4,697 | 110.22 / 4,798 | $4.24 | 1.65 |

Every listed game ended with `BANKRUPTCY`. The frontier games used medium effort and a 400-turn cap, except R191 at 600. Mini games used medium effort with 500 or 600 turns. Turns are engine player turns, not complete four-player rounds.

The duration column uses the earliest `request_start_ms` and latest `response_end_ms` inside resolved decisions. It excludes later artifact generation and can include laptop suspension or pauses. R166 has one recorded attempt lasting 44,124,652 ms, about 12.26 hours. R172's total request latency is 3.51 hours despite an 8.93-hour span. These are evidence of elapsed-time irregularities, not proof that a provider spent that long generating. Do not derive elapsed time from deterministic event `ts_ms` values.

The whole checked `runs/` directory uses about 180 MiB, `saved_games/` about 791 MiB, and the top-level `quality_check/` about 59 MiB. The eight saved packages total 34,784 files. Some local runs are only smoke tests or interrupted games, so total directory size is not a per-game estimate.

Three additional completed local examples are useful checks.

| Directory under `runs/` | Turns | Resolved decisions | Allocated MiB | Files | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| `mock-22567-da4680b6` | 200 | 428 | 34.09 | 2,774 | All 428 decisions fell back. It is not evidence of successful paid model play. |
| `mock-39153-ed400138` | 50 | 150 | 17.95 | 1,011 | Capped smoke game. |
| `mock-89623-7b535b81` | 50 | 197 | 24.09 | 1,283 | Capped smoke game. |

Those local sizes exclude their sibling quality directories. The complete saved packages give the better retention estimate.

The mean core game is 61.85 MiB. Historical complete packages have 54.8 to 160.9 million logical bytes, with a mean of about 88.0 million. A practical initial allowance is 100 to 250 MB per full game, including analysis, manifests, operational records and export overhead. Budget 0.5 to 1.25 GB for five completed games, and reserve at least 2.5 GB of working space for those five because staging, backups, and ZIP creation temporarily duplicate data. Use a 20 GB data allocation at minimum; an 80 GB VPS disk is comfortable for the first campaign if monitored. A 400-turn negotiation-heavy game may exceed this range. Do not enforce a storage quota by silently dropping logs.

The eight games average 462 decisions and 473.75 provider attempts. Mean input is 2,066,659 tokens and mean completion is 492,685 tokens per game. Weighted per decision, including corrective retries, that is about 4,473 input and 1,066 completion tokens. Five games imply about 2,310 decisions, 2,369 logical attempts, 10.33 million input tokens and 2.46 million completion tokens at this historical workload. Transport retries can add calls beyond the resolver attempt count.

### Cost projection at the user's prices

The better primary template for the requested frontier roster is the five frontier games. For each old provider family, I kept its measured input and completion totals and substituted the requested new model price. Formula: input tokens divided by one million times input price, plus completion tokens divided by one million times output price. I did not add reasoning tokens again because the recorded completion totals already carry the provider's completion accounting. I did not assume caching discounts, free BYOK use, unchanged latency, or unchanged behavior.

| New seat model | Mean historical frontier input / completion tokens | Requested price per million | Projected cost per mixed game | Five mixed games |
| --- | ---: | ---: | ---: | ---: |
| Claude Opus 5.5 | 753,001 / 80,616 | $4 / $20 | $4.62 | $23.12 |
| GPT-6.1 Sol | 743,998 / 287,553 | $10 / $50 | $21.82 | $109.09 |
| Gemini 4 Argon | 446,342 / 63,547 | $2 / $10 | $1.53 | $7.64 |
| Grok 4.7 | 313,617 / 44,532 | $2 / $6 | $0.89 | $4.47 |
| Total | 2,256,958 / 476,248 | Four seats combined | $28.86 | $144.32 |

These are contributions to a game with one seat per model, not four homogeneous games. Historical models received unequal numbers of decisions because survival and interactions differed. The five frontier templates project to $16.27, $21.94, $33.04, $34.55, and $38.53. Using all eight templates instead gives a mean of $25.08 and $125.42 for five games. Historical actual cost totals $113.84 across the eight games. R191 has one missing-usage attempt, so its recorded total is incomplete.

At today's standard GPT-6.1 Sol endpoint price, its projected contribution is $4.36. The primary mixed-game estimate becomes $11.41, or $57.05 for five. Across the five frontier templates that price produces about $7.53 to $15.81 per game. A 50% planning contingency gives about $86 for five at catalog rates, or $216 at the user's rates. A hypothetical $50 per-game and $250 five-game ceiling would provide more room, but neither ceiling is approved by this plan. A main campaign needs a separate budget. For scale, 24 games at the primary mean imply $274 at catalog rates or $693 at the user's rates, before contingency, funding fees, and taxes.

Raw measurements are in `/tmp/mb-cloud-plan/run_measurements.json`. They identify each complete saved-game directory and preserve the provider-level token totals used in these calculations.

## Model configuration and current public availability

The public catalog was fetched without an API key. Exact snapshots are saved in `/tmp/mb-cloud-plan/openrouter-models.json`, `selected_models.json`, and four endpoint JSON files. All four entries advertise `reasoning`, `tools`, and `tool_choice`. All support the shared intersection `low`, `medium`, `high`. [OpenRouter model catalog](https://openrouter.ai/api/v1/models)

| Requested ID | Context tokens | Standard endpoint output maximum | Native catalog effort choices | Price verified on requested provider |
| --- | ---: | ---: | --- | --- |
| `anthropic/claude-opus-5.5` | 1,000,000 | 128,000 | low, medium, high, xhigh, max | $4 / $20, provider tag `anthropic`. [Endpoint](https://openrouter.ai/api/v1/models/anthropic/claude-opus-5.5/endpoints) |
| `openai/gpt-6.1-sol` | 1,050,000 | 128,000 | low, medium, high, xhigh, max | $2 / $10 on `openai`, not the requested $10 / $50. [Endpoint](https://openrouter.ai/api/v1/models/openai/gpt-6.1-sol/endpoints) |
| `google/gemini-4-argon` | 1,048,576 | 943,718 | low, medium, high | $2 / $10 on `google-ai-studio`. The endpoint also exposes discount and internal-reasoning metadata. Preserve it without assuming an extra discount. [Endpoint](https://openrouter.ai/api/v1/models/google/gemini-4-argon/endpoints) |
| `x-ai/grok-4.7` | 500,000 | 450,000 | low, medium, high, xhigh | $2 / $6 on `xai`. [Endpoint](https://openrouter.ai/api/v1/models/x-ai/grok-4.7/endpoints) |

The output maxima are catalog limits, not recommended budgets. OpenAI lists higher prices above 272,000 input tokens; xAI above 200,000. Current historical average prompts are far below those thresholds, but the cost estimator must still understand threshold pricing.

The repo already supports `PlayerConfig.reasoning` and `PlayerConfig.provider`. It accepts effort only, with low, medium, or high, and rejects explicit thinking-token budgets. Provider controls are `only`, `order`, `allow_fallbacks`, and `require_parameters`. See `python/packages/arena/src/monopoly_arena/player_config.py:49` and `player_config.py:269`.

The shared resolver forwards reasoning and provider routing on the initial attempt and the corrective retry. It uses `tool_choice="auto"` and `parallel_tool_calls=False`. It does not send temperature, top-p, model seed, or output-token limits. See `python/packages/arena/src/monopoly_arena/decision_resolver.py:215` and `:289`, plus `openrouter_client.py:50`. Transport retries default to two, separate from the one model-output corrective retry. The current HTTP timeout defaults to 30 seconds. This is an HTTP operation timeout, not an overall multi-hour job timeout.

The normal API `PlayerSpec` does not expose reasoning or provider fields. Config-file defaults supply them. New IDs are absent from the hardcoded default-provider map. Merging a new model ID into an existing configured seat can preserve an old seat's provider unless the server resolves the full tuple explicitly. See `python/apps/api/src/monopoly_api/main.py:63`, `player_config.py:52`, and `player_config.py:152`. The new create-game endpoint should accept a registered roster and a supported common effort, then resolve provider pins server-side. Do not trust arbitrary browser-supplied routing JSON.

An important preflight mismatch needs a scoped fix. Claude Opus 5.5's current endpoint advertises `auto` tool choice but not forced `required` or a named function. Production MonopolyBench uses `auto`, so that metadata does not prove the production request is incompatible. The old preflight forces a named function in `scripts/research/capture_openrouter_preflight.py:288`. A new contract must validate the actual production request shape and require a valid returned tool action. It must not weaken the game tool requirement or mark the old forced-call gate as passed without evidence.

Same effort does not mean the same reasoning-token count, latency, cost, or internal computation. Provider-native meanings and mappings differ. Record requested effort, supported efforts, returned usage, and any unavailable fields. Do not pool different efforts as one treatment. OpenRouter can translate effort to provider-native controls. [Reasoning documentation](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)

Provider base slugs can match provider variants or regions. A base slug does not itself opt into a premium service tier, but it is not an immutable endpoint revision. Freeze the intended provider policy, save endpoint catalogs, record returned identities, and reconcile each call. The app must not select a cheaper provider automatically. [Provider routing documentation](https://openrouter.ai/docs/guides/routing/provider-selection)

## Frontend and current design

The application uses React, Vite, Tailwind, and Zustand. It routes through pathname checks in `frontend/src/App.tsx:10`. It already has run history, run detail, batch, model, research artifact, microbench, and replay/review pages. These are useful starting points rather than reasons to rebuild the UI.

The live page subscribes to the global `/ws` stream and polls `/run/status` every 2.5 seconds. The Zustand store contains one snapshot and one event buffer of 200 events. See `frontend/src/pages/LiveBenchPage.tsx:43`, `frontend/src/state/store.ts:45`, and `frontend/src/net/ws.ts:45`. Existing historical pages use run-scoped REST paths, while live controls are global. `GameControls.tsx:10` defaults to only 50 turns.

The default API URL logic adds port 8000 when a public page has no explicit port. That needs changing for a same-origin HTTPS deployment. See `frontend/src/net/ws.ts:33`. Setting environment variables alone can work, but the production default should be a same-origin `/api` base with a development override.

The visual language is Inter, JetBrains Mono for data, warm gray `#f4f3f0`, white panels, near-black borders, small corner radii, crisp offset shadows, and saturated pink, green, blue, and yellow accents. See `frontend/src/index.css:3` and `frontend/src/components/ui/NeoPrimitive.tsx`. The current run grid already uses three columns on large screens in `frontend/src/pages/RunsPage.tsx:66`.

Use the reference screenshots for a workspace sidebar, summary line, search/filter row, card grid, and three-step modal. Keep MonopolyBench's fonts, panel treatment, and accents. Do not introduce the reference's serif/maroon identity as a second design system.

Current run cards indicate that replay files exist, not that their contents report success. The live page can label any stopped runner with a run ID as complete. Fix both when job state becomes persistent. Completion, research eligibility, replay validity, and upload status are separate fields.

## Existing campaign safeguards

`campaigns/monopoly-long-v1-e1-pilot-random-v1.json` is dry-run by default, uses eight balanced cells, requests concurrency 1, sets a $100 campaign budget, requires $110 available credit, and references a fresh authorized preflight. The implementation requires the correct preflight version and roster, valid route/tool/billing verdicts, OpenAI BYOK confirmation, matching roster-registry SHA-256, sufficient credits, and a snapshot no older than six hours. See `python/packages/arena/src/monopoly_arena/long_campaign.py:2320` and `:2386`.

The billing guard checks requested route, returned model/provider, and required BYOK status before an action is applied. A violation writes an artifact and fails the cell. See `long_campaign.py:836`. Failed gates retain planned cells with explicit not-started reasons. Existing tests cover credit failure, preflight failure, routing/BYOK violations, zero budgets, and preserving later cells after failure in `python/packages/arena/tests/test_research_campaign.py:354` onward.

There are limits to these protections. Budget checks run between games and compare accumulated reported cost plus historical next-game estimates. They do not stop an individual game as it spends. See `python/packages/arena/src/monopoly_arena/batch_artifacts.py:363` and `long_campaign.py:209`. Concurrency is explicitly reported as effective 1 at `long_campaign.py:438`. The direct API/CLI launch paths do not run the campaign gates. A web launch must not use those paths as an alternate way to execute a campaign cell.

Build a new versioned campaign contract for the current roadmap. Preserve E1 as historical evidence and leave its fail-closed tests intact. Generalize reusable validation through explicit new policy definitions, not flags that switch old gates off. New billing may use standard OpenRouter credits for all four providers if that is the chosen contract. Do not inherit historical assumptions that OpenAI BYOK is free. BYOK can charge the upstream account even when an OpenRouter cost field is zero.

## Hosting comparison and monthly cost

Prices below were checked on public pages on 24 October 2026 unless explicitly marked otherwise. They exclude tax, exchange-rate movements, a domain, paid model calls, and engineering time. Memory requirements have not been measured. CPU and RAM estimates are sizing assumptions, not benchmark results.

### Long-running Python host

| Option | Current price basis and useful starting size | Expected fit |
| --- | --- | --- |
| Hetzner | Published CX33 price is EUR 8.49 or $9.99 monthly. The intended class is 4 shared vCPU, 8 GB RAM, and 80 GB local disk; confirm its specification, region, and stock at selection. Backups add 20%. Allow a small additional IPv4 charge if needed. | Lowest predictable cash cost. Enough provisional headroom for five mostly network-bound games and one finalizer. Owner must maintain Linux, patches, backups, and restore procedures. Default choice. [Price adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/), [billing FAQ](https://docs.hetzner.com/cloud/billing/faq/) |
| Railway | Hobby has a $5 monthly minimum that includes $5 of usage. Published rates are roughly $10 per GB-month of RAM, $20 per vCPU-month, $0.15 per GB-month of volume, and $0.05 per GB of egress. At 2 GB average RAM, 0.1 average vCPU, and 5 GB disk, estimate $23 monthly. At 4 GB, about $43. Hobby's 5 GB volume limit is restrictive; Pro has a $20 minimum and larger volumes. | Convenient Git-based deploys. Actual resource billing can beat fixed larger machines if memory remains low, but a resident Python working set is billable while waiting on providers. Confirm volume and replica constraints before choosing a topology. [Pricing](https://railway.com/pricing) |
| Fly.io | In a low-cost region, a shared-CPU 2-vCPU machine with 2 GB is about $13.39 monthly. Extra RAM is about $6 per GB-month. A 4 GB machine plus a 20 GB volume is about $28.39; an 8 GB machine plus that volume is about $52.39. Volumes are $0.15 per GB-month, with separate snapshot and egress charges. | Good managed fallback. Keep all five workers and their local volume on one machine initially. Disable automatic stopping while jobs are queued, active, or finalizing. A volume is local storage, so R2 remains necessary for host-loss recovery. [Pricing](https://docs.fly.io/about/pricing) |
| Render | Paid compute is $25 monthly for 1 CPU / 2 GB, $85 for 2 CPU / 4 GB, and $175 for 4 CPU / 8 GB. A 20 GB persistent disk adds $5 at $0.25 per GB-month. | A 2 GB service might work only after measurement. The safer 4 GB choice is about $90 monthly, well above the other options. Persistent disks attach to one service, so do not design separate API and worker services that assume one shared disk. Free services do not meet this task. [Pricing](https://render.com/pricing), [compute plans](https://render.com/docs/compute-plans), [disk behavior](https://render.com/docs/disks) |

For the VPS recommendation, $13 to $16 monthly is an allowance, not an exact quote. It combines the published $9.99 base, approximately $2 backup cost, and a modest allowance for addressing and a domain. IPv4 price and domain choice are not verified here. If the cheap instance is unavailable, compare the actual replacement against Fly and Railway instead of assuming all Hetzner SKUs cost the same. Hetzner's published CPX22 is materially more expensive at $22.99 before extras.

The first five games are likely to cost several times more in model calls than one month of infrastructure. Operational simplicity, correct accounting, and avoiding a lost campaign matter more than saving one or two dollars on static hosting.

### Frontend hosting

| Option | Price and behavior | Recommendation |
| --- | --- | --- |
| Serve the Vite build from the same server | No second hosting bill. A reverse proxy serves static files and forwards `/api` and WebSockets to FastAPI. | Default. One HTTPS origin, one authentication policy, no production CORS setup, and no unnecessary cross-vendor dependency. |
| Cloudflare Pages | Free static hosting is enough for this frontend; the free plan allows 500 builds per month. Dynamic Pages Functions are a separate execution product. | Good alternative if independent frontend deployment is useful. Keep the actual game workers on the persistent host. [Limits](https://developers.cloudflare.com/pages/platform/limits/) |
| Vercel | Hobby can be free for eligible personal use; Pro starts at $20 monthly. The existing Vite app does not need Next.js or a server rendering migration. | Fine if already preferred, but it does not replace the worker host. [Pricing](https://vercel.com/pricing) |

Ordinary serverless request handlers do not fit the game loop. Current Vercel limits include 300 seconds on Hobby, 800 seconds on Pro, and up to 1,800 seconds for an extended-duration option. Even 30 minutes is shorter than these games. Workflows can span longer logical durations by storing state between steps, but adopting them would require the same durable decision boundaries proposed here plus a platform-specific execution rewrite. A detached asyncio task after returning HTTP is not a durable job. See [Vercel function limits](https://vercel.com/docs/functions/limitations).

Cloudflare Workers and hosted workflow products could implement a durable scheduler, but they do not run this existing Python/filesystem workload unchanged. Keeping the existing engine and artifact writers on Linux is the shortest route to a comparable benchmark.

### Artifact storage

| Option | Price and limits | Use |
| --- | --- | --- |
| Cloudflare R2 Standard | $0.015 per GB-month, with 10 GB-month free. The monthly free operation allowances are 1 million Class A and 10 million Class B operations. Additional Class A operations cost $4.50 per million and Class B $0.36 per million. Internet egress is free. Billing rounds operation quantities to its documented units. | Default durable object store and download source. At 100 GB retained, storage alone is about $1.35 monthly after the free allowance. [Pricing](https://developers.cloudflare.com/r2/pricing/) |
| Amazon S3 Standard | Indicative US East prices are $0.023 per GB-month, $0.005 per 1,000 PUT requests, and $0.0004 per 1,000 GET requests, plus applicable egress. These exact current regional rates were not exposed by the pricing page renderer and should be verified before purchase. | Technically suitable, but R2 is easier to predict when the owner repeatedly downloads complete archives. Do not treat illustrative S3 prices as a verified quote. [Pricing](https://aws.amazon.com/s3/pricing/) |
| Host persistent disk only | Included on the VPS, roughly $0.15 per GB-month on Fly/Railway, or $0.25 on Render. | Required for active append-heavy work. Insufficient as the only copy because a lost host, mistaken deletion, or filesystem failure can lose a campaign. A volume is not a complete backup policy. |

At the 250 MB planning allowance, 24 games occupy about 6 GB and 48 games about 12 GB before duplicate exports and backups. Even doubling that storage remains inexpensive. About 5,000 immutable files per game means 100 games produce roughly 500,000 object writes before checkpoints and exports. Individual-file uploads are acceptable initially. At 1,000 games the five million writes alone exceed the free operation allowance, so compressed checkpoint packs become useful. Avoid overwriting a growing JSONL object after every event, which repeatedly uploads its whole prefix.

### Run index

| Option | Current cost and fit | Decision |
| --- | --- | --- |
| SQLite | No service bill. WAL mode permits concurrent readers and short serialized writes on one local persistent filesystem. Five workers generating a heartbeat every ten seconds create only 0.5 heartbeat writes per second. | Default. Store job and campaign metadata, leases, budget reservations, and artifact locations. Keep raw prompts and logs in files/object storage. Back up SQLite with its supported online backup method. |
| Neon | Free plan lists 100 CU-hours per project monthly and 1 GB storage. Launch compute is $0.106 per CU-hour, plus storage at $0.35 per GB-month. A continuously active 0.25 CU database uses roughly 180 CU-hours per 30-day month, or $19.08 compute at that rate. | Useful when multiple worker hosts need a shared index. Frequent heartbeats can prevent scale-to-zero, so the free plan is not an automatic always-on solution. [Pricing](https://neon.com/pricing) |
| Supabase | Free includes a 500 MB database, 1 GB file storage, and 5 GB egress, with inactivity pausing. Pro starts at $25 monthly and includes a compute credit, 8 GB database storage, 100 GB file storage, and 250 GB egress. | Convenient managed auth and SQL, but unnecessary for one owner and one worker host. Its free storage allowance is poorly matched to raw run retention. [Pricing](https://supabase.com/pricing) |

Move to Postgres when work must be scheduled across two independent hosts, multiple owners need isolation, or measured SQLite contention becomes material. Do not add it because the artifacts contain many JSON files. SQLite must stay on local block storage, not an object-store mount or a shared network filesystem.

## Execution and durability design

### Processes and ownership

Use one immutable deployment image containing the installed Python packages and the built frontend. Run the API and supervisor as separate services. The supervisor starts at most five independent Python game subprocesses. Each worker has one job, one engine instance, one OpenRouter client, and exclusive write access to its run directory. Run at most one CPU-heavy finalizer at a time. The API can restart without terminating those workers.

The initial worker service can stay on one pinned image until its jobs drain. A deployment stops accepting jobs into the old service, lets its games finish, and starts the new release after the old worker service is idle. Keep the old image available for recovery. Do not upgrade a resumed game to whatever source happens to be checked out now. Parallel execution of several code releases can be a later feature.

Use a small SQLite job ledger instead of Redis, Celery, Kubernetes, or one container platform service per game. Minimum tables are:

| Table | Required fields and constraints |
| --- | --- |
| `jobs` | Job ID, engine run ID, owner, immutable resolved configuration and hash, code/image digest, campaign/cell ID, seed, status, queued/started/ended timestamps, game outcome, last committed event/decision, artifact state, error classification, and idempotency key. |
| `job_attempts` | Execution-attempt ID, worker identity, lease token/version, process identity, heartbeat, start/end, recovery reason, and exit status. Never reuse an execution-attempt ID after a crash. |
| `campaign_cells` | Registered roster, seat assignment, seed, fixed order, preregistration/config hashes, launch eligibility, linked job, and explicit not-started or failure reasons. |
| `spend_reservations` | Job/campaign/owner scope, provider request identity, estimated maximum charge, reconciliation status, actual charge when known, raw usage references, and uncertainty reason. |
| `exports` | Run/campaign scope, immutable archive version, manifest hash, object key, size, archive hash, and build status. |

Use WAL, full durability settings, a busy timeout, and short transactions. Do not hold a database transaction during a provider call, upload, or replay. Resolve an omitted seed exactly once before committing the job. Persist the full protected player configuration before any paid work. Browser-provided names and notes are administrative metadata and must not be inserted into prompts.

Keep `job_id` separate from `engine_run_id`. Existing baseline policies use the run ID in their own deterministic seeds in `python/packages/arena/src/monopoly_arena/baselines.py:398`. Changing that ID during recovery changes behavior. Fresh jobs need collision-safe IDs and a configuration hash that includes reasoning, routes, limits, and campaign membership. A retry of the same HTTP idempotency key returns the same job; it must not choose a new seed or issue a second start.

A supervisor claims a job in a transaction, increments a fencing token, and obtains an exclusive filesystem lock before starting its writer. Workers heartbeat every ten seconds. A stale heartbeat after roughly 90 seconds triggers inspection, not immediate duplicate execution. Reclaim only after confirming the previous process is dead or otherwise unable to write. A database lease alone does not fence an old process still writing local files. On a single host, process identity plus the filesystem lock makes that ownership check practical.

Use explicit job states: queued, checking prerequisites, running, pausing, paused, recovering, finalizing, completed, failed, budget exhausted, and cancelled. Store the engine's game outcome separately. A worker that stops spending before game end is paused or failed, not a completed game. A game with `GAME_ENDED` can still be finalizing or have an export failure.

### Crash-safe writes and replay

Add a versioned execution journal alongside the existing artifacts. Keep the existing `events.jsonl`, `actions.jsonl`, `decisions.jsonl`, snapshots, prompt filenames, and quality files unchanged for normal consumers. The journal records storage commits and request recovery state; it does not introduce engine rules or replace engine events as the game record.

Each committed transition needs a durable journal record containing the exact serialized bytes or immutable blob references for its output records, expected file offsets, sequence bounds, and hashes. The writer first persists and fsyncs that record, then materializes the canonical files. On restart it can complete a partially materialized commit without appending an action or event twice. Immutable JSON files use write-to-temp, fsync, and atomic rename. Canonical turn snapshots retain the existing first-write rule.

The transaction boundary must include every engine advance that emits events, not only selected actions. An action commit includes the selected legal action, resolution metadata, corresponding decision record, all generated events, and required snapshots. Compute these through the engine, persist them as one recoverable commit, then publish them to viewers. This may require buffering a bounded transition before the runner yields it. It must not reimplement event generation in telemetry.

Persist provider-call intent before the request and the received raw response immediately after receipt, before validation or action application. Record the logical attempt index and each physical transport attempt separately. Existing prompt names and resolver attempt meanings stay stable. Added transport records are operational sidecars unless a deliberately versioned downstream contract is required.

Recovery has four distinct cases:

1. A committed action has only partly reached canonical files. Verify matching existing bytes and finish the journal projection. Do not invoke the model again.
2. A response is durably recorded but no action is committed. Reuse that response, restore the original logical attempt and retry state, validate it against the reconstructed legal decision, and proceed without a new provider call.
3. A request intent exists but its response is unknown. Reconcile available generation metadata without making a new completion request. If uncertainty remains, mark an ambiguous external request and pause or fail according to the approved technical-failure policy. Do not silently restart at attempt zero.
4. The game ended but finalization is partial. Run the idempotent finalizer from the committed logs. Do not replay the game through new model decisions.

For reconstruction, start the same engine version with the same seed, identities, engine run ID, and settings; replay the committed action sequence; verify the event prefix; then rebuild prompt memory. The existing replay implementation is the base. The new layer repairs known journal projections before calling it. An inconsistent file without a matching committed journal entry is a failure requiring evidence preservation, not something to skip with a permissive JSONL reader.

Quarantine partial trailing bytes in a recovery sidecar and retain their hashes. Never silently discard a contradictory complete record. Recovery reports should describe the interrupted execution attempt, repaired files, reused provider responses, remaining uncertainty, and canonical replay verdict. All wall-clock leases and timings stay outside deterministic game progression.

No design can guarantee exactly-once billing across an external API timeout without provider-supported idempotency or reconciliation. The enforceable guarantees are one active writer, exactly-once application of each committed engine action, preserved attempt history, explicit uncertain charges, and no automatic unrecorded retry policy.

### Scheduling and browser independence

`POST /api/jobs` validates the complete request, commits the job, and returns 202 with a job ID. It does not execute the game in the request task. `GET /api/jobs`, `GET /api/jobs/{id}`, and scoped actions read and mutate the ledger. A sixth eligible game waits in the queue. Starting another game never stops the first five.

The worker publishes committed progress to the ledger and a bounded notification path. The API reads that progress and fans it out. A slow WebSocket must not be awaited by the game process. A viewer subscribes to `/api/jobs/{id}/ws` with its last observed sequence; reconnect uses a snapshot and event backfill. Deduplicate by run ID and event sequence. If a client falls far behind, send a resync instruction rather than retaining an unbounded queue.

Keep the current global endpoints only as explicitly deprecated compatibility wrappers for a selected job, or remove them in a coordinated API/frontend change. They must not retain singleton stop-on-start semantics. Dashboard polling should use cheap indexed summaries, with cursors and pagination, rather than opening every scorecard or parsing every decision file on each request.

## Artifact durability, completeness, and export

Use a persistent parent directory such as `/data/monopolybench/` with `runs/`, `quality_check/`, job records, journals, and finalization staging below it. Preserve the existing relative layout. At the export boundary, produce the same saved-game wrapper already used locally:

```text
<saved-game>/
  run/                      Existing run files and unchanged prompt/state paths
  quality_check/            Existing wire request and response files
  analysis/                 Generated analysis and any later review materials
  saved_game_manifest.json  Existing saved-game metadata
  cloud/                    Versioned operational metadata and recovery evidence
```

The `cloud/` addition is optional to existing consumers. Document it and test that local scripts ignore it correctly. Do not replace existing manifests or reinterpret legacy fields. Add a recursive storage manifest covering every relative file, byte length, SHA-256, role, and completion state. Exclude the storage manifest's own digest from its contents and put its hash in the job/export record. Hash the completed ZIP separately. The current selected-file manifest is retained for compatibility.

### During the game

Upload closed prompt, response, quality, and snapshot files after each committed decision. Upload append-only logs as immutable committed segments, identified by byte offsets and hashes. Upload a checkpoint manifest only after every object it references exists. That manifest is the remote commit marker. Retain the original JSONL byte order; assembling segments must reproduce the original file exactly.

To protect against host loss, upload the raw received response and its recovery metadata before admitting the next paid decision. The remote checkpoint should normally trail by no more than one decision. If remote durability is unavailable for more than the approved tolerance, stop admitting new provider calls at a safe boundary and mark the job paused for storage. Do not keep spending while silently accumulating an unbounded unrecoverable tail. A process crash before a received response is recorded anywhere still has the external-request uncertainty described above.

An append segment or small compressed checkpoint pack is preferable to uploading the whole expanding `decisions.jsonl` after every turn. Keep the manifest mapping transparent so a downloader can restore plain local files without a cloud SDK inside the analysis tools. At this scale, a simple uploader with retry, checksum verification, and backpressure is sufficient.

Take consistent SQLite backups using its backup API and upload those separately. Copying just a live database file while ignoring its WAL is not a reliable backup. Store frozen run configuration, pricing/provider catalog snapshots, code/image digests, and deployment manifests with the job so a host rebuild does not depend on a laptop checkout.

### After the game

Run usage, replay, scorecard, and trace finalization from committed artifacts, then standard analysis in an isolated staging directory. The existing standardization script has archive and cleanup behavior. Refactor its useful functions into a safe finalizer or call a narrowly scoped adapter; do not run a broad historical standardization command against the live root.

Publish completion only when required artifacts exist, the integrity inventory is complete, and the final upload manifest is committed. Keep separate statuses for game outcome, replay verdict, analysis completion, remote durability, and export availability. A replay mismatch remains visible even if every file uploaded correctly. The historical R191 mismatch must not be relabeled as a pass during import.

Build a complete ZIP64 archive in staging or stream it to a temporary object. Include the raw run, quality files, analysis, and manifests. The existing analysis-only ZIP can remain an optional smaller download. Do not create a full archive in API memory or regenerate it for every click. Use an immutable object key containing the export version and manifest hash.

Authenticated export endpoints return a short-lived signed download URL or an authenticated stream. Support resumable HTTP range downloads where the object service supports them. Long exports need a practical expiry and a way to obtain a fresh URL for the same immutable archive. Private thoughts, system prompts, and raw provider metadata must not become public bucket objects.

Add a bulk export command such as `python -m monopoly_arena.cloud_export --campaign <id> --destination <path>`. It should list committed manifests, download to temporary files, verify hashes, atomically finish each package, and skip verified existing versions. It must never delete unrelated local files. A campaign download includes its contract, preflight evidence, full planned-cell ledger, matrices, aggregate reports, and member games.

Keep completed artifacts by default. Archiving is a visibility flag, not deletion. Delete a local cache only after remote verification and according to an explicit retention setting. Keep failed and cancelled runs, partial logs, and uncertain-call evidence. Set disk-space admission checks before a new job and pause safely before filling the volume; do not satisfy a quota by dropping prompt files.

## Dashboard and create-game design

The reference layout fits the existing frontend well. Keep Inter and JetBrains Mono, the warm background, black borders, compact radii, and existing bright accent colors. Use a 220 to 240 pixel sidebar on desktop, a centered main area, and a responsive card grid with three columns on wide screens, two on tablets, and one on phones. Do not add a second serif-led brand.

### Dashboard

The sidebar contains the workspace name, All games, Active, Archived, and a clear Create game action. Retain existing links to campaigns, research artifacts, and microbench rather than hiding those working surfaces. A compact recent-games list can mirror the reference's funds list.

The main title is All games. The summary line shows running, queued, and completed counts plus known spend for the selected scope. If some usage is unresolved, label the amount as known spend and show the pending amount separately. Search accepts run ID, name, seed, model, or campaign. Filters include status, campaign, model roster, reasoning effort, and replay result.

Each card contains:

- A deterministic board thumbnail derived from a server snapshot, or a simple static board preview while queued. It must not infer ownership or rules independently.
- A human-readable name and run ID, a status label with text as well as color, and campaign or exploratory classification.
- The four seat/model labels, common reasoning effort, and seed.
- Current turn and configured cap, elapsed wall time, last progress time, known cost, and budget. A turn count is not a reliable time-to-finish percentage.
- Separate replay and storage/export indicators. Existence of `replay_report.json` is not a passing verdict.
- Watch or View, Export when ready, and an overflow menu with archive and permitted operational controls. Omit a public Share button because these artifacts contain private model material.

Load card summaries from the job index. Poll active summaries about every five seconds, slower when the page is hidden. Subscribe to detailed events only for an opened game. Five dashboard cards must not instantiate five complete replay viewers and parse thousands of prompt files.

### Three-step create flow

| Step | Fields and behavior |
| --- | --- |
| 1. Game and models | Choose a registered campaign cell or an explicitly exploratory game. Show four fixed seat positions and the approved model/provider pairs. Offer the common low, medium, or high effort supported by the roster, default medium. An optional game name is metadata only. Campaign-defined roster, seat, and effort fields are read-only. |
| 2. Rules and budget | Seed, turn cap, existing trade and auction limits, and spend ceiling. Default new exploratory full games to a proposed 400-turn cap, 20 trade exchanges, and 200 auction actions, subject to the final contract. Show a historical cost range and the catalog date. Explain that a fixed wall-clock finish is not guaranteed. Campaign cells inherit their preregistered settings. |
| 3. Review and launch | Show the exact resolved configuration, provider pins, effort, seed, code version, research classification, per-game/global remaining budgets, queue position, and current gate verdicts. Disable launch with specific reasons for stale or missing preflight, missing budget authority, or unsupported settings. Submit once with an idempotency key and navigate to the returned job. |

Use the reference's visible step count, Continue/Back footer, selectable option cards, and focused modal. Preserve field values while moving backward. Handle Escape, focus trapping, keyboard navigation, form errors, and small-screen scrolling. Queue saturation is an ordinary queued state, not an error or a reason to cancel another game.

Do not expose arbitrary system prompts, tools, retry policies, fallback rules, or raw provider JSON in this flow. The user requested model, route, and reasoning configuration, not a general benchmark mutation console.

### Game detail and live view

Use a run-scoped route with the existing board and event UI. The header shows status, seed, roster/effort, campaign, elapsed time, committed turn, known spend, and remote checkpoint age. Tabs can reuse live view, decisions, artifacts, replay, and analysis. Event and decision lists should be paginated or virtualized; fetch large prompt details on demand.

A disconnected browser shows its connection state without changing the job. Reopening the URL reconstructs the view from server state and sequence-based backfill. A paused or failed job shows a concrete reason and the latest preserved artifacts. Resume is offered only when replay, code-version, policy, budget, and ownership checks allow it. A paused job does not automatically become eligible merely because the user reopened the page.

The frontend remains render-only. The API and engine decide legality, launch eligibility, state transitions, game outcome, and whether resume is safe. UI validation helps explain constraints but never replaces server checks.

## Authentication and spending controls

### Public deployment security

Start with one owner, not a public multiuser game service. Put the site behind an identity-aware proxy such as Cloudflare Access with an explicit account allowlist, or equivalent authenticated session middleware. Validate proxy identity tokens at the origin and prevent bypass through an unprotected public origin. Use HTTPS, authenticated WebSocket upgrades, strict allowed origins, and CSRF protection where cookie authentication permits cross-site requests. Confirm the chosen Access plan's current free allowance before relying on it. [Cloudflare plans](https://www.cloudflare.com/plans/zero-trust-services/)

Keep the OpenRouter key only in the worker's server-side secret environment. The frontend build, API responses, logs, archives, and saved wire files must not contain authorization headers or secret values. Use a dedicated project key with an approved spending limit. Limit R2 credentials to the needed bucket/prefix and actions. Do not expose the object bucket publicly.

Authorize every artifact read, export, live stream, and control action. Use opaque job IDs plus ownership checks, not guessability as security. Validate run IDs and relative artifact paths against stored inventory entries to prevent traversal. Bound request body sizes and accepted engine limits. Do not accept filesystem paths, executable commands, or provider credentials from the create form. Keep an audit log of starts, resumes, cancellations, budget changes, and downloads without copying secrets into it.

Provider billing credentials and optional notification credentials need separate handling. Notifications should contain run status and a protected link, not prompt bodies. Sending email, Slack, or other external messages needs an explicitly selected destination and authorization. This planning round sends none.

### Shared budget enforcement

Implement admission and spending policy in the shared execution path, not only in the UI. Cloud API jobs, campaign jobs, CLI launch, recovery, corrective retries, and transport retries must all pass the relevant policy. Mock and baseline runs use an explicit zero-spend mode. A campaign cell cannot be launched through the exploratory endpoint to evade its contract.

The policy has per-game, per-campaign, and workspace-wide ceilings, plus maximum active games of five. Reserve a conservative possible charge in a short SQLite transaction before each physical paid HTTP attempt. Count active reservations against every relevant ceiling. This prevents five workers from independently seeing the same remaining dollar and all spending it.

Estimate the input bound from the actual serialized request and the applicable provider pricing tier. Reserve output against the provider's permitted maximum under the existing request policy. The current code sends no `max_tokens`, so a tight reservation can be expensive. Do not quietly add an output cap to make budget math convenient. If a lower output cap is wanted, it is a separately approved model-facing contract change with preservation/version tests.

Reconcile reservations using returned usage, generation metadata, and provider billing evidence. Preserve raw token fields and distinguish actual billed cost, estimated cost, pending reconciliation, and possible upstream BYOK cost. Unknown calls retain a conservative reservation until resolved. A missing cost field is not zero. Cache discounts and threshold pricing should come from the recorded endpoint/pricing data, not hardcoded optimism.

Use a dedicated OpenRouter key limit as a second control. OpenRouter exposes key credit/limit information and may reject calls when available budget is insufficient for in-flight reservations. More keys do not bypass provider rate limits. The application ledger still matters because a key limit cannot allocate budget fairly across games or label research outcomes. [OpenRouter limits](https://openrouter.ai/docs/api_reference/limits)

Do not promise mathematically exact final dollar caps when provider accounting or timeout outcomes can be delayed. Use conservative admission, retain uncertain reservations, reserve a contingency, and stop further requests when reconciliation is unsafe. Budget exhaustion is an operational pause/failure, not a model-invalid-output event. It must not silently generate deterministic fallback actions until the engine reaches a nominal completion.

For sizing only, a proposed ceiling of $50 per full game and $250 for the first five-game window leaves room above the historical projections. This is not spending approval. With today's catalog, the five-game expected workload is about $57, or $86 with a 50% planning allowance. At the user's listed prices, it is about $144, or $216 with that allowance. New models may use more or fewer tokens, so confirm actual paid smoke usage before setting a final unattended cap.

### Progress, stalls, and alerts

Separate a worker heartbeat from game progress. A healthy process can be waiting on a slow provider. Record current request start, last response, last committed decision, and upload checkpoint age. Flag no committed progress for five minutes for inspection. A longer threshold, such as 15 minutes, should pause new work at a safe boundary or trigger the approved technical-failure path; it must not kill an otherwise healthy in-flight call solely to meet a four-hour target.

Use the existing transport and corrective retry policy unchanged unless a versioned amendment explicitly changes it. Record physical transport retries for accounting. Apply conservative global/provider admission limits around requests rather than modifying their prompts. On repeated provider failures, storage failure, disk pressure, or an exhausted shared budget, stop admitting more calls and retain evidence.

Persist finish/failure notification jobs so an API restart does not lose them. Start with in-app notifications and an optional owner-approved email or webhook. The dashboard should remain sufficient when no external notification integration is configured.

## Research integrity and campaign integration

The deployment is an execution environment, not a new experimental treatment by accident. Freeze the following before the first paid request of each game:

- Engine settings, player IDs and seat order, seed, engine run ID, complete resolved model/provider/effort configuration, and prompt/tool/memory policy hashes.
- Git SHA, release/image digest, dependency lock hashes, Python and runtime versions, platform/architecture, board/schema versions, and code archive or reproducible image reference.
- Campaign version, registered roster and seed IDs, cell order, preregistration hash, budget authority, preflight evidence, pricing snapshot, and endpoint catalog.
- Requested provider policy and billing mode. Record actual response model/provider, generation IDs, raw usage, and any routing mismatch for each call.

The current standalone `run_config.json` and experiment manifest are not a complete code/environment lock. Add a versioned execution manifest without leaking these research labels into model inputs. Fetch the start pricing snapshot before execution, then optionally record an end snapshot as a separate observation. Never replace the start snapshot with a newer price file.

Use the exact same engine and arena path for local and cloud runs. Compare canonical engine event hashes, actions, prompt payloads, and resolver behavior under scripted responses. Wall-clock metadata, worker IDs, job IDs, and storage locations must not enter engine seeds or prompt construction. The engine run ID needs particular care because baseline policies already use it.

Define a new campaign JSON and protocol document for the requested roster. The contract should specify common effort, strict provider pins, billing mode, preflight procedure, concurrency, seed/seat balance, stopping rules, technical-failure handling, replacement policy, and budget. Preserve historical E1 documents and tests. Update the roadmap only after the new contract is accepted, without overwriting the user's uncommitted research draft.

Concurrency changes operational conditions and provider contention. Record requested and effective concurrency, queue time, rate-limit responses, and timing separately. Do not start whichever seed happens to finish fastest next if the preregistered execution order requires something else. A parallel scheduler can reserve the next eligible fixed cells while preserving the planned matrix and explicit completion/failure records.

Five convenient games are an operational shakedown, not a balanced confirmatory design. For one four-model roster, six fresh seeds times four seat rotations would give 24 games if that design is selected. The draft's two-roster design would give 48. At the frontier-template estimate, 24 games cost roughly $274 at today's catalog or $693 at the user's listed prices, before contingency. Neither campaign size is authorized by this plan. Model availability and prices must be rechecked before that later campaign.

Cloud execution alone does not finish either paper. The two-paper roadmap still needs its declared samples, metric/codebook decisions, review procedure, analysis, and writing. Keep operational demo games clearly labeled so they do not silently replace preregistered evidence.

## Implementation phases and file-level work

This is a proposed sequence, not changes made in this round. A reasonable planning allowance is six to ten focused engineering days for a tested single-host release, with substantial uncertainty around crash recovery. A mock dashboard can appear sooner. Do not shorten the critical path by spending before the durability and policy checks exist.

### Phase 0. Freeze the contract and acceptance criteria

Create a new protocol under `docs/research_protocol/` and a new configuration under `campaigns/` for the requested roster. Resolve the OpenAI price discrepancy, billing mode, common effort, approved cap, and whether the first five games are exploratory. Add model/provider registry entries through existing patterns. Document launch and recovery policy, including ambiguous external requests. Keep existing E1 contracts intact.

Update `docs/artifact_reference.md` with operational sidecars, recursive manifests, full exports, and completion states. Plan all new API types together in `contracts/`, examples, Python responses, and TypeScript consumers. The engine snapshot/action/event schemas should not change merely to add cloud jobs. If a changed decision envelope is unavoidable, version and update every producer and consumer in the same change.

Acceptance: the complete proposed configuration and budget are reviewable, old gate tests still describe the old contract, and no paid path can be enabled by an undocumented bypass flag.

### Phase 1. Persistent jobs and isolated mock workers

Add focused modules such as `monopoly_arena/job_store.py`, `worker.py`, and `supervisor.py`. Use existing project packaging rather than a new framework. Put orchestration in arena and keep FastAPI thin. Replace singleton execution ownership in `python/apps/api/src/monopoly_api/run_manager.py` with a service that reads the ledger and delegates work; retain useful artifact readers separately. Add job endpoints in `main.py` with typed request/response contracts.

Implement transactional admission, idempotency, frozen config/seed resolution, worker locks, heartbeat, queue ordering, and independent finalizer capacity. Configure a single data parent that covers both run and quality roots. Avoid starting paid jobs in this phase.

Acceptance: five deterministic scripted jobs progress independently, a sixth queues, closing every browser has no effect, and restarting the API does not stop workers. Two submissions with the same idempotency key create one job.

### Phase 2. Durable decisions and recovery

Add a storage journal writer in telemetry, with the runner/resolver controlling semantic commit boundaries. Likely touched files are `llm_runner.py`, `decision_resolver.py`, `openrouter_client.py`, `run_files.py`, `writer_jsonl.py`, and the existing recovery/replay helpers. Add an operational request-attempt recorder at the shared HTTP boundary while preserving payloads and retry behavior.

Persist complete player configuration before play. Implement response reuse, atomic projection, strict corruption handling, replay-based reconstruction, execution-attempt history, and idempotent post-game finalization. Make early crashes recoverable without requiring that every player has already produced an observed prompt.

Acceptance: injected termination at every write boundary either restores exactly the expected committed trajectory without another model call or fails with explicit preserved evidence. It must never append duplicate actions, silently skip records, or overwrite attempt-zero files on resume.

### Phase 3. Remote artifacts and complete exports

Add telemetry modules for immutable upload/checkpoint manifests, recursive integrity inventory, safe finalization, and export. Add a storage abstraction with a local test backend and an R2/S3-compatible implementation. Refactor reusable pieces from `scripts/standardize_saved_games.py` into an explicit safe entry point. Add the bulk export CLI and authenticated export endpoints.

Acceptance: kill and replace the host after a remote checkpoint, restore a job from the bucket plus its saved metadata, and continue from the same committed sequence. A downloaded full ZIP contains every expected raw and analysis file, preserves byte hashes, and works with existing local replay/analysis commands. Remote failure pauses further spending rather than dropping artifacts.

### Phase 4. Shared policy, live costs, and new-roster preflight

Add a shared execution-policy and spending-ledger layer used by cloud, batch, campaign, CLI, and recovery paths. Reuse the strict checks in `long_campaign.py` through explicit versioned policies. Update `player_config.py` and the new create request schema to resolve the requested models, exact provider pins, and common effort. Fix route merging so changing a model cannot accidentally retain an incompatible old provider.

Implement the new preflight that tests production `auto` tool choice while preserving the old E1 forced-tool contract. Add provider catalog snapshots, route verification, actual/estimated/pending cost distinctions, and atomic reservations. Add a zero-spend mock mode that cannot construct a live completion request.

Acceptance: missing or stale authorization, unknown billing, wrong provider, missing usage, exhausted budgets, and competing reservations all fail closed with durable reasons. Existing E1 tests continue to pass. Identical scripted decisions produce identical model-facing payloads before and after these changes apart from explicitly approved model/route/effort settings.

### Phase 5. Dashboard, authentication, and deployment

Extend `frontend/src/pages/RunsPage.tsx`, `LiveBenchPage.tsx`, `state/store.ts`, `net/ws.ts`, and `App.tsx`. Add a create-game wizard and run-scoped data hooks/components using existing UI primitives. Update the production API base to same-origin `/api`. Keep replay, research, and microbench routes working. Read replay verdicts rather than checking file existence.

Add authentication/authorization middleware, scoped exports, server-side input limits, and audit records. Add deployment files under a focused `deploy/` directory: immutable image build, service definitions, reverse proxy, persistent mount, health checks, backup/restore, log rotation, and drain procedure. Update `.env.example` with names and explanations only, never real secrets.

Acceptance: an unauthorized browser cannot start jobs, read prompts, open live streams, or download an export. An authorized owner can launch five jobs from five tabs and later see all five independently. Refresh, reconnect, pagination, archive, and export work on desktop and mobile. Starting a sixth does not cancel any active game.

### Phase 6. Verification and paid rollout

Run the full repository verification from the root using `pwsh -File scripts/verify.ps1` where available, or the inspected `scripts/verify.sh` on the supported local environment. The Bash script covers contract checks, Ruff, mypy, engine, API, arena, telemetry, frontend lint, and frontend build. It does not run the microbench package tests, so run those explicitly as well. Run prompt-preservation tests and fixtures wherever the shared resolver, model config, recovery, or prompt-adjacent path changes.

Then run a five-game, full-length scripted/mock campaign with complete file output and post-run analysis. This must exercise legal tool selection and successful actions, not the historical smoke pattern where every decision fell back. Measure peak RSS by process, total resident memory, CPU, disk I/O, file counts, upload lag, and finalization time. Use that evidence to retain 8 GB or reduce to 4 GB. Test with the laptop disconnected and with API, worker, and host termination at controlled points.

Only after the contract and budget are approved, execute bounded paid preflight calls using the actual four routes and effort setting. The preflight itself needs a budget reservation. Follow with one short exploratory game, then one full game, then the five-game unattended window. Record every smoke artifact and keep it outside confirmatory analysis. A short turn cap is a declared smoke-test configuration, not a hidden modification of a full research game.

Do not claim a three-to-four-hour completion SLA until measured live results support it. A successful release guarantees browser independence, durable progress, explicit failure states, complete artifacts, and controlled spending.

## Required test matrix

| Surface | Tests that establish the guarantee |
| --- | --- |
| Job admission | Concurrent starts, identical/different idempotency bodies, seed frozen once, five active plus one queued, duplicate worker claim, stale lease with live writer, and authorization per owner. |
| Determinism | Same seed/settings/players/engine run ID and scripted response sequence run alone, concurrently, and after recovery produce the same canonical events and applied actions. Baseline policies get their original run ID. |
| Prompt preservation | Exact system text, user payload, tools, tool choice, memory, public/private message requirements, corrective retry text, and fallback selection are unchanged. Cloud metadata does not enter prompts. |
| Crash recovery | Terminate before request, after request intent, after raw response, before/after validation, during action/decision/event projection, during snapshot rename, after game end, after summary, and during final manifest publication. |
| Corruption | Truncated trailing JSONL, contradictory complete rows, altered action/event/decision bytes, absent prompt files, incorrect hashes, missing remote segments, and stale checkpoint manifests fail explicitly without erasing evidence. |
| Spending | Two workers compete for the final available reservation; transport and corrective retries reserve separately; zero budget sends no live request; unknown usage retains a reservation; wrong route/BYOK state stops before application; an exhausted cap never becomes an ordinary fallback game. |
| Campaign policy | New contract has positive and negative tests for freshness, roster hash, seed/seat matrix, billing, tool support, code version, fixed scheduling order, and technical-failure handling. All existing E1 gate tests remain intact. |
| Storage/export | Root mount includes quality files, snapshots are never overwritten, final manifest covers recursive trees, interrupted upload/download resumes safely, full ZIP hashes match local files, and existing local analysis/replay accepts restored packages. |
| API/live UI | API restart leaves workers running; browser disconnect changes no state; per-run WebSocket isolation and sequence backfill; slow viewers cannot block workers; no stopped-equals-complete shortcut; replay verdict reflects report contents. |
| Security | No credentials in bundles or artifacts, rejected path traversal, authenticated export and WebSockets, origin/token validation, launch rate limits, and unauthorized resume/budget changes denied. |
| Capacity/operations | Five full mock games plus a finalizer stay within measured RAM/disk limits; disk full, object-store outage, provider stall, supervisor restart, deployment drain, backup restore, and notification deduplication behave as documented. |

Do not run destructive chaos tests against the user's historical directories. Use temporary roots and isolated test buckets. Preserve reference artifacts read-only. A failed benchmark check is evidence to report, not a reason to regenerate historical ground truth until it passes.

## Risks and decisions to settle

| Issue | Default recommendation and how to resolve uncertainty |
| --- | --- |
| Three-to-four-hour expectation | Treat this as a desired observation window. Keep jobs alive beyond it and report progress. Measure one complete cloud game before promising a duration. Do not invent an undeclared time-based engine stopping rule. |
| Model prices | Use the verified standard OpenAI $2/$10 route in estimates after confirming that this is the intended service tier. Preserve the user's $10/$50 scenario for comparison. Snapshot again before paid launch. |
| Common reasoning | Default medium, expose low/medium/high, and label them provider-native effort. Do not describe them as equal compute. Freeze effort for confirmatory cells. |
| Billing | Use one dedicated capped OpenRouter project key and a new explicit billing contract. Decide whether upstream BYOK is required. Do not inherit the old free-OpenAI assumption. |
| Budget | Propose $50 per game and $250 for the first five-game window, with no auto top-up. Obtain a concrete budget decision before paid rollout. Lower caps are possible but may pause long games. |
| Campaign scope | Treat the first five as operational/exploratory unless mapped to an accepted new campaign matrix. The second roster and 48-game campaign remain undecided. |
| Hosting | Choose an available 8 GB Hetzner instance at the quoted class; use Fly if availability, region, or maintenance burden makes that impractical. Confirm resource use with five mock games before downsizing. |
| Single-host failure | Accept temporary unavailability initially, backed by remote checkpoints and tested restore. High availability would require extra hosts and a shared scheduler, which are not necessary to close the laptop. |
| Unknown paid response | Pause with preserved evidence when reconciliation cannot determine the outcome. A policy that automatically repeats such requests must be declared and budgeted, not added as hidden recovery behavior. |
| Model alias drift | Store canonical catalog IDs and returned identities, but do not assume an alias guarantees immutable weights. Recheck availability and register any treatment change before a campaign. |
| Storage growth | Monitor bytes, file count, remote lag, and free disk. Long games and raw reasoning may exceed historical averages. Never solve growth by dropping requested artifacts. |
| Existing dirty work | Do not deploy an unrecorded dirty tree as a research release. Incorporate the owner's intended changes into an explicit reviewed release while preserving their current files. |
| Public access and notifications | Default to owner-only access and no public sharing. Add an external notification channel only after the owner selects and authorizes it. |

The essential decisions for implementation are the billing mode and cap, the intended standard OpenAI route, the exploratory versus confirmatory classification of the first five games, and the hosting/region preference. Everything else above has a practical default and can be implemented without a large database or a multi-vendor application rewrite.

## Inspection record and reproducibility

This round used read-only code inspection, file statistics, recorded usage data, and public unauthenticated model/pricing GETs. It did not test live provider compatibility, actual cloud RAM use, deployment throughput, recovery under injected failures, or paid spending controls. Those are future acceptance checks, not findings claimed as passed.

The raw local measurements are in `/tmp/mb-cloud-plan/run_measurements.json`. Model catalog and endpoint snapshots used for this review are also in `/tmp/mb-cloud-plan/`. They contain public data. The repository working tree was not changed. The complete implementation should be developed in a separately authorized working phase, keeping the user's current roadmap and historical outputs intact.
