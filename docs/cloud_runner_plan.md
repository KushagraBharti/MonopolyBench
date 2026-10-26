# MonopolyBench cloud runner: complete plan

Date: 2026-10-24, revision 3
Status: proposal. Nothing in this document is implemented yet.
Authors: Claude (Opus 5.5) with Codex `gpt-6-astra` at xhigh effort. Both investigated the code independently, argued two rounds, and Astra reviewed a full draft adversarially. Revision 3 applies all of the owner's decisions and is meant to be read on its own. Supporting evidence (measurements, dated price snapshots, review notes, and the two design reference screenshots) is archived with SHA-256 hashes in `docs/research_raw/cloud_runner_2026-10-24/`.

## Contents

1. Goal and outcome
2. Final decisions
3. What the code does today
4. Measured workload and cost
5. Models, OpenRouter, and BYOK
6. Architecture
7. Railway setup, step by step
8. Data layout on the volume
9. The job ledger (SQLite schema)
10. How games run
11. Durability, crash repair, and recovery
12. Provider errors, outages, and deadlines
13. Cost accounting
14. Removing the turn cap
15. Campaigns, smoke games, and research integrity
16. Artifacts, packages, and export to the laptop
17. API
18. Dashboard and frontend
19. Access control
20. Code changes, file by file
21. Tests
22. Rollout
23. Operations runbook
24. Risks
25. Effort estimate
26. Review history
27. Sources

## 1. Goal and outcome

Start several full Monopoly games from a web dashboard, close the laptop, and come back hours later to finished games. Each game must keep every artifact a local run writes today. Finished games must be easy to copy to the laptop in the layout the existing analysis tools already read.

Every full game from now on counts for the paper, so the very first full game must already run under the final, frozen setup. Short smoke games of 5 to 10 turns test the deployment beforehand and never enter the paper.

When this plan is done:

- One Railway service supports up to eight games at once and queues the rest in a fixed, preregistered order. The default worker-slot setting remains five.
- Each game runs in its own worker process. Closing the browser or the laptop changes nothing.
- A crash, deploy, or platform restart is repaired or resumed automatically. A game that cannot be repaired fails visibly with all evidence kept, and its campaign cell is rerun once.
- Every artifact is written in the same layout as a local run, plus records of every HTTP call and every repair.
- One command downloads finished games to `saved_games/` with hash checks.

## 2. Final decisions

| Topic | Decision |
| --- | --- |
| Host | Railway Pro, one service, one persistent volume. Hetzner, Fly, and Cloudflare are not used. |
| Frontend | Served by the same Railway service. Vercel is not used. |
| Database | SQLite on the Railway volume. Supabase and Neon are not used. |
| Security | One dashboard password and one export token. No Cloudflare Access or Tunnel. |
| Models | `anthropic/claude-opus-5.5`, `openai/gpt-6.1-sol`, `google/gemini-4-argon`, `x-ai/grok-4.7`. |
| Reasoning effort | `medium` for all four seats. |
| Billing | All calls through OpenRouter. OpenAI and Anthropic seats use your own keys through OpenRouter BYOK. Google and xAI seats use OpenRouter credits. |
| Spending | No cap. Every cost is recorded and shown. |
| Turn cap | None for full games. Games end by bankruptcy. Smoke games use a 5 to 10 turn cap. |
| Trade and auction limits | Unchanged: 20 trade exchanges and 200 auction actions per negotiation or auction. These bound a single negotiation or auction, not the game. |
| Paper status | Every full game counts. Smoke games are labeled `smoke` and excluded. |
| Crash repair | Built in from the start. A properly repaired game counts as a valid game. "Properly" is defined in section 11. |
| Provider outages | Outage policy v1: the decision stays pending, the game pauses, and the same saved request is retried every 5 minutes, at most 12 times. |
| Notifications | None. Status lives on the dashboard. |
| Number of games | Decided later. The campaign format supports adding seed blocks over time. |

## 3. What the code does today

These findings come from the code at commit `c370c87c` and the eight saved games. Python paths are under `python/`. Each item explains why a change in section 20 exists.

1. The API runs one game. `RunManager` holds one runner, one asyncio task, one snapshot, and one set of WebSocket clients (`apps/api/src/monopoly_api/run_manager.py:30`). Starting a different run stops the active run (`run_manager.py:77`). `/run/stop`, `/run/pause`, `/run/resume`, `/run/status`, and `/ws` take no run ID.
2. Batch and campaign runs are sequential. `long_campaign.py` records `concurrency_requested` but sets `concurrency_effective` to 1 (`packages/arena/src/monopoly_arena/long_campaign.py:440`).
3. Games need separate processes. The OpenRouter client is async httpx (`openrouter_client.py:25`), and each runner has its own engine and RNG. Finalization, replay verification, scorecards, and trace analysis are synchronous and load whole JSONL files, so in a shared asyncio loop one finishing game would delay the other four.
4. A slow browser can slow a game, because the runner awaits WebSocket sends inside its event path (`run_manager.py:181`, `run_manager.py:210`).
5. Recovery exists, but only at a clean boundary. `POST /run/recover` replays recorded actions from the seed, compares the full canonical event stream, and rebuilds prompt memory (`packages/arena/src/monopoly_arena/llm_runner.py:141`). It rejects a replay with no pending decision (`llm_runner.py:189`). Nothing scans for interrupted games at startup.
6. The recovery reader hides damage. `_read_jsonl` in `run_manager.py:960` skips malformed lines instead of failing.
7. Recovery overwrites evidence. Attempt-0 prompt files are named `decision_<id>_{system,user,tools,response,parsed}` (`run_files.py:368`) and written with `write_text`, so a resumed call overwrites files from the lost attempt in `prompts/` and `quality_check/`. A crash during a request can leave no standalone prompt files, though `decisions.jsonl` may hold the `decision_started` payload (`decision_resolver.py:198`).
8. Each decision is written in four separate steps: the action in memory, then a line in `actions.jsonl`, then the resolved entry in `decisions.jsonl`, then each event (`llm_runner.py:335` to `llm_runner.py:370`). A crash between the action line and its events makes recovery fail its event-equality check.
9. Writes are not durable. `append_jsonl` does not fsync (`telemetry/.../writer_jsonl.py:8`), and JSON files use a direct `write_text`.
10. Wire-file write failures are ignored. The quality-artifact writer catches `OSError` and lets the decision continue (`decision_resolver.py:859`).
11. Finalization is inline and not idempotent. The runner writes `summary.json` first, then usage, pricing, experiment, scorecard, replay, trace, and manifest files (`llm_runner.py:235` to `llm_runner.py:263`). Recovery refuses any run that has `summary.json` (`run_manager.py:114`).
12. The pricing snapshot is a fresh catalog GET at the end of the run (`llm_runner.py:274`), not the start.
13. Transport failures become game moves. After transport retries fail, `decision_resolver.py:268` returns a deterministic fallback outcome, which `LlmRunner` applies at `llm_runner.py:335`. HTTP 402 is classified as `http_4xx` (`openrouter_client.py:110` to `openrouter_client.py:119`), and a missing key returns `no_api_key` (`openrouter_client.py:79`). Both fall back, so an empty account would let games run to the end on fallback moves.
14. One resolver attempt can send up to three HTTP requests, and the corrective retry three more (`openrouter_client.py:105`). The 30-second httpx timeout applies per read, so no request has a total deadline. Generation-metadata lookups (`decision_resolver.py:399`) and the end-of-run catalog GET (`llm_runner.py:287`) have no total deadline either.
15. Cost is wrong for BYOK calls. The repo's July 2026 BYOK probe (`analysis/research_protocol/control_audit/openrouter_byok_probe_*`) found that BYOK calls report `usage.cost` as 0 and the provider cost in `cost_details.upstream_inference_cost`. `usage.py` builds cost from `usage.cost`, and only from `decision_resolved` rows (`usage.py:32`).
16. The new models are unknown to the code. `DEFAULT_PROVIDER_BY_MODEL_ID` in `packages/arena/src/monopoly_arena/player_config.py` and `apps/api/src/monopoly_api/config/players.json` list only older models. `PlayerSpec` in `POST /run/start` has no reasoning or provider field. Overriding a seat's model can keep the old seat's provider pin (`player_config.py:152`).
17. The old preflight cannot test the new roster. It forces a named tool (`scripts/research/capture_openrouter_preflight.py:288`). Production sends `tool_choice="auto"`, and the Opus 5.5 endpoint advertises `auto` but not a forced tool.
18. The engine always has a turn cap. `Engine._should_end_game` ends the game when `turn_index >= max_turns` (`packages/engine/src/monopoly_engine/engine.py:3075`). `max_turns` is an integer in the campaign schema (`contracts/schemas/research_registry.schema.json:206`), the artifact schema (`benchmark_artifact.schema.json:261`), and `contracts/ts/research.ts:83`. It never appears in prompts or snapshots.
19. Each run writes to two trees. `quality_check/<run_id>/` sits beside `runs/`, not inside it (`run_files.py:223`).
20. The local standardizer would move new cloud files. `scripts/standardize_saved_games.py:82` preserves only `run`, `quality_check`, `analysis`, and `saved_game_manifest.json`, and lines 238 to 246 move every other root entry into `run/`.
21. The frontend assumes one global run. It opens one WebSocket to `/ws`, polls `/run/status` every 2.5 seconds (`frontend/src/pages/LiveBenchPage.tsx:91`), keeps one snapshot (`state/store.ts:45`), and labels any stopped run with an ID as complete. Run cards infer replay status from which report files exist (`RunsPage.tsx:77`). CORS allows only localhost, and there is no auth.
22. The campaign runner already builds a run matrix with Latin-square seats and a fixed execution order, and has credit and preflight gates and a billing guard (`long_campaign.py:836`, `long_campaign.py:2320`). The cloud scheduler reuses the matrix and order.

