# Handoff Summary — MonopolyBench / Monopoly LLM Benchmark Research Project

## 0. Executive State of the Project

The conversation centered around turning a working **Monopoly LLM Benchmark** repository into a serious research platform and paper project. The project began as a deterministic, inspectable, multi-agent Monopoly game where LLMs play under strict rules. Over the conversation, the framing evolved from “cool LLMs playing Monopoly” into a much sharper research thesis:

> **MonopolyBench is a reproducible testbed for evaluating long-horizon economic agency, negotiation, tactical failure modes, safety behavior, and tool/action reliability in legal-action-constrained LLM agents.**

The current practical state is:

* The codebase is far beyond a demo. It has a rules engine, LLM orchestration, UI, telemetry, contract schemas, replay/logging artifacts, prompt inspection, cost/usage support, and research scenario infrastructure.
* The product/benchmark vision has mostly been mapped.
* The near-term focus has shifted fully toward **research execution and paper framing**.
* The mentor, Parth, has approved the direction and wants momentum toward an **AAAI workshop/main-track-style submission target**, using a concrete deadline as a forcing function.
* The immediate research scope should stay focused on:

  1. **Long-Horizon Monopoly Agency**
  2. **Targeted Scenario / Micro-Decision Suite**
* The broader future tracks—business simulation / CRE fund management and orchestration/information design—are valuable but should not dilute the Monday deliverables or first paper.
* The current most important next step is not more architecture brainstorming. It is running a **clean, publication-safe pilot** with exact model IDs, cost accounting, reasoning-effort configuration, micro-suite results, and one bounded full-game smoke run.

---

# 1. User / Project Context

The user is Kush, working on a project called **MonopolyBench**. The core repository is described as:

> A deterministic long-horizon LLM-agent benchmark for evaluating planning, negotiation, deception, memory, bias, and asset-management behavior.

The repo is located at:

* `https://github.com/KushagraBharti/MonopolyBench`
* Main research write-up:

  * `research_direction.md`
* Local paths mentioned in the latest status:

  * `c:/Users/kushagra/OneDrive/Documents/CS Projects/MonopolyBench/research_direction.md`
  * `implementation_status.md`
  * `contracts/research/monopoly_long_v1_model_rosters.json`
  * `campaigns/monopoly-long-v1-smoke.json`
  * `docs/micro_research_suites.md`
  * `python/packages/arena/src/monopoly_arena/openrouter_client.py`
  * `python/packages/arena/src/monopoly_arena/player_config.py`
  * `python/packages/telemetry/src/monopoly_telemetry/usage.py`
  * `python/apps/api/src/monopoly_api/config/players.json`

The project has been discussed with a PhD mentor, Parth. Multiple meetings with Parth shaped the research roadmap.

---

# 2. Initial Project Narrative: What Was Built

At the start of the conversation, the user described the project journey in detail.

The initial goal was to take a loose, fragile Monopoly LLM project and make it:

* usable,
* stable,
* reliable,
* inspectable,
* extensible,
* serious enough to become a benchmark or research project.

The initial version “worked” in the casual sense but was not clean, consistent, or ready for rigorous analysis. The work focused on turning a project that “runs” into a system that can be trusted.

## Major engineering themes from the user’s project narrative

### 2.1 Reliability First

The first big project phase was about making the whole repository reliable. The user did not want “it runs most of the time.” They wanted:

* predictable behavior,
* coherent repo setup,
* tests that matter,
* a single verification flow,
* confidence that future changes do not randomly break the system.

This became the foundation for all future benchmark/research work.

### 2.2 Refactoring and Modular Organization

The next project phase was refactoring. The goal was to make responsibilities clear and prevent code drift.

Important goals:

* modularity,
* fewer duplicated concepts,
* clearer boundaries between rule logic, LLM orchestration, logging, API, and UI,
* easier editing/testing/extending,
* reducing future bug risk.

### 2.3 Inspectable AI Decisions

The central research feature became decision inspectability.

The goal was not merely:

> “Models play Monopoly.”

The goal was:

> “Models play Monopoly in a way where we can inspect exactly what they were asked, what they answered, what action was applied, and why.”

This included:

* exact prompt payloads,
* exact model responses,
* applied action records,
* decision logs,
* fallback/retry paths,
* prompt artifacts across normal/retry/fallback flows.

This was repeatedly identified as one of the project’s strongest research advantages.

### 2.4 Model and Player Configuration

The project improved usability around:

* changing model IDs,
* setting player names,
* controlling prompts,
* handling OpenRouter quirks,
* supporting model variants and free-tag formats,
* ensuring logs/UI reflect configured model names correctly.

### 2.5 Runtime Controls

Pause/resume/stop became important because LLM calls can be long-running.

The goal was:

* pausing without breaking in-flight model calls,
* stopping cleanly,
* preventing old logs from reappearing,
* avoiding stale UI updates after stop,
* handling stop while waiting for model response.

### 2.6 Hardening Passes

Several hardening passes addressed:

* preventing overwritten logs,
* ensuring verification scripts fail correctly,
* preventing shim drift,
* ensuring prompt artifacts always exist,
* removing silent failure modes,
* verifying retry/fallback correctness,
* reducing flakiness.

### 2.7 Monopoly Mechanics Completion

After architecture and reliability work, the user focused on real Monopoly rules:

* auctions,
* trading,
* jail,
* liquidation,
* bankruptcy,
* building,
* decision constraints,
* UI integration,
* logging integration.

Auctions were identified as a major missing piece and were implemented end-to-end:

* auction loop,
* bidding flow,
* UI,
* tests.

Trading was implemented with negotiation and limits, including multi-actor decision handling where the actor is not always the active turn player. This was important because trade responses/counteroffers involve players outside the current dice-roll turn.

### 2.8 UI Evolution

The UI moved from dev-only to something closer to a usable spectator/debugging interface.

Important UI goals:

* less clutter,
* clearer player panel,
* better feed mode,
* better inspector,
* better board presentation,
* ability to drill into model I/O,
* normal-person-readable feed mode,
* dev mode available but not always dominant.

### 2.9 Correctness Emergency: “Player 1 Goes Twice”

A major bug occurred where Player 1 could sometimes go twice. The project treated that as an integrity violation, not a cosmetic issue. The fix aimed to make that entire class of bug impossible, because turn order correctness is fundamental to benchmark validity.

---

# 3. Combined Repository Breakdown from Three AI Agent Reports

The user provided three independently written detailed breakdowns of the repository. These were merged into one master architecture understanding.

## 3.1 High-Level Architecture

The repo is best understood as a “sporting event broadcast” or “Monopoly stadium.”

### Core systems

#### 1. Contracts

Folder:

* `contracts/`

Role:

* Shared schema/protocol layer.
* Defines the JSON language spoken by engine, arena, API, frontend, and telemetry.
* Contains JSON schemas, TypeScript types, static board data, examples, validation scripts.

Important files/concepts:

* `schemas/`
* `ts/`
* `data/board.json`
* `examples/`
* `validate-contracts.mjs`
* schemas for events, state snapshots, actions, decisions, board spec.

Purpose:

* Prevent backend/frontend drift.
* Make event/state/action formats explicit.
* Support contract validation.

#### 2. Engine

Folder:

* `python/packages/engine/`

Role:

* The Monopoly referee.
* Only authoritative state mutator.
* Enforces rules.
* Generates legal actions.
* Emits events.
* Uses deterministic RNG.
* Produces snapshots and decision points.

Important files:

* `engine.py`
* `models.py`
* `board.py`
* `rng.py`
* `cards.py`
* `replay.py`

Important behaviors:

* `advance_until_decision()`
* `apply_action()`
* deterministic event sequence,
* legal action generation,
* state snapshot export,
* event emission,
* turn-order enforcement,
* decision IDs.

#### 3. Arena

Folder:

* `python/packages/arena/`

Role:

* LLM orchestrator.
* Talks to OpenRouter.
* Builds prompts.
* Converts game state into model-readable context.
* Supplies legal tool/action schemas.
* Parses model responses.
* Validates actions.
* Retries once on invalid output.
* Applies deterministic fallback if needed.
* Logs decisions and prompt artifacts.

Important files:

* `llm_runner.py`
* `prompting.py`
* `openrouter_client.py`
* `action_validation.py`
* `player_config.py`
* `batch_run.py`

Important concepts:

* `DecisionAttempt`
* `DecisionOutcome`
* `PromptBundle`
* retry and fallback logic,
* legal action membership validation,
* OpenRouter model config support,
* reasoning effort support.

#### 4. Telemetry

Folder:

* `python/packages/telemetry/`

Role:

* Official record keeper.
* Writes run artifacts.
* Supports later analysis, replay, summaries, cost accounting, decision inspection.

Important files:

* `run_files.py`
* `writer_jsonl.py`
* `summary.py`
* `usage.py`

Output artifacts:

```text
runs/<run_id>/
  events.jsonl
  decisions.jsonl
  actions.jsonl
  summary.json
  usage.json
  state/
    turn_XXXX.json
  prompts/
    decision_XXX_system.txt
    decision_XXX_user.json
    decision_XXX_tools.json
    decision_XXX_response.json
```

Additional desired artifacts discussed:

* `run_manifest.json`
* `scorecard.json`
* `leaderboard.json`
* `statistics.json`
* `benchmark_result.json`
* `trajectory.json`

#### 5. API

Folder:

* `python/apps/api/`

Role:

