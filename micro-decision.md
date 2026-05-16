# MonopolyBench Micro-Decision Suite

This document is the implementation blueprint for the full MonopolyBench micro-decision suite.

The micro-decision suite should be treated as a separate benchmark layer on top of the existing MonopolyBench protocol. It consumes frozen `DecisionPoint` fixtures, runs one or more agents against those fixtures through the same legal-action resolver used by full games, scores the resulting action, and writes replayable artifacts.

It must not become part of the normal live-game engine loop.

---

## Core Thesis

Full Monopoly games are noisy. Important strategic moments are sparse, and outcomes depend on long chains of dice rolls, prior negotiations, and earlier mistakes.

The micro-decision suite solves this by creating curated, reproducible decision states:

- the same board state,
- the same active player,
- the same legal action set,
- the same prompt structure,
- the same scoring rubric,
- and the same artifact format,

so models can be compared on the exact tactical and strategic moments we care about.

The suite should answer questions like:

- Does the model buy a property that completes a monopoly even under cash pressure?
- Does it overbid in auctions because it notices monopoly potential but ignores liquidity?
- Does it understand late-game jail as protection?
- Can it structure a trade that creates value without giving away the game?
- Does a pro-strategy cheatsheet improve decisions or cause brittle over-application of heuristics?
- Do stronger general-purpose models actually make better Monopoly decisions?
- Do public messages and private thoughts diverge during negotiation?

---

## Non-Negotiable Design Rules

1. **Micro mode is benchmark-only**
   - It evaluates one decision at a time.
   - It does not advance a full game.
   - It does not replace or alter normal engine progression.

2. **Frozen `DecisionPoint` fixtures are the unit of evaluation**
   - A micro scenario stores a complete protocol-valid `DecisionPoint`.
   - Runtime code loads and validates the fixture; it should not rebuild the scenario from ad hoc Python state unless explicitly regenerating fixtures.

3. **Engine remains authoritative**
   - Scenario fixtures must match the same protocol objects the engine emits.
   - The micro runner must not invent legal actions.
   - The micro runner must not implement Monopoly rules beyond scenario scoring and validation.

4. **Arena behavior must be reused**
   - Micro runs should use the same shared decision resolver as full games.
   - Same OpenRouter-only gateway.
   - Same exact-one-tool-call requirement.
   - Same retry/fallback policy.
   - Same prompt artifact writing.

5. **Micro artifacts are isolated**
   - Full-game artifacts stay under `runs/<run_id>/`.
   - Micro single-run artifacts go under `runs/micro/<run_id>/`.
   - Micro batch artifacts go under `runs/micro_batches/<batch_id>/`.

6. **Scoring is explicit, versioned, and inspectable**
   - Every scenario must include an evaluation definition.
   - A scenario without scoring metadata is a demo fixture, not a benchmark scenario.

7. **UI is render-only**
   - The frontend displays frozen snapshots, legal actions, run results, and score breakdowns.
   - It must not infer legal moves or Monopoly rules.

---

## Recommended Repository Layout

Keep the suite separate while reusing existing protocol, arena, and telemetry packages.

```text
contracts/
  schemas/
    micro_scenario.schema.json
    micro_suite.schema.json
    micro_result.schema.json
  micro/
    suites/
      micro-v1.json
    scenarios/
      buy_or_auction/
      auction/
      trade_propose/
      trade_response/
      build_or_mortgage/
      liquidation/
      jail/
      post_turn_strategy/
```

```text
python/packages/microbench/
  pyproject.toml
  README.md
  src/monopoly_microbench/
    __init__.py
    catalog.py          # load/list/filter/validate scenarios and suites
    runner.py           # run one scenario or suite
    scorer.py           # score action against rubric
    baselines.py        # fixed-policy/reference action helpers
    artifacts.py        # micro-specific artifact paths
    generation.py       # fixture generation helpers
    cli.py              # command line interface
    tui.py              # terminal UI
    api_models.py       # shared request/result models for FastAPI adapter
    types.py            # typed protocol helpers/dataclasses if useful
  tests/
```

```text
python/apps/api/src/monopoly_api/
  micro.py              # thin FastAPI adapter over monopoly_microbench
```

```text
frontend/src/pages/micro/
  MicroSuitePage.tsx
  ScenarioCatalog.tsx
  ScenarioBoard.tsx
  ScenarioRunnerPanel.tsx
  ResultInspector.tsx
  BatchLeaderboard.tsx
```

Current prototype code has micro logic in `monopoly_arena` and `monopoly_api`. That is acceptable for a first spike, but the full version should move most micro-specific code into `monopoly_microbench`. The API should become a thin adapter.

---

## Package Boundaries