## 4. Measured workload and cost

Numbers come from the eight saved games (`docs/research_raw/cloud_runner_2026-10-24/run_measurements.json`). Core means `run/` plus `quality_check/`, in logical bytes. Span is first request to last response.

| Game | Models | Turns | Decisions / attempts | Core MiB | Core files | Recorded cost | Span hours |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R115 | frontier | 115 | 366 / 377 | 47.6 | 3,163 | $14.61 | 1.96 |
| R163 | frontier | 163 | 364 / 371 | 44.3 | 3,167 | $12.06 | 1.39 |
| R166 | frontier | 166 | 488 / 502 | 66.2 | 4,212 | $21.91 | 15.49 |
| R172 | frontier | 172 | 613 / 631 | 79.3 | 5,246 | $24.60 | 8.93 |
| R191 | frontier | 191 | 583 / 604 | 78.1 | 5,043 | $27.71 | 3.95 |
| Mini154 | mini | 154 | 396 / 401 | 55.1 | 3,400 | $4.65 | 1.34 |
| Mini157 | mini | 157 | 346 / 355 | 48.7 | 3,029 | $4.04 | 1.28 |
| Mini273 | mini | 273 | 540 / 549 | 75.5 | 4,697 | $4.24 | 1.65 |

Frontier means Opus 4.8, Gemini 3.1 Pro, Grok 4.3, and GPT-5.5 at medium effort. All eight ended by bankruptcy.

### Storage

Core bytes average 61.85 MiB per game. In R191, `decisions.jsonl` alone is 30 MB and `prompts/` holds 3,020 files. Plan for 100 to 250 MB per final package. The new call records and the crash-repair journal add roughly the size of `decisions.jsonl` again while a game runs. The journal is compacted to a hash index at finalization. A 50 GB volume holds well over 100 games with room for staging.

### Time

In the five frontier games, the per-game median attempt latency was about 9 to 12 seconds, GPT-5.5's median about 13 to 38 seconds, and the per-game 95th percentile about 38 to 81 seconds. Six games spanned 1.3 to 4.0 hours. R166 contains a single 12.26-hour attempt interval, and R172 spans 8.93 hours with only 3.51 hours of attempt latency. The artifacts do not say what caused those gaps. A server removes laptop sleep, but nothing guarantees a 3 to 4 hour finish. If every game takes 3.5 hours and five run at once, 24 games take about 17.5 hours and 48 games about 35 hours.

### Model cost per game

For each lab: recorded prompt tokens times the new input price, plus recorded completion tokens times the new output price, divided by one million. Reasoning tokens sit inside completion tokens, and no cache discounts were applied. R191 has one attempt without usage. These are scenarios, not bounds. New models can play longer or shorter games, and without a turn cap a long game costs more.

| Seat | Mean cost per game | Paid from | Per 24 games | Per 48 games |
| --- | ---: | --- | ---: | ---: |
| GPT-6.1 Sol, $2 / $10 | $4.36 | Your OpenAI account through BYOK | $105 | $209 |
| Claude Opus 5.5, $4 / $20 | $4.62 | Your Anthropic account through BYOK | $111 | $222 |
| Gemini 4 Argon, $2 / $10 | $1.53 | OpenRouter credits | $37 | $73 |
| Grok 4.7, $2 / $6 | $0.89 | OpenRouter credits | $21 | $43 |
| Total | $11.41, range $7.53 to $15.81 | | $274 | $548 |

OpenRouter may also charge a BYOK fee from your OpenRouter credits. Third-party write-ups describe 5% above a monthly free threshold but disagree on the threshold, so check OpenRouter's pricing page. Keep OpenRouter credits funded, because BYOK calls fall back to them (section 5).

### Hosting cost

Railway Pro has a $20 monthly minimum that includes $20 of usage. RAM is $10 per GB-month, CPU $20 per vCPU-month, and volume storage $0.15 per GB-month, billed by the minute. Assuming 0.1 average vCPU, 2 to 4 GB of average RAM, and 10 to 20 GB of data, that is about $25 to $45 a month. Backups are incremental and priced like volume storage. Egress is $0.05 per GB, so downloading 12 GB to the laptop costs about $0.60.

## 5. Models, OpenRouter, and BYOK

### Model routes

| Model | Context | Standard route and price per 1M in/out | Other endpoints for the same model | Effort levels |
| --- | ---: | --- | --- | --- |
| `anthropic/claude-opus-5.5` | 1,000,000 | `anthropic`, $4 / $20 | `anthropic/fast` $8 / $40; Bedrock, Vertex, Azure | low, medium, high, xhigh, max |
| `openai/gpt-6.1-sol` | 1,050,000 | `openai`, $2 / $10; $4 / $15 above 272,000 prompt tokens | `/flex` $1 / $5, `/fast` $4 / $20, `/ultrafast` $12 / $60, Azure | low, medium, high, xhigh, max |
| `google/gemini-4-argon` | 1,048,576 | `google-ai-studio`, $2 / $10 | `/flex` $1 / $5, `/priority` $3.60 / $18, Vertex | low, medium, high |
| `x-ai/grok-4.7` | 500,000 | `xai`, $2 / $6; $4 / $12 above 200,000 prompt tokens | `xai/zdr`, `xai/zdr/us` $2.20 / $6.60, `/priority` $4 / $12 | low, medium, high, xhigh |

All four support `tools`, `tool_choice`, `reasoning`, and `reasoning_effort`. Prompts are a few thousand tokens per call, far below the long-context thresholds. These prices come from the public catalog on 2026-10-24, and the execution manifest records the catalog at the start of every game.

Each seat sends `reasoning: {"effort": "medium"}` and `provider: {"only": ["<standard route>"], "allow_fallbacks": false}`. A base route matches the provider's variants and regions but not its paid service tiers. The worker saves the eligible endpoint set at launch and records the returned model, provider, and any endpoint identity on every call. A response from the wrong model or provider stops the game before its action is applied.

The same effort label does not mean the same reasoning compute, because each provider maps effort to its own controls. The UI calls it "provider-native effort". Artifacts record the requested effort and the returned reasoning tokens.

### OpenRouter account setup

1. Create a dedicated OpenRouter API key for this deployment. It goes into Railway as `OPENROUTER_API_KEY`. Do not reuse your local key, so you can revoke one without the other.
2. In OpenRouter's BYOK settings, add your OpenAI and Anthropic keys.
3. Leave "Always use for this provider" off. With it off, a BYOK call that fails on your key (out of credits or rate-limited) falls back to OpenRouter credits on the same provider, so the game keeps going. Because each seat is pinned to one provider, the same model serves the call either way.
4. Fund OpenRouter credits to cover Gemini, Grok, BYOK fees, and any fallback calls.
5. Leave the key's spending limit empty, per the no-cap decision.

### What BYOK changes in the app

BYOK does not change what a model sees or how the game plays. It changes who pays and how OpenRouter reports cost. The app:

- records `usage.is_byok` on every call
- computes the call's cost as described in section 13, keeping every raw usage field
- records when a seat switches between your key and OpenRouter credits, without stopping the game

Your OpenAI and Anthropic account rate limits apply to BYOK calls. Eight games make at most eight concurrent calls per provider. A five-turn smoke test at the intended worker count checks observed capacity; it cannot guarantee availability or throughput for a full campaign.

## 6. Architecture

```text
Laptop or phone browser
        |
        |  HTTPS on the Railway domain, password login
        v
Railway Pro: one service, one container, one replica
  web process         FastAPI. Serves the built React app, the game API,
                      per-game live views, and exports.
  supervisor process  Campaign queue, up to 5 worker processes, heartbeats,
                      recovery on boot, drain on SIGTERM, 1 finalizer at a time.
    worker (x5)       One game each: engine, LlmRunner, journal writer, artifacts.
  /data volume        runs/, quality_check/, jobs/, campaigns/, ledger.sqlite,
                      exports/  (50 GB, daily and weekly Railway backups)
        |
        |  model calls
        v
OpenRouter: BYOK for OpenAI and Anthropic, credits for Google and xAI

Laptop: cloud_export command copies finished games into saved_games/
```

