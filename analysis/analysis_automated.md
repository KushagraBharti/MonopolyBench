# MonopolyBench Automated Analysis

This file describes what MonopolyBench already automates after a full game, what is still manual, and how to run the current automated saved-game analysis suite. It is the operational companion to `analysis_process.md` and `analysis.md`.

Use the three analysis files this way:

| File | Role |
|---|---|
| `analysis_process.md` | The high-level step-by-step workflow for analyzing a completed full game. |
| `analysis.md` | The deep research memo: what to analyze, why it matters, metric ideas, labels, formulas, and interpretive boundaries. |
| `analysis_automated.md` | The current automation map: what scripts generate, what remains manual, and how to run the automated artifacts for a saved game. |

## Current Automation Map

| Part | Automated Now? | Output |
|---|---:|---|
| Raw run capture | Yes | `runs/<run_id>/events.jsonl`, `actions.jsonl`, `decisions.jsonl`, `state/`, `prompts/` |
| Prompt/response audit files | Yes | `quality_check/<run_id>/*_request.txt`, `*_response.txt` |
| Summary | Yes | `summary.json` |
| Scorecard | Yes | `scorecard.json`, `scorecard_players.json`, `scorecard_decisions.jsonl`, `scorecard_events.jsonl` |
| Usage/cost/token accounting | Yes | `usage.json`, `usage_attempts.jsonl`, `usage_decisions.jsonl`, `cost_report.json` |
| Replay verification | Yes | `state_replay_report.json`, `artifact_replay_report.json`, `replay_report.json` |
| Trace/failure detection | Yes | `trace_findings.jsonl`, `trace_summary.json`, `failure_findings.jsonl`, `failure_summary.json` |
| Review queue | Yes, basic | `review_queue.jsonl` |
| Saved-game packaging | Yes | `saved_games/<name>/run/`, `quality_check/`, `saved_game_manifest.json` |
| CSV table generation | Yes | `analysis/tables/*.csv` |
| Graph generation | Yes | `analysis/plots/*.png` |
| Coverage/inventory | Yes | `analysis/coverage/*.csv` |
| Written reports | Yes, basic | `analysis/reports/analysis_report.md`, `coverage_report.md`, `data_dictionary.md` |
| Analysis zip | Yes | `<saved_game_name>-analysis.zip` |
| Manual deception/collusion review | Not fully automated | Needs human labels |
| Promise lifecycle review | Not fully automated | Planned |
| Trade surplus / regret oracle | Not automated yet | Planned |
| Branch counterfactuals | Not automated yet | Planned |
| Cross-run statistical modeling | Not automated yet | Planned |
| Paper-ready case studies | Mostly manual | Analyst-written from evidence |

## Main Automation Entry Points

| Script/module | What it automates |
|---|---|
| `scripts/standardize_saved_games.py` | Standardizes saved-game layout, archives older analysis outputs, generates tables, plots, reports, coverage files, manifest, and analysis zip. |
| `scripts/verify.ps1` | Runs the repo verification suite. This checks the codebase, not one specific saved game, but it should pass before trusting new behavioral or artifact changes. |
| `python/packages/telemetry/src/monopoly_telemetry/summary.py` | Builds run summary artifacts. |
| `python/packages/telemetry/src/monopoly_telemetry/scorecard.py` | Builds scorecard artifacts. |
| `python/packages/telemetry/src/monopoly_telemetry/usage.py` | Builds OpenRouter usage, token, and cost artifacts from actual provider data. |
| `python/packages/telemetry/src/monopoly_telemetry/analysis.py` | Builds deterministic trace and failure findings. |
| `python/packages/telemetry/src/monopoly_telemetry/experiment.py` | Builds experiment manifests and review-cost aggregate artifacts. |
| `python/packages/telemetry/src/monopoly_telemetry/review.py` | Stores human review labels and review summaries. |
| `python/packages/arena/src/monopoly_arena/replay_verification.py` | Builds state replay, artifact replay, replay navigation, replay flags, replay steps, event hashes, and replay diff artifacts. |
| `python/packages/arena/src/monopoly_arena/batch_artifacts.py` | Builds batch-level scorecard, replay, usage, cost, token, trace, failure, leaderboard, and manifest artifacts. |
| `python/packages/arena/src/monopoly_arena/batch_run.py` | Runs configured batches from the command line. |
| `python/packages/arena/src/monopoly_arena/long_campaign.py` | Plans and executes long-horizon campaigns and aggregates run-level artifacts. |
| `python/packages/arena/src/monopoly_arena/run.py` | Runs a full game from the command line. |
| `python/packages/microbench/src/monopoly_microbench/cli.py` | Runs and reports targeted micro suites. |