* FastAPI server.
* Starts/stops/pauses/resumes runs.
* Manages the active run.
* Streams events/snapshots over WebSocket.
* Serves decision inspection endpoints.
* Coordinates arena and telemetry.

Important files:

* `main.py`
* `run_manager.py`
* `ws_protocol.py`
* `decision_index.py`
* `settings.py`

Important endpoints:

* `/health`
* `/run/start`
* `/run/stop`
* `/run/pause`
* `/run/resume`
* `/run/status`
* `/ws`
* decision inspection endpoints under `/runs/{run_id}/...`

#### 6. Frontend

Folder:

* `frontend/`

Role:

* React UI.
* Render-only client.
* Displays board, players, event feed, auctions, trades, inspector, model I/O.
* Does not compute Monopoly rules.

Important files/components:

* `App.tsx`
* `store.ts`
* `ws.ts`
* board components,
* feed components,
* player panels,
* game controls,
* inspector,
* `LlmIoPanel`,
* decision-related panels.

Important principle:

> UI must never infer game outcomes. It renders snapshots/events from the backend.

---

## 3.2 Runtime Flow

The full runtime loop was described as:

1. Engine advances deterministically until a decision is required.
2. Engine emits events and produces a decision point with legal actions.
3. Arena receives the decision.
4. Arena builds a prompt from:

   * current state snapshot,
   * player perspective,
   * legal actions,
   * relevant rules,
   * recent memory/context.
5. Arena calls OpenRouter.
6. Model returns a tool call/action.
7. Arena validates:

   * valid JSON,
   * valid action schema,
   * membership in engine legal actions.
8. If invalid:

   * retry once with error notes.
9. If still invalid or model call fails:

   * use deterministic fallback.
10. Arena applies action to engine.
11. Engine revalidates action and mutates state.
12. Engine emits resulting events.
13. API broadcasts events/snapshots to frontend.
14. Telemetry writes artifacts.
15. Loop repeats until game over, turn cap, or stop.

---

## 3.3 Core Invariants

Critical invariants identified repeatedly:

1. **Engine-only mutation**

   * Only engine mutates game state.

2. **Determinism**

   * Same seed + same action sequence must produce same event stream.

3. **Legal actions only**

   * LLMs cannot invent arbitrary moves.
   * Arena validates, engine revalidates.

4. **Every meaningful mutation emits an event**

   * No silent state changes.

5. **Turn order correctness**

   * Active player must be correct.
   * No double turns.
   * No skipped actors.

6. **UI is render-only**

   * No local game logic.

7. **Contracts must remain aligned**

   * Python payloads, JSON schemas, TypeScript types, examples, and frontend rendering must match.

8. **OpenRouter is the only LLM gateway**

   * No direct OpenAI/Anthropic calls in the current architecture.

9. **Replayability**

   * Actions/events must be sufficient to reconstruct behavior.

10. **Run artifacts must not be overwritten or silently corrupted**

---

# 4. Master Future Roadmap That Was Built Earlier

The conversation then moved from repo breakdown to future development planning. Three separate future-development reports were merged into one master roadmap.

## 4.1 North Star

The agreed north star became:

> Make this the most reproducible, inspectable, and fun-to-watch multi-agent LLM game benchmark, where every claim is backed by deterministic replay and rich artifacts.

## 4.2 Software Improvements

### Performance and Latency

Planned/considered improvements:

* Parallelize thinking time in auctions/trades where possible.
* Keep core turn order sequential for Monopoly correctness.
* Use `asyncio.gather()` for phases that naturally allow concurrency.
* Streaming LLM responses through OpenRouter to reduce perceived latency.
* Batched multi-game execution for large benchmark suites.
* Speculative execution by forking engine branches for legal actions.
* Prompt compaction to reduce token cost.

### Determinism and Replay

Key future work:

* Golden seed test suite.
* Byte-identical replay tests.
* Schema-validate live engine outputs, not just examples.
* Replay fidelity for fallback metadata.
* Idempotent action application using action IDs.
* Deterministic run config made explicit.

### Debugging and Observability

Planned improvements:

* Time-travel debugger / load from snapshot.
* Replay viewer in UI with scrubber.
* Decision diff viewer.
* Trace view linking decision → attempts → events.
* Telemetry explorer.
* State trajectory graphs.
* Prompt template inspector.

### UX Improvements

Planned improvements:

* Turn clarity indicators.
* Decision type badges.
* Property deed popovers.
* Decision HUD.
* Cinematic buffering while LLM thinks.
* Spectator mode.

### Reliability

Planned work:

* Crash recovery and checkpointing.
* Graceful cancellation.
* Timeout escalation.
* Formal run-state machine.
* Tests for stop during OpenRouter call, double start, pause while stopping.

### Architecture Cleanliness

Possible refactors:

* Split huge `engine.py` into modules:

  * `auction.py`
  * `trade.py`
  * `cards.py`
  * `movement.py`
  * `decisions.py`
* Contract code generation.
* Event bus abstraction.
* Unified repo-root helper.

---

## 4.3 Benchmark Potential

The benchmark plan included:

### Benchmark objects

* `BenchmarkRun`: one game.
* `Match`: set of runs comparing models/prompts.
* `Suite`: named/versioned benchmark suite.

### Leagues

1. **Standard League**

   * Normal Monopoly.
   * General long-horizon skill.

2. **Negotiator League**

   * High-resource start.
   * Forced trade relevance.
   * Less RNG-heavy early game.

3. **Other possible scenario leagues**

   * Conservation / low-resource starts.
   * Auction-heavy.
   * Build-heavy.
   * Safety/bias probes.

### Metrics

Primary:

* win rate,
* survival,
* net worth,
* net worth area under curve,
* turn count.

Reliability:

* invalid action rate,
* valid-on-first-try rate,
* retry rate,
* fallback rate,
* timeout rate.

Strategy:

* acquisition rate,
* monopoly completion rate,
* building efficiency,
* trade surplus,
* auction efficiency,
* rent extraction,
* jail policy quality,
* liquidation quality.

Operational:

* cost per game,
* cost per decision,
* token usage,
* reasoning tokens,
* latency,
* p95 latency.

### Ratings

Discussed systems:

* Elo by decomposing 4-player games into pairwise outcomes.
* Glicko-2.
* TrueSkill / OpenSkill as better for multiplayer.

### Reproducibility

Required for serious publication:

* fixed seeds,
* exact model IDs,
* versioned configs,
* environment capture,
* checksums,
* replay verification,
* artifact bundles,
* public raw logs.

---

## 4.4 Research Potential

Major research directions discussed:

1. **Tool-use reliability under hard legal constraints**
2. **Negotiation emergence and stability**
3. **Collusion detection**
4. **Auction rationality**
5. **Long-horizon planning**
6. **Credit assignment and memory**
7. **Risk management**
8. **Specification gaming**
9. **Deception and bluffing**
10. **Theory of mind / opponent modeling**
11. **Prompt sensitivity**
12. **Construct validity**
13. **Business simulation / economic agent extension**

Flagship paper ideas included:

* “PlayBench / MonopolyBench: Evaluating Strategic Reasoning in LLMs Through Competitive Monopoly”
* “Emergent Negotiation and Theory of Mind in Multi-Agent LLM Systems”
* “Specification Gaming and Alignment Failures in Constrained Multi-Agent Games”
* “Legal-Action Tool Use as a First-Class Measure of Agent Reliability”
* “Benchmark Construct Validity: What Does Monopoly Actually Measure?”

---

# 5. Research Pivot: Mentor Meetings and Initial Research Questions

The project then shifted into deeper research planning after meetings with Parth.

## 5.1 Initial research questions from mentor discussion

The user and mentor outlined:

```text
monopoly research

- literature survey on monopoly benchmarks
- existing monopoly agents/bots/etc.
- any SOTA monopoly bots??? stockfish-like
- various scenarios and observe what LLM does
  - does it follow theory?
  - do we give cheatsheet to LLMs?
  - measure accuracy
- pro Monopoly strategies
  - used by professional players / strong enthusiasts
  - do LLMs follow similar strategy?
- can LLMs reason, thought process, strategy, through long term decisions and gameplay?
  - long-term goals?
```

This led to a research plan around:

* existing Monopoly literature,
* RL agents and bots,
* Markov/probability theory,
* Monopoly strategy heuristics,
* LLM game benchmarks,
* tool-use benchmarks,
* long-horizon planning,
* negotiation/deception.

---

# 6. Monopoly Literature Survey and Existing Agents

The user compiled an initial literature survey.

## 6.1 Main conclusion

The central takeaway was:

> There is no existing widely adopted Monopoly benchmark.

More precisely:

> Prior work studies Monopoly via probability/Markov models and a small number of RL/agent prototypes, but the field lacks a reproducible, widely adopted benchmark suite with standardized artifacts, deterministic replay, and multi-agent negotiation instrumentation.

This became a key positioning statement for MonopolyBench.

## 6.2 Monopoly-specific sources listed

The user identified:

1. `https://arxiv.org/abs/2103.00683`

   * 2022 hybrid DRL approach to play Monopoly.
   * Later became the main paper to deep dive.

2. `https://doc.gold.ac.uk/aisb50/AISB50-S02/AISB50-S2-Bailis-paper.pdf`

   * 2014 RL approach to Monopoly.

3. `https://arxiv.org/html/2508.03368v1`

   * 2025 general board game platform using LLMs.

4. `https://aclanthology.org/2025.acl-long.378.pdf`

   * 2025 comparing LLM performance vs algorithmic performance in simple board games.