A Railway volume attaches to one service, so the web process, supervisor, and workers share one container, and the service must run exactly one replica. The web process and the supervisor share only the SQLite ledger and the files on the volume. They never call each other directly.

Every deploy and every platform restart stops the container. The design treats that as routine:

- On SIGTERM, the supervisor stops starting games and tells each worker to stop at its next safe boundary. Railway waits `RAILWAY_DEPLOYMENT_DRAINING_SECONDS` (set to 180) before killing the container. A call that finishes inside the window is committed. A call still in flight becomes an interrupted call.
- On boot, the supervisor repairs and resumes every interrupted game (section 11).
- Automatic deploys from GitHub stay off. Deploys happen between campaigns through a script that records the code version.
- Every job records its git SHA and image digest. Recovery refuses to resume a game on different code.

## 7. Railway setup, step by step

### One-time setup

1. Create a Railway account and upgrade to the Pro plan. Hobby volumes start at 5 GB, which is too small.
2. Install the Railway CLI on the laptop and run `railway login`.
3. Create a project, then an empty service named `monopolybench`. Link the repo directory with `railway link`.
4. Add a volume to the service. Mount path `/data`, size 50 GB.
5. Set the service to exactly 1 replica.
6. Set the restart policy to restart on failure.
7. Set the health check path to `/api/health` with a 120-second timeout.
8. Generate a Railway domain under Networking (for example `monopolybench.up.railway.app`). A custom domain is optional.
9. Under the service's Backups tab, enable the Daily and Weekly schedules. Daily backups are kept 6 days and weekly backups 27 days. Add a Monthly schedule if you want 89 days of history.
10. Set the variables below.
11. Leave the service disconnected from automatic GitHub deploys. All deploys go through `scripts/deploy_railway.sh`.

### Variables

| Variable | Value | Purpose |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | dedicated key | Model calls. Secret. |
| `MB_MODE` | `cloud` | Turns on the cloud API, disables the old global `/run/*` controls. |
| `MB_DATA_DIR` | `/data/monopolybench` | Root of everything on the volume. |
| `RUNS_DIR` | `/data/monopolybench/runs` | Existing setting. `quality_check/` lands beside it at `/data/monopolybench/quality_check`. |
| `MB_DASHBOARD_PASSWORD` | long random string | Dashboard login. Secret. |
| `MB_SESSION_SECRET` | 32 or more random bytes, hex | Signs the login cookie. Secret. |
| `MB_EXPORT_TOKEN` | long random string | Read-only token for the export command. Secret. |
| `MB_MAX_ACTIVE_GAMES` | `5` | Shared worker slots, supported maximum 8. |
| `MB_DISK_RESERVE_GB` | `5` | Free space the supervisor keeps before starting calls. |
| `MB_REQUEST_DEADLINE_S` | `1200` | Total deadline per HTTP completion request. |
| `RAILWAY_DEPLOYMENT_DRAINING_SECONDS` | `180` | Time between SIGTERM and SIGKILL on deploy. |

### Build and start files

`deploy/Dockerfile` builds the frontend, installs the Python workspace, and bakes in build information:

```dockerfile
FROM node:22-bookworm-slim AS web
WORKDIR /src
COPY contracts ./contracts
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci
COPY frontend ./frontend
RUN cd frontend && npm run build

FROM python:3.12-slim-bookworm AS app
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/
WORKDIR /app
COPY python ./python
COPY contracts ./contracts
COPY campaigns ./campaigns
COPY scripts ./scripts
COPY deploy ./deploy
COPY build_info.json ./build_info.json
RUN cd python && uv sync --frozen --all-packages --no-dev
COPY --from=web /src/frontend/dist ./frontend/dist
ENV MB_MODE=cloud MB_DATA_DIR=/data/monopolybench PATH="/app/python/.venv/bin:$PATH"
CMD ["python", "-m", "monopoly_api.serve"]
```

Pin the Python version to the one the local `uv` environment uses and record it. 3.12 above is a placeholder.

`railway.json` at the repo root:

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": { "builder": "DOCKERFILE", "dockerfilePath": "deploy/Dockerfile" },
  "deploy": {
    "startCommand": "python -m monopoly_api.serve",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 120,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "numReplicas": 1
  }
}
```

Check the keys against Railway's config-as-code reference when implementing.

`monopoly_api.serve` starts the supervisor as a child process and runs uvicorn in its own process. On SIGTERM it sets the drain flag in the ledger, forwards SIGTERM to the supervisor, waits for the supervisor to report that all workers stopped or the drain window is nearly over, stops uvicorn, and exits with code 0. A zero exit keeps Railway from reporting a crashed deploy.

`scripts/deploy_railway.sh`:

1. Refuses to run if `git status --porcelain` is not empty.
2. Refuses to run if the ledger reports running games, unless `--force-interrupt` is given.
3. Writes `build_info.json` with the git SHA, branch, `python/uv.lock` and `frontend/package-lock.json` hashes, and the build time.
4. Runs the full verification (`bash scripts/verify.sh` plus microbench tests).
5. Runs `railway up` and waits for the health check.
6. Records the deploy in a local `deploy_log.jsonl`.

## 8. Data layout on the volume

```text
/data/monopolybench/
  runs/<run_id>/                 unchanged layout: events, actions, decisions, state/, prompts/, finalization files
  quality_check/<run_id>/        unchanged wire request and response text files
  jobs/<job_id>/
    job.json                     frozen configuration, hashes, execution policy version, image digest, git SHA
    execution_manifest.json      code, environment, start-of-run pricing, endpoint catalog
    journal.jsonl                crash-repair journal (section 11), compacted at finalization
    calls/<call_id>.intent.json  exact request payload and context, written before sending
    calls/<call_id>.response.json raw response, written as soon as it arrives
    recovery/                    repair records, archive plans, quarantined bytes, recovery reports
    pricing_start.json           catalog snapshot taken before the first call
  campaigns/<campaign_id>/       frozen campaign file, cell matrix, launch order, reruns, campaign reports
  ledger.sqlite                  job ledger (section 9), WAL mode
  exports/                       finished packages (section 16)
