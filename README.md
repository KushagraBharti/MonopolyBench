# MonopolyBench

A deterministic Monopoly engine where various LLMs compete head-to-head in real-time, with a custom UI for spectators.

This repository is meant to serve three purposes:
1. **Live demo** - A real-time UI for watching LLMs play Monopoly.
2. **Benchmark** - A reproducible benchmark for testing LLMs on Monopoly.
3. **Research** - A research-grade dataset for studying LLM behavior in Monopoly.

![MonopolyBench](MonopolyBench.png)
[Video Demo](https://youtu.be/44xiBJf1nDk)

The goal is to test LLMs on 
1) **Raw Monopoly Performance** - Which LLM is the best at playing Monopoly?
2) **Long-Horizon Planning and Execution** - Are LLMs able to plan and execute long-term strategies?
3) **Negotiation, Bluffing, and Deception** - Are LLMs able to negotiate, bluff, and deceive?
4) **Uncovering LLM Biases** - Using the Monopoly harness to uncover biases in LLMs. Using biases from Thinking, Fast, and Slow by Daniel Kahneman

I plan to publish a paper in correlation to this project as well.

Future Implementations: 
1. **TrueSkill** - A TrueSkill ranking system for LLMs playing Monopoly.
2. **Multiplayer** - A multiplayer version of Monopoly where humans can play against LLMs.
3. **Custom Rules** - A custom ruleset for Monopoly that is more challenging for LLMs.
4. **Micro-Decisions** - A micro-decision suite to observe LLMs on specific interesting scenarios in Monopoly.

---

## What you can do

- Start a 4-player game where each player is an LLM (via OpenRouter).
- Watch the game live in a custom React UI fed by a FastAPI WebSocket.
- Inspect each LLM decision (attempts, retries, validation errors, fallbacks, timing).
- Run headless single games or batches for benchmarking.

---

## Architecture

![MonopolyBench Architecture](benchmark_architecture.jpeg)

---

## Repo layout

- `contracts/`: schemas + TS types + examples + board spec
- `frontend/`: render-only UI (React/Vite)
- `python/packages/engine`: deterministic Monopoly rules engine
- `python/packages/arena`: OpenRouter orchestration + prompting + strict validation + retries/fallbacks
- `python/packages/telemetry`: run folder management + writers + summary builder
- `python/apps/api`: FastAPI + WebSocket server
- `scripts/`: verification scripts
- `runs/`: output artifacts (generated)

---

## How it works

MonopolyBench is designed so runs are **replayable**, **inspectable**, and **comparable** across models. The rules engine is the source of truth, models can only choose from explicitly allowed actions, and every state change is recorded as an ordered event.

### One run, end-to-end

1. **Engine advances the game (authoritative + deterministic)**
   - The engine is the only component that can mutate game state.
   - Dice, movement, payments, card draws, etc. are resolved using seeded randomness.

2. **When a player (LLM) must choose, the engine creates a `DecisionPoint`**
   - Includes `decision_id`, `decision_type`, `player_id`
   - Includes the full board state (player info, properties, past actions/messages/thoughts, etc.)
   - Includes a complete `legal_actions` menu, where each action has a name + argument schema (models never invent moves; they pick from this list)

3. **Arena prompts the model (OpenRouter tools) and enforces legality**
   - The arena converts `legal_actions` into an OpenRouter tool schema and sends the decision context.
   - The model must return **exactly one tool call** that matches a legal action and its schema.
   - If output is invalid → **exactly one** corrective retry with validation errors.
   - If still invalid → a **deterministic fallback** action is applied and logged.

4. **Engine applies the chosen action and emits resulting events**
   - The applied action (and args) is logged for replay.
   - The resulting state changes are represented by events, which are the canonical replay surface.

5. **API streams the run; UI renders only**
   - The API streams snapshots/events over WebSocket.
   - The frontend is render-only: it displays snapshots/events and does not implement rules or infer legality.