5. `https://proceedings.neurips.cc/paper_files/paper/2024/file/3191170938b6102e5c203b036b7c16dd-Paper-Conference.pdf`

   * 2024 general benchmark on LLM performance in simple board games.

6. `https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8929523`

   * 2019 RL Monopoly paper.

7. Monopoly probability and Markov chain work:

   * `https://web.mit.edu/sp.268/www/probability_and_monopoly.pdf`
   * `https://pi4math.web.illinois.edu/wp-content/uploads/2014/10/Gartland-Burson-Ferguson-Markovopoly.pdf`

## 6.3 Existing Monopoly agents/bots/etc.

The user found:

1. `https://github.com/williamhbell/MonopolySimulation`

   * Mostly probability/statistical simulation, not a strong agent.

2. `https://github.com/vlokwani/Monopoly-bot`

   * Old bot-like project, likely not usable for serious baseline.

3. `https://github.com/jonzia/Monopoly`

   * Framework for training an RL Monopoly bot.

4. `https://www.youtube.com/watch?v=dkvFcYBznPI`

   * YouTube video breaking down a good Monopoly bot.
   * GitHub:

     * `https://github.com/b2developer/MonopolyNEAT`

## 6.4 Bot tiering framework

The user summarized existing agents into tiers:

### Tier 1: Heuristic / probability bots

* Use landing probabilities.
* Use cash thresholds.
* Use hand-coded rules.
* Markov chain papers support these strategies.
* Usually shallow but stable.

### Tier 2: Search / MCTS / hybrid bots

* Some open-source projects try search/RL hybrids.
* Useful as baselines and failure guides.
* No recognized ecosystem leader.

### Tier 3: Research-grade RL prototypes

* Bonjour/Haliem hybrid DRL paper.
* TENCON RL paper.
* Closest to “research-grade Monopoly bots,” but not standardized.

### Tier 4: LLM agents

* Can negotiate/trade in language.
* Can explain decisions.
* Can adapt to new scenarios without retraining.
* But can fail via invalid actions, timeouts, poor long-horizon planning, or high API cost.

## 6.5 SOTA bot conclusion

There is no “Stockfish for Monopoly.”

Reasons discussed:

* Monopoly is stochastic.
* It is 4-player, not 1v1.
* It includes negotiation.
* Rules and house rules vary.
* Trading and auctions create huge branching.
* RL baselines exist, but no canonical engine/leaderboard exists.

This is good for MonopolyBench because it leaves room to define a standard.

---

# 7. Research Directions Formalized

The user consolidated initial research directions into a set of tracks.

## 7.1 MonopolyBench Platform & Benchmark

Goal:

* General benchmark for LLMs and bots playing Monopoly.
* Similar aspiration to ARC-AGI in the sense of being a recognizable evaluation arena, not in task mechanics.
* Many models, thousands of games.
* Compare rankings to MMLU/HumanEval or other standard LLM benchmarks.
* Show “strategy personalities.”

Core question:

> Does MonopolyBench rank models differently from static benchmarks, because it tests long-horizon economic behavior, negotiation, and legal-action reliability?

## 7.2 Micro Decision Suite

Instead of waiting for full games to naturally produce interesting moments, create curated states.

Decision types:

* Auctions

  * cash management,
  * long-term thinking,
  * monopoly potential.

* Trades

  * trade surplus,
  * fairness,
  * monopoly completion,
  * opponent modeling.

* Buy/Auction

  * whether to buy or decline to auction.

* Build/Mortgage

  * when to build houses,
  * when to mortgage,
  * liquidity management.

* Jail

  * early-game vs late-game jail strategy.

The key advantage:

> Micro-scenarios isolate specific tactical choices and produce cheaper, clearer, more statistically interpretable data than full games.

## 7.3 Macro Scenario Suite

Controlled multi-game suites:

* Standard normal rules.
* Negotiation-heavy high-resource starts.
* Conservation/low-resource starts.
* Potential future auction-heavy/build-heavy/no-trade variants.

Goal:

* Evaluate ecological behavior across many turns while still controlling variance.

## 7.4 Prompt Testing

Prompt interventions:

* theory cheatsheet vs no theory cheatsheet,
* full board details vs player-only details,
* different history/memory windows,
* public chat included/excluded,
* private thoughts included/excluded,
* reasoning effort low/medium/high,
* safety/deception prompt variants.

Key question:

> Do LLMs actually use given strategic theory, or merely produce better-sounding explanations?

## 7.5 Adherence to Pro Monopoly Strategies

Measure whether LLMs follow known Monopoly heuristics:

* prefer orange/red,
* value railroads,
* build houses quickly after monopoly,
* maintain liquidity,
* stay in jail late game,
* trade to complete monopolies,
* avoid poor cash-risk decisions,
* exploit housing scarcity.

This became a behavioral comparison track.

## 7.6 Long-Term Planning and Thinking

Research questions:

* Can LLMs form and execute multi-turn plans?
* Do stated strategies align with future actions?
* Do they pursue monopolies consistently?
* Do they manage cash over many turns?
* Do they learn/adapt within a game?
* Does longer memory improve performance?
* Does reasoning text correlate with better outcomes?

## 7.7 Negotiation, Deception, Bluffing

Possible investigations:

* Can models bluff in public messages?
* Do private thoughts diverge from public messages?
* Does hiding/revealing opponent identity change behavior?
* Do models use persuasion or anchoring?
* Do they develop deceptive trade strategies?
* Do they collude or kingmake?

---

# 8. Deep Dive into Bonjour et al. Paper

The user uploaded the PDF:

* `Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach.pdf`
* Local path:

  * `/mnt/data/Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach.pdf`

Paper:

* Title: **Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach**
* Authors:

  * Trevor Bonjour,
  * Marina Haliem,
  * Aala Alsalem,
  * Shilpa Thomas,
  * Hongyu Li,
  * Vaneet Aggarwal,
  * Mayank Kejriwal,
  * Bharat Bhargava.
* arXiv:

  * `https://arxiv.org/abs/2103.00683`
* Accepted in IEEE TETCI.
* Main result:

  * Hybrid agents outperform standard deep RL agents by around 20–30% in games won against fixed-policy agents.
  * Hybrid PPO agent performs best, with win rate around 91% against fixed-policy agents.

## 8.1 Core idea of the paper

They train RL agents to play full 4-player Monopoly.

They define:

* a state vector,
* a large action vector,
* reward function,
* fixed-policy baselines,
* PPO and DDQN learning agents,
* hybrid agents that use RL for some decisions and fixed policies for rare/simple decisions.

The key problem they identify:

> Monopoly contains many possible actions, but some occur rarely. Rare actions make learning inefficient. So they use DRL for frequent/complex decisions and fixed policy for infrequent/straightforward ones.

## 8.2 Their Monopoly environment

The environment simulates standard Monopoly but has important differences/simplifications:

* 4-player Monopoly.
* Standard 40-square board.
* Properties, railroads, utilities, taxes, Chance/Community Chest, jail.
* They do not fully model special doubles behavior.
* Trading is supported but constrained.

Trade constraints:

* Only unimproved and unmortgaged properties can be traded.
* Players can send trade offers to multiple players.
* If one offer is accepted, other offers involving same property are terminated.
* A player can have only one outstanding trade offer at a time.

They split gameplay into three phases:

1. **Pre-roll**

   * Active player can take actions before rolling.
   * Then concludes actions.

2. **Out-of-turn**

   * Other players may act in round-robin.
   * Handles actions like trades/mortgage/building outside active turn.
   * A preset number of rounds is used, but exact count was not clearly specified in the paper summary.

3. **Post-roll**

   * Active player rolls and moves.
   * If landing on unowned property, decides whether to buy.

This phase system matters because it defines legal actions.

## 8.3 State representation

They use a **240-dimensional vector**.

### Player features: 16 dimensions total

For each of 4 players:

* current location,
* cash,
* in jail flag,
* has get-out-of-jail-free card flag.

### Property features: 224 dimensions total

For 28 ownable properties:

* owner represented by one-hot vector,
* mortgaged flag,
* monopoly flag,
* fraction of houses/hotels built versus allowed.

The paper abstracts some full board complexity into a compact numeric representation.

## 8.4 Action representation

They use a **2922-dimensional action space**.

The action space includes:

* trade offers,
* buy offers,
* sell offers,
* property exchanges,
* build/sell houses/hotels,
* mortgage/unmortgage,
* sell property,
* skip,
* conclude actions,
* jail actions,
* accept trade,
* buy property.

Trade actions dominate the dimensionality.

Important trade encoding:

* exchange actions:

  * 2268 dimensions,
  * player × offered property × requested property.
* buy/sell offers:

  * 252 dimensions each.
* cash amounts are discretized into:

  * 0.75× purchase price,
  * 1.0× purchase price,
  * 1.25× purchase price.

They rely heavily on **action masking** so the RL agent chooses only legal actions from the large vector.

## 8.5 Reward function

They use:

1. Sparse terminal reward:

   * win = +c,
   * loss = –c,
   * with c tuned.

2. Dense in-game reward:

   * based on net worth relative to other players.

The reward formula is roughly:

```text
r_x = nw_x / sum(nw_y for y != x)
```

They compute net worth using cash plus asset values and include a property bonus:

* b = 1.5 if property is not in monopoly,
* b = 2 if property is part of monopoly.

This reward encourages accumulating valuable monopolies.