```

Nothing inside `runs/<run_id>/` or `quality_check/<run_id>/` changes shape. The existing `pricing_snapshot.json` keeps its end-of-run meaning, and the start-of-run snapshot lives in the job folder.

## 9. The job ledger (SQLite schema)

The ledger lives at `/data/monopolybench/ledger.sqlite` with WAL mode, `synchronous=FULL`, a 5-second busy timeout, and short transactions that never span an HTTP call or file upload. It indexes jobs and records operational state. The research data stays in files.

| Table | Columns | Notes |
| --- | --- | --- |
| `campaigns` | `campaign_id` PK, `config_json`, `config_sha256`, `status` (`draft`, `frozen`, `running`, `paused`, `done`), `frozen_at`, `git_sha`, `image_digest` | A frozen campaign cannot change except through an amendment row. |
| `campaign_amendments` | `campaign_id`, `amendment_index`, `reason`, `diff_json`, `affected_cells_json`, `created_at` | Adds seed blocks or records approved changes. |
| `cells` | `campaign_id`, `cell_index`, `run_id`, `seed`, `seat_order_json`, `execution_rank`, `status`, `job_id`, `rerun_count`, `not_started_reason` | One row per planned game. `execution_rank` fixes the launch order. |
| `jobs` | `job_id` PK, `kind` (`campaign`, `smoke`), `campaign_id`, `cell_index`, `run_id` UNIQUE, `rerun_of_job_id`, `config_json`, `config_sha256`, `seed`, `status`, `pause_reason`, `outcome_json`, `replay_status`, `analysis_status`, `export_status`, `repaired`, `recovered`, `git_sha`, `image_digest`, `idempotency_key`, `created_at`, `started_at`, `ended_at`, `last_progress_at`, `archived` | Status values are listed in section 10. |
| `executions` | `execution_id` PK, `job_id`, `fencing_token`, `pid`, `started_at`, `heartbeat_at`, `ended_at`, `exit_status`, `recovery_generation`, `reason` | A new row each time a worker starts on a job. |
| `commits` | `job_id`, `commit_seq`, `journal_seq`, `offsets_json`, `last_event_seq`, `action_count`, `decision_id`, `snapshot_path`, `snapshot_sha256`, `recovery_generation`, `committed_at`; PK (`job_id`, `commit_seq`) | One row per committed transition. |
| `calls` | `call_id` PK, `job_id`, `decision_id`, `resolver_stage`, `transport_attempt`, `recovery_epoch`, `state` (`intent`, `responded`, `failed`, `unknown`), `http_status`, `error_type`, `model_returned`, `provider_returned`, `generation_id`, `is_byok`, `usage_cost`, `upstream_cost`, `total_cost`, `cost_status`, `created_at`, `completed_at` | Mirrors the call files for fast queries and dashboard totals. |
| `pauses` | `job_id`, `reason`, `retries_used`, `next_retry_at`, `since`, `detail_json` | Persisted outage and credit-admission state. |
| `account_state` | `key` PK, `value_json`, `updated_at` | Holds the account-wide stop flag, the drain flag, and the latest preflight verdict. |
| `exports` | `export_id` PK, `scope` (`job`, `campaign`), `scope_id`, `revision`, `kind` (`completed`, `diagnostic`, `campaign`), `path`, `bytes`, `manifest_sha256`, `created_at` | Immutable once written. |
| `audit` | `ts`, `actor`, `action`, `detail_json` | Starts, pauses, resumes, cancels, freezes, amendments, deploys, export downloads. |

The ledger is backed up with the volume. The exporter also writes a frozen copy of each job's rows into its package.

## 10. How games run

### Job states

| Status | Meaning |
| --- | --- |
| `queued` | Waiting for a free slot. |
| `running` | A worker owns the run directory and is playing. |
| `paused` | Stopped at a safe boundary and able to continue. Reason is `account_error`, `credit_admission`, `provider_unavailable`, `storage`, `drain`, or `operator`. |
| `recovering` | A worker is repairing files and replaying committed actions after an interruption. |
| `finalizing` | The game ended, and the finalizer is building summaries, replay reports, analysis, and the package. |
| `completed` | Finalization passed and the package is ready. |
| `failed` | A technical failure that repair could not fix. Evidence is preserved, and the cell is rerun once. |
| `cancelled` | You stopped it. Reported as a cancelled cell. |

The ledger keeps separate fields for the engine outcome (winner and termination reason), replay verdicts, analysis status, export status, and whether the game was repaired or recovered.

### Supervisor loop

Every 2 seconds the supervisor:

1. Reads the drain flag and account-wide stop. While either is set, it starts nothing new.
2. Checks free disk against `MB_DISK_RESERVE_GB`.
3. Inspects every running job's heartbeat. After 90 seconds without one, it checks whether the process is alive and holds the run lock. It marks the job interrupted only when the process is gone and the lock is free.
4. Starts recovery workers for interrupted jobs, before any new game.
5. Wakes paused jobs whose retry time has come (section 12).
6. Fills free slots, up to `MB_MAX_ACTIVE_GAMES`, from queued jobs in campaign `execution_rank` order, with smoke games first.
7. Runs at most one finalizer at a time.

Starting a job runs one SQLite transaction that claims the job, increments its fencing token, and inserts an `executions` row. The supervisor then starts `python -m monopoly_arena.worker --job <job_id> --execution <execution_id>`.

### Worker lifecycle

1. Load `job.json` and refuse to run if the git SHA or image digest differs from the running code.
2. Take an exclusive `flock` on `runs/<run_id>/.writer.lock`. Exit if it is held.
3. Fresh game: write `pricing_start.json`, the execution manifest, the run config, players, and seat assignment through the journal, then start the runner.
4. Interrupted game: run the recovery procedure in section 11.
5. Heartbeat every 10 seconds into `executions.heartbeat_at`, and update `jobs.last_progress_at` on every commit.
6. On SIGTERM: finish the current engine transition or HTTP call if it completes before the drain deadline, commit, and exit with status `drained`. Otherwise exit and leave the call as interrupted.
7. On game end: commit the final transition, set the job to `finalizing`, release the lock, and exit. The supervisor queues the finalizer.

### Determinism

Workers call the same engine and `LlmRunner` code as local runs. Wall-clock time, job IDs, worker IDs, and paths never reach engine seeds or prompts. The job ID is separate from the engine run ID. Baseline policies seed themselves from the run ID (`baselines.py:398`), and decision IDs embed it (`engine.py:1324`), so recovery and repair keep the original run ID.

## 11. Durability, crash repair, and recovery

### When a repaired game counts

A game that was interrupted, repaired, or resumed counts as a valid paper game when all of these hold:

1. Every repair only completed bytes that the journal recorded and hashed before the crash.
2. Every resumed decision continued at its saved resolver stage under execution policy v1, and every interrupted call is recorded.
3. The finalizer's state replay and artifact replay both pass on the final files.
4. The game reached `GAME_ENDED` by bankruptcy.

Repaired and recovered games are flagged in the ledger and the package. The paper's methods section reports how many there were. A game that fails any check is `failed`, keeps its evidence, and its cell is rerun once.

### Write rules

1. Every append to a canonical JSONL file is followed by fsync. When a file or directory is first created, its parent directory is fsynced too.
2. JSON files are written to a temp file, fsynced, renamed into place, and the parent directory is fsynced.
3. Canonical turn snapshots keep the existing first-write rule: the first snapshot for a turn is never overwritten, and differing later states go to variant files.
4. A write or fsync failure stops the worker. The `OSError` swallow at `decision_resolver.py:859` is removed.

### The journal

Every change to canonical files goes through `jobs/<job_id>/journal.jsonl`. A transition is one engine step and its artifacts:

- an engine advance: the events from `advance_until_decision`, plus any snapshot that advance triggers
- a decision start: the `decision_started` line in `decisions.jsonl`
- an applied action: the `actions.jsonl` line, the `decision_resolved` line, the action's events, and any snapshot they trigger
- per-call wire and prompt files, written when the resolver builds an attempt
- the game end: the final events and snapshot

For each transition the writer:

1. Computes every byte it will write: each JSONL line, each snapshot, each prompt and quality file.
2. Appends one journal record with `journal_seq`, the transition kind, the decision ID, and for each target its path, expected starting offset, byte length, SHA-256, and the bytes themselves. Then it fsyncs the journal.
3. Appends or writes each target file and fsyncs it.
4. Inserts the `commits` row in SQLite with the new offsets.
5. Publishes the batch to live viewers.

The existing runner already gets each step's events as a list (`advance_until_decision` and `apply_action` return lists), and `get_snapshot()` returns the post-step state, so committing a step as one unit keeps snapshot contents byte-identical to today's. A test compares a scripted game's run directory under the old writer and the journaled writer, excluding wall-clock timing fields, and requires identical bytes.

At finalization the journal is compacted to `journal_index.jsonl`, which keeps hashes and offsets but drops the duplicated bytes.

### Recovery procedure

When a worker starts on an interrupted job:

1. Confirm the previous writer is gone and take the lock. Increment the recovery generation.
2. Read the last `commits` row and the journal records after it.
3. Repair the files. For the journal record after the last commit, check each target file:
   - Length equals the expected offset: write the journaled bytes.
   - Length is past the offset and the existing bytes match the start of the journaled bytes: write the rest.
   - Length equals offset plus length and the hash matches: nothing to do.
   - Anything else is a contradiction: mark the job `failed` and keep the files untouched.
   Then insert the missing `commits` row and write a repair record to `recovery/repairs.jsonl` listing each file, the byte range completed, and the hashes.
4. Handle any partial journal record (the crash came while the journal itself was being written). Its transition never touched canonical files, because those writes happen only after the journal fsync. Move the partial bytes to `recovery/quarantine/` with their hash. The engine replay in the next step regenerates that transition.
5. Check that no canonical file has bytes past the last committed or repaired offset. Unjournaled bytes are a contradiction and fail the job.
6. Replay every committed action through a fresh engine with the same seed, players, settings, and run ID. Require the replayed canonical events to equal the recorded events exactly. Rebuild prompt memory from the events.
7. Find the pending decision and its call records, then continue the resolver from its saved stage:
   - The stage's response is saved: reuse it with no new call. Validate it against the legal actions. If valid, apply it. If the initial attempt is invalid, move on to the corrective request, exactly as an uninterrupted run would. If the corrective attempt is invalid, apply the deterministic fallback.
   - Only an intent is saved: the request's outcome is unknown. Re-send the exact saved payload at the same stage under the interruption policy below.
   - No intent exists: nothing was sent. Send the stage's request normally.
8. Before writing any prompt or quality file for the resumed decision, compare it with an existing file of the same name. Identical bytes are kept. Different bytes are moved to `prompts/interrupted/r<generation>/` or `quality_check/<run_id>/interrupted/r<generation>/` with an archive plan written first. Matching covers every attempt variant, including the compact hashed names from `run_files.py:376`.
9. Set the job to `running` and continue.

The interruption policy allows at most 1 repeat of an unknown request per decision and 3 per game. Each repeat gets a new call ID and an `after_interruption` record outside the model payload. Beyond those limits, the job fails and the cell is rerun.

### Finalization

Finalization is its own idempotent job that runs from committed files:

1. Replay the full game through a new terminal replay path. `_restore_interrupted_run` cannot be reused, because it rejects a replay with no pending decision (`llm_runner.py:189`).
2. Write `summary.json`, usage files, `pricing_snapshot.json`, experiment, scorecard, replay, trace, and failure-taxonomy files, plus the artifact manifest, using today's writers. Writes use the atomic rules above.
3. Freeze the first end-of-run catalog observation and reuse it on retries, so a retry produces the same files.
4. Build the standard analysis in staging (section 16).
5. Check that every required artifact exists and cross-file references resolve.
6. Compact the journal, build the package, and set the job `completed`. If a check fails, build a diagnostic package and set the job `failed`.

### What happens at each interruption point

| Interruption point | Behavior |
| --- | --- |
| Waiting on a model call, which covers most of a game's wall time | Repair nothing, replay, re-send the saved request at the same stage. |
| After a response arrived and was saved, before its action was committed | Reuse the saved response. No new call. |
| While writing a committed transition's files | Finish the files from the journal, then continue. |
| While writing the journal record | Quarantine the partial record and regenerate the transition by replay. |
| During finalization | Re-run the finalizer. |
| Deploy or platform restart | Workers stop at a safe boundary within 180 seconds. Anything still in flight is handled by the rows above. |
| Volume loss | Restore the latest Railway backup. Games running at backup time are rerun. Finished games already exported to the laptop are safe. |

## 12. Provider errors, outages, and deadlines

### Deadlines

- Each physical completion request has a 20-minute total deadline (`MB_REQUEST_DEADLINE_S`), measured on a monotonic clock. The existing per-read timeouts stay. A deadline hit is recorded as `total_timeout` and follows the existing transport-retry path without resetting its counter.
- Generation-metadata lookups, catalog GETs, and credit checks each get a 60-second total deadline. The completion response is saved before any metadata lookup, and a metadata timeout records the metadata as unavailable without sending another completion request.
- The dashboard marks a game "slow" when its current request is older than 5 minutes or it has made no progress for 5 minutes. This is display only and never stops a worker.

### Account and credit errors

- A missing key, HTTP 401, or HTTP 403 pauses the game as `account_error` before any fallback can happen. It also sets the account-wide stop, so every worker pauses before its next request.
- For HTTP 402, the worker saves the body and headers and reads `error.metadata.limit_source` and `reason`. Exhausted OpenRouter credits become `account_error` with the account-wide stop. A temporary in-flight credit rejection becomes `credit_admission` and follows the outage retry schedule.
- After you fix the account, "Retry eligible games" clears the stop and resumes eligible games at their saved stage. Manual and campaign holds remain paused; readiness and budget checks still apply.

### Outage policy v1

- When a resolver stage fails on transport after its existing retries (429, 5xx, timeouts, dropped connections), no fallback is applied. The decision stays pending and the game pauses as `provider_unavailable`.
- Every 5 minutes, the worker re-sends the same saved request at the same resolver stage, up to 12 times. Each retry is a real, recorded decision attempt, and a successful one is used.
- After 12 failed retries, the game stays paused until you press Resume, which restarts the schedule.
- Account stops take priority over outage handling.
- Pause state and retry counts live in the `pauses` table and survive restarts.
- Invalid model output keeps today's rule: one corrective retry, then a deterministic fallback.

The deadlines, interruption limits, rerun rule, outage policy, and credit-admission handling together form execution policy v1. Each job records the version. None of it changes prompt text, tools, memory, or retry wording.

## 13. Cost accounting

There is no spending cap, but every dollar is recorded.

For each call:

| Billing | Provider cost | OpenRouter charge | Total |
| --- | --- | --- | --- |
| BYOK (`usage.is_byok` true) | `usage.cost_details.upstream_inference_cost`, paid by your OpenAI or Anthropic account | `usage.cost`, the BYOK fee from OpenRouter credits, often 0 | both added |
| Credits | included in `usage.cost` | `usage.cost` | `usage.cost` |

Rules:

- Every raw usage field is kept in the call record and in `decisions.jsonl` as today.
- A missing cost is recorded as `cost_status: missing` with an estimate from tokens and the start-of-run catalog price. It is never recorded as 0.
- A call lost in a crash is recorded as `cost_status: unknown` with an estimate from the saved payload's input tokens.
- Calls lost in crashes appear in a new execution cost report. Existing `usage.json` fields keep their meaning, and a new `usage.py` option computes BYOK-aware totals for the paper's cost tables.
- The dashboard shows total spend, spend per game, and the split between your provider accounts and OpenRouter credits.

## 14. Removing the turn cap

Full games end only by bankruptcy. The turn cap never reaches prompts or snapshots, so removing it changes no model input. It does change the engine, two schemas, and replay, so it is handled as a protocol change:

- `Engine(max_turns: int | None = 30)`. When `max_turns` is `None`, `_should_end_game` skips the turn check (`engine.py:3075`).
- `replay.py` and `_restore_interrupted_run` compute `max_auto_steps` from `max_turns`. With `None` they use a fixed constant, `UNCAPPED_MAX_AUTO_STEPS = 10_000`, the same in play and in replay.
- `run_config.json` records `"max_turns": null`.
- `contracts/schemas/research_registry.schema.json` and `benchmark_artifact.schema.json` allow `null` for `max_turns`, with a schema version bump. `contracts/ts/research.ts` becomes `max_turns: number | null`. The examples gain an uncapped case.
- Campaign run IDs hash `max_turns` as `null`.
- Smoke games keep a cap of 5 to 10 turns.

An uncapped game could in principle run very long. Every saved game ended between turns 115 and 273. The dashboard marks a game "long" past turn 300 and shows its turn count and spend. You can cancel it at any time, and a cancelled game is reported as a cancelled cell. Nothing stops a game automatically.

## 15. Campaigns, smoke games, and research integrity

### Campaign file

Full games run only as cells of a frozen campaign. The campaign file extends today's `long_horizon_campaign_config_v1` as `long_horizon_campaign_config_v2`:

```json
{
  "schema_version": "v2",
  "campaign_config_version": "long_horizon_campaign_config_v2",
  "campaign_id": "monopoly-long-v2-frontier-2026q4",
  "benchmark_id": "monopoly-long-v1",
  "seed_cohort": "frontier_2026q4_v1",
  "model_roster": "frontier_2026q4_medium_4lab",
  "repetitions_per_seed": 1,
  "seat_permutation": "cyclic_4",
  "max_turns": null,
  "max_trade_exchanges": 20,
  "max_auction_actions": 200,
  "concurrency": 5,
  "execution_order_seed": 0,
  "execution_policy_version": "execution_policy_v1",
  "rerun_policy": { "max_reruns_per_cell": 1, "same_seed_and_seats": true },
  "preflight": { "version": "openrouter_campaign_preflight_v3", "max_age_hours": 6 },
  "billing": { "openai": "byok_preferred", "anthropic": "byok_preferred", "google": "credits", "xai": "credits", "enforcement": "observe" },
  "prompt_pipeline": { "status": "unchanged" }
}
```

The `execution_order_seed` value is drawn once when the campaign is created. The field list is a starting point for the implementation.

- The roster `frontier_2026q4_medium_4lab` goes into `contracts/research/monopoly_long_v1_model_rosters.json`. It has four new actors with their model IDs, provider pins, `reasoning: {"effort": "medium"}`, and billing modes.
- The seed cohort goes into `contracts/research/monopoly_long_v1_seed_registry.json`, drawn with `scripts/research/draw_seed_cohort.py`.
- `cyclic_4` plays each seed in four seat orders, so every model plays every seat on every seed.
- Billing enforcement is `observe`. The billing guard records billing mode per call but stops a game only for a wrong model or provider. The old `byok_required` mode and its E1 tests stay unchanged.
- The game count is open. A campaign starts with some number of seed blocks, and an amendment can add more blocks later without touching existing cells.

### Freezing

Freezing records the campaign in the ledger with the git SHA, image digest, roster and seed-registry hashes, the cell matrix, the launch order, and a passing preflight. After freezing, any change is an amendment that names the cells it affects. Code changes during a campaign are amendments too, so deploys happen between campaigns.

### Preflight

`scripts/research/capture_openrouter_preflight_v3.py` sends one production-shaped request to each of the four routes, with `tool_choice="auto"`, the campaign effort, and a real decision prompt from a fixture. It checks for a legal tool call, the expected model and provider, and the billing mode, and it records cost. It runs before freezing, and the supervisor reruns it automatically after every boot before starting new cells. The old E1 preflight and its gates stay unchanged.

### Smoke games

You choose the models, seat order, effort, and a 5 to 10 turn cap. Smoke jobs run through the same code path as campaign games and carry `kind: smoke` in `job.json`, the ledger, the dashboard, and any export. They never enter campaign exports or paper tables.

### Research integrity rules

1. Each job records an execution manifest before its first paid request. It holds the git SHA (deploys refuse a dirty tree), image digest, lockfile hashes, Python version, prompt, tool, and memory policy hashes, start-of-run pricing, the endpoint catalog, and execution policy v1.
2. Failed, cancelled, and rerun games stay in the ledger and in campaign exports. A rerun never hides its predecessor.
3. Execution policy v1 handles transport failures by pausing instead of playing fallback moves, which differs from the E0 games. Analysis keeps the new campaign and E0 apart.
4. Prompt-preservation tests prove that model-facing payloads are byte-identical to before for scripted decisions, apart from the new model, route, and effort settings. Cloud metadata never enters a prompt.
5. `research_direction.md` and `docs/two_paper_plan.md` get updated once you accept the campaign file. Both have uncommitted edits of yours that this plan does not touch.

## 16. Artifacts, packages, and export to the laptop

### Packages

Every finished job produces a package.

- A completed package passes the required-artifact and cross-reference checks.
- A diagnostic package covers failed, cancelled, and rerun games. It holds every raw file that exists, the repair and quarantine evidence, the replay findings, and the final status. It never fabricates a summary.

Layout:

```text
<campaign_id>/<cell_index>-<run_id>/
  run/                       copy of runs/<run_id>/
  quality_check/             copy of quality_check/<run_id>/
  analysis/                  tables, coverage, plots, reports, expanded metrics, manifest
  cloud/                     job.json, execution_manifest.json, journal_index.jsonl, calls/, recovery/, frozen ledger rows
  saved_game_manifest.json   existing format
  storage_manifest.json      storage_manifest_v1