6. **Telemetry writes artifacts for replay and inspection**
   - Everything needed to debug and reproduce a run is written under `runs/<run_id>/`:
     events, decisions (including retries/fallbacks), actions, per-turn snapshots, prompts, and summaries.

For repo boundaries and “don’t break the benchmark” rules (determinism, contracts, logging), see `AGENTS.md`.

---

## Quickstart

### Prerequisites
- Node.js (for the frontend)
- Bun
- Python via `uv` (workspace is under `python/`)
- OpenRouter API key

### Configuration

- Required: `OPENROUTER_API_KEY`
- Default player configuration lives at: `python/apps/api/src/monopoly_api/config/players.json`

---

### 1) Configure environment

Environment Variable file at repository root (`.env`):
```bash
OPENROUTER_API_KEY=...
```

### 2) Install dependencies

I recommend using `uv` for Python and `bun` for the frontend.
I also recommend using a Python virtual environment.

Frontend:
```bash
cd frontend
bun install
```

Python (from repo root):
```bash
conda create -n monopolybench python=3.13 -y
conda activate monopolybench
cd python
uv sync --all-packages
```

### 3) Run verification (recommended before pushing)

From repo root (must have powershell 7+):
```powershell
pwsh -File scripts/verify.ps1
```
On macOS/Linux:
```bash
./scripts/verify.sh
```

This will ensure that everything is running perfectly.

### 4) Run the backend
```bash
cd apps/api
uv run python -m uvicorn monopoly_api.main:app --host 127.0.0.1 --port 8000 --reload
```

Health check: open `http://127.0.0.1:8000/health` and expect `{"ok": true}`.

### 5) Run the frontend
```bash
cd frontend
bun run dev
```

Open `http://localhost:5173`.

---

## Research Artifacts

MonopolyBench writes research artifacts under `runs/`. Ordinary full-game runs live at
`runs/<run_id>/`; full-game batch artifacts live at `runs/batches/<batch_id>/`.

The prompt pipeline is benchmark-critical. Infrastructure work must not change prompt
content, formatting, message order, OpenRouter tool schemas, retry wording, or any other
model-facing request payload. The artifact and review systems are post-hoc only.

### Headless Full Game

```bash
cd python/packages/arena
uv run python -m monopoly_arena.run --seed 123 --max-turns 20
```

Every completed full-game run writes the core event/action/decision logs plus:

- `run_config.json`
- `players.json`
- `seat_assignment.json`
- `scorecard.json`
- `scorecard_players.json`
- `scorecard_decisions.jsonl`
- `scorecard_events.jsonl`
- `usage.json`
- `usage_decisions.jsonl`
- `usage_attempts.jsonl`
- `cost_report.json`
- `replay_report.json`
- `replay_steps.jsonl`
- `replay_flags.jsonl`
- `replay_navigation.json`
- `trace_findings.jsonl`
- `trace_summary.json`
- `failure_findings.jsonl`
- `failure_summary.json`
- `review_queue.jsonl`
- `reviews/review_labels.jsonl`
- `reviews/review_summary.json`
- `artifact_manifest.json`

Replay verification compares canonicalized replayed events against the original
`events.jsonl` using the recorded `actions.jsonl` and `run_config.json`.

### Full-Game Batches

```bash
cd python/packages/arena
uv run python -m monopoly_arena.batch_run --config ../../../batches/batch.example.json
```

Batch artifacts are written to `runs/batches/<batch_id>/`. The default batch settings
are research-facing:

- `seat_permutation: "latin_square"`
- `cost_budget: 50.0`
- `concurrency: 1`
- `budget_policy: "stop_immediately"`
- `max_turns: 200`
- `resume: true`
- `continue_on_failure: false`
- `replay_after_run: true`
- scorecard, trace, and failure artifact generation enabled

Batch outputs include:

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
- `model_cards/<safe_model_id>.json`
- `model_cards/<safe_model_id>.md`
- `artifact_manifest.json`

Seat assignment is deterministic. Supported modes are `latin_square`, `full`,
`seeded_random`, and `configured_order`. Per-run `seat_assignment.json` records the
permutation mode, id, seed material, digest, and player-to-seat mapping.