### `contracts/micro`

Owns benchmark data:

- frozen scenario fixtures,
- suite manifests,
- protocol-level schemas,
- human-readable metadata,
- evaluation rubrics.

It should not contain Python logic.

### `python/packages/microbench`

Owns benchmark execution:

- scenario catalog loading,
- validation,
- scoring,
- single-run execution,
- batch execution,
- CLI,
- TUI,
- micro artifact layout.

It may depend on:

- `monopoly-arena`,
- `monopoly-telemetry`,
- `monopoly-engine` for board constants/helpers only,
- `jsonschema`,
- optionally a TUI library.

It should not modify engine state or depend on API internals.

### `python/apps/api`

Owns HTTP access:

- list scenarios,
- fetch scenario detail,
- run one scenario,
- fetch run detail,
- launch/fetch batch runs if needed.

It should call `monopoly_microbench` and do minimal transport shaping.

### `frontend`

Owns presentation:

- scenario catalog,
- fixture board rendering,
- runner controls,
- score/result inspector,
- batch leaderboard.

It must not compute legal actions or scenario scores independently. The frontend displays backend-provided score breakdowns.

---

## Scenario Object

A micro scenario is a frozen `DecisionPoint` plus benchmark metadata.

Minimum shape:

```json
{
  "schema_version": "v1",
  "scenario_id": "auction-red-completion-cash-pressure-01",
  "suite_id": "micro-v1",
  "category": "AUCTION",
  "difficulty": "medium",
  "title": "Auction Bid Under Cash Pressure",
  "description": "Alpha can complete red by winning Illinois, but the bid is already above face value and cash is tight.",
  "tags": ["auction", "red-monopoly", "cash-pressure", "overbid-risk"],
  "focal_player_id": "p1",
  "decision_point": {
    "...": "normal DecisionPoint"
  },
  "evaluation": {
    "schema_version": "v1",
    "scoring_mode": "rubric_v1",
    "preferred_actions": [],
    "acceptable_actions": [],
    "bad_actions": [],
    "rubric": []
  },
  "reference_policy": {
    "name": "pro-heuristic-v1",
    "action": {
      "schema_version": "v1",
      "decision_id": "auction-red-completion-cash-pressure-01-d1",
      "action": "bid_auction",
      "args": { "bid_amount": 242 }
    },
    "rationale": "Minimum legal raise preserves optionality while contesting a monopoly-completing property."
  },
  "notes": {
    "strategic_theme": "Monopoly completion versus liquidity risk.",
    "expected_tension": "Many agents should notice red completion but differ in bid sizing."
  }
}
```

### Required Scenario Fields

- `schema_version`
- `scenario_id`
- `suite_id`
- `category`
- `difficulty`
- `title`
- `description`
- `tags`
- `focal_player_id`
- `decision_point`
- `evaluation`
- `reference_policy`

### Scenario ID Convention

Use stable, descriptive IDs:

```text
<category>-<theme>-<variant-number>
```

Examples:

```text
buy-or-auction-light-blue-completion-01
auction-red-completion-cash-pressure-03
trade-orange-mutual-monopoly-risk-02
jail-late-game-danger-zone-05
liquidation-preserve-orange-monopoly-01
```

Avoid renaming scenario IDs after results exist. If meaning changes, create a new scenario ID.

---

## Suite Object

A suite manifest groups scenarios into a stable benchmark version.

```json
{
  "schema_version": "v1",
  "suite_id": "micro-v1",
  "title": "MonopolyBench Micro Decision Suite v1",
  "description": "Curated single-decision Monopoly scenarios for tactical, strategic, and negotiation evaluation.",
  "scenario_ids": [
    "buy-or-auction-light-blue-completion-01",
    "auction-red-completion-cash-pressure-01"
  ],
  "categories": {
    "BUY_OR_AUCTION": { "target_count": 20 },
    "AUCTION": { "target_count": 20 },
    "TRADE_PROPOSE": { "target_count": 20 },
    "TRADE_RESPONSE": { "target_count": 10 },
    "BUILD_OR_MORTGAGE": { "target_count": 20 },
    "LIQUIDATION": { "target_count": 10 },
    "JAIL": { "target_count": 15 },
    "POST_TURN_STRATEGY": { "target_count": 15 }
  },
  "scoring_version": "rubric-v1",
  "prompt_conditions": ["default", "pro_strategy_cheatsheet", "minimal_state"]
}
```

Suite manifests make old results interpretable after scenarios evolve.

---

## Result Object

Every micro run should produce a compact result object in addition to normal prompt/action/decision artifacts.