## 8.6 Agents

They train:

1. **PPO**

   * policy-gradient / actor-critic style.

2. **DDQN**

   * value-based Q-learning style.

3. **Hybrid PPO**

   * PPO plus fixed-policy handling for rare/simple actions.

4. **Hybrid DDQN**

   * DDQN plus fixed-policy handling.

## 8.7 Hybrid split

Their hybrid agent uses fixed policy for:

1. **Buy Property**
2. **Accept Trade Offer**

RL handles everything else.

Fixed buy rule:

* Buy if property completes monopoly and agent can afford it.
* Otherwise buy only if the player has $200 more than the property price.

Fixed accept-trade rule:

* Accept if it increases number of monopolies.
* Otherwise accept if trade net worth is positive.

## 8.8 Fixed-policy opponents

They evaluate against three fixed-policy agents:

* FP-A
* FP-B
* FP-C

All prioritize:

* monopolies,
* trading,
* houses/hotels,
* rent generation.

Differences:

* FP-A:

  * equal property priority.
* FP-B:

  * prioritizes railroads and Boardwalk/Park Place,
  * de-prioritizes utilities.
* FP-C:

  * prioritizes orange or sky-blue group.

These fixed policies are important because the headline results are against these agents, not human players or arbitrary strong agents.

## 8.9 Experiments they did

The experiments were categorized as:

### A. Reward tuning

#### PPO c-sweep

Hybrid PPO trained with:

```text
c ∈ {0, 1, 10, 20, 50, 100}
```

Result:

* c did not matter much for PPO.
* They set c = 0 for PPO.

#### DDQN c-sweep

Same c values for DDQN.

Result:

* c mattered more.
* Best around c = 10.

### B. Standard vs Hybrid training

#### PPO standard vs hybrid

* Train both for 2000 games.
* Compare learning curves.
* Same architecture/hyperparams except hybrid fixed-policy takeover.
* Hybrid PPO converges better.

#### DDQN standard vs hybrid

* Train for 10,000 games.
* Hybrid DDQN improves over standard DDQN.

### C. Representation ablations

They compare:

* their 240-dim state representation,
* Bailis et al. state,
* Arun et al. state.

Mostly shown with DDQN hybrid.

Their representation performs best.

### D. Reward ablations

They compare:

* their reward,
* earlier rewards from prior works.

Their reward performs best.

### E. Final evaluation

Evaluation protocol:

* five iterations of 2000 games,
* 10,000 games total per matchup,
* randomized play order.

Results summarized:

* Standard PPO vs fixed-policy:

  * about 69.95% win rate.
* Hybrid PPO vs fixed-policy:

  * about 91.65% win rate.
* Standard DDQN vs fixed-policy:

  * about 47.41%.
* Hybrid DDQN vs fixed-policy:

  * about 76.91%.
* Hybrid PPO is strongest overall.
* In mixed tables, hybrid agents outperform standard agents.

### F. Memory appendix

They try one-step lookback memory in state.

Result:

* Similar performance,
* slower convergence.

## 8.10 Hyperparameters from the paper

Neural network:

* fully connected feed-forward,
* hidden layers:

  * 1024,
  * 512,
* ReLU,
* output size 2922,
* action masking.

PPO:

* γ = 0.9999,
* λ = 0.95,
* actor lr = 1e-6,
* critic lr = 1e-6,
* batch size = 5,
* memory size = 20.

DDQN:

* γ = 0.9999,
* learning rate = 1e-5,
* batch size = 128,
* replay memory = 1e4,
* target network update every 500 episodes.

---

# 9. PPO and DDQN Explained

The user asked what DDQN and PPO are.

## 9.1 DDQN

DDQN stands for **Double Deep Q-Network**.

It is a value-based reinforcement learning algorithm.

Core idea:

> Learn how good each action is in a state.

It learns:

```text
Q(state, action) = expected future reward
```

Then chooses the action with highest Q-value.

Why “Double”:

* Original DQN overestimates action values.
* DDQN uses one network to select the action and another to evaluate it.
* This improves stability.

In Monopoly paper:

* state = 240-dim vector,
* actions = 2922 possible actions,
* DDQN outputs Q-values over all actions,
* invalid actions are masked.

Weakness in Monopoly:

* huge action space,
* rare actions are hard to learn,
* noisy long-horizon rewards.

## 9.2 PPO

PPO stands for **Proximal Policy Optimization**.

It is policy-based / actor-critic reinforcement learning.

Core idea:

> Learn the probability of choosing each action directly.

It outputs a probability distribution over actions.

It uses:

* actor network:

  * chooses action probabilities.
* critic network:

  * estimates value of state.

Why “proximal”:

* It prevents the policy from changing too much in one update.
* This makes training more stable.

In the paper:

* PPO outputs probabilities over 2922 actions,
* masks illegal actions,
* trains over games,
* hybrid PPO performs best.

## 9.3 Why PPO/DDQN matter for this project

PPO/DDQN are strong at:

* mechanical decisions,
* repeated frequent actions,
* stable policies once trained,
* legal action selection when masked.

They are weak at:

* natural negotiation,
* adapting to new rule variants without retraining,
* explaining decisions,
* flexible trade proposals,
* human-like strategic reasoning.

This motivates an LLM comparison/hybrid research track.

---

# 10. Gap an LLM Agent Can Fill Compared to PPO

This became a central research angle.

## 10.1 The RL agent’s strengths

The Bonjour PPO agent is strong because:

* it learns from many games,
* it has action masking,
* it is optimized for a fixed environment,
* it handles repeated mechanical choices well,
* it has no language-formatting errors.

## 10.2 The RL agent’s limitations

Important limitations:

1. **Legality is solved by masking**

   * The RL agent is not tested on producing valid tool calls.
   * LLMs must generate structured actions correctly.
   * MonopolyBench can test this.

2. **Trade space is discretized**

   * Cash values limited to 0.75×, 1.0×, 1.25×.
   * Property exchanges are fixed-dimensional.
   * No natural language persuasion.

3. **No explanation**

   * PPO selects an action index.
   * It does not produce strategy rationales.

4. **Poor flexibility**

   * Rule variants require retraining or re-engineering.
   * LLMs can adapt via prompt.

5. **Limited opponent modeling**

   * RL trained against fixed policies.
   * LLMs can model named opponents, personalities, prior behavior, and negotiation history.

## 10.3 LLM-shaped opportunity

LLMs may help most in:

* trade proposals,
* trade responses,
* negotiation,
* liquidation planning,
* explaining strategy,
* adapting to scenario variants,
* opponent modeling,
* deception/bluffing studies,
* long-horizon strategy tracking.

The clean research framing:

> The question is not whether LLMs replace PPO entirely. The stronger question is whether LLMs fill the rare, strategic, social, and interpretable decision gaps that PPO-style agents either simplify or avoid.

## 10.4 Hybrid idea

A strong proposed architecture:

* PPO or heuristic policy handles:

  * mechanical decisions,
  * auctions,
  * build/mortgage,
  * jail,
  * routine buy decisions.

* LLM handles:

  * trade proposals,
  * trade responses,
  * liquidation planning,
  * negotiation,
  * strategic explanations.

This directly extends Bonjour’s hybrid insight:

> Their hybrid uses fixed policy for rare actions. MonopolyBench can test whether LLMs are a better rare/complex decision module than fixed policy.

---

# 11. Trevor Bonjour Outreach

Parth suggested contacting Trevor Bonjour.

The user sent an email asking for:

1. environment/ruleset details,
2. fixed-policy opponent configs,
3. exact state/action representations,
4. reward function constants,
5. hybrid decision partition,
6. training/evaluation protocol,
7. code repo/checkpoints/evaluation harness.

The final email text used was:

```text
Hi Trevor — I’m building a reproducible Monopoly multi-agent benchmark focused on deterministic replay + rich artifacts (events/decisions/snapshots), and your hybrid DRL Monopoly paper is the strongest “non-LLM baseline” I’ve found.

Would you be open to sharing any of the following so I can replicate your setup faithfully?

1) Environment/ruleset details (exact Monopoly rules, especially auctions/trades/out-of-turn actions)  
2) Definitions/configs for the fixed-policy opponents used in evaluation  
3) Exact state and action representations (feature list + action encoding)  
4) Reward function (full formula + constants)  
5) The hybrid decision partition (which decisions are DRL vs fixed-policy)  
6) Training/evaluation protocol (seeds, #games, hyperparams, compute)  
7) If possible: code repo, trained checkpoints, or evaluation harness

My goal is to reimplement the same architecture as a baseline in my framework, then measure where LLM agents help (negotiation/trades, adaptability, tool reliability under strict legality constraints) vs PPO-style policies.

If sharing code isn’t possible, even a config/spec doc for state/action/reward + opponent policies would still let me reproduce the core results.

Thanks — happy to credit you prominently and share replication results back.
```

Current status:

* Email sent.
* Waiting on Trevor’s response.

---

# 12. Agentic Benchmark Research

Parth asked to look into other agentic benchmarks.

Sources mentioned:

* Berkeley Function Calling Leaderboard / BFCL:

  * `https://gorilla.cs.berkeley.edu/blogs/15_bfcl_v4_web_search.html`
* Artificial Analysis:

  * `https://artificialanalysis.ai/models`
* AgentBench:

  * `https://arxiv.org/abs/2308.03688`
  * `https://github.com/THUDM/AgentBench`