Batch run ids include seed, player order, `max_turns`, trade/auction limits, and seat
permutation id. Changing one of those settings intentionally creates a different run id.

### Cost And Token Accounting

Usage accounting relies on OpenRouter actuals only. The code preserves usage objects,
request ids, generation ids, native token fields, and reported costs when OpenRouter
returns them. Local tokenizer estimates are intentionally not used. Missing usage is
represented explicitly as `missing_openrouter_usage`.

When chat completion usage is incomplete and the OpenRouter client supports it, the
runner queries the OpenRouter `/generation` endpoint by generation id and backfills
missing official token/cost fields into post-hoc artifacts. This backfill changes only
stored accounting metadata, not model-facing requests.

Batch budget preflight uses known historical OpenRouter actuals only. After at least
one run with known actual cost, the runner uses the maximum observed run cost as a
conservative next-run estimate and stops before starting another run if the remaining
budget cannot cover it. If no prior actual cost is known, the estimate is recorded as
unavailable rather than guessed.

The batch runner attempts to snapshot OpenRouter model metadata through `/models` and
credit metadata through `/credits` when the configured client supports those endpoints.
If metadata is unavailable, the artifact records that status instead of guessing.

### Failure Taxonomy And Trace Analysis

The failure taxonomy is versioned at `contracts/taxonomy/failure_taxonomy.json`.
Trace and failure findings are generated from stored artifacts after the game. Subjective
behavioral labels remain human-reviewed only; no LLM classifiers are used for deception,
collusion, false claims, kingmaking, spite, or related labels.

### Review Workflow

Human review labels are saved as JSONL:

- queue: `runs/<run_id>/review_queue.jsonl`
- labels: `runs/<run_id>/reviews/review_labels.jsonl`
- summary: `runs/<run_id>/reviews/review_summary.json`

Reviewer identity is a simple `reviewer_id` string. If omitted, it defaults to
`local_reviewer`.

### Micro Scenario Metadata

Micro scenarios may include `research_metadata` for filtering, review, taxonomy tags,
expected failure modes, and paper organization. Its visibility is explicitly
`research_only_never_prompt`. It is not part of the `decision_point`, not sent to the
LLM, and not used to build OpenRouter messages or tools.

### Artifact Schemas And Versions

Core game protocol schemas remain in `contracts/schemas/`:

- `state.schema.json`
- `event.schema.json`
- `decision.schema.json`
- `action.schema.json`
- `micro_scenario.schema.json`

Research artifact contracts are grouped in
`contracts/schemas/benchmark_artifact.schema.json`. The shared TypeScript companion is
`contracts/ts/artifacts.ts`, and the frontend artifact client imports those shared
types. Examples are validated by `node contracts/validate-contracts.mjs`.

Current artifact versions include:

- run artifact manifest: `artifact_manifest_v1`
- batch artifact manifest: `batch_artifact_manifest_v1`
- batch protocol: `batch_protocol_v1`
- model card: `model_card_v1`
- scorecard: `scorecard_v1`
- replay step: `replay_step_v1`
- replay flag: `replay_flag_v1`
- review label: `review_label_v1`
- review summary: `review_summary_v1`
- micro research metadata: `micro_research_metadata_v1`

Usage/cost artifacts use OpenRouter actual data only. Missing OpenRouter accounting is
stored as missing/unknown; local tokenizer estimates are not used for final benchmark
accounting.

### Artifact API

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

The UI must remain render-only: it may load, filter, and display artifacts, but it must
not implement Monopoly rules, infer legality, or mutate game state.

---

## License

This project is licensed under the Apache License 2.0. See Details at [LICENSE](LICENSE)

## Citation

If you use MonopolyBench in academic work, please cite:

Kushagra Bharti. *MonopolyBench: A Multi-Agent LLM Benchmark for Monopoly.*  
GitHub repository, 2026.

A BibTeX entry is available via [CITATION.cff](CITATION.cff)