```

Smoke packages go under `smoke/<run_id>/`.

`storage_manifest_v1` lists every regular file except itself, with relative path, byte count, SHA-256, and role. It rejects symlinks and unsafe or duplicate paths. The tree hash sorts relative POSIX paths by Unicode code point and, for each file, hashes the UTF-8 path, a NUL byte, the lowercase hex SHA-256, and a newline. This adopts R191's encoding as an explicit contract. Older saved games keep their own formats.

The finalizer builds the standard analysis in staging with functions refactored out of `scripts/standardize_saved_games.py`. That script archives and cleans up, so it never runs against the live data root. Its `ROOT_PRESERVE_NAMES` gains `cloud` and `storage_manifest.json`, so a later local run does not move cloud evidence into `run/`. The package is a ZIP64 file under `exports/`.

A campaign export adds the frozen campaign file, amendments, preflight evidence, the cell matrix, the actual launch order, unstarted cells with reasons, rerun links, and campaign cost and outcome reports.

### Export command

```bash
cd python
uv run python -m monopoly_telemetry.cloud_export \
  --url https://monopolybench.up.railway.app \
  --token "$MB_EXPORT_TOKEN" \
  --dest ../saved_games \
  [--campaign monopoly-long-v2-frontier-2026q4] [--include-smoke]
