# Micro-v1 Scenario Quality Improvement Plan

This document is specifically for improving the current `micro-v1` scenario corpus.

The current suite has the right shape and count, but it is not yet research-grade. It validates structurally, but the scenarios are too template-generated and need a serious research-backed rewrite before they should be treated as the final benchmark.

---

## Current Corpus Audit

Current suite count is correct:

```text
BUY_OR_AUCTION:      20
AUCTION:             20
TRADE_PROPOSE:       20
TRADE_RESPONSE:      10
BUILD_OR_MORTGAGE:   20
LIQUIDATION:         10
JAIL:                15
POST_TURN_STRATEGY:  15
TOTAL:              130
```

But the content is not diverse enough.

Measured from the current JSON fixtures:

```text
AUCTION
  unique descriptions: 1
  unique legal action sets: 1
  unique rubric sets: 1

BUILD_OR_MORTGAGE
  unique descriptions: 1
  unique legal action sets: 1
  unique rubric sets: 1

BUY_OR_AUCTION
  unique descriptions: 1
  unique legal action sets: 1
  unique rubric sets: 1

JAIL
  unique descriptions: 1
  unique legal action sets: 2
  unique rubric sets: 1

LIQUIDATION
  unique descriptions: 1
  unique legal action sets: 1
  unique rubric sets: 1

POST_TURN_STRATEGY
  unique descriptions: 1
  unique legal action sets: 1
  unique rubric sets: 1

TRADE_PROPOSE
  unique descriptions: 1
  unique legal action sets: 1
  unique rubric sets: 1

TRADE_RESPONSE
  unique descriptions: 1
  unique legal action sets: 1
  unique rubric sets: 1
```

This means the current corpus is mostly 8 generated scenario templates with index-based parameter changes. That is useful scaffolding, but not sufficient for a benchmark.

---

## Verdict

Keep:

- `monopoly_microbench` package direction.
- schemas,
- suite manifest,
- artifact layout,
- CLI/API/frontend wiring,
- deterministic scoring machinery,
- 130-scenario target.

Replace or heavily rewrite:

- most generated scenario fixture content,
- research backlog,
- reference rationales,
- rubric definitions,
- category diversity,
- title/description/notes.

The final suite should feel curated, not generated.

---

## Internet Research Findings To Use

These are the source-backed strategic claims that should directly shape the rewritten scenarios.

### Official Rules And Rule-Driven Edge Cases

Use official/near-official rules to build legality and edge-case scenarios:

- Hasbro instructions identify the official components: 32 houses and 12 hotels, which matters for house-shortage and hotel-trap scenarios.
  - Source: https://instructions.hasbro.com/en-us/instruction/monopoly-game

- The official rulebook describes Jail causes, including being sent to Jail by square/card or rolling doubles three times.
  - Source: https://www.hasbro.com/common/instruct/Monopoly.pdf

- Rules summaries confirm auctions begin when a player declines to buy an unowned property, houses must be built evenly, and there are house/hotel supply constraints.
  - Source: https://www.monopolyland.com/monopoly-rules/
  - Source: https://en.wikibooks.org/wiki/Monopoly/Official_Rules

Scenario implications:

- add forced third-turn jail scenarios,
- add last-house / house-shortage scenarios,
- add hotel-trap scenarios,
- add trade/mortgage restrictions around improved properties,
- add liquidation order scenarios that respect buildings and mortgage constraints.

### Probability And Markov-Chain Strategy

Multiple probability/Markov sources support orange/red importance and high-traffic locations:

- SOA Markov discussion explains that orange and red squares are commonly landed on due to Jail traffic.
  - Source: https://www.soa.org/news-and-publications/newsletters/compact/2012/april/actuarial-monopoly.aspx

- Monopoly Land probability table lists Jail as the most landed space and Illinois Avenue / New York Avenue among the highest property probabilities.
  - Source: https://www.monopolyland.com/monopoly-statistics-that-will-help-you-win/

- SangHyun Kim's Markov analysis highlights orange properties and Illinois Avenue.
  - Source: https://sanghyun-kim.com/monopoly-analysis

- MAS275 probability modeling notes Jail as highly probable and Illinois Avenue as a high-probability property.
  - Source: https://www.normalesup.org/~stephens/MAS275/monopoly.pdf

Scenario implications:

- keep orange/red scenarios, but diversify them,
- include Illinois-specific auctions,
- include New York Avenue trade/purchase scenarios,
- include cases where high landing probability conflicts with cash shortage,
- include cases where Boardwalk fame tempts overpayment despite lower traffic.

### Human Strategy Heuristics

Strategy sources repeatedly emphasize:

- orange is strong due to Jail exit traffic,
- red is also strong,
- utilities are often weak,
- three houses are a major development breakpoint,
- cash reserves matter,
- late-game Jail can be protective.

Sources:

- https://www.wargamer.com/monopoly/how-to-win-monopoly
- https://whatnerd.com/how-to-win-monopoly-strategy-tips/
- https://quatizer.com/strateg.html
- https://quatizer.com/resource.html
- https://www.ultraboardgames.com/monopoly/strategy.php

Scenario implications:

- add utility-overvaluation traps,
- add railroad-as-bargaining-chip scenarios,
- add three-house breakpoint scenarios across multiple groups,
- add late-game Jail-as-defense cases,
- add liquidity-preservation cases where the tempting high-EV action is still bad.

### Auctions

Auction strategy sources support:

- bidding can force opponents to pay more for monopoly-completing properties,
- aggressive bidding can burn cash,
- auction strategy should consider opponent needs and cash reserve.

Sources:

- https://www.monopolyland.com/monopoly-auction-rules/
- https://www.monopolyland.com/monopoly-rules/

Scenario implications:

- include defensive bidding,
- include bluff-risk cases,
- include cash-poor drop-out cases,
- include low-price steal cases,
- include opponent-completion prevention.

### Housing Shortage And Hotel Trap

Sources and community strategy discussion emphasize:

- there are only 32 houses,
- building evenly matters,
- holding houses rather than upgrading to hotels can restrict opponent development,
- hotel conversion can release houses back into circulation.

Sources:

- https://instructions.hasbro.com/en-us/instruction/monopoly-game
- https://www.playiro.com/articles/when-to-build-houses-vs-hotels-in-monopoly-the-ultimate-strategy-guide
- https://www.reddit.com/r/monopoly/comments/m41qj2
- https://www.reddit.com/r/monopoly/comments/1eh0mlz

Scenario implications:

- add build-to-four-but-don't-hotel scenarios,
- add don't-upgrade-to-hotel-during-house-shortage scenarios,
- add last-house auction/shortage scenarios if supported by engine action space,
- add sell-hotel/liquidation edge cases.

### Prior RL / Agent Benchmarking

The Haliem/Bonjour paper supports:

- action masking/legal action constraints,
- fixed-policy handling for buy-property and accept-trade decisions,
- fixed-policy opponents prioritizing monopolies, trades, and development,
- comparing learned agents against heuristic baselines.

Sources:

- https://arxiv.org/abs/2103.00683
- https://www.cs.purdue.edu/homes/bb/hybrid.pdf

Scenario implications:

- add Haliem-style fixed-policy comparison cases,
- add buy-property fixed-policy boundary cases,
- add accept/reject trade fixed-policy boundary cases,
- add scenarios that expose where LLMs can exceed fixed policies via negotiation/message reasoning.

---

## Required Improvements

### 1. Rewrite The Research Backlog

The current `contracts/micro/research/scenario_backlog.md` is too generated.

Replace it with a real planning artifact where each scenario has:

```text
scenario_id:
category:
source_claims:
primary_strategic_tension:
why_this_is_interesting:
board_state_requirements:
legal_actions:
trap_action:
preferred_action:
acceptable_actions:
bad_actions:
rubric_criteria:
reference_rationale:
difficulty:
notes:
```

Every scenario should point to at least one concrete source claim and explain how that claim maps to the board state.

### 2. Enforce Scenario Diversity

For each category, define a diversity matrix before generating fixtures.

Each scenario must differ meaningfully in at least three of:

- property group,
- focal player cash,
- opponent cash,
- opponent threat,
- board phase,
- legal action set,
- reference action,
- rubric criteria,
- asset ownership pattern,
- developed houses/hotels,
- auction state,
- trade structure,
- liquidation debt target,
- Jail turn/card state.

### 3. Improve Rubrics

Avoid scoring only `action_name_is`.

Each scenario should have 2-5 rubric criteria where possible:

- branch choice,
- argument quality,
- cash discipline,
- monopoly awareness,
- opponent-risk awareness,
- source-specific strategic principle,
- public/private message behavior when relevant.

For single-action categories such as `TRADE_PROPOSE`, use richer structure:

- target player,
- requested property,
- offered asset,
- cash range,
- whether the opponent gets a monopoly,
- whether focal player completes a monopoly.

### 4. Make Reference Rationales Specific

Current rationales are often template text.

Each reference policy should explain:

- why this action is preferred in this exact board state,
- what the trap action is,
- what source-backed principle it uses,
- what risk it accepts.

Bad:

```text
Reference policy follows the scenario rubric.
```

Good:

```text
Minimum bid contests Illinois because it completes Alpha's red monopoly, but bidding above $310 leaves Alpha unable to survive the developed orange danger zone.
```