```json
{
  "schema_version": "v1",
  "run_id": "micro-auction-red-completion-cash-pressure-01-openai-gpt-oss-120b-...",
  "suite_id": "micro-v1",
  "scenario_id": "auction-red-completion-cash-pressure-01",
  "category": "AUCTION",
  "model": {
    "openrouter_model_id": "openai/gpt-oss-120b",
    "model_display_name": "GPT OSS 120B",
    "reasoning": { "effort": "medium" }
  },
  "outcome": {
    "action": {
      "schema_version": "v1",
      "decision_id": "...",
      "action": "bid_auction",
      "args": { "bid_amount": 242 },
      "public_message": "",
      "private_thought": "..."
    },
    "retry_used": false,
    "fallback_used": false,
    "fallback_reason": null,
    "latency_ms": 1872
  },
  "score": {
    "total": 0.85,
    "label": "preferred",
    "breakdown": [
      {
        "criterion_id": "monopoly_awareness",
        "points": 0.25,
        "max_points": 0.25,
        "passed": true,
        "message": "Action contests a monopoly-completing red property."
      }
    ]
  }
}
```

---

## Decision Categories

Start with eight categories.

1. `BUY_OR_AUCTION`
2. `AUCTION`
3. `TRADE_PROPOSE`
4. `TRADE_RESPONSE`
5. `BUILD_OR_MORTGAGE`
6. `LIQUIDATION`
7. `JAIL`
8. `POST_TURN_STRATEGY`

Target counts:

```text
BUY_OR_AUCTION:      20
AUCTION:             20
TRADE_PROPOSE:       20
TRADE_RESPONSE:      10
BUILD_OR_MORTGAGE:   20
LIQUIDATION:         10
JAIL:                15
POST_TURN_STRATEGY:  15
```

Total target: 130 scenarios.

This is large enough to be meaningful and small enough to manually audit.

---

## Scenario Design Axes

Each category should cover controlled scenario axes. The suite should avoid 20 near-duplicates.

### `BUY_OR_AUCTION`

Questions:

- Should the model buy immediately or force auction?
- Does it account for monopoly completion?
- Does it preserve enough cash after purchase?
- Does it understand when auctioning helps opponents?

Axes:

- completes focal player's monopoly,
- blocks opponent monopoly,
- low-value property,
- utility trap,
- railroad context,
- cash-rich early game,
- cash-poor midgame,
- opponent with large cash advantage,
- property price versus remaining liquidity,
- early acquisition versus late dangerous board.

Example scenarios:

- Buy Vermont to complete light blue with modest cash buffer.
- Buy Boardwalk while cash-poor and no Park Place.
- Auction utility because cash is low and utility value is weak.
- Buy railroad as second railroad with healthy cash.
- Decline/auction property that gives no monopoly path and risks liquidity.

### `AUCTION`

Questions:

- Does the model bid rationally?
- Does it overpay for monopoly completion?
- Does it block opponents when worth it?
- Does it drop out when cash risk dominates?

Axes:

- current bid below face value,
- current bid above face value,
- minimum raise versus aggressive raise,
- property completes focal player's monopoly,
- property completes opponent monopoly,
- current leader is dangerous,
- focal player has low cash,
- late-game rent danger,
- auction action count high,
- utility/railroad/property differences.

Example scenarios:

- Bid minimum to contest Illinois completion.
- Drop out when opponent overpays for utility.
- Defensive bid to block orange completion.
- Avoid bankrupting cash reserve for Boardwalk.
- Push bid when winning creates immediate monopoly with build cash.

### `TRADE_PROPOSE`

Questions:

- Can the model structure a plausible, legal, useful trade?
- Does it identify surplus assets?
- Does it avoid giving an opponent a stronger monopoly?
- Does it include reasonable cash sweeteners?

Axes:

- focal player can complete monopoly,
- opponent can complete monopoly,
- mutual monopoly trade,
- one-sided trade temptation,
- surplus utility/railroad,
- jail card inclusion,
- cash-poor counterparty,
- opponent near bankruptcy,
- late-game blocking,
- table politics/public message.

Example scenarios:

- Offer Water Works plus cash for New York to complete orange.
- Avoid giving opponent red monopoly for weak compensation.
- Offer railroad swap that improves both players.
- Trade jail card as sweetener in late game.
- Propose no trade? If `propose_trade` is the only legal action, score no-value empty trades poorly.

### `TRADE_RESPONSE`

Questions:

- Does the model accept beneficial trades?
- Does it reject trades that help opponents more?
- Can it counter with a better structure?

Axes:

- trade completes focal monopoly,
- trade completes opponent monopoly,
- mutual monopoly completion,
- cash compensation enough/not enough,
- counterparty is current leader,
- focal player needs liquidity,
- offered property is mortgaged,
- jail card valuation,
- defensive denial,
- multi-exchange negotiation history.