* Sierra agent benchmark:

  * `https://sierra.ai/blog/benchmarking-agents-in-collaborative-real-world-scenarios`

## 12.1 BFCL / Berkeley Function Calling Leaderboard

Key idea:

> Evaluate tool-use reliability under strict function/tool schemas.

Metrics and concepts to import:

* task success rate,
* function call correctness,
* argument correctness,
* pass^k,
* invalid tool rate,
* schema violation rate,
* category breakdown,
* latency,
* cost,
* model/tool reliability.

Mapping to Monopoly:

* Monopoly decisions are tool calls.
* Legal actions are function schemas.
* Decision types become tool categories.
* Model failure can be measured via:

  * invalid JSON,
  * missing fields,
  * wrong property ID,
  * illegal action,
  * timeout,
  * fallback.

Useful MonopolyBench metrics inspired by BFCL:

* valid-on-first-try rate,
* retry recovery rate,
* fallback rate,
* pass^1 / pass^2,
* error taxonomy by decision type,
* cost per valid decision,
* latency per decision type.

## 12.2 Sierra / τ-bench style collaborative benchmark

Key idea:

> Evaluate agents in realistic interactive, multi-turn environments where success depends on tools, policies, and coordination.

Important concepts:

* solo vs interactive modes,
* multi-turn task success,
* automatic verification through simulator state,
* compositional task generation,
* simulator audits,
* pass^k reliability,
* collaboration quality.

Mapping to Monopoly:

* Monopoly is naturally multi-actor.
* Trade requires another actor’s response.
* Negotiation is interactive.
* Full games are long-horizon multi-step tasks.
* Success is not just one correct tool call but long-term state improvement.

Potential Monopoly metrics:

* trade completion success,
* negotiation rounds to agreement,
* surplus capture,
* repeated interaction adaptation,
* communication clarity,
* opponent-specific offer changes.

## 12.3 AgentBench

Key idea:

> Standardized multi-environment framework for evaluating LLM agents acting in interactive environments.

Important design patterns:

* observe → think → act → environment transition loop,
* task suites,
* standardized scoring,
* reproducible configs,
* multiple environments,
* leaderboard-style aggregation.

Mapping to Monopoly:

* MonopolyBench can define:

  * micro-decision task suites,
  * macro full-game suites,
  * safety/bias suites,
  * negotiation suites.
* Each suite can have:

  * config,
  * scenarios,
  * scoring,
  * artifacts,
  * leaderboard.

## 12.4 Artificial Analysis

Key use:

* Model selection,
* cost/performance context,
* latency and pricing awareness,
* model version tracking.

Mapping to Monopoly:

Use for selecting:

* frontier model track,
* budget model track,
* open-weight/reference model track.

MonopolyBench should report:

* win/score,
* cost,
* latency,
* tokens,
* reliability,
* cost-normalized performance.

## 12.5 Combined insight from agentic benchmarks

MonopolyBench should evaluate three axes:

1. **Reliability under strict interfaces**

   * inspired by BFCL.

2. **Long-horizon multi-turn task completion**

   * inspired by AgentBench and τ-bench.

3. **Coordination / negotiation / collaborative failure**

   * inspired by Sierra-style interactive tasks.

This became a strong framing:

> MonopolyBench combines strategic multi-agent gameplay, strict legality contracts, and negotiation, with deterministic replay artifacts behind every claim.

---

# 13. Fifth Meeting with Parth: New Research Instructions

The fifth meeting introduced further research asks.

Parth takeaways:

```text
- Research into board game psychology and game enthusiasts
  - do people employ some specific personality/mentality?
  - can we replicate that?
  - LLM is dominating? or the specific personality is dominating? (1v1)

- Configs for how many players playing and others

- Full Run!!!!!!!
```

The user also wanted deep research into:

* board game psychology,
* player personalities,
* Monopoly strategies,
* game enthusiast mentalities,
* long-horizon planning,
* prompt testing,
* tool calling,
* negotiation/deception/bluffing,
* memory management,
* risk management,
* pro Monopoly strategies,
* business simulation feasibility.

A deep research task was initiated around this broad fifth-meeting prompt. No full final research report from that tool was included in the conversation before the latest update, but it established the intended expansion areas.

Important outstanding research thread:

> Board game psychology and player archetypes could become prompt/personality configurations: aggressive, conservative, negotiator, monopolist, risk-averse, shark, colluder, spiteful/kingmaker, etc. A key experiment is whether the LLM model dominates outcomes, or whether the prompted personality dominates outcomes in controlled matchups.

---

# 14. Business Simulation / CRE Extension

The user raised a future possibility:

> Can this go beyond Monopoly into a realistic business simulation?

Possible idea:

* Agents operate in a simulated business/economic world.
* Could involve:

  * real estate underwriting,
  * leverage,
  * tenants,
  * rent rolls,
  * refinancing,
  * market cycles,
  * exits,
  * investor reporting,
  * fund management,
  * capital allocation,
  * acquisitions/dispositions.

This became Direction 2:

> **Real Estate / Asset Management Benchmark**

The current advice in the conversation:

* This is valuable and potentially compelling.
* It should remain future scope for now.
* It should not distract from Monday or first paper.
* It is likely a follow-on paper/platform extension after MonopolyBench is established.

Feasibility considerations mentioned:

* API cost could be higher.
* Need realistic but controlled scenarios.
* Harder to validate than Monopoly because “correct” business decisions are less objective.
* Could use the same architecture:

  * contracts,
  * legal actions,
  * state snapshots,
  * events,
  * telemetry,
  * scenarios,
  * agent prompts,
  * cost/reasoning metrics.
* Would need domain-specific evaluators:

  * NPV,
  * IRR,
  * DSCR,
  * leverage risk,
  * cash flow,
  * tenant default risk,
  * refinance risk,
  * market downturn resilience.

Current recommendation:

* Keep business simulation as Direction 2 / future track.
* Do not expand into it before first MonopolyBench research pilot.

---

# 15. Latest Discord / Mentor Update

The user provided the latest Discord thread with Parth.

## 15.1 Timeline

Parth asked for updates:

```text
Parth — 6/2/2026 3:06 PM
Hi @Kush are you there?
Any updates on the project?
```

User replied later, apologizing for missed Discord notifications:

```text
hey parth! so sorry, i just saw these messages
i have notifications disabled for discord so just didn’t see them (turning them on now though)
but yea as you can see i have been working on it throughout
```

User shared screenshots and explained the four research directions are solidified and linked:

```text
research_direction.md
https://github.com/KushagraBharti/MonopolyBench/blob/main/research_direction.md
```

User told Parth:

* research directions are now solidified,
* directions 1 and 2 are up and running,
* tests were done on two models:

  * `gpt-5.4-mini`
  * `claude-haiku-4.5`
* missing:

  1. cost analysis,
  2. reasoning/effort level support, especially Anthropic abstraction.

User planned to implement those and rerun experiments.

User asked Parth for help reviewing results and identifying interesting paper framing.

Parth replied positively:

```text
Good that you’re making progress! The directions are looking good too.
Sure, we can discuss how to frame the experiments for a paper.
I was thinking we should target some AAAI workshop so that we have a deadline to work towards.
Lets meet on Monday to catchup.
Are you interning somewhere in the summer?
```

User replied:

* will get cost analysis and reasoning effort implemented,
* will rerun experiments,
* will look for AAAI deadlines,
* Monday availability before 5 PM,
* working at UT Southwestern technically.

Parth set meeting:

```text
Monday 11:30 AM
```

## 15.2 Four research directions sent to Parth

The user’s four directions:

### 1. Long-Horizon Monopoly Agency

Question:

> Can LLMs play a full economic game coherently, or do they drift, mismanage cash, trade badly, and collapse over time?

### 2. Real Estate / Asset Management Benchmark

Extend same architecture to realistic CRE/fund management:

* underwriting,
* leverage,
* tenants,
* market cycles,
* exits,
* investor reporting.

### 3. Targeted Scenario Suite

Isolate noisy full-game behavior into clean probes:

* tactical choices,
* biases,
* deception,
* collusion,
* negotiation,
* safety failures.

### 4. Control / Orchestration / Information Design

Test the system around the model:

* prompts,
* memory,
* summaries,
* guardrails,
* orchestrators,
* performance and safety improvements.

## 15.3 Current strategic read from latest analysis

The latest readiness analysis said:

> The near-term paper should stay focused on Direction 1 and Direction 3.

Directions 2 and 4 are future tracks.

Clean paper framing:

> **MonopolyBench is a reproducible benchmark for long-horizon economic agency, negotiation, and safety in multi-agent LLM systems.**

---

# 16. Current Repo / Implementation Status from Latest Update

The latest analysis said the repo is farther along than a demo.

## 16.1 Implemented / verified surfaces

### Long-horizon campaign registry/config

Files:

* `contracts/research/monopoly_long_v1_model_rosters.json`
* `campaigns/monopoly-long-v1-smoke.json`

### Micro research overlays

File:

* `docs/micro_research_suites.md`

### OpenRouter reasoning support

Files:

* `openrouter_client.py`
* `player_config.py`

Reasoning support includes:

```json
"reasoning": {
  "effort": "low" | "medium" | "high"
}
```

### Cost/usage artifact support

File:

* `usage.py`

Cost accounting is implemented from OpenRouter actuals, including:

* cost,
* cached tokens,
* reasoning tokens when returned.

## 16.2 Important gaps

### Gap 1: Unsafe default player config

File:

* `players.json`

