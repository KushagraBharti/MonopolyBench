# MonopolyBench

**A live Monopoly arena and research benchmark for testing whether LLM agents can survive as long-horizon economic actors.**

MonopolyBench is not just "LLMs play Monopoly." It is a deterministic, replayable benchmark where language models must manage scarce cash, auctions, trades, rent shocks, mortgages, housing supply, jail timing, negotiation pressure, and bankruptcy risk through an enforced legal-action interface. The same repository serves three jobs:

1. **Live demo** - watch four LLM agents play Monopoly in a real-time React UI.
2. **Benchmark** - run reproducible games, batches, model rosters, seat rotations, scorecards, and replay checks.
3. **Research platform** - extract full-game failures into targeted micro-scenarios for bias, deception, collusion, tactical-error, and long-horizon planning studies.

![MonopolyBench live UI](MonopolyBench.png)

[Video demo](https://youtu.be/44xiBJf1nDk)

## What makes it interesting

- **31k lines across 5 Python packages**: deterministic rules engine, OpenRouter arena, telemetry, microbench, and FastAPI service.
- **178 tests** covering engine rules, schemas, replay, artifacts, micro-scenarios, prompting contracts, and API behavior.
- **130 micro-scenarios** for auctions, purchases, trades, building, liquidation, jail, rent shocks, safety probes, and behavioral-bias checks.
- **19 legal actions across 10 decision types** exposed to models as strict tool schemas.
- **6 baseline actors** for comparing LLM behavior against controlled non-LLM policies.
- **Three-tier replay verification**: action replay, state replay, and artifact/event-stream replay with canonical event hashes.
- **OpenRouter-actuals-only accounting**: usage and cost reports use provider-returned actual token/cost metadata, never local tokenizer guesses.

The current committed runs are scripted validation games and artifact checks, not a finished leaderboard. The codebase is built so leaderboard claims can be made later with fixed seed cohorts, seat rotations, stable rosters, replay verification, pricing snapshots, and uncertainty estimates.

## What you can do

- Start a four-agent LLM Monopoly game through OpenRouter.
- Watch the board, events, model decisions, retries, validation errors, fallbacks, timing, and game flow live.
- Run headless single games or full-game batches.
- Inspect every prompt, tool call, action, state snapshot, event, usage record, and replay report.
- Generate targeted micro-benchmark reports for tactical decisions, safety labels, bias probes, counterfactual pairs, and campaign-style scenario sequences.

## Architecture

![MonopolyBench architecture](benchmark_architecture.jpeg)

MonopolyBench keeps the benchmark boundary strict: the engine owns rules, the arena owns model orchestration, the telemetry layer owns artifacts, and the UI renders stored state without re-implementing game logic.

### Runtime loop

1. **The engine advances the game**
   - The Python engine is the only component allowed to mutate game state.
   - Dice, movement, rent, cards, auctions, trades, mortgages, houses, hotels, jail, liquidation, and bankruptcy all resolve through seeded deterministic rules.

2. **The engine emits a decision point**
   - Each LLM turn produces a `DecisionPoint` with a stable `decision_id`, `decision_type`, `player_id`, full board state, visible history, and complete `legal_actions`.
   - Models never invent moves. They choose one legal action from an engine-provided menu.

3. **The arena converts legal actions into tools**
   - The OpenRouter prompt includes the decision context and a tool schema generated from the legal-action list.
   - The model must return exactly one tool call matching a legal action and its argument schema.
   - Invalid output gets one corrective retry with validation errors. A second failure triggers a deterministic fallback, which is logged.

4. **The engine applies the action**
   - The chosen action and arguments are recorded.
   - Resulting state transitions are emitted as canonical events, which become the replay and analysis surface.

5. **The API streams and the UI renders**
   - FastAPI exposes run state and artifact endpoints.
   - WebSocket streaming powers the live board.
   - The React frontend is render-only: it displays snapshots and artifacts but does not infer legality or mutate state.

6. **Telemetry writes the research trail**
   - Each run writes events, decisions, actions, snapshots, prompts, attempts, usage, costs, scorecards, replay reports, review queues, and artifact manifests under `runs/<run_id>/`.

## Research direction

The canonical roadmap lives in [research_direction.md](research_direction.md). The strongest framing is that MonopolyBench tests durable economic agency under enforceable rules and adversarial incentives.

The near-term paper track centers on two layers:

- **Long-horizon full games**: survival, rank, net worth, cash management, rent exposure, auction discipline, trade surplus, liquidation quality, invalid attempts, reasoning cost, and bankruptcy trajectories.
- **Targeted scenario suites**: frozen decision states that isolate tactical mistakes, behavioral biases, deception risk, collusion risk, public/private mismatch, kingmaking, spite, and negotiation behavior.

Future tracks include real-estate/asset-management extensions and orchestration studies such as memory windows, prompt conditions, legal-action formats, private/public visibility, and model identity framing. Those tracks are versioned separately so they do not silently change the default benchmark surface.

## Repository map

- `contracts/` - JSON schemas, TypeScript types, board spec, examples, model rosters, taxonomy, micro-scenario fixtures, and research overlays.
- `frontend/` - React/Vite render-only UI for live games, runs, batches, artifacts, and review workflows.
- `python/packages/engine` - deterministic Monopoly rules engine.
- `python/packages/arena` - OpenRouter client, prompts, legal tool schemas, model runners, batches, replay verification, scorecards, and artifact generation.
- `python/packages/telemetry` - run-folder management, writers, summaries, manifests, and persisted research artifacts.
- `python/packages/microbench` - targeted scenario runner, scorer, research overlays, reports, counterfactuals, campaigns, and human-review queues.
- `python/apps/api` - FastAPI service, WebSocket stream, run APIs, artifact APIs, and review APIs.
- `scripts/` - repo verification scripts.
- `runs/` - generated run, batch, browser-check, and micro-benchmark outputs.

For repo boundaries and benchmark invariants, see [AGENTS.md](AGENTS.md).

## Research artifacts

Full-game runs write to `runs/<run_id>/`. Batch runs write to `runs/batches/<batch_id>/`. Micro-scenario runs write to `runs/micro/` and `runs/micro_batches/`.

Core full-game artifacts include:

- `run_config.json`, `players.json`, `seat_assignment.json`
- `events.jsonl`, `actions.jsonl`, `decisions.jsonl`, per-turn snapshots, prompts, attempts, and summaries
- `scorecard.json`, `scorecard_players.json`, `scorecard_decisions.jsonl`, `scorecard_events.jsonl`
- `usage.json`, `usage_decisions.jsonl`, `usage_attempts.jsonl`
- `cost_report.json`, `token_report.json`, `budget_report.json`
- `replay_report.json`, `state_replay_report.json`, `artifact_replay_report.json`, `event_hashes.json`
- `trace_findings.jsonl`, `failure_findings.jsonl`, summaries, review queues, labels, and `artifact_manifest.json`

Replay verification has three levels:

- **Action replay** checks that `actions.jsonl` and `run_config.json` reproduce the game trajectory.
- **State replay** verifies state transitions from authoritative engine state.
- **Artifact replay** strictly compares canonical event streams, including LLM observation metadata and event hashes.

Cost accounting uses OpenRouter actuals only. If provider usage is incomplete and the client can fetch `/generation` metadata, the runner backfills official token and cost fields into post-hoc artifacts. Missing provider accounting is stored as missing/unknown rather than estimated.

## Micro-scenario research

Micro-scenarios are frozen Monopoly states with legal-action menus and deterministic scoring rules. They let the benchmark ask why a model failed, not only whether it won.

The current research overlays live in `contracts/micro/research_suites/`:

- `bias-v1` - behavioral-bias categories and counterfactual framing hooks.
- `safety-v1` - deception, collusion, kingmaking, public/private mismatch, and human-review-only labels.
- `counterfactual-v1` - paired-fixture stability analysis.
- `campaign-v1` - multi-step fixture sequences for longer tactical chains.

Subjective safety and behavior labels are not finalized by code. The system can queue review tasks, but deception, collusion, spite, kingmaking, and similar labels are human-reviewed with evidence and confidence fields.

Generate a research report from `python/`:

```powershell
uv run python -m monopoly_microbench.cli research-report --suite safety-v1 --runs-dir ../runs
```

Join completed model results:

```powershell
uv run python -m monopoly_microbench.cli research-report --suite bias-v1 --runs-dir ../runs --result-batch-id <micro-batch-id>
```

Create review queues and validate labels:

```powershell
uv run python -m monopoly_microbench.cli review-queue --suite safety-v1 --out ../runs/safety_review_queue.jsonl
uv run python -m monopoly_microbench.cli validate-labels --labels path/to/labels.jsonl
```

## Quickstart

### Prerequisites

- Node.js
- Bun
- Python 3.10+ through `uv`
- PowerShell 7+ for the Windows verification script
- OpenRouter API key

### Configure environment

Create `.env` at the repository root:

```bash
OPENROUTER_API_KEY=...
```

Default player configuration lives at:

```text
python/apps/api/src/monopoly_api/config/players.json
```

### Install dependencies

Frontend:

```bash
cd frontend
bun install
```

Python:

```bash
conda create -n monopolybench python=3.13 -y
conda activate monopolybench
cd python
uv sync --all-packages
```

### Verify the repo

From the repo root:

```powershell
pwsh -File scripts/verify.ps1
```

On macOS/Linux:

```bash
./scripts/verify.sh
```

Contract-only validation:

```powershell
node contracts/validate-contracts.mjs
```

### Run the live demo

Backend:

```bash
cd python/apps/api
uv run python -m uvicorn monopoly_api.main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

```text
http://127.0.0.1:8000/health
```

Frontend:

```bash
cd frontend
bun run dev
```

Open:

```text
http://localhost:5173
```

### Run a headless full game

```bash
cd python/packages/arena
uv run python -m monopoly_arena.run --seed 123 --max-turns 20
```

### Run a full-game batch

```bash
cd python/packages/arena
uv run python -m monopoly_arena.batch_run --config ../../../batches/batch.example.json
```

Default batch settings are research-facing: Latin-square seat rotation, deterministic run IDs, budget preflight, resume support, replay-after-run, scorecard generation, trace/failure artifacts, and cost/token reports.

### API artifact endpoints

The FastAPI server exposes stored artifacts without recomputing rules:

- `GET /runs/{run_id}/artifacts`
- `GET /runs/{run_id}/artifacts/{artifact_name}`
- `GET /runs/{run_id}/review/queue`
- `GET /runs/{run_id}/review/labels`
- `POST /runs/{run_id}/review/labels`
- `GET /runs/{run_id}/review/summary`
- `GET /batches`
- `GET /batches/{batch_id}`
- `GET /batches/{batch_id}/artifacts`
- `GET /batches/{batch_id}/artifacts/{artifact_name}`
- `GET /batches/{batch_id}/model_cards/{card_id}`
- `GET /micro/research-reports`
- `GET /micro/research-reports/{report_id}`
- `GET /micro/research-reports/{report_id}/artifacts`
- `GET /micro/research-reports/{report_id}/artifacts/{artifact_name}`

## Benchmark invariants

These are the rules that keep MonopolyBench research-grade:

- The engine is authoritative and deterministic.
- The frontend is render-only.
- Models can only choose engine-provided legal actions.
- Prompt content, message order, tool schemas, retry wording, and model-facing payloads are benchmark-critical.
- Research metadata is never included in model prompts.
- Usage/cost reports use OpenRouter actuals only.
- Subjective behavioral labels require human review.
- Serious leaderboard claims require repeated runs, seat rotations, replay verification, and uncertainty estimates.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).

## Citation

If you use MonopolyBench in academic work, please cite:

Kushagra Bharti. *MonopolyBench: A Multi-Agent LLM Benchmark for Monopoly.* GitHub repository, 2026.

A BibTeX entry is available via [CITATION.cff](CITATION.cff).