```

It lists finished packages, downloads each to a temp file with resumable HTTP range requests, verifies every file hash and the tree hash, unpacks into place, skips packages already verified, and never deletes local files. It uses the Python standard library for HTTP, so the telemetry package gains no dependency. Run it after each batch of finished games so the laptop holds a second copy.

Each dashboard card also has an Export button that streams the same ZIP.

### After export

The local workflow runs unchanged: `scripts/analyze_saved_game.py`, `scripts/analyze_negotiation_tactics.py`, replay verification, and the qualitative review. Local analysis after export is a new derived version and never edits files covered by the downloaded manifest.

## 17. API

All routes sit under `/api` and require the login cookie, except `/api/health` and `/api/auth/login`. Export routes also accept the export token.

| Method and path | Purpose |
| --- | --- |
| `POST /api/auth/login`, `POST /api/auth/logout` | Password login and logout. |
| `GET /api/health` | Liveness for Railway. Returns ok when the web process is up. |
| `GET /api/status` | Account-wide stop, drain flag, free disk, active workers, total spend, latest preflight. |
| `GET /api/campaigns`, `GET /api/campaigns/{id}` | Campaign files in the image and frozen campaigns, with cells, statuses, and costs. |
| `POST /api/campaigns/{id}/freeze` | Freeze a campaign after a passing preflight. |
| `POST /api/campaigns/{id}/amend` | Record an amendment, such as adding a seed block. |
| `POST /api/campaigns/{id}/run`, `POST /api/campaigns/{id}/pause` | Start filling slots in campaign order, or stop starting new cells. |
| `POST /api/smoke/prepare`, `POST /api/smoke` | Prepare a smoke batch with exact seeds and seat orders, then launch it with an idempotency key. |
| `GET /api/jobs` | Job summaries with filters for status, kind, campaign, and search, with cursor pagination. |
| `GET /api/jobs/{job_id}` | Full job detail, including outcome, repairs, pauses, and costs. |
| `POST /api/jobs/{job_id}/pause`, `/resume`, `/cancel`, `/archive` | Operator controls. The server refuses actions that are not allowed in the current state. |
| `POST /api/resume-all` | Clear the account-wide stop and retry eligible paused games; preserve manual/campaign holds and report skipped reasons. |
| `GET /api/jobs/{job_id}/decisions`, `/artifacts`, `/snapshots` | Run-scoped readers, reusing today's artifact readers by run ID. |
| `WS /api/jobs/{job_id}/ws` | Live view (section 18). |
| `GET /api/jobs/{job_id}/export` | Stream the job's package ZIP. |
| `GET /api/exports`, `GET /api/exports/{export_id}/download` | Package list and download with HTTP range support, for the export command. |
| `POST /api/preflight/run`, `GET /api/preflight/latest` | Run and read the preflight. |

When `MB_MODE=cloud`, the old global routes (`/run/start`, `/run/stop`, `/run/pause`, `/run/resume`, `/run/recover`, `/ws`) are not registered. Local mode keeps them for single-run development.

## 18. Dashboard and frontend

### Style

The screenshots set the layout and interaction. MonopolyBench's existing design sets the style: Inter and JetBrains Mono, the `#f4f3f0` background, white panels with 2px black borders, small radii, offset shadows, and the existing accent colors from `frontend/src/index.css` and `components/ui/NeoPrimitive.tsx`. The reference's serif type and maroon buttons are not used. The UI stays render-only: the server decides legality, status, outcome, and which actions are allowed.

### Routes

| Route | Page |
| --- | --- |
| `/login` | Password form. |
| `/` | All games dashboard. |
| `/campaigns/<id>` | Campaign view: cell grid in launch order, progress, costs, reruns, Run and Pause buttons. |
| `/games/<job_id>` | Game page with Live, Decisions, Artifacts, Replay, and Analysis tabs. |
| `/runs`, `/research`, `/micro`, `/runs/<id>/replay` | Existing pages, unchanged. |

### All games page

A sidebar holds the workspace name, All games, Active, Completed, Archived, Campaigns, a Run button, and recent games, plus links to the existing pages. Its footer shows total spend, free disk, and active workers. When the account-wide stop is set, a banner explains why and offers "Resume all".

The main area has the title "All games" and a summary line, for example "5 running, 14 queued, 5 completed, campaign 5 of 24, $63.10 spent". Search covers run ID, seed, model, and campaign. Cards sit in 3 columns on wide screens, 2 on tablets, and 1 on phones. Each card shows:

- a board thumbnail drawn from the snapshot in the latest commit
- cell or game name, run ID, status with a colored dot, and a Campaign or Smoke badge
- four seat chips in seat order, effort, and seed
- turn, elapsed time, time since last progress, and cost so far, with "slow" and "long" markers
- for finished games, the winner and termination reason; for paused and failed games, the reason and a link to any rerun
- a Repaired or Recovered marker when it applies
- the replay verdict and export status, shown separately
- Watch, Export when ready, and a menu with Archive, Pause, Cancel, and Resume when allowed

The page polls job summaries every 5 seconds and never opens more than one live stream.

### Run modal, 3 steps

| Step | Contents |
| --- | --- |
| 1. What to run | The next cells of a frozen campaign, or a smoke game. |
| 2. Settings | Campaign: read-only roster, effort, and seeds, plus how many slots to fill, up to 5. Smoke: four models and seat order, effort as three option cards (Low, Medium, High) with Medium selected, a 5 to 10 turn cap, and how many games. A cost estimate per game from the server. |
| 3. Review and launch | Each game's seed and seat order, routes, effort, code version, and the latest preflight verdict. Launch opens the campaign or game view. |

The modal never shows system prompts, tools, retry rules, or raw provider JSON.

### Game page and live view

The game page reuses `Board`, `PlayerStackPanel`, `EventFeed`, `ChatFeed`, `Inspector`, `AuctionPanel`, `TradeInspectorPanel`, `LlmIoPanel`, and `ThoughtsPanel`. Long lists are paginated, and prompt details load on demand.

The API runs one tailer per viewed game. The tailer reads committed offsets from the ledger, reads `events.jsonl` up to that offset, and sends each event batch with its committed snapshot. The live envelope keeps the existing `HELLO`, `SNAPSHOT`, and `EVENT` messages and adds `job_id`, `run_id`, `recovery_generation`, `commit_seq`, and the snapshot's event sequence, with a version bump. A reconnecting client sends its last commit sequence and receives a backfill. A recovery generation change triggers a reset to a committed snapshot. Each viewer has a bounded queue and a send timeout, and a viewer that falls behind is disconnected and can reconnect.

### Frontend changes

| File | Change |
| --- | --- |
| `src/App.tsx` | Add `/login`, `/`, `/campaigns/<id>`, and `/games/<job_id>` routes. Redirect to `/login` on a 401. |
| `src/net/ws.ts` | Same-origin `/api` base by default, keeping `VITE_API_BASE` for development. Per-job WebSocket URLs with reconnect and backfill by commit sequence. |
| `src/net/jobs.ts` (new) | Typed client for jobs, campaigns, smoke, status, exports, and auth. |
| `src/state/store.ts` | Key snapshot and events by job ID. Remove the global run status in cloud mode. Fix "stopped means complete" by reading job status from the server. |
| `src/pages/GamesPage.tsx` (new) | All games dashboard. |
| `src/pages/CampaignPage.tsx` (new) | Campaign view. |
| `src/pages/LoginPage.tsx` (new) | Password form. |
| `src/pages/LiveBenchPage.tsx` | Becomes the Live tab of the game page, taking a job ID and dropping global polling. |
| `src/pages/RunsPage.tsx` | Read replay verdicts from report contents instead of file existence. |
| `src/components/games/GameCard.tsx`, `MiniBoard.tsx`, `RunModal.tsx` (new) | Card, thumbnail, and the 3-step modal. |
| `src/components/panels/GameControls.tsx` | Hidden in cloud mode. Job controls live on the game page. |

## 19. Access control

The site has one password, stored as `MB_DASHBOARD_PASSWORD`. The login route compares it in constant time and sets a signed, HTTP-only, `Secure`, `SameSite=Lax` cookie that lasts 30 days. Every page, API route, live view, and export requires the cookie. Login attempts are rate-limited. The export command uses `MB_EXPORT_TOKEN` in an `Authorization: Bearer` header, which allows read-only export routes only.

The OpenRouter key lives only in Railway variables and never reaches the browser, logs, artifacts, or exports. The API checks artifact paths against the stored inventory to block path traversal. Nothing in the create flow accepts file paths, commands, or credentials.

This is the minimum. The Railway URL is public, the OpenRouter key has no spending cap, and the artifacts contain private model reasoning. Without a password, anyone who finds the URL could start games on your accounts.

## 20. Code changes, file by file

Paths under `python/` unless noted. "New" marks a new file.

### Engine (`packages/engine/src/monopoly_engine/`)

| File | Change |
| --- | --- |
| `engine.py` | `max_turns: int | None`. `_should_end_game` skips the turn check when `None`. No other rule changes. |
| `replay.py` | `max_turns: int | None`, using `UNCAPPED_MAX_AUTO_STEPS` when `None`. |
| tests | Uncapped games end only by bankruptcy. Capped behavior is unchanged. Replay matches for uncapped games. |

### Arena (`packages/arena/src/monopoly_arena/`)

| File | Change |
| --- | --- |
| `player_config.py` | Add provider pins for the four new models. Reset a seat's provider pin when its model changes. Effort stays low, medium, or high. |
| `openrouter_client.py` | Before and after hooks on every physical POST, so each one gets a call record. Total deadline per completion request. Distinct error types for 401, 403, 402 (with its subtype read from the body), missing key, and `total_timeout`. 60-second deadline on metadata GETs. Request payloads stay byte-identical. |
| `decision_resolver.py` | Restructure the resolver as explicit stages (initial request, initial response, corrective request, corrective response, outcome), with state saved in call records and resumable from any stage. Account errors raise an operational pause instead of returning a fallback. Transport failures follow outage policy v1. Write failures raise. The response is saved before the metadata lookup. |
| `llm_runner.py` | Route every canonical write through the journal writer, one transition per engine step. Accept a resume plan from the recovery procedure. Move finalization out of `run()` into a callable that the finalizer job uses. Add the terminal replay path. Accept `max_turns=None`. Write `pricing_start.json`. |
| `long_campaign.py`, `research_registry.py` | Campaign config v2 with `max_turns: null`, `cyclic_4` seats, the rerun policy, `execution_policy_version`, and billing enforcement `observe`. Cell matrix and launch order reused for the supervisor. E1 configs and tests unchanged. |
| `route_validator.py` (new) | Checks the returned model and provider on every response, records billing mode, and replaces the per-campaign billing guard for cloud jobs. |
| `execution_policy.py` (new) | Execution policy v1 constants and rules: deadline, interruption limits, rerun rule, outage schedule, credit-admission handling. |
| `job_store.py` (new) | SQLite schema, migrations, and typed access for section 9. |
| `supervisor.py` (new) | The loop in section 10, drain handling, recovery dispatch, and the single finalizer. |
| `worker.py` (new) | The worker lifecycle in section 10 and the recovery procedure in section 11. |
| `journal.py` (new) | Journal writer, repair logic, and compaction. |
| `finalizer.py` (new) | Idempotent finalization and package building. |

### Telemetry (`packages/telemetry/src/monopoly_telemetry/`)

| File | Change |
| --- | --- |
| `writer_jsonl.py` | fsync after append and for new directory entries. A strict reader that fails on malformed lines and reports trailing bytes. |
| `run_files.py` | Atomic JSON writes. Hooks so the journal writer controls every canonical write. Prompt and quality writes compare against existing files and archive differing ones. |
| `usage.py` | BYOK-aware cost: provider cost from `upstream_inference_cost`, OpenRouter charge from `usage.cost`, missing and unknown cost states. Existing fields keep their meaning. |
| `execution_cost.py` (new) | Execution cost report that includes calls lost in crashes. |
| `inventory.py` (new) | `storage_manifest_v1` and the tree hash. |
| `export.py` (new) | Completed, diagnostic, and campaign package builders. |
| `cloud_export.py` (new) | The laptop export command. |

### API (`apps/api/src/monopoly_api/`)

| File | Change |
| --- | --- |
| `main.py` | Register cloud routes when `MB_MODE=cloud` and legacy routes otherwise. Serve `frontend/dist`. Add the auth middleware. |
| `serve.py` (new) | Container entrypoint: starts the supervisor and uvicorn and handles SIGTERM. |
| `auth.py` (new) | Password login, signed cookie, export token, rate limiting. |
| `jobs_api.py` (new) | Job, campaign, smoke, status, preflight, and export routes from section 17. |
| `live.py` (new) | Per-job tailer and WebSocket handler. |
| `run_manager.py` | Split the artifact readers into a reusable module. The execution half stays for local mode only. Replace `_read_jsonl` with the strict reader. |
| `settings.py` | Read the variables in section 7. |
| `config/players.json` | New models for local development. |

### Contracts (`contracts/`)

| File | Change |
| --- | --- |
| `schemas/research_registry.schema.json` | Campaign config v2. `max_turns` nullable. |
| `schemas/benchmark_artifact.schema.json` | `max_turns` nullable. |
| `schemas/cloud.schema.json` (new) | Job summary and detail, live envelope v2, call record, commit record, journal record, repair record, execution manifest, storage manifest v1. |
| `ts/research.ts`, `ts/cloud.ts` (new) | Matching TypeScript types. |
| `examples/` | Examples for every new or changed shape, checked by `validate-contracts.mjs`. |
| `research/monopoly_long_v1_model_rosters.json`, `research/monopoly_long_v1_seed_registry.json` | New roster and seed cohort. |

### Scripts, deploy, and docs

| File | Change |
| --- | --- |
| `scripts/standardize_saved_games.py` | Analysis functions callable from the finalizer. `ROOT_PRESERVE_NAMES` gains `cloud` and `storage_manifest.json`. |
| `scripts/research/capture_openrouter_preflight_v3.py` (new) | Production-shaped preflight. |
| `scripts/mock_openrouter_server.py` (new) | Zero-cost test server (section 21). |
| `scripts/deploy_railway.sh` (new) | Deploy script from section 7. |
| `deploy/Dockerfile`, `railway.json` (new) | Build and service config. |
| `deploy/README.md` (new) | The runbook in section 23. |
| `.env.example` | Variable names with explanations, no values. |
| `campaigns/monopoly-long-v2-frontier-2026q4.json` (new) | The campaign file, frozen before the first full game. |
| `docs/artifact_reference.md` | Document `jobs/`, the journal, call records, repair records, `cloud/`, and `storage_manifest_v1`. |
| `docs/research_protocol/` | Execution policy v1 and the new campaign's protocol. |

## 21. Tests

### Zero-cost mock server

`scripts/mock_openrouter_server.py` speaks the OpenRouter completion, catalog, endpoint, generation, and credit APIs. Scenarios are keyed by game, decision, resolver stage, and transport attempt, so five interleaved games stay deterministic. It can return valid, invalid, and malformed tool calls, 401, 402 of both kinds, 403, 429, and 5xx responses, slow and trickled bodies, dropped connections, missing cost, BYOK-shaped usage, and wrong models or providers. Payload sizes come from saved runs. In test mode, every client gets the mock URL and a dummy key, real keys are cleared, other outbound hosts are blocked, and the test asserts that no request reached a real provider.