## Automation Dependency Graph

The automated pipeline has three stages:

```text
full game runner
  -> raw run artifacts in runs/<run_id>/
  -> quality-check text in quality_check/<run_id>/
  -> post-run telemetry artifacts in runs/<run_id>/
  -> saved-game folder assembly
  -> scripts/standardize_saved_games.py
  -> saved_games/<name>/analysis/
  -> saved_games/<name>/<name>-analysis.zip
```

The full-game runner is responsible for the canonical evidence: events, actions, decisions, snapshots, prompts, responses, usage, scorecards, and replay reports. The saved-game standardizer is responsible for the analysis layer: tables, plots, reports, coverage, layout cleanup, manifest, and zip.

The standardizer does not call the models, does not mutate the game, and does not rewrite canonical run artifacts. It reads the saved run and produces derived analysis outputs.

## Command Recipes

### Run Code Verification

Use this when source code, schemas, replay logic, telemetry, analysis code, or frontend/API behavior changed:

```powershell
pwsh -File scripts/verify.ps1
```

This is a repo-level verification suite. It is not a substitute for inspecting a particular saved game.

### Run A CLI Full Game

The UI is normally used for live full-game experiments, but the CLI entrypoint exists:

```powershell
uv run python -m monopoly_arena.run --seed 123 --max-turns 20
```

Use CLI runs mainly for controlled smoke/debug work unless the experiment plan explicitly says otherwise.

### Run Saved-Game Analysis

Use this after `saved_games/<saved_game_name>/run/` and ideally `saved_games/<saved_game_name>/quality_check/` exist:

```powershell
uv run python scripts/standardize_saved_games.py <saved_game_name>
```

### Run Saved-Game Analysis For The Two Current Canonical Saved Games

```powershell
uv run python scripts/standardize_saved_games.py frontier-191-mock-83265-81ed4937-openai-gpt-5-5 frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview
```

### Run The Built-In Default Saved-Game List

```powershell
uv run python scripts/standardize_saved_games.py
```

Only use the default list when it matches the saved games you intend to refresh. For new runs, pass the saved-game name explicitly.

## Expected Saved-Game Layout

The automated saved-game analysis expects this structure:

```text
saved_games/<saved_game_name>/
  run/
    events.jsonl
    actions.jsonl
    decisions.jsonl
    state/
    prompts/
    summary.json
    scorecard.json
    usage.json
    replay_report.json
    state_replay_report.json
    artifact_replay_report.json
    ...
  quality_check/
    decision_<run_id>-dec-000000_request.txt
    decision_<run_id>-dec-000000_response.txt
    ...
```

After running the automated analysis, the folder should also contain:

```text
saved_games/<saved_game_name>/
  analysis/
    manifest.json
    coverage/
    plots/
    reports/
    tables/
  saved_game_manifest.json
  <saved_game_name>-analysis.zip
```

`run/` and `quality_check/` are the canonical evidence folders. `analysis/` is regenerated from those artifacts. Previous generated analysis folders and zips are archived under `saved_games/archive/<saved_game_name>/` instead of being deleted.

## Remote Artifact Workflow

When another laptop runs the expensive game and pushes everything to Git, the analyzer should not re-run the game. The intended workflow is:

1. Pull the commit containing `runs/<run_id>/` and `quality_check/<run_id>/`.
2. Create a saved-game folder:

```text
saved_games/<saved_game_name>/
  run/
  quality_check/
```

3. Copy the pulled raw run artifacts into `run/`.
4. Copy the pulled quality-check artifacts into `quality_check/`.
5. Run:

```powershell
uv run python scripts/standardize_saved_games.py <saved_game_name>
```

6. Review `analysis/reports/analysis_report.md`, `analysis/reports/coverage_report.md`, and the generated plots/tables.
7. Commit the polished saved-game folder if it is meant to become canonical.

This preserves the expensive model run exactly as played while allowing analysis to happen on any laptop.

## How To Run Automated Analysis For A Saved Game

From the repo root:

```powershell
uv run python scripts/standardize_saved_games.py <saved_game_name>
```

Example:

```powershell
uv run python scripts/standardize_saved_games.py frontier-191-mock-83265-81ed4937-openai-gpt-5-5
```

For multiple saved games:

```powershell
uv run python scripts/standardize_saved_games.py frontier-191-mock-83265-81ed4937-openai-gpt-5-5 frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview
```

If no saved-game names are passed, the script uses its built-in default saved-game list.

## How To Package A Raw Run Before Analysis

If a run comes from another laptop through Git and only has raw folders:

```text
runs/<run_id>/
quality_check/<run_id>/
```

create a saved-game folder with this shape:

```text
saved_games/<saved_game_name>/
  run/            copied from runs/<run_id>/
  quality_check/  copied from quality_check/<run_id>/
```

Then run:

```powershell
uv run python scripts/standardize_saved_games.py <saved_game_name>
```

The saved-game name should encode the important paper-facing identity:

```text
frontier-<turns>-<run_id>-<winning-model>
frontier-mini-<turns>-<run_id>-<winning-model>
```

Example:

```text
frontier-191-mock-83265-81ed4937-openai-gpt-5-5
frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview
```

## What The Standardizer Generates

`scripts/standardize_saved_games.py` currently generates:

| Area | Files |
|---|---|
| Manifest | `analysis/manifest.json`, `saved_game_manifest.json` |
| Coverage | `analysis/coverage/artifact_presence.csv`, `file_inventory.csv`, `file_inventory_summary.csv` |
| Reports | `analysis/reports/analysis_report.md`, `coverage_report.md`, `data_dictionary.md` |
| Usage tables | `model_usage.csv`, `per_call_usage.csv`, `per_turn_usage_by_player.csv`, `per_turn_usage_total.csv`, `top_costliest_calls.csv`, `top_slowest_calls.csv`, `top_output_token_calls.csv`, `top_reasoning_token_calls.csv` |
| Run tables | `run_summary.csv`, `players.csv`, `actions.csv`, `decisions.csv`, `events.csv`, `events_by_turn.csv`, `decision_type_counts.csv`, `event_counts.csv` |
| State/property tables | `state_by_turn_player.csv`, `property_holdings_by_turn.csv`, `bank_inventory_by_turn.csv` |
| Mechanism tables | `cash_flow.csv`, `asset_flow.csv`, `auction_threads.csv`, `negotiation_threads.csv` |
| Review tables | `trace_findings.csv`, `failure_findings.csv`, `review_queue.csv` |
| Cost/token plots | `cost_by_turn.png`, `cost_per_call.png`, `cumulative_cost_by_call.png`, `tokens_by_turn.png`, `output_tokens_per_call.png`, `reasoning_tokens_per_call.png`, `cost_by_model.png`, `total_tokens_by_model.png`, `reasoning_tokens_by_model.png` |
| Game-state plots | `net_worth_estimate_by_turn.png`, `cash_by_turn.png`, `property_value_by_turn.png`, `building_value_by_turn.png`, `mortgage_liability_by_turn.png`, `property_count_by_turn.png`, `houses_by_turn.png`, `hotels_by_turn.png`, `bank_inventory_by_turn.png` |
| Reliability/activity plots | `latency_per_call.png`, `calls_by_turn.png`, `calls_by_model.png`, `decision_type_counts.png`, `event_counts.png` |
| Share artifact | `<saved_game_name>-analysis.zip` |

The current output is strong for descriptive analysis: cost, tokens, model activity, event frequency, state trajectories, property holdings, outlier calls, and artifact coverage.

## Source-To-Output Map

Use this map when debugging a missing table or plot.