Problem:

* Uses aliases like:

  * `openai/gpt-latest`
  * `anthropic/claude-opus-latest`
* Prior run showed these caused OpenRouter HTTP 400 failures.
* Do not run publication experiments from this config.

Resolution:

* Use exact current model IDs.
* Create clean experiment configs separate from default API config.

### Gap 2: Long smoke campaign artifacts missing

`monopoly-long-v1-smoke` looks like planning/config only.

Missing execution artifacts:

* `leaderboard.json`
* `statistics.json`
* `execution_result.json`

### Gap 3: Recent full-game runs are raw partial runs

Recent June 5 runs:

* contain valid OpenRouter calls,
* include costs,
* but lack:

  * `usage.json`,
  * `scorecard.json`,
  * campaign packaging,
  * `GAME_ENDED`.

They should not be treated as benchmark results.

### Gap 4: Strongest complete micro result so far

For:

* `openai/gpt-oss-120b`

On:

* all 130 `micro-v1` scenarios.

Metrics:

* average score: `0.701919`
* retry rate: `0.061538`
* fallback rate: `0.0`

Strong categories:

* `BUY_OR_AUCTION`
* `JAIL`

Weak categories:

* `TRADE_RESPONSE`
* `LIQUIDATION`

This suggests a likely early research finding:

> Models handle common tactical/property decisions better than complex negotiation/liquidation decisions.

## 16.3 Current model facts from latest analysis

Useful valid model IDs listed:

* `openai/gpt-5.4-mini`
* `anthropic/claude-haiku-4.5`
* `openai/gpt-5.2`
* `anthropic/claude-sonnet-4.5`
* `openai/gpt-oss-120b`

OpenRouter notes from latest analysis:

* `reasoning` supports `effort`.
* Reasoning tokens count as output cost.
* Anthropic can use direct `reasoning.max_tokens`, possibly cleaner than abstract effort.
* Official OpenRouter docs referenced:

  * reasoning token docs,
  * parameters docs,
  * models API.

Important caveat:

* These model IDs and API details should be rechecked immediately before running publication experiments because model availability and routing can change.

## 16.4 AAAI deadline facts from latest analysis

Latest pasted analysis said:

* AAAI-27 main-track deadlines posted:

  * abstracts due July 21, 2026,
  * full papers due July 28, 2026.
* AAAI-26 workshop deadlines are past.
* AAAI-27 workshop CFPs do not appear posted yet.

Official pages referenced:

* AAAI-27 page,
* AAAI-26 workshops call.

Important caveat:

* Recheck official AAAI dates before committing a submission strategy.

---

# 17. Current Execution Plan for Monday, June 8

The latest plan for Monday’s 11:30 AM meeting with Parth:

## 17.1 Paper scope decision

Proposed scope:

> **MonopolyBench: Long-Horizon Economic Agency and Tactical Failures in Legal-Action-Constrained LLM Agents**

Stay focused on:

* Direction 1: long-horizon Monopoly agency.
* Direction 3: targeted micro-decisions/bias/safety probes.

Avoid expanding into:

* Direction 2 business simulation,
* Direction 4 orchestration/information design,

until after first clean pilot/paper framing.

## 17.2 Model selection

Start with:

* `openai/gpt-5.4-mini`
* `anthropic/claude-haiku-4.5`

Potential optional baseline/reference:

* `openai/gpt-oss-120b`

Use:

* exact model IDs,
* same prompt,
* same reasoning policy,
* same temperature,
* same scenario set,
* cost accounting.

## 17.3 Micro-suite pilot

Run:

* 130-scenario `micro-v1`
* both models
* reasoning effort low first
* generate joined:

  * bias-v1 reports,
  * safety-v1 reports,
  * category breakdowns,
  * scorecards,
  * cost tables.

Then repeat with `medium` only if cost acceptable.

## 17.4 Long-horizon smoke

Run:

* one or two fixed seeds,
* Latin-square seats if possible,
* capped max_turns,
* exact model IDs,
* artifact generation enabled.

Important framing:

* If no `GAME_ENDED`, call it bounded-horizon evaluation.
* Do not overclaim full-game dominance.

## 17.5 Artifacts to bring Parth

Bring:

* micro leaderboard,
* category breakdown,
* 5–10 representative failure cases,
* cost/token table,
* replay/validity/fallback table,
* short list of claims that can and cannot be made yet,
* one bounded full-game smoke artifact,
* model configs/manifests.

---

# 18. Concrete Engineering Step Identified

Before spending more money:

1. Update or create clean experiment config using exact model IDs.
2. Do not use default `players.json` for publication runs until unsafe aliases are replaced or isolated.
3. Run tiny 2–3 scenario dry run.
4. Confirm:

   * model calls succeed,
   * reasoning config accepted,
   * usage/cost fields appear,
   * scorecards generated,
   * no HTTP 400 alias failures,
   * no fallbacks due to config mismatch.
5. Then run full 130-scenario micro suite.

---

# 19. Paper Framing Established in the Latest Assistant Response

The latest response reframed the current state as:

> The project has moved from “can this work?” to “can we package clean evidence by Monday?”

The main risk:

> Messy experiment execution, not implementation.

Risk factors:

* wrong model aliases,
* partial full-game runs,
* missing campaign artifacts,
* unclear claims.

## 19.1 Recommended thesis

> **MonopolyBench is a reproducible testbed for long-horizon economic agency, negotiation, tactical failure, and safety behavior in legal-action-constrained LLM agents.**

## 19.2 More precise first-paper framing

> **LLMs can be evaluated as long-horizon economic agents through Monopoly, with targeted micro-scenarios exposing specific tactical, bias, negotiation, and safety failures that full games alone obscure.**

## 19.3 Contribution list

Possible first paper contributions:

1. Deterministic Monopoly-based benchmark environment.
2. Replayable artifacts:

   * events,
   * decisions,
   * actions,
   * prompts,
   * costs.
3. Micro-decision scenario suite.
4. Initial model comparison across matched reasoning/cost settings.
5. Failure taxonomy:

   * invalid actions,
   * retries,
   * fallbacks,
   * bad trades,
   * poor liquidation,
   * cash mismanagement.
6. Cost/reasoning analysis.

---

# 20. Likely Questions from Parth and Prepared Answers

## 20.1 What is the core scientific question?

Prepared answer:

> Can LLM agents maintain coherent long-horizon economic strategy under a strict legal-action interface, and where do their tactical, negotiation, and safety failures emerge?

## 20.2 Why Monopoly?

Prepared answer:

> Monopoly combines stochasticity, resource management, negotiation, auctions, liquidation, and long-horizon planning in one controlled environment. It is simple enough to instrument fully, but complex enough to expose agent failures that static benchmarks miss.

## 20.3 Why not just full-game win rate?

Prepared answer:

> Full-game win rate is noisy and expensive. The micro-decision suite isolates specific skills and produces clearer, cheaper, more statistically interpretable signals. Full games are still useful as ecological validation.

## 20.4 What is the first result?

Prepared answer:

> Early micro-v1 results already show category-level differences: models perform relatively well on buy/jail decisions but struggle on trade response and liquidation. The next run will compare exact model IDs with matched reasoning settings and cost accounting.

## 20.5 What is missing before a paper?

Prepared answer:

> Clean runs, campaign packaging, a consistent model set, cost/reasoning analysis, representative qualitative failures, and a tight statistical summary.

---

# 21. Strong Claims vs Unsafe Claims

## 21.1 Safe claims right now

Safe:

* The system supports deterministic/replayable Monopoly LLM runs.
* The micro suite exposes category-specific decision behavior.
* Early complete micro results show stronger performance on buy/jail than trade/liquidation for at least one model.
* Cost/reasoning infrastructure is important and now apparently wired.
* Full games are expensive/noisy and should be complemented by micro probes.

## 21.2 Unsafe claims right now

Avoid:

* “Model A is better at Monopoly than Model B.”
* “LLMs are better than PPO at Monopoly.”
* “MonopolyBench proves general intelligence.”
* “Full-game win rate conclusions” from partial/no-`GAME_ENDED` runs.
* “AAAI workshop deadline” unless specific CFP exists.
* Any claim based on unsafe alias model configs.
* Any claim without exact model/version and run manifest.

## 21.3 Strong near-term claim after clean micro runs

Potential:

> Under matched legal-action-constrained prompts, models differ systematically across Monopoly decision categories, with complex trade/liquidation scenarios producing more tactical failures than simpler buy/jail decisions, and reasoning/cost settings exposing a quality-efficiency tradeoff.

---

# 22. Micro-Decision Suite: Recommended Detailed Shape

The micro-suite has become one of the most important research assets.

## 22.1 Why micro-scenarios matter

Full games are:

* noisy,
* expensive,
* stochastic,
* long,
* hard to interpret,
* difficult to sample enough for statistical confidence.

Micro-scenarios are:

* targeted,
* cheaper,
* interpretable,
* repeatable,
* easier to score,
* useful for paper plots.

## 22.2 Core micro decision categories

### BUY_OR_AUCTION

Measures:

* property value judgment,
* liquidity preservation,
* monopoly pursuit,
* early-game acquisition logic.

Possible metrics:

* buy when completing monopoly,
* avoid buying when cash buffer dangerously low,
* compare to heuristic buy policy.

### AUCTION_BID

Measures:

* bidding rationality,
* overbidding,
* underbidding,
* budget management,
* monopoly-completion value.

Possible metrics:

* bid relative to property price,
* bid relative to cash,
* bid relative to monopoly potential,
* regret vs heuristic fair value.

### TRADE_RESPONSE

Measures:

* surplus evaluation,
* fairness,
* opponent modeling,
* willingness to trade,
* avoiding bad monopoly giveaways.

Possible metrics:

* accept/reject correctness,
* net value delta,
* monopoly delta,
* fairness ratio,
* exploitability.

This has already appeared as a weak category for `gpt-oss-120b`.

### TRADE_PROPOSE

Measures:

* ability to construct beneficial trades,
* negotiation creativity,
* surplus capture,
* monopoly-completion planning.

Possible metrics:

* trade plausibility,
* expected acceptance,
* own EV gain,
* opponent EV gain,
* fairness vs exploitation.

### BUILD / MORTGAGE

Measures:

* investment timing,
* housing strategy,
* liquidity discipline,
* risk of overbuilding,
* monopoly exploitation.

Possible metrics:

* build-to-3-houses speed,
* cash buffer after building,
* mortgage choice quality,
* rent ROI.

### LIQUIDATION

Measures:

* forced cash management,
* minimizing long-term damage,
* sequencing assets,
* avoiding collapse.

This has also appeared as a weak category.

Possible metrics:

* required cash raised,
* asset value destroyed,
* monopoly preservation,
* avoid unnecessary liquidation,
* long-term net worth loss.

### JAIL

Measures:

* early vs late game strategy,
* danger-zone awareness,
* board-state reasoning.

Possible metrics:

* leave jail early game,
* stay in jail late game when board dangerous,
* use/pay/roll decision quality.

This appeared as a strong category for `gpt-oss-120b`.

### BIAS / SAFETY / COLLUSION / DECEPTION PROBES

Measures:

* whether model treats named/personality-coded opponents differently,
* whether model engages in deceptive messaging,
* whether model colludes,
* whether model sacrifices self-interest irrationally,
* whether guardrails change strategy.

---

# 23. Full-Game / Long-Horizon Suite

## 23.1 Purpose

The full-game suite answers:

> Can LLMs sustain coherent economic agency over many turns?

It should measure:

* drift,
* collapse,
* liquidity mismanagement,
* bad trading,
* strategy inconsistency,
* accumulated tactical failures,
* survival,
* net worth trajectories.

## 23.2 Current caution

Recent full-game runs were partial and did not emit `GAME_ENDED`.

Therefore, the immediate long-horizon work should be framed as:

* bounded-horizon smoke,
* pipeline validation,
* artifact generation,
* trajectory/failure inspection,

not final win-rate benchmark.

## 23.3 Full run requirements

For serious full-run claims:

* exact model IDs,
* fixed seeds,
* seat rotation,
* max_turns,
* cost limits,
* run manifests,
* usage files,
* campaign packaging,
* replay verification,
* GAME_ENDED or explicit bounded-horizon termination.

---

# 24. Cost and Reasoning Effort

This became a major missing piece and then an implemented support area.

## 24.1 Why cost matters

For research:

* Full games are expensive.
* Reasoning models can produce extra tokens.
* Model comparison must include practical cost.
* A cheaper model might be more useful if near-equal quality.

Metrics needed:

* cost per scenario,
* cost per decision,
* cost per full game,
* cost per valid decision,
* tokens per decision,
* reasoning tokens,
* cached tokens,
* output tokens,
* input tokens,
* latency.

## 24.2 Why reasoning effort matters

Research question:

> Does higher reasoning effort improve Monopoly decision quality, and is the improvement worth the cost?

Important for:

* OpenAI-style reasoning effort,
* Anthropic token-budget differences,
* cost-quality tradeoffs,
* prompt/orchestrator studies.

## 24.3 Current implementation

Latest status says:

* cost accounting implemented from OpenRouter actuals,
* reasoning tokens captured when returned,
* reasoning effort wired through:

  * low,
  * medium,
  * high.

Need verify in runs.

---

# 25. Board Game Psychology / Personality Track

This was introduced in the fifth meeting and is now an important possible research direction.

## 25.1 Core question

> Do board game players employ specific personalities or mentalities, and can LLMs replicate them?

Related Parth question:

> Is the LLM dominating, or is the specific personality dominating?

This suggests a controlled experiment:

* same model,
* different strategy/personality prompts,
* 1v1 or controlled 4-player setups,
* compare outcomes.

## 25.2 Possible Monopoly player archetypes

Potential prompted personalities:

1. **Aggressive monopolist**

   * buys aggressively,
   * trades to complete sets,
   * builds fast,
   * tolerates low cash.

2. **Conservative banker**

   * preserves liquidity,
   * avoids risky trades,
   * builds slowly,
   * prioritizes survival.

3. **Negotiator / dealmaker**

   * proposes many trades,
   * seeks mutually beneficial deals,
   * uses persuasion.

4. **Predatory trader**

   * tries to exploit opponents,
   * anchors unfairly,
   * targets weak liquidity players.

5. **Risk-neutral EV maximizer**

   * follows expected value heuristics.

6. **Risk-averse survivalist**

   * avoids bankruptcy above all.

7. **Kingmaker / spiteful actor**

   * may harm self to affect others.
   * useful for safety/failure detection, not necessarily benchmark baseline.

8. **Collusive/cooperative actor**

   * tests collusion/deception/safety.

9. **Pro-strategy player**

   * follows known Monopoly heuristics.

10. **Entertainer/chatty player**

* tests whether public messaging affects performance or distracts strategy.

## 25.3 Personality vs model experiment

Basic design:

* Select one model.
* Run same micro/full scenarios with different personality prompts.
* Compare:

  * score,
  * trade frequency,
  * risk exposure,
  * invalid actions,
  * cost,
  * long-horizon survival.

Then:

* Select multiple models.
* Use same personality prompts.
* Compare whether:

  * model identity explains more variance,
  * personality prompt explains more variance,
  * interaction matters.

Potential statistical framing:

* two-way ANOVA style:

  * model,
  * personality,
  * model × personality interaction.

## 25.4 Why this is promising

It connects:

* board-game psychology,
* prompting,
* strategy personalities,
* model behavior,
* safety/persona concerns,
* reproducible agent evaluation.

It also gives a more original research angle than pure leaderboard results.

---

# 26. Pro Monopoly Strategy Track

The conversation identified known strong Monopoly heuristics.

## 26.1 Common pro/enthusiast strategies

Strategies to operationalize:

* buy aggressively early,
* prioritize completing monopolies,
* orange/red groups are valuable,
* railroads are strong early/steady income,
* utilities are less valuable,
* build houses quickly,
* three houses is often a key rent jump,
* maintain enough liquidity,
* mortgage strategically but not destructively,
* stay in jail late game when board is dangerous,
* leave jail early game to acquire property,
* trade only if it improves monopoly prospects or net position,
* avoid giving opponents dangerous monopolies,
* use housing scarcity strategically.

## 26.2 How to measure adherence

Metrics:

* color-group preference index,
* railroad acquisition rate,
* utility avoidance/preference,
* monopoly completion rate,
* time-to-first-house after monopoly,
* time-to-three-houses,
* cash buffer after builds,
* jail decision by game phase,
* trade-to-monopoly rate,
* bad-trade rate,
* mortgage damage score.

## 26.3 Prompt intervention

Test:

* no strategy prompt,
* pro strategy cheatsheet,
* specific personality strategy,
* EV-maximizer prompt,
* conservative prompt.

Then ask:

* Does the model behave closer to pro heuristics?
* Does score improve?
* Does reasoning mention strategy but actions fail to follow?
* Does cost increase?

---

# 27. Negotiation, Deception, Bluffing Track

## 27.1 Why Monopoly is ideal

Monopoly includes:

* structured trades,
* private incentives,
* public messages,
* repeated interactions,
* asymmetric positions,
* bargaining,
* possible deception.

## 27.2 Key research questions

* Do LLMs bluff in public messages?
* Do they misrepresent trade value?
* Do private thoughts reveal different intent than public messages?
* Do models adapt offers to opponents?
* Does opponent identity influence offers?
* Do models collude or kingmake?
* Does deception improve trade surplus or harm long-term survival?

## 27.3 Possible metrics

* trade acceptance rate,
* surplus capture,
* fairness ratio,
* offer improvement after rejection,
* identity-conditioned offer differences,
* deception markers,
* public/private contradiction score,
* collusion graph,
* kingmaking events,
* value transferred to non-self players.

## 27.4 Safety framing

This can be framed as:

> MonopolyBench reveals safety-relevant strategic behavior in constrained multi-agent settings, including deception, collusion, and self-other value misalignment.

Need avoid overclaiming “true deception.” Better phrasing:

* deceptive signals,
* apparent bluffing behavior,
* inconsistency between public messages and private intent,
* negotiation strategies that reduce opponent welfare.

---

# 28. Control / Orchestration / Information Design

This is Direction 4, currently future scope.

Core idea:

> The model is not the whole agent. The system around it—prompting, memory, summaries, legal-action design, retry/fallback, guardrails—strongly affects performance.

Possible variables:

* memory length,
* summary quality,
* full state vs compact state,
* public chat visibility,
* private thoughts visibility,
* opponent identity hidden/revealed,
* legal action formatting,
* retry messages,
* reasoning effort,
* strategy cheatsheets,
* guardrails against deception/collusion.

Possible metrics:

* performance,
* reliability,
* cost,
* safety,
* negotiation quality,
* long-horizon coherence.

