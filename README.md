# MonopolyBench

A deterministic multi-agent LLM research benchmark testing long-horizon planning, negotiation, deception, memory, and economic decision-making across multiple complete Monopoly games.

Instead of asking models isolated questions, MonopolyBench places tool-calling agents inside a persistent economic system where every decision affects later liquidity, bargaining power, rent exposure, property control, and survival. Every action is constrained by the rules engine, validated against legal moves, and preserved in a replayable research artifact.

**Research paper forthcoming.**

The current executable treatment is `audit_corrected_v2`. See the
[audit fixes and evaluation limits](docs/benchmark_audit_fixes.md) for rule variants,
observation limits, fixture quarantine, recovery guarantees, and verification.
Historical runs used earlier treatments and remain exploratory evidence.

![MonopolyBench live UI](MonopolyBench.png)

[Video demo](https://youtu.be/44xiBJf1nDk)

## Product and highlights

MonopolyBench is simultaneously:

- A live arena where four LLM agents play complete Monopoly games.
- A reproducible benchmark for comparing long-horizon agent behavior.
- A research platform for studying planning, negotiation, deception, memory, cooperation, collusion, bias, and economic decision-making.
- A deterministic simulation where models cannot fabricate actions or bypass the game rules.
- A replayable evaluation system that preserves every decision, prompt, response, action, event, state transition, and cost record.

The benchmark implements a documented Monopoly variant with auctions, trades, mortgages, housing shortages, rent shocks, jail decisions, liquidity management, liquidation, and bankruptcy. Public messages expose negotiation and table talk. Private generated analysis is an observable output, not proof of hidden intent.

Full games provide trajectories for studying strategy across dependent decisions. Frozen micro-scenarios probe individual decisions; their scores and related-fixture comparisons are not validated measures of full-game competence or causal behavioral effects. Fixtures with illegal reference actions are quarantined before paid execution.

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
