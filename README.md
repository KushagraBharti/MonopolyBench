# MonopolyBench

A deterministic multi-agent LLM research benchmark testing long-horizon planning, negotiation, deception, memory, and economic decision-making across multiple complete Monopoly games.

Instead of asking models isolated questions, MonopolyBench places tool-calling agents inside a persistent economic system where every decision affects later liquidity, bargaining power, rent exposure, property control, and survival. Every action is constrained by the rules engine, validated against legal moves, and preserved in a replayable research artifact.

**Research paper forthcoming.**

![MonopolyBench live UI](MonopolyBench.png)

[Video demo](https://youtu.be/44xiBJf1nDk)

## Run everything with Docker

With Docker Engine/Desktop and Compose v2 installed, run from this checkout:

```sh
docker compose up --build
```

Open **http://localhost:8000**. The first startup prints a generated dashboard
password. One image and one container run the frontend, API, scheduler, game
workers, and artifact finalizer; a named volume keeps games and credentials
across restarts. No host Python, Node, or database installation is required.

For real models, put `OPENROUTER_API_KEY=...` in a root `.env` file before starting.
Without a key, the dashboard starts and shows the failed preflight. For a complete
zero-cost demo that automatically runs a short game using local mock models:

```sh
MB_DEMO=1 docker compose up --build
```

The demo gateway runs inside the same container and uses a separate data volume.
In PowerShell, set `$env:MB_DEMO="1"` before running the Compose command.
See [container setup and operations](deploy/README.md) for password retrieval,
exports, background startup, configuration, and Railway deployment.

## Product and highlights

MonopolyBench is simultaneously:

- A live arena where four LLM agents play complete Monopoly games.
- A reproducible benchmark for comparing long-horizon agent behavior.
- A research platform for studying planning, negotiation, deception, memory, cooperation, collusion, bias, and economic decision-making.
- A deterministic simulation where models cannot fabricate actions or bypass the game rules.
- A replayable evaluation system that preserves every decision, prompt, response, action, event, state transition, and cost record.

The benchmark covers the full strategic surface of Monopoly: auctions, trades, mortgages, housing shortages, rent shocks, jail decisions, liquidity management, liquidation, and bankruptcy. Public messages expose negotiation and table talk, while private model reasoning allows researchers to compare stated intent with observable behavior.

Full games test whether an agent can preserve a coherent strategy over hundreds of dependent decisions. Frozen micro-scenarios isolate specific behaviors—such as auction discipline, trade quality, loss aversion, kingmaking, deception, or liquidation errors—under controlled conditions.

## How MonopolyBench works

![MonopolyBench architecture](benchmark_architecture.jpeg)

### Evaluation loop

Each turn follows the same controlled pipeline:

1. **The engine advances the game.**  
   A seeded Python rules engine resolves dice, cards, movement, rent, auctions, trades, mortgages, building, jail, liquidation, and bankruptcy.

2. **The engine creates a decision point.**  
   The active agent receives the current state, visible history, and a complete list of legal actions.

3. **Legal actions become tool schemas.**  
   The arena converts the engine’s legal-action menu into schema-bound OpenRouter tools. The model must choose exactly one legal action with valid arguments.

4. **The response is validated.**  
   Invalid output receives one corrective retry containing the validation errors. A second failure triggers a deterministic fallback, which is recorded rather than hidden.

5. **The engine applies the action.**  
   Only the engine can mutate game state. Each resulting transition emits canonical events.

6. **The run is streamed and persisted.**  
   FastAPI streams snapshots and events to the React spectator interface while the telemetry system writes the complete research trail.

This boundary is central to the benchmark: the model has strategic freedom, but no freedom to invent game state or illegal moves.

### Determinism and replay

A serious agent benchmark must be able to prove what happened. MonopolyBench therefore separates four protocol objects:

- **Snapshots:** authoritative serialized game state.
- **Decisions:** the legal choices exposed to an agent.
- **Actions:** the structured move selected by the agent.
- **Events:** append-only state transitions emitted by the engine.

Given the same seed, configuration, players, and applied action sequence, the engine can reconstruct the game independently of model latency or network timing.

Replay verification operates at three levels:

- Action replay reconstructs the game from recorded actions.
- State replay validates the resulting state trajectory.
- Artifact replay compares the canonical event stream and event hashes.

### Research design

MonopolyBench supports two complementary evaluation modes.

**Full-game evaluation** measures:

- Survival and final rank
- Net worth and cash management
- Rent exposure and portfolio quality
- Auction and trade discipline
- Invalid-action and fallback rates
- Liquidation quality
- Reasoning cost and token usage
- Bankruptcy trajectory
- Seat and seed sensitivity

**Micro-scenario evaluation** places a model inside frozen decision states covering purchases, auctions, trades, building, jail, liquidation, safety, and behavioral bias. Scripted baseline actors provide controlled comparison policies.

Batch evaluation supports fixed seed cohorts, stable model rosters, Latin-square seat rotation, scorecards, model cards, category breakdowns, and cost reports.

### Technologies and external dependencies

- **Simulation and research:** Python, Pydantic, JSON Schema, Pytest
- **API and streaming:** FastAPI, Uvicorn, WebSockets, orjson
- **Model gateway:** OpenRouter
- **Frontend:** React, TypeScript, Vite, Zustand, Tailwind CSS
- **Tooling:** uv, Node.js, npm, Ruff, mypy
- **Artifact format:** JSON, JSONL, typed snapshots, event streams, and manifests

OpenRouter is the only model gateway. Usage and cost reports use provider-returned actuals rather than locally estimated token counts.

### Repository structure

```text
MonopolyBench/
├── contracts/                  # Schemas, TypeScript contracts, board data, fixtures
├── frontend/                   # Render-only React spectator and research UI
├── python/
│   ├── packages/
│   │   ├── engine/             # Deterministic Monopoly rules and legal decisions
│   │   ├── arena/              # LLM orchestration, prompts, tools, batches, replay
│   │   ├── telemetry/          # Run artifacts, summaries, costs, manifests
│   │   └── microbench/         # Frozen scenarios, scoring, reports, review queues
│   └── apps/api/               # FastAPI lifecycle, run APIs, WebSocket streaming
├── runs/                       # Generated games, batches, reports, and artifacts
├── batches/                    # Batch configurations
├── scripts/                    # Verification and repository tooling
├── research_direction.md       # Research roadmap
└── CITATION.cff                # Academic citation metadata
```

## Quick start

Requirements: Python 3.10+, `uv`, Node.js 22.12+ with npm, and an OpenRouter API key.

```bash
OPENROUTER_API_KEY=...
```

Install dependencies:

```bash
cd python
uv sync --all-packages

cd ../frontend
npm ci
```

Run the API:

```bash
cd python/apps/api
uv run python -m uvicorn monopoly_api.main:app --host 127.0.0.1 --port 8000 --reload
```

Run the frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

Verify the repository:

```bash
bash scripts/verify.sh
```