This could become a later paper:

> How orchestration and information design change LLM economic-agent behavior.

For first paper, only include if needed as a small ablation.

---

# 29. Suggested Monday Deliverable Package

Before meeting Parth, prepare a concise artifact package.

## 29.1 Folder contents

Recommended folder:

```text
monday_parth_2026_06_08/
  README.md
  configs/
    micro_v1_gpt54mini_low.json
    micro_v1_claudehaiku45_low.json
    long_smoke_seedXXXX.json
  results/
    micro_leaderboard.json
    micro_statistics.json
    micro_usage.json
    micro_scorecards/
    category_breakdown.csv
    cost_summary.csv
    reliability_summary.csv
  failures/
    01_bad_trade_response.md
    02_bad_liquidation.md
    03_good_jail_decision.md
    ...
  full_smoke/
    events.jsonl
    decisions.jsonl
    actions.jsonl
    usage.json
    summary.json
    scorecard.json
  notes/
    claims_we_can_make.md
    claims_we_cannot_make.md
    paper_outline.md
```

## 29.2 One-page summary for Parth

Should include:

* thesis,
* models tested,
* scenario suite,
* cost,
* headline scores,
* category strengths/weaknesses,
* reliability stats,
* example failures,
* next experiment plan,
* submission target.

---

# 30. Immediate To-Do List

## 30.1 Before running experiments

* Replace/avoid unsafe aliases.
* Create exact model config.
* Confirm OpenRouter accepts model IDs.
* Confirm reasoning config accepted.
* Confirm cost fields returned.
* Confirm `usage.json` generated.
* Confirm scorecards generated.
* Confirm no campaign packaging gap.

## 30.2 Micro suite

Run:

* `micro-v1`,
* all 130 scenarios,
* `gpt-5.4-mini`,
* `claude-haiku-4.5`,
* reasoning low,
* same prompt/settings.

Collect:

* average score,
* per-category score,
* retry rate,
* fallback rate,
* cost,
* latency,
* representative examples.

## 30.3 Optional second pass

Only if cost acceptable:

* reasoning medium for same models.

Compare:

* quality delta,
* cost delta,
* reliability delta.

## 30.4 Long smoke

Run:

* one or two bounded full-game seeds,
* exact model IDs,
* capped max_turns,
* artifact generation.

Goal:

* prove full-run pipeline,
* not claim final win rate.

## 30.5 Analysis

Prepare:

* failure taxonomy,
* claim list,
* charts/tables,
* paper framing.

---

# 31. Current Best Paper Direction

The best near-term paper is not “Monopoly as a product.” It is:

> **MonopolyBench: Evaluating Long-Horizon Economic Agency and Tactical Failure Modes in Legal-Action-Constrained LLM Agents**

## 31.1 Core contributions

1. A deterministic Monopoly benchmark with strict legal-action constraints.
2. A micro-decision suite for targeted tactical and safety probes.
3. Initial model comparison across exact model IDs.
4. Cost/reasoning/reliability analysis.
5. Failure taxonomy and qualitative examples.
6. Bounded long-horizon smoke evidence.

## 31.2 Why this is strong

It is:

* implementable now,
* grounded in existing repo,
* aligned with Parth’s guidance,
* connected to agentic benchmark literature,
* not overly dependent on huge full-game sample sizes,
* publishable if results are clean.

## 31.3 Why not business simulation first

Business simulation is interesting but:

* harder to validate,
* broader,
* more expensive,
* less mature,
* could dilute the first paper.

It should remain the next platform expansion, not Monday’s focus.

---

# 32. Open Questions / Outstanding Items

## 32.1 Trevor Bonjour response

Waiting.

Potential outcomes:

* He shares code/checkpoints/configs.
* He shares enough specs to reproduce.
* He does not respond.

If no response:

* implement approximate baseline from paper.
* clearly label it as “paper-inspired fixed/RL baseline,” not exact replication.

## 32.2 Exact AAAI target

Need decide:

* AAAI-27 main track,
* AAAI-27 workshop once CFPs appear,
* alternative venue/workshop.

Need verify current deadlines directly before committing.

## 32.3 Model availability and IDs

Need recheck OpenRouter right before experiment runs.

Avoid:

* `latest` aliases,
* unstable provider routes,
* unpublished model names in paper without exact versions.

## 32.4 Full-game termination

Need resolve:

* why recent full runs did not emit `GAME_ENDED`,
* whether max_turn cap creates summary cleanly,
* whether bounded-horizon scoring is sufficient.

## 32.5 Campaign packaging

Need confirm:

* `leaderboard.json`,
* `statistics.json`,
* `execution_result.json`,
* `usage.json`,
* `scorecard.json`

are generated for actual campaign runs.

---

# 33. Important Files / Artifacts Mentioned Across Conversation

## Repository

* `research_direction.md`
* `implementation_status.md`
* `contracts/research/monopoly_long_v1_model_rosters.json`
* `campaigns/monopoly-long-v1-smoke.json`
* `docs/micro_research_suites.md`
* `python/packages/arena/src/monopoly_arena/openrouter_client.py`
* `python/packages/arena/src/monopoly_arena/player_config.py`
* `python/packages/telemetry/src/monopoly_telemetry/usage.py`
* `python/apps/api/src/monopoly_api/config/players.json`

## Paper PDF

* `/mnt/data/Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach.pdf`

## External research links collected

### Monopoly literature

* `https://arxiv.org/abs/2103.00683`
* `https://doc.gold.ac.uk/aisb50/AISB50-S02/AISB50-S2-Bailis-paper.pdf`
* `https://arxiv.org/html/2508.03368v1`
* `https://aclanthology.org/2025.acl-long.378.pdf`
* `https://proceedings.neurips.cc/paper_files/paper/2024/file/3191170938b6102e5c203b036b7c16dd-Paper-Conference.pdf`
* `https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8929523`
* `https://web.mit.edu/sp.268/www/probability_and_monopoly.pdf`
* `https://pi4math.web.illinois.edu/wp-content/uploads/2014/10/Gartland-Burson-Ferguson-Markovopoly.pdf`

### Existing agents/bots

* `https://github.com/williamhbell/MonopolySimulation`
* `https://github.com/vlokwani/Monopoly-bot`
* `https://github.com/jonzia/Monopoly`
* `https://www.youtube.com/watch?v=dkvFcYBznPI`
* `https://github.com/b2developer/MonopolyNEAT`

### Agentic benchmarks

* `https://gorilla.cs.berkeley.edu/blogs/15_bfcl_v4_web_search.html`
* `https://artificialanalysis.ai/models`
* `https://arxiv.org/abs/2308.03688`
* `https://github.com/THUDM/AgentBench`
* `https://sierra.ai/blog/benchmarking-agents-in-collaborative-real-world-scenarios`

### OpenRouter / AAAI links from latest status

* `https://openrouter.ai/docs/guides/best-practices/reasoning-tokens`
* `https://openrouter.ai/docs/api/reference/parameters`
* `https://openrouter.ai/api/v1/models`
* `https://aaai.org/conference/aaai/aaai-27/`
* `https://aaai.org/conference/aaai/aaai-26/workshops-call/`

---

# 34. The Core Intellectual Arc of the Conversation

The entire conversation can be summarized as the transformation of the project through four stages.

## Stage 1: Engineering maturity

The project went from loose demo to reliable, deterministic, inspectable engine.

Focus:

* engine,
* arena,
* UI,
* telemetry,
* contracts,
* tests,
* runtime controls.

## Stage 2: Benchmark platform vision

The project became MonopolyBench:

* long-horizon benchmark,
* micro/macro suites,
* reproducibility,
* leaderboard,
* ratings,
* cost,
* replay.

## Stage 3: Research positioning

The project was situated in:

* Monopoly RL literature,
* board game LLM benchmarks,
* agentic tool-use benchmarks,
* negotiation/safety research,
* pro Monopoly strategy,
* long-horizon planning.

## Stage 4: Paper execution

The current stage is:

* run clean experiments,
* package results,
* focus scope,
* prepare for Monday with Parth,
* target AAAI-style venue.

---

# 35. Final Current Handoff State

The next person/agent picking this up should assume:

1. The codebase is largely implemented.
2. The product roadmap is known.
3. The research directions are known.
4. The mentor wants concrete results.
5. The near-term paper should focus on Direction 1 + Direction 3.
6. The immediate blocker is clean experiment hygiene, not architecture.
7. Do not run publication experiments from unsafe alias configs.
8. The next deliverable is a publication-safe pilot by Monday.

## The precise immediate mission

Produce, before Monday:

* clean `micro-v1` results for:

  * `openai/gpt-5.4-mini`
  * `anthropic/claude-haiku-4.5`
* with:

  * exact configs,
  * cost accounting,
  * reasoning effort,
  * scorecards,
  * category breakdown,
  * retry/fallback reliability,
  * representative failures.
* plus one bounded full-game smoke run with artifacts.

## The precise paper story to bring Parth

> MonopolyBench evaluates LLMs as long-horizon economic agents under strict legal-action constraints. Full Monopoly games reveal accumulated strategic drift and economic collapse, while targeted micro-scenarios isolate tactical, negotiation, liquidation, bias, and safety failures. Early results suggest models differ strongly by decision category, with simple tactical choices easier than trade/liquidation decisions. The benchmark records deterministic, replayable artifacts and cost/reasoning data, enabling reproducible comparison across models and prompting/orchestration settings.

That is the current handoff state.