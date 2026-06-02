# Monopoly Microbench

`monopoly_microbench` owns the benchmark-only micro-decision suite. It loads frozen
DecisionPoint fixtures from `contracts/micro`, validates scenario and suite
metadata, reuses the shared arena decision resolver, scores deterministic rubric
criteria, and writes isolated artifacts under `runs/micro` and
`runs/micro_batches`.

Common commands from `python/`:

```bash
uv run --project packages/microbench monopoly-micro validate
uv run --project packages/microbench monopoly-micro list --suite micro-v1
uv run --project packages/microbench monopoly-micro run --scenario buy-or-auction-vermont-light-blue-tempo-01 --model openai/gpt-oss-120b --prompt-condition live_game
uv run --project packages/microbench monopoly-micro run-suite --suite micro-v1 --model openai/gpt-oss-120b --prompt-condition live_game
uv run --project packages/microbench monopoly-micro compare --suite micro-v1 --models configs/micro-models.json --prompt-condition live_game
uv run --project packages/microbench monopoly-micro score --run-id <run-id> --write
uv run --project packages/microbench monopoly-micro export --batch-id <batch-id> --format csv --out micro-results.csv
uv run --project packages/microbench monopoly-micro tui
```

## What is in micro-v1

`micro-v1` contains 130 frozen `DecisionPoint` fixtures under
`contracts/micro/scenarios`, with exact category counts from
`micro-decision.md`:

- `BUY_OR_AUCTION`: 20
- `AUCTION`: 20
- `TRADE_PROPOSE`: 20
- `TRADE_RESPONSE`: 10
- `BUILD_OR_MORTGAGE`: 20
- `LIQUIDATION`: 10
- `JAIL`: 15
- `POST_TURN_STRATEGY`: 15

The suite manifest is `contracts/micro/suites/micro-v1.json`. Research notes
and the scenario backlog live in `contracts/micro/research/scenario_backlog.md`.
The fixture generator is deliberately definition-driven rather than index-pattern
driven: scenario IDs, descriptions, trap actions, source claims, reference
rationales, legal-action context, and rubrics are curated per scenario.

## API and artifacts

FastAPI exposes the thin adapter endpoints:

- `GET /micro/scenarios`
- `GET /micro/scenarios/{scenario_id}`
- `GET /micro/suites`
- `GET /micro/suites/{suite_id}`
- `POST /micro/run`
- `GET /micro/runs/{run_id}`
- `POST /micro/batches`
- `GET /micro/batches/{batch_id}`
- `GET /micro/batches/{batch_id}/leaderboard`

Single-run artifacts are isolated under `runs/micro/<run_id>`. Batch artifacts
are isolated under `runs/micro_batches/<batch_id>`.

`prompt_condition` is recorded on each run and currently supports only
`live_game`. Micro runs intentionally use the same prompt path as normal
MonopolyBench game decisions so micro-decision results are directly comparable
to live-game behavior. The `/micro` frontend page exposes single runs, category
batches, full-suite batches, result inspection, artifact paths, and category
leaderboards using this fixed prompt mode.

The Rich TUI (`monopoly-micro tui`) mirrors the micro dashboard workflow in a
terminal-friendly form: search/filter scenarios, inspect scenario details, run a
single scenario, run the filtered/category scope, run the full suite, and review
leaderboards, score breakdowns, artifacts, and failures. Batch runs continue
after individual scenario failures and show progress bars instead of streaming
model output. It supports keyboard navigation with arrows, tab/shift-tab, enter,
escape, and shortcut keys, plus terminal mouse clicks where the terminal reports
SGR mouse events.