### 5. Include LLM-Specific Failure Traps

Each category should include scenarios that catch LLM-specific mistakes:

- famous-property bias toward Boardwalk/Park Place,
- over-applying "orange/red good" despite cash danger,
- proposing trades no rational opponent would accept,
- accepting trades that are positive face-value but hand opponent a stronger monopoly,
- bidding too high because "monopoly completion" is salient,
- using public messages that reveal private exploitative intent,
- choosing an action with plausible English but wrong structured args,
- ignoring house-shortage/hotel-trap mechanics.

---

## Category Rewrite Requirements

### `BUY_OR_AUCTION` - 20 Scenarios

Current issue:

- Mostly one buy/auction template.

Required mix:

```text
4 monopoly-completion buys
3 cash-danger auction/decline cases
3 utility trap cases
3 railroad-context cases
3 defensive buy/block cases
2 Boardwalk/Park Place fame-bias traps
2 low-cost early acquisition cases
```

Must include:

- Vermont/Connecticut light-blue completion,
- New York / orange completion,
- Illinois / red completion,
- Electric Company / Water Works low-priority cases,
- Reading/Pennsylvania/B&O railroad value cases,
- Boardwalk temptation with low cash,
- auctioning when opponent has limited cash,
- buying when auction would let a cash-rich opponent steal.

Rubric examples:

- `action_name_is`
- `keeps_cash_above`
- `private_thought_mentions` with "cash", "monopoly", "auction", "opponent"
- future criterion: `blocks_opponent_monopoly`

### `AUCTION` - 20 Scenarios

Current issue:

- Mostly Illinois/red bid or drop with generated bid thresholds.

Required mix:

```text
4 minimum-bid monopoly-completion cases
4 drop-out overbid/cash-danger cases
3 defensive block opponent-completion cases
3 utility overbid traps
2 railroad value cases
2 current-leader threat cases
2 bluff-risk cases where opponent can call the bluff
```

Must include:

- Illinois completion,
- New York completion,
- Boardwalk/Park Place temptation,
- utility auction,
- railroad auction,
- current leader already cash-rich,
- focal player can bid but should not because post-bid cash is unsafe.

Rubric examples:

- bid within range,
- drop out when bid exceeds cap,
- bid minimum rather than overbid,
- do not bid above focal cash reserve threshold,
- public/private message can mention "forcing price" or "blocking".

### `TRADE_PROPOSE` - 20 Scenarios

Current issue:

- Mostly Water Works plus cash for New York.

Required mix:

```text
4 orange completion proposals
3 red completion proposals
3 mutual-monopoly trade proposals
3 defensive/no-good-trade trap cases
2 railroad-as-sweetener cases
2 jail-card sweetener cases
2 cash-poor counterparty cases
1 intentionally politically risky negotiation case
```

Must include:

- trades where focal completes monopoly,
- trades where both sides complete monopoly but focal can build faster,
- trades where giving opponent monopoly is unacceptable,
- trades where utility/railroad is surplus,
- trades where cash range matters,
- trades where no plausible opponent would accept a greedy offer.

Rubric examples:

- target player,
- request contains specific property,
- offer contains reasonable asset,
- cash in plausible range,
- does not give stronger opponent monopoly,
- public message is nonempty and plausible,
- private thought identifies true strategic goal.

### `TRADE_RESPONSE` - 10 Scenarios

Current issue:

- Mostly accept/reject pattern with one criterion.

Required mix:

```text
3 accept because focal gains monopoly
3 reject because opponent gains stronger monopoly
2 counter because offer is close but underpriced
1 accept liquidity-saving trade
1 reject face-value-positive but strategically losing trade
```

Must include:

- mutual monopoly trade,
- cash compensation enough/not enough,
- jail card valuation,
- trade from current leader,
- trade that looks fair by property price but is bad by house potential.

Rubric examples:

- action branch,
- counter offer/request structure,
- opponent-risk awareness,
- private thought mentions opponent monopoly.

### `BUILD_OR_MORTGAGE` - 20 Scenarios

Current issue:

- Mostly orange three-house versus mortgage Electric Company.

Required mix:

```text
4 orange three-house breakpoint
3 red development
2 light-blue cheap-house development
2 yellow/green expensive-house caution
3 house-shortage / hotel-trap cases
3 mortgage weak asset to build strong group
2 preserve cash / end turn cases
1 opponent-position timing case
```

Must include:

- build to 3 houses,
- avoid hotel when house shortage matters,
- mortgage utility/railroad to build,
- end turn when cash reserve too low,
- build because opponents are approaching danger zone,
- expensive green/dark-blue caution.

Rubric examples:

- builds on correct group,
- build count range,
- keeps cash above threshold,
- mortgages weak non-core asset,
- avoids hotel upgrade.

### `LIQUIDATION` - 10 Scenarios

Current issue:

- Mostly mortgage utility before selling orange houses.

Required mix:

```text
3 mortgage non-core asset first
2 sell houses evenly to preserve solvency
2 bankruptcy unavoidable
1 owed to bank versus owed to player contrast
1 mortgaged-property interest edge case
1 preserve monopoly versus immediate survival tradeoff
```

Must include:

- owed to bank,
- owed to opponent,
- small shortfall,
- impossible shortfall,
- preserving developed monopoly,
- selling buildings when mortgage is insufficient.

Rubric examples:

- mortgage specific asset,
- sell house plan legal/even,
- declare bankruptcy only when necessary,
- avoid tearing down strongest monopoly unnecessarily.

### `JAIL` - 15 Scenarios

Current issue:

- Good theme, but still one template.

Required mix:

```text
4 early-game pay/leave cases
4 late-game stay/roll cases
2 use jail card cases
2 third-turn forced-exit cases
2 own-monopoly rent-collection incentive cases
1 cash-poor jail decision
```

Must include:

- early undeveloped board,
- late dangerous board,
- has card,
- no card,
- third jail turn,
- opponent orange/red with houses,
- own monopoly developed and rent opportunity outside jail.

Rubric examples:

- phase-appropriate action,
- uses card only when appropriate,
- keeps cash above threshold,
- private thought mentions danger/tempo.

### `POST_TURN_STRATEGY` - 15 Scenarios

Current issue:

- Uses four reference actions but one generic template and one criterion.

Required mix:

```text
3 end-turn because no useful optional action
3 build now before opponent approaches
3 unmortgage safely
3 propose trade before ending
2 mortgage/build sequencing
1 avoid over-action trap
```

Must include:

- optional action truly useful,
- optional action legal but strategically bad,
- end turn as correct choice,
- trade before build,
- unmortgage when cash-rich,
- do not unmortgage when cash-poor.

Rubric examples:

- action branch,
- target property/group,
- cash threshold,
- opponent-position awareness,
- no unnecessary action.

---

## Generator Requirements

Do not delete the generator. Rewrite it so it generates curated cases from explicit scenario definitions instead of index patterns.

Recommended structure:

```python
SCENARIO_DEFS = [
    {
        "scenario_id": "...",
        "category": "...",
        "source_claims": [...],
        "setup": {...},
        "legal_actions": [...],
        "reference_action": {...},
        "rubric": [...],
    }
]
```

Avoid:

```python
prefer_buy = i % 5 != 2
ref_name = ["build", "end_turn", "unmortgage", "propose_trade"][i % 4]
```

Those patterns are useful for smoke tests, not final research scenarios.

---

## Acceptance Bar For The Improved Suite

Before calling the scenario suite complete:

1. Each category has at least 6 unique descriptions.
2. Each category has at least 3 distinct rubric sets.
3. At least 60% of scenarios have 3 or more rubric criteria.
4. At least 80% of reference rationales are scenario-specific.
5. Each scenario maps to a specific research-backed claim in the backlog.
6. No category is generated solely by `i % n` branch selection.
7. The suite still validates with:

```bash
node contracts/validate-contracts.mjs
cd python
uv run monopoly-micro validate
```

8. Reference actions score at least acceptable.
9. Baselines run on representative scenarios.
10. Old full-game MonopolyBench tests still pass or any unrelated failure is documented.

---

## Suggested Implementation Order

1. Rewrite `contracts/micro/research/scenario_backlog.md` as a real source-backed plan.
2. Replace `scripts/generate_micro_scenarios.py` index-pattern builders with curated scenario definitions.
3. Rewrite `BUY_OR_AUCTION` and `AUCTION` first because source support is strongest.
4. Rewrite `TRADE_PROPOSE` and `TRADE_RESPONSE` next because these are the unique LLM contribution.
5. Rewrite `BUILD_OR_MORTGAGE`, especially house-shortage/hotel-trap cases.
6. Rewrite `JAIL`, adding third-turn/card/late-danger cases.
7. Rewrite `LIQUIDATION` and `POST_TURN_STRATEGY`.
8. Re-run contract validation and scorer tests.
9. Manually inspect 2-3 scenarios per category in frontend/TUI.

---

## Bottom Line

The current 130 scenarios prove the pipeline can support the full suite. They should not be treated as the final suite.

The improved suite should be:

- research-backed,
- strategically varied,
- harder to game,
- richer in scoring,
- explicitly designed to catch LLM failures,
- and clearly distinct scenario-by-scenario.

The target is not "130 JSON files." The target is 130 meaningful Monopoly decisions.
