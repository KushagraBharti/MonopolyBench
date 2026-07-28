# Bankruptcy windows

Run: `mock-64394-c3bb8d94`  
Method: decision-centered ±5 windows, joined to events, actions, prompts/responses, and snapshots. A declaration is called “forced” only when the model-visible liquidation menu and authoritative asset state cannot cover the obligation.

## Window 1 — OpenAI GPT 5.4 mini, turn 143

### Decision window

| Relative | Decision | Turn | Actor | Canonical action |
|---:|---|---:|---|---|
| -5 | `...dec-000306` | 138 | Grok | end turn after orange hotels |
| -4 | `...dec-000307` | 139 | GPT | end turn |
| -3 | `...dec-000308` | 140 | Claude | end turn after $130 green rent |
| -2 | `...dec-000309` | 141 | Gemini | end turn after $36 Kentucky rent |
| -1 | `...dec-000310` | 142 | Grok | end turn after $36 Kentucky rent |
| 0 | `...dec-000311` | 143 | GPT | declare bankruptcy |
| +1 | `...dec-000312` | 144 | Claude | end turn |
| +2 | `...dec-000313` | 146 | Grok | build four houses |
| +3 | `...dec-000314` | 146 | Grok | end turn |
| +4 | `...dec-000315` | 147 | Claude | end turn |
| +5 | `...dec-000316` | 148 | Gemini | roll for doubles in jail |

### Pre-state and exposure

- At start turn 143: GPT cash $357; estimated net worth $2,692; ten deeds; three mortgages (Baltic, Pennsylvania Railroad, Water Works); three yellow houses; complete red and yellow control; no jail card. Grok had $311, orange hotels, and occupied Kentucky.
- GPT rolled eight from Jail/visiting position 10 to Tennessee, owing $950.
- Model-visible menu (`run/decisions.jsonl`, `...dec-000311`; mirrored in `run/state/turn_0143_decision_0001.json`): mortgage Reading, Kentucky, Indiana, or Illinois; sell a house on Atlantic, Ventnor, or Marvin; or declare bankruptcy. The prompt explicitly said the engine would ask again after each liquidation.

### Selected action and reported rationale

- Public: “I can’t cover 950 from liquidations.”
- Private: calculated `$357 + $120 + $110 + $110 + $100 + $150 = $947`.
- Selected: immediate `declare_bankruptcy`; no sale or mortgage attempt.

### Adjudication

- Three yellow houses cost $150 each and sell for $75 each, yielding $225, not the reported $150.
- Available mortgages total $440: Reading $100, Kentucky $110, Indiana $110, Illinois $120.
- Maximum offered liquidation cash is at least `$357 + $225 + $440 = $1,022`, $72 above the debt.
- **Finding:** avoidable bankruptcy caused by a $75 house-sale undercount and failure to follow the iterative legal menu. This is a valid-but-strategically/arithmetically incorrect action, not a replay, prompt, or validator defect.

### Immediate and downstream effects

- Events `...evt-002328`–`...-002340`: $357 and ten deeds transfer to Grok; GPT is eliminated.
- Grok immediately owns orange hotels plus complete red/yellow and inherited yellow houses. On turn 146 it spends $600 to develop red 1/1/1 and yellow to 2/1/1.
- Later hotel receipts finance red 3/3/2 and yellow 2/2/2; yellow produces the final $330 Ventnor rent.
- Supported alternative: sell the three yellow houses, then mortgage any combination totaling at least $368 (e.g., all three red deeds for $340 plus Reading for $100), pay $950, and remain in game with $72. No oracle supports a claim about eventual win probability; only immediate legal survival is established.

## Window 2 — Claude Haiku 4.5, turn 153

### Decision window

| Relative | Decision | Turn | Actor | Canonical action |
|---:|---|---:|---|---|
| -5 | `...dec-000324` | 152 | Grok | build red layer |
| -4 | `...dec-000325` | 152 | Grok | build yellow layer |
| -3 | `...dec-000326` | 152 | Grok | add two red houses |
| -2 | `...dec-000327` | 152 | Grok | end turn |
| -1 | `...dec-000328` | 153 | Claude | mortgage States |
| 0 | `...dec-000329` | 153 | Claude | mortgage Virginia; automatic bankruptcy follows |
| +1 | `...dec-000330` | 154 | Gemini | third jail roll |
| +2 | `...dec-000331` | 154 | Gemini | pay required jail fine |
| +3 | `...dec-000332` | 154 | Gemini | sell three green houses |
| +4 | `...dec-000333` | 154 | Gemini | mortgage Boardwalk |
| +5 | `...dec-000334` | 154 | Gemini | mortgage Pennsylvania |