### Test list

- Engine: uncapped games end only by bankruptcy, capped games are unchanged, and uncapped replay matches.
- Journal writer: a scripted game's run directory is byte-identical under the old and new writers, excluding wall-clock fields.
- Scheduling: five running with the rest queued in campaign order, idempotent launches, duplicate claims, a stale heartbeat with a live writer, and a lock that blocks a second writer.
- Determinism: the same run ID, seed, players, settings, and scripted responses give identical canonical events, actions, and payloads alone, alongside four other games, and after recovery.
- Prompt preservation: system text, user payload, tools, tool choice, memory, message requirements, corrective retry text, and invalid-output fallback are unchanged.
- Repair at every boundary: kills after each journal fsync, after each canonical file write, before and after each commit row, during prompt and quality writes, and during the journal write itself. Each case repairs and passes replay, or fails visibly when the files contradict the journal.
- Response reuse: kills after an initial response is saved, after a corrective response is saved, and between validation and commit. Each resumes with no new call and the same outcome as an uninterrupted run.
- Unknown requests: kills during initial and corrective requests resume at the same stage with the same payload, and the repeat limits end in a failure.
- Drain: SIGTERM inside and outside the 180-second window, and a full redeploy mid-batch on Railway.
- Corruption: truncated lines, malformed lines, edited records, bytes past the commit with no journal record, missing prompt files, and wrong hashes fail with evidence kept.
- Errors and outages: 401, 403, missing keys, and exhausted credits pause without fallback and stop all workers. A temporary 402 retries on schedule. Outage policy v1 through failures, a restart while paused, success on retry, and 12 failed retries.
- Cost: BYOK calls take `upstream_inference_cost`, credit calls take `usage.cost`, a seat switching billing mid-game is recorded, and missing and unknown costs are never 0.
- Validator and preflight: wrong model, wrong provider, and a mismatch on a corrective attempt.
- Live view and access: the snapshot paired with a multi-event batch, a reconnect with backfill, a recovery generation change, a viewer that never reads, and requests without the password or token refused.
- Export: completed, diagnostic, and campaign package round trips with matching hashes on macOS and Windows, and the standardizer and both analysis scripts on an exported copy.
- Full repository check: `bash scripts/verify.sh` (or `pwsh -File scripts/verify.ps1` on Windows) plus `uv run pytest` in `python/packages/microbench`, which `verify.sh` does not run.

## 22. Rollout

1. Build everything locally and pass the full verification.
2. Run five full-length uncapped games at once locally against the mock server, with fault injection. Measure memory per worker, total memory, CPU, disk use, journal size, finalization time, and package size.
3. Set up Railway (section 7) and deploy with `scripts/deploy_railway.sh`.
4. Repeat the five-game mock soak on Railway with the laptop closed. Trigger a redeploy mid-batch and confirm every game repairs or resumes and passes replay. Restore a backup into a scratch volume once to prove backups work. Set the service's memory limit from the measured numbers.
5. Run the v3 preflight against the four real routes at medium effort.
6. Run real-model smoke games of 5 to 10 turns: five at once, one interrupted by a redeploy, and one exported to the laptop with hash checks. Confirm BYOK costs appear for the OpenAI and Anthropic seats and credit costs for Gemini and Grok.
7. Create the campaign file with its first seed blocks, draw seeds, freeze it, and record the code version.
8. Press Run on the campaign. Five games start, and each finished game starts the next cell. Export after each batch of finished games.

## 23. Operations runbook

| Situation | What to do |
| --- | --- |
| Start a campaign | Dashboard, Campaigns, pick the frozen campaign, Run, fill 5 slots. |
| Add more games | Draw a new seed block, record an amendment, and the new cells join the queue. |
| Check progress | All games page or the campaign view. "Slow" means a call has run past 5 minutes. "Long" means past turn 300. |
| Account error banner | Fix the key or top up credits, then press "Resume all". |
| Game paused for an outage after 12 retries | Check OpenRouter status, then press Resume on the game. |
| Game failed | Open the game to read the failure. Its rerun is already queued. Both stay in the export. |
| Stop a game | Cancel from the card menu. It is reported as a cancelled cell. |
| Deploy new code | Only between campaigns. Pause the campaign, wait for running games to finish, then run `scripts/deploy_railway.sh`. |
| Railway restarted the service | Nothing. Games repair or resume on boot. |
| Volume problem | Restore the latest backup from the Backups tab, then redeploy. Games running at backup time are rerun. |
| Copy results to the laptop | Run the export command in section 16. |
| Rotate the OpenRouter key | Pause the campaign, update `OPENROUTER_API_KEY`, redeploy, resume. |

## 24. Risks

| Risk | What we do about it |
| --- | --- |
| A game runs very long without a turn cap | The dashboard marks it past turn 300 with its spend. You decide whether to cancel. |
| Games take longer than 4 hours | They keep running. 3 to 4 hours is a target, not a guarantee. |
| Uncapped spending | Every cost is recorded and shown. Account errors stop all workers instead of producing fallback moves. Retry limits stop runaway loops. |
| Your OpenAI or Anthropic rate limits are low | Smoke tests run five games at once first. BYOK calls fall back to OpenRouter credits on the same provider, and the switch is recorded. |
| A provider outage overnight | Outage policy v1 pauses and retries for an hour, then waits for you. |
| A crash in a file-write window | The journal repairs it. Contradictory files fail visibly and the cell is rerun. |
| Railway restarts or deploys mid-campaign | Auto-deploy is off. The 180-second drain and repair on boot handle restarts. |
| Volume loss | Railway backups plus regular exports to the laptop. Games in progress are rerun. |
| Models or routes change during the campaign | Every call records the returned identities, and the preflight reruns after every boot. |
| A dirty tree gets deployed | The deploy script refuses uncommitted changes. Your uncommitted research files go into a reviewed commit first. |
| Effort means different compute per lab | Reasoning tokens are recorded per call, and effort is reported as provider-native. |

## 25. Effort estimate

About 9 to 12 focused engineering days for one engineer working with coding agents:

| Part | Days |
| --- | ---: |
| Ledger, supervisor, worker, drain, recovery dispatch | 2 |
| Journal, repair, response reuse, resolver stages | 3 to 4 |
| Requests, deadlines, errors, outage policy, cost accounting | 1 |
| Campaign v2, roster, seeds, preflight v3, uncapped engine | 1 |
| Finalizer, packages, manifests, export command | 1 |
| API, auth, live view | 1 |
| Frontend dashboard, campaign view, game page, modal | 1 to 2 |
| Deploy files, Railway setup, soak and fault tests | 1 |

The riskiest part is the journal and resolver-stage recovery, because it must produce byte-identical artifacts and identical prompts across every crash point. Smoke tests and the campaign itself add elapsed time but little engineering time.

## 26. Review history

- Round 1. Claude and Astra planned independently. Both found the single-run limit, the recovery gaps, and the GPT price mix-up.
- Round 2. They settled the overall design: workers per game, a SQLite ledger, per-call records, writer locks, strict failure, and bounded repeats of interrupted calls that keep the resolver stage.
- Round 3. Astra's adversarial review raised 38 issues. The main ones: never roll back an applied action, a production-shaped preflight, BYOK cost reporting, the export hash contract, the standardizer conflict, and corrected latency and storage figures.
- Revision 2 moved hosting to Railway, dropped Cloudflare, and deferred crash repair.
- Revision 3 brings crash repair and response reuse back into the first build, which matches Astra's round-2 position that paper games should have them. It also removes the turn cap and notifications and leaves the game count open. Astra has not reviewed revisions 2 and 3.

## 27. Sources

Archived copies and hashes are in `docs/research_raw/cloud_runner_2026-10-24/`.

- OpenRouter model catalog and endpoints, fetched 2026-10-24: https://openrouter.ai/api/v1/models and `/api/v1/models/<id>/endpoints`
- OpenRouter provider routing: https://openrouter.ai/docs/guides/routing/provider-selection
- OpenRouter BYOK: https://openrouter.ai/docs/features/byok
- OpenRouter limits and 402 reasons: https://openrouter.ai/docs/api_reference/limits
- Railway plans: https://docs.railway.com/pricing/plans
- Railway volumes: https://docs.railway.com/volumes/reference
- Railway backups: https://docs.railway.com/reference/backups
- Railway deployment teardown and draining: https://docs.railway.com/deployments/deployment-teardown
- Railway config as code: https://docs.railway.com/reference/config-as-code
- Vercel function limits: https://vercel.com/docs/functions/limitations
- Neon pricing: https://neon.com/pricing
- Supabase pricing: https://supabase.com/pricing
- HTTPX timeouts: https://www.python-httpx.org/advanced/timeouts/