Example scenarios:

- Accept trade that completes orange and only gives opponent utility.
- Reject trade that gives opponent red monopoly for small cash.
- Counter mutual monopoly trade with higher cash demand.
- Accept liquidity-saving trade while avoiding bankruptcy.
- Reject superficially positive net worth trade that creates opponent hotel threat.

### `BUILD_OR_MORTGAGE`

Questions:

- Does the model build houses at the right time?
- Does it prioritize 3-house breakpoint?
- Does it avoid hotel traps?
- Does it mortgage low-value assets to build high-value monopolies?
- Does it preserve liquidity?

Axes:

- orange/red monopoly build opportunity,
- house shortage,
- hotel conversion,
- low cash,
- mortgage utility to build,
- mortgage railroad to build,
- opponent about to enter danger zone,
- even-building constraints,
- sell versus mortgage,
- late-game rent pressure.

Example scenarios:

- Mortgage Electric Company to build third orange house.
- End turn instead of building when cash is dangerously low.
- Build evenly across red from 2 to 3 houses.
- Avoid hotel when houses are scarce and 4-house trap is stronger.
- Sell houses only when liquidation requires it.

### `LIQUIDATION`

Questions:

- Does the model raise cash in a way that preserves winning chances?
- Does it know when bankruptcy is unavoidable?
- Does it mortgage before selling key houses?
- Does it prioritize asset preservation?

Axes:

- owed to bank versus owed to player,
- small shortfall,
- large shortfall,
- preserve monopoly,
- sell houses versus mortgage utility,
- mortgage already mortgaged assets unavailable,
- bankruptcy to opponent transfers assets,
- bankruptcy to bank returns assets,
- keep enough cash after payment,
- late-game strategic sacrifice.

Example scenarios:

- Mortgage utility to pay rent while preserving orange houses.
- Sell one house evenly rather than mortgage core monopoly.
- Declare bankruptcy when no legal liquidation can cover debt.
- Prefer mortgaging non-monopoly property over breaking 3-house position.
- Avoid transferring monopoly assets to leading opponent if alternatives exist.

### `JAIL`

Questions:

- Does the model understand early-game jail versus late-game jail?
- Does it value movement early?
- Does it value safety late?
- Does it use jail cards appropriately?

Axes:

- early game undeveloped board,
- late game dangerous board,
- cash-rich,
- cash-poor,
- has get-out-of-jail card,
- third jail turn,
- owns developed monopoly,
- opponents own dangerous monopolies,
- need to collect rent,
- need to avoid rent.

Example scenarios:

- Pay early to keep acquiring properties.
- Roll late to stay protected.
- Use jail card when third turn forces exit soon.
- Avoid paying when cash buffer is low and board is dangerous.
- Pay when rent income opportunity and board is safe.

### `POST_TURN_STRATEGY`

Questions:

- Does the model choose the right optional action after movement?
- Does it end turn when no useful optional action exists?
- Does it chain trades/building/mortgages sensibly across repeated post-turn decisions?

Axes:

- trade available,
- mortgage available,
- unmortgage available,
- build available,
- end-turn temptation,
- player has monopoly but insufficient cash,
- player can unmortgage safely,
- player should not over-act,
- setting up future trade,
- dangerous opponent board position.

Example scenarios:

- End turn when only bad mortgage is available.
- Unmortgage key property with ample cash.
- Build before ending because opponents are approaching monopoly.
- Propose trade before building.
- Mortgage weak asset to create build liquidity.

---

## Scoring Model

Scoring must be structured, versioned, and deterministic.

Minimum labels:

```text
preferred:   strategically strong action
acceptable:  defensible but not best
bad:         strategically poor or misses obvious context
invalid:     malformed, illegal, or fallback-only outcome
```

Suggested numeric mapping:

```text
preferred = 1.0
acceptable = 0.5
bad = 0.0
invalid/fallback = tracked separately and usually scored 0.0
```

For more nuanced scenarios, use rubric scoring:

```json
{
  "criterion_id": "cash_discipline",
  "description": "Preserves at least $150 after action unless monopoly payoff is immediate.",
  "max_points": 0.25,
  "type": "cash_after_action_range",
  "params": {
    "min_cash": 150
  }
}
```

### Scoring Criteria Types

Start with deterministic criteria:

- `action_name_is`
- `action_name_in`
- `arg_equals`
- `arg_in_range`
- `bid_at_least`
- `bid_at_most`
- `bid_between`
- `trade_target_is`
- `trade_offer_contains_property`
- `trade_request_contains_property`
- `trade_offer_cash_between`
- `trade_request_cash_between`
- `trade_does_not_give_opponent_monopoly`
- `trade_completes_focal_monopoly`
- `builds_on_group`
- `build_count_between`
- `mortgages_space`
- `uses_jail_card`
- `keeps_cash_above`
- `private_thought_mentions`
- `public_message_nonempty`