| Output | Main source artifacts |
|---|---|
| `analysis/tables/actions.csv` | `run/actions.jsonl` |
| `analysis/tables/decisions.csv` | `run/decisions.jsonl` |
| `analysis/tables/events.csv` | `run/events.jsonl` |
| `analysis/tables/model_usage.csv` | `run/usage_attempts.jsonl`, `run/usage.json` |
| `analysis/tables/per_call_usage.csv` | `run/usage_attempts.jsonl` |
| `analysis/tables/per_turn_usage_total.csv` | `run/usage_attempts.jsonl` grouped by `turn_index` |
| `analysis/tables/state_by_turn_player.csv` | `run/state/*.json` |
| `analysis/tables/property_holdings_by_turn.csv` | `run/state/*.json`, board metadata |
| `analysis/tables/bank_inventory_by_turn.csv` | `run/state/*.json` |
| `analysis/tables/cash_flow.csv` | `run/cash_flow.jsonl` if present |
| `analysis/tables/asset_flow.csv` | `run/asset_flow.jsonl` if present |
| `analysis/tables/auction_threads.csv` | `run/auction_threads.jsonl` if present |
| `analysis/tables/negotiation_threads.csv` | `run/negotiation_threads.jsonl` if present |
| `analysis/tables/trace_findings.csv` | `run/trace_findings.jsonl` |
| `analysis/tables/failure_findings.csv` | `run/failure_findings.jsonl` |
| `analysis/tables/review_queue.csv` | `run/review_queue.jsonl` |
| `analysis/plots/*cost*` | usage tables |
| `analysis/plots/*tokens*` | usage tables |
| `analysis/plots/*net_worth*`, `*cash*`, `*property*`, `*houses*`, `*hotels*` | state/player/property tables |
| `analysis/reports/coverage_report.md` | artifact presence and file inventory |
| `<saved_game_name>-analysis.zip` | Current `analysis/` folder |

If a source artifact is missing, the generated table may be empty or absent. Empty tables are not necessarily script failures; they can mean the run had no events of that type or the source artifact was not generated.

## What Is Automated During A Full Game

During and immediately after a full game, the run pipeline already writes:

1. Event stream: `events.jsonl`.
2. Applied actions: `actions.jsonl`.
3. Decision records: `decisions.jsonl`.
4. State snapshots: `state/`.
5. Prompt/response JSON artifacts: `prompts/`.
6. Human-readable quality-check request/response files: `quality_check/<run_id>/`.
7. Summary: `summary.json`.
8. Usage and cost accounting from OpenRouter actuals.
9. Scorecards.
10. Trace/failure findings.
11. Review queue.
12. Replay artifacts.

The exact post-run artifacts are generated by the runner and telemetry modules. The saved-game standardizer assumes those artifacts already exist and then builds the polished analysis layer.

## What Is Not Fully Automated Yet

The remaining work is research-level analysis, not basic file generation.

| Not automated | Why it matters |
|---|---|
| Manual deception/collusion labels | Deception and collusion require evidence-linked human judgment, not automatic keyword matching. |
| Promise lifecycle tracking | The system needs to link promise creation, maintenance, breach, and downstream effect across turns. |
| Trade surplus / regret oracle | Requires counterfactual valuation of accepted/rejected trades, not just accounting totals. |
| Branch counterfactuals | Requires replaying alternate actions under declared continuation policies. |
| Robust cross-run statistics | Requires multiple balanced seat/seed blocks and model/route controls. |
| Paper-ready case studies | Requires analyst-written narratives with source IDs, economic context, and bounded claims. |

These should remain separate from model-facing prompts. They are downstream research labels and should never leak into the decision surface.

## Current Automation Limits

The current automation is intentionally conservative. It creates evidence and triage material, but it does not pretend to solve subjective or counterfactual research questions.

| Limit | Current behavior | What future automation should do |
|---|---|---|
| Deception/collusion | Produces candidates and review queues, but final labels require humans. | Build richer review packets and adjudication summaries. |
| Promise tracking | Some communication traces exist, but promise lifecycle is not fully linked. | Extract promise creation, modification, fulfillment, breach, and excuse windows. |
| Trade value | Tables show trade terms and board effects where available. | Add oracle/branch estimates for proposer/counterparty/third-party value. |
| Auction value | Tables show bids and events. | Add blocker/synergy/winner's-curse decomposition. |
| Regret | Decision tables exist, but robust regret needs branch/oracle support. | Add declared oracle tiers and sensitivity intervals. |
| Cross-run statistics | Batch/campaign summaries exist, but paper claims still need balanced design. | Add seat/seed block statistics and uncertainty reports. |
| Visual publication polish | Current plots are analysis-grade. | Add paper-specific figures with locked styling and captions. |

## Post-Run Sanity Checks

After running the standardizer, inspect these files first:

```text
saved_games/<saved_game_name>/saved_game_manifest.json
saved_games/<saved_game_name>/analysis/manifest.json
saved_games/<saved_game_name>/analysis/reports/coverage_report.md
saved_games/<saved_game_name>/analysis/reports/analysis_report.md
saved_games/<saved_game_name>/analysis/tables/model_usage.csv
saved_games/<saved_game_name>/analysis/tables/run_summary.csv
saved_games/<saved_game_name>/analysis/tables/state_by_turn_player.csv
saved_games/<saved_game_name>/analysis/plots/net_worth_estimate_by_turn.png
saved_games/<saved_game_name>/<saved_game_name>-analysis.zip
```

The first manual checks should be:

1. Does `saved_game_manifest.json` point to the expected `run/`, `quality_check/`, and `analysis/` layout?
2. Does `coverage_report.md` show missing critical artifacts?
3. Does `run_summary.csv` match the expected winner, turn count, and endpoint?
4. Does `model_usage.csv` match the UI/summary cost and token totals?
5. Do the net-worth and cost plots include all expected players/models?
6. Was the analysis zip regenerated after the latest `analysis/` folder?

## Recommended Full Automated Pass

For a finished saved game, the current automated pass is:

1. Confirm the saved game has `run/` and, ideally, `quality_check/`.
2. Confirm `run/replay_report.json`, `run/state_replay_report.json`, and `run/artifact_replay_report.json` exist.
3. Run:

```powershell
uv run python scripts/standardize_saved_games.py <saved_game_name>
```

4. Confirm these exist:

```text
saved_games/<saved_game_name>/analysis/manifest.json
saved_games/<saved_game_name>/analysis/reports/analysis_report.md
saved_games/<saved_game_name>/analysis/reports/coverage_report.md
saved_games/<saved_game_name>/analysis/tables/model_usage.csv
saved_games/<saved_game_name>/analysis/tables/per_call_usage.csv
saved_games/<saved_game_name>/analysis/plots/net_worth_estimate_by_turn.png
saved_games/<saved_game_name>/analysis/plots/cost_by_turn.png
saved_games/<saved_game_name>/saved_game_manifest.json
saved_games/<saved_game_name>/<saved_game_name>-analysis.zip
```

5. Run the repo verification suite when code changed:

```powershell
pwsh -File scripts/verify.ps1
```

If only new run artifacts were added and no source code changed, the saved-game standardizer plus artifact inspection is usually the relevant run-specific check. If source code, schemas, replay logic, telemetry, or analysis scripts changed, run `scripts/verify.ps1`.

## Research Readiness Checklist

Automated artifacts are ready for manual research review when:

1. `state_replay_report.json` passes, or any failure is understood and documented.
2. `artifact_replay_report.json` is either passed or has a clear strict-metadata explanation.
3. `usage_attempts.jsonl` has one row per model call attempt or explicit missingness.
4. `scorecard.json` and `summary.json` agree with the final snapshot.
5. `analysis/coverage/artifact_presence.csv` does not show missing artifacts needed for the claim.
6. `analysis/tables/model_usage.csv` reconciles with `usage.json`.
7. Graphs and tables were regenerated after the final run artifacts were frozen.
8. The analysis zip matches the current `analysis/` folder.

After this point, move to the manual parts of `analysis_process.md`: review trades, bankruptcy windows, public/private messages, deception/collusion candidates, promise lifecycle, critical decisions, and paper case studies.