### Buildup

- Turn 150 start: Claude cash $986, estimated net worth $1,806, five deeds, no mortgages/buildings. It paid $950 at St. James and then voluntarily mortgaged Connecticut, Short Line, and B. & O., ending with $296.
- The model described this as survival from a failed “complete Light Blue” strategy; canonically it never owned a monopoly, so the missed-build retrospective was false.
- Grok used Claude's $950 and salary to build red to 3/3/2 and yellow to 2/2/2.

### Terminal obligation and legal menu

- Turn 153: Claude rolled five from St. James to three-house Kentucky and owed $700.
- First liquidation menu: cash $296, shortfall $404; mortgageable States and Virginia; no buildings to sell.
- Claude mortgaged States for $70. Second menu: cash $366, shortfall $334; only Virginia mortgageable.
- Claude mortgaged Virginia for $80. Maximum cash became $446, still $254 short. With no legal liquidation remaining, the engine automatically bankrupted Claude; no `declare_bankruptcy` model decision occurred.

### Adjudication and effects

- **Finding:** forced bankruptcy. The available asset sequence was fully exercised and could not cover $700.
- Reported amounts were inaccurate (Claude called the mortgages $60 and approximately $30), and it continued to mislabel pink deeds as light blue, but those semantic errors did not change the terminal solvency arithmetic.
- Events `...evt-002489`–`...-002496`: $446 and five deeds transfer to Grok. Claude retains its jail-free-card count in the bankrupt player record; it provides no cash path in the exposed menu.
- Supported alternative: none within the terminal legal menu. Earlier trading or different turn-150 buffer choices may have changed exposure, but no deterministic oracle establishes a superior historical policy.

## Window 3 — Gemini 3.5 Flash, turn 156

### Decision window

| Relative | Decision | Turn | Actor | Canonical action |
|---:|---|---:|---|---|
| -5 | `...dec-000340` | 154 | Gemini | offer full portfolio for $200 |
| -4 | `...dec-000341` | 154 | Grok | reject |
| -3 | `...dec-000342` | 154 | Gemini | mortgage Pacific |
| -2 | `...dec-000343` | 154 | Gemini | end turn |
| -1 | `...dec-000344` | 155 | Grok | end turn |
| 0 | `...dec-000345` | 156 | Gemini | declare bankruptcy |
| +1 | engine-only | 157 | — | game ends; Grok wins |

### Buildup and prior survival

- At turn 154 start Gemini was jailed with $279, estimated net worth $2,349, five deeds, and green 1/1/1.
- Third failed jail roll forced a $50 payment and movement to St. James. To cover $950, it sold all three green houses for $300 and mortgaged Boardwalk $200, Pennsylvania $160, and Electric $75. It paid with $964 and retained $14.
- It offered the full five-deed portfolio to Grok for $1,000, $500, then $200. Grok rejected each to avoid recapitalizing the sole opponent. Gemini mortgaged Pacific for $150 and ended with $164, leaving North Carolina unmortgaged.

### Terminal obligation and legal menu

- Turn 156: rolled eleven from St. James to two-house Ventnor and owed $330.
- Cash $164; only mortgageable deed North Carolina for $150; no buildings to sell; maximum cash $314.
- The menu allowed mortgage or declare bankruptcy. Gemini declared immediately and accurately reported the $16 gap.

### Adjudication and effects

- **Finding:** forced in outcome. Mortgaging North Carolina first could not avoid bankruptcy; it would only alter whether the transferred deed arrived mortgaged and how much cash passed through.
- Events `...evt-002596`–`...-002605`: $164 and five deeds transfer to Grok; `GAME_ENDED` emits at turn 157.
- The final $330 rent was enabled by assets inherited from GPT and developed with bankruptcy proceeds, closing the causal loop from the avoidable first elimination to the forced last elimination.
- No-oracle caveat: accepting Gemini's $200 portfolio offer might have prolonged play, but Grok's rejection is supported by its immediate win objective; this analysis does not assert counterfactual win probabilities.

## Reconciliation

- Three bankrupt players, all `bankrupt_to = Grok 4.3`, reconcile with one `GAME_ENDED/BANKRUPTCY` event.
- Classification: one avoidable declaration (GPT), one automatic forced bankruptcy after exhausting mortgages (Claude), one forced-in-outcome declaration with a $16 gap (Gemini).
- This is a single-run mechanism analysis, not a rate or ranking.