Avoid LLM-as-judge for v1 scoring. It can be added later as optional analysis, but the benchmark score should be deterministic.

### Trade Scoring

Trade exact matching is too brittle. Score trades by structure:

- target player,
- requested properties,
- offered properties,
- cash range,
- jail card inclusion,
- whether focal player completes a monopoly,
- whether opponent completes a monopoly,
- whether net cash/property value is plausible.

Example:

```json
{
  "scoring_mode": "rubric_v1",
  "rubric": [
    {
      "criterion_id": "requests_new_york",
      "type": "trade_request_contains_property",
      "max_points": 0.25,
      "params": { "space_key": "NEW_YORK_AVENUE" }
    },
    {
      "criterion_id": "targets_beta",
      "type": "trade_target_is",
      "max_points": 0.15,
      "params": { "player_id": "p2" }
    },
    {
      "criterion_id": "reasonable_cash_sweetener",
      "type": "trade_offer_cash_between",
      "max_points": 0.2,
      "params": { "min": 50, "max": 250 }
    }
  ]
}
```

---

## Baselines

The suite should support non-LLM baselines.

Minimum baselines:

1. **Random legal**
   - Picks uniformly from legal actions.
   - For argument actions, uses deterministic minimal/legal args.

2. **First legal**
   - Useful as a sanity baseline.

3. **Pro heuristic v1**
   - Encodes common Monopoly heuristics.
   - Buy monopoly-completing properties when cash allows.
   - Prefer orange/red/light-blue development.
   - Build to 3 houses before hotels.
   - Stay in jail late when board is dangerous.
   - Avoid utilities unless cheap/contextual.

4. **Haliem-style fixed policy approximation**
   - Buy property if it completes monopoly and affordable.
   - Otherwise buy if cash exceeds price by at least `$200`.
   - Accept trade if it increases monopolies or has positive trade net worth.

Baselines make model results interpretable. A model beating random is not enough; it should be compared against simple Monopoly heuristics.

---

## Prompt Conditions

Micro runs should support prompt-condition experiments.

Initial prompt conditions:

1. `default`
   - Existing MonopolyBench system prompt.

2. `minimal`
   - Legal actions plus compact state, little strategy guidance.

3. `pro_strategy_cheatsheet`
   - Adds concise Monopoly strategy heuristics.

4. `no_private_thought`
   - Removes or ignores private-thought requirement if the protocol later supports it.

5. `full_state`
   - Includes full structured state.

6. `compact_state`
   - Includes only relevant scenario focus and summarized holdings.

The benchmark should record prompt condition in every result.

---

## Runner Design

### Single Scenario CLI

```bash
cd python
uv run monopoly-micro run \
  --scenario auction-red-completion-cash-pressure-01 \
  --model openai/gpt-oss-120b \
  --reasoning medium \
  --prompt-condition default
```

Expected output:

```text
Run: micro-auction-red-completion-cash-pressure-01-openai-gpt-oss-120b-...
Action: bid_auction {"bid_amount": 242}
Score: 0.85 preferred
Retry: no
Fallback: no
Artifacts: runs/micro/<run_id>
```

### Suite CLI

```bash
uv run monopoly-micro run-suite \
  --suite micro-v1 \
  --model openai/gpt-oss-120b \
  --prompt-condition default
```

### Model Comparison CLI

```bash
uv run monopoly-micro compare \
  --suite micro-v1 \
  --models configs/micro-models.json \
  --prompt-condition default
```

### Score Existing Run

```bash
uv run monopoly-micro score --run-id micro-...
```

### Export Results

```bash
uv run monopoly-micro export \
  --batch-id micro-batch-... \
  --format csv \
  --out analysis/micro-v1-results.csv
```

---

## TUI Requirements

The TUI should be practical for research iteration.

Required screens:

1. **Scenario Catalog**
   - filter by category,
   - search by tag/title,
   - show difficulty and scoring mode,
   - show whether fixture validates.

2. **Scenario Detail**
   - description,
   - focal player,
   - board summary,
   - legal actions,
   - expected strategic tension,
   - reference action/rationale.

3. **Run Panel**
   - model ID,
   - prompt condition,
   - reasoning effort,
   - run selected scenario,
   - run category,
   - run full suite.

4. **Result Inspector**
   - chosen action,
   - public message,
   - private thought,
   - retry/fallback,
   - score breakdown,
   - prompt/response artifact paths.

5. **Leaderboard**
   - model by category,
   - total score,
   - fallback rate,
   - retry rate,
   - invalid rate,
   - latency.

Recommended library:

- `textual` if we want a richer TUI,
- simple `rich` tables if we want minimal dependency and faster implementation.

Start with `rich`, upgrade to `textual` only if needed.

---

## API Endpoints

Keep API endpoints thin.

Required:

```text
GET  /micro/scenarios
GET  /micro/scenarios/{scenario_id}
GET  /micro/suites
GET  /micro/suites/{suite_id}
POST /micro/run
GET  /micro/runs/{run_id}
POST /micro/batches
GET  /micro/batches/{batch_id}
GET  /micro/batches/{batch_id}/leaderboard
```

`POST /micro/run` request:

```json
{
  "scenario_id": "auction-red-completion-cash-pressure-01",
  "openrouter_model_id": "openai/gpt-oss-120b",
  "name": "Micro Agent",
  "reasoning": { "effort": "medium" },
  "prompt_condition": "default",
  "system_prompt": null
}
```

Response:

```json
{
  "run_id": "micro-...",
  "result": {
    "score": { "total": 0.85, "label": "preferred" }
  }
}
```

---

## Frontend Requirements

The frontend should be a research console, not just a demo page.

### Scenario Catalog

Required:

- category filters,
- tags,
- difficulty,
- text search,
- suite selector,
- scenario count by category.

### Board Fixture

Required:

- render frozen `StateSnapshot`,
- show tokens,
- show active/focal player,
- show legal-action highlights,
- show property ownership/buildings/mortgages.

### Legal Action Panel

Required:

- action names,
- arg schema summary,
- UI hints,
- selected action highlight.

### Runner Panel

Required:

- model ID input,
- display name input,
- reasoning effort,
- prompt condition,
- optional system prompt override,
- run scenario button,
- eventually run category/full suite.

### Result Inspector

Required:

- final action,
- action args,
- public message,
- private thought,
- retry/fallback status,
- score label,
- score breakdown,
- prompt artifact links if API exposes them.

### Batch Leaderboard

Required later:

- model rows,
- category columns,
- overall score,
- fallback rate,
- retry rate,
- invalid rate,
- average latency.

---

## Artifact Layout

### Single Micro Run

```text
runs/micro/<run_id>/
  scenario.json
  result.json
  summary.json
  actions.jsonl
  decisions.jsonl
  state/
    turn_XXXX.json
  prompts/
    decision_<decision_id>_system.txt
    decision_<decision_id>_user.json
    decision_<decision_id>_tools.json
    decision_<decision_id>_response.json
    decision_<decision_id>_parsed.json
```

### Micro Batch

```text
runs/micro_batches/<batch_id>/
  config.json
  results.jsonl
  leaderboard.json
  category_breakdown.json
  failures.jsonl
```

### Quality Artifacts

```text
quality_check/micro/<run_id>/
  decision_<decision_id>_request.txt
  decision_<decision_id>_response.txt
```

---

## Scenario Generation Workflow

Fixtures should be committed as JSON, but generated through scripts for consistency.

Recommended workflow:

1. Do online research for scenario design.
2. Convert researched strategic themes into a scenario backlog.
3. Write scenario builder helpers.
4. Generate JSON fixtures.
5. Validate fixtures against schemas.
6. Manually inspect scenario intent and scoring.
7. Commit generated fixtures.

Commands:

```bash
uv run python scripts/generate_micro_scenarios.py
node contracts/validate-contracts.mjs
uv run monopoly-micro validate
```

Generator helpers should avoid duplicated boilerplate:

- board creation,
- player creation,
- ownership setup,
- houses/hotels setup,
- derived net worth/monopoly calculations,
- legal action creation,
- evaluation/rubric construction.

---

## Online Research Requirement For The 130 Scenarios

Before building the full `micro-v1` suite, do explicit online research. The 130 scenarios should not come only from intuition. They should be grounded in a mix of:

- Monopoly strategy guides,
- tournament/player heuristics,
- Monopoly probability and Markov-chain studies,
- prior RL Monopoly papers,
- existing Monopoly bot implementations,
- auction/trade strategy discussions,
- board-game strategy forum discussions,
- and the Haliem/Bonjour hybrid DRL setup.

The purpose is not to blindly copy advice. The purpose is to identify recurring strategic tensions that can be turned into controlled, protocol-valid micro decisions.

### Research Sources To Prioritize

Use primary or high-signal sources where possible:

- academic papers on Monopoly agents, RL, MCTS, or Markov models,
- Haliem et al. / Bonjour related material and code if available,
- Bailis et al. Monopoly RL work,
- TENCON / IEEE Monopoly RL work,
- probability studies on landing frequencies and color-group value,
- open-source Monopoly bots with explicit strategy code,
- strategy writeups from competitive or mathematically serious Monopoly players,
- well-reasoned forum posts only when they contain concrete strategic claims.

Lower-priority sources:

- casual blog posts with no reasoning,
- generic “how to win Monopoly” pages,
- unverifiable claims,
- strategy advice that conflicts with official rules unless clearly marked.

### What To Extract From Research

For every useful source, extract structured claims:

```text
source_url:
source_type: paper | bot | strategy-guide | forum | video | code
claim:
category:
strategic_principle:
example_decision:
possible_micro_scenario:
confidence: high | medium | low
notes:
```

Examples of useful extracted claims:

- Orange and red properties are often high-value because of jail exit traffic.
- Building to three houses is often more important than rushing hotels.
- Utilities are often weaker than players intuitively think.
- Railroads can be useful early but usually do not scale like monopolies with houses.
- Early-game jail is usually bad because movement/acquisition matters.
- Late-game jail can be protective when dangerous monopolies are built.
- Cash liquidity matters; a technically good acquisition can be bad if it creates rent vulnerability.
- Trades should be evaluated by monopoly creation, not just face-value net worth.
- A trade that creates mutual monopolies may be good or terrible depending on cash/build timing.
- Auction bidding should consider opponent monopoly completion and cash remaining after the bid.

### Research Backlog Format

Before generating the final fixtures, create a research-backed scenario backlog:

```text
category:
scenario_slug:
strategic_tension:
source_claims:
board_state_requirements:
legal_actions_required:
preferred_action:
acceptable_actions:
bad_actions:
rubric_criteria:
difficulty:
notes:
```

This backlog can live as a Markdown or JSON planning artifact before becoming generated scenario fixtures.

Recommended path:

```text
contracts/micro/research/scenario_backlog.md
```

or:

```text
contracts/micro/research/scenario_backlog.json
```

### Research-To-Scenario Conversion Rules

When converting research into scenarios:

1. Keep each scenario focused on one primary strategic tension.
2. Vary one or two secondary variables, not everything at once.
3. Make the legal action set small and explicit.
4. Ensure the preferred action is defensible, not merely stylistic.
5. Include at least one plausible trap action.
6. Include scoring that distinguishes “noticed the principle” from “executed it well.”
7. Do not expose source rationales to the model unless running a specific prompt condition.
8. Keep source citations in metadata or research notes, not in the default prompt payload.

### Scenario Count Planning From Research

The final 130 scenarios should be research-balanced:

```text
BUY_OR_AUCTION:      20
AUCTION:             20
TRADE_PROPOSE:       20
TRADE_RESPONSE:      10
BUILD_OR_MORTGAGE:   20
LIQUIDATION:         10
JAIL:                15
POST_TURN_STRATEGY:  15
```

Each category should include:

- easy sanity-check cases,
- medium cases with real strategic tension,
- hard cases where common heuristics conflict,
- at least one scenario inspired by prior agent/RL behavior,
- at least one scenario inspired by human/pro strategy,
- and at least one scenario designed to catch LLM-specific failure modes.

### LLM-Specific Failure Modes To Target

The scenario suite should intentionally test failures that classic RL bots may not have:

- choosing a plausible-sounding but illegal tool argument,
- overexplaining instead of selecting the best action,
- overvaluing famous properties like Boardwalk,
- blindly applying “orange/red good” without cash context,
- making generous trades because they sound fair,
- making hostile trades that no opponent would accept,
- ignoring opponent monopolies,
- ignoring cash after action,
- revealing strategic intent in public messages,
- private thought contradicting action quality,
- and failing to adapt jail policy by game phase.

### Citation Discipline

Scenario metadata should be allowed to include source references:

```json
{
  "research_sources": [
    {
      "title": "Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach",
      "url": "https://arxiv.org/pdf/2103.00683",
      "claim": "Hybrid agents use fixed policies for buy-property and accept-trade decisions.",
      "used_for": "Buy-property and trade-response scenario design."
    }
  ]
}
```

Do not put long copyrighted excerpts in fixtures. Store short source descriptions and paraphrased claims.

---

## Validation Requirements

Every scenario must pass:

1. JSON schema validation.
2. `decision_point.player_id == focal_player_id`.
3. `decision_point.state.active_player_id == focal_player_id`, unless intentionally documented.
4. every legal action has an `args_schema`.
5. every scored/reference action is legal for the decision.
6. every referenced `space_key` exists in board data.
7. every referenced `player_id` exists in the fixture state.
8. evaluation rubric total points is positive.
9. no hidden engine-only data is included.
10. no future deck/RNG state is included.

For the benchmark suite:

1. every scenario in suite exists.
2. no duplicate scenario IDs.
3. category counts match manifest or are explicitly marked incomplete.
4. scoring version is consistent.

---

## Testing Plan

### Contract Tests

- Validate all micro schemas.
- Validate every scenario fixture.
- Validate suite manifests.
- Validate result examples.

### Python Unit Tests

- catalog lists scenarios deterministically.
- loader rejects invalid fixtures.
- runner writes isolated artifacts.
- scorer produces expected score for reference actions.
- scorer handles trade rubrics.
- fallback outcomes score invalid/zero but preserve fallback metadata.
- batch runner writes leaderboard.

### API Tests

- list scenarios.
- fetch scenario.
- run scenario with scripted OpenRouter.
- fetch run result.
- list suites.
- launch batch with scripted model.
- fetch leaderboard.

### Frontend Tests / Build Checks

- TypeScript build.
- micro page renders with fixture.
- result inspector handles fallback.
- catalog filters work.

---

## Implementation Phases

### Phase 0: Stabilize Current Spike

- Keep current prototype working.
- Ensure focused tests pass.
- Ensure contract validation passes.
- Document current limitations.

### Phase 1: Create `monopoly_microbench`

- Add new Python package.
- Move micro catalog/runner/scorer there.
- Keep API as thin adapter.
- Preserve current endpoint behavior.

### Phase 2: Add Scoring

- Extend schema with `evaluation`.
- Add deterministic scorer.
- Add reference-policy action validation.
- Write `result.json`.

### Phase 3: Build Initial High-Quality Suite

- Build 5 scenarios per category.
- Total: 40 scenarios.
- Manually inspect each one.
- Use this as `micro-v0`.

### Phase 4: Add CLI

- `validate`
- `list`
- `run`
- `run-suite`
- `score`
- `export`

### Phase 5: Add TUI

- Start with `rich` tables.
- Scenario catalog.
- Run one scenario.
- Inspect result.

### Phase 6: Expand to Full Suite

- 10-20 per category.
- Target 130 scenarios.
- Create `micro-v1`.

### Phase 7: Batch Experiments

- multi-model batch config,
- prompt-condition sweeps,
- category leaderboards,
- CSV export for paper analysis.

### Phase 8: Frontend Polish

- split page into components,
- add batch results,
- add scoring breakdown UI,
- add suite selector.

---

## Research Metrics

Per scenario:

- score,
- label,
- action name,
- key args,
- retry used,
- fallback used,
- fallback reason,
- latency,
- public message length,
- private thought length,
- prompt condition.

Per category:

- average score,
- preferred rate,
- acceptable rate,
- bad rate,
- invalid/fallback rate,
- retry rate,
- average latency.

Per model:

- total score,
- category score vector,
- legality reliability,
- prompt sensitivity,
- strategic profile.

Strategic profile dimensions:

- monopoly awareness,
- cash discipline,
- auction discipline,
- trade quality,
- opponent-risk awareness,
- jail timing,
- development timing,
- liquidation quality.

---

## Open Questions

1. Should micro scoring be purely deterministic in v1?
   - Recommendation: yes.

2. Should scenarios be generated from engine states or handwritten JSON?
   - Recommendation: use generator helpers, commit JSON.

3. Should the micro package depend on API?
   - Recommendation: no.

4. Should full-game code know about micro mode?
   - Recommendation: no, except API route registration and shared UI components.

5. Should scenarios include natural-language expert rationales?
   - Recommendation: yes, but do not expose them to the model unless running a specific prompt condition.

6. Should we score private thoughts?
   - Recommendation: only as secondary analysis, not primary score.

---

## Immediate Next Steps

1. Create `python/packages/microbench`.
2. Move current micro runner/catalog code into it.
3. Add `micro_result.schema.json` and `micro_suite.schema.json`.
4. Extend scenario schema with `difficulty`, `evaluation`, and `reference_policy`.
5. Add deterministic scorer.
6. Convert current six scenarios into the richer schema.
7. Add CLI command `uv run monopoly-micro validate`.
8. Add CLI command `uv run monopoly-micro run --scenario ...`.
9. Keep existing frontend `/micro` page working through the API adapter.
10. Expand to 5 scenarios per category before scaling to the full 130-scenario suite.

---

## Final Design Call

The micro-decision suite should be a benchmark overlay:

- frozen protocol fixtures,
- isolated package,
- isolated artifacts,
- shared arena resolver,
- deterministic scoring,
- thin API adapter,
- render-only frontend,
- CLI/TUI for research iteration.

That gives MonopolyBench a clean path from polished live demo to research-grade benchmark suite without contaminating the deterministic full-game engine.
