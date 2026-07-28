# Bankruptcy Windows

Run: `mock-1038910349-f66fa07c`

This review treats bankruptcy as an engine/legal-state question first. “Avoidable” is used only when the visible liquidation menu demonstrates a unilateral way to pay. Negotiated rescues are identified as speculation unless an actual offer existed. No branch oracle was run.

## Reconciliation

| Eliminated player | Landing turn | Debt | Cash at prompt | Shortfall | Legal liquidation menu | Unilateral result | Creditor | Canonical evidence |
|---|---:|---:|---:|---:|---|---|---|---|
| Grok 4.3 | 114 | $600 Connecticut hotel rent | $295 | $305 | Mortgage Baltic and/or Tennessee; or bankruptcy | **Unavoidable.** Their combined mortgage proceeds are $120, below the $305 shortfall. | Claude | `dec-000257`; `evt-001880`–`001897`; `run/state/turn_0114.json` |
| Gemini 3.1 Pro Preview | 150 | $1,000 Pennsylvania three-house rent | $56 | $944 | Mortgage Marvin, Park Place, and/or Boardwalk; or bankruptcy | **Unavoidable.** Their combined mortgage proceeds are $515, below the $944 shortfall. | Claude | `dec-000348`; `evt-002549`–`002571`; `run/state/turn_0150.json` |
| OpenAI GPT 5.5 | 162 | $925 Illinois four-house rent | $213 | $712 | Bankruptcy only; no assets or buildings | **Unavoidable.** No unilateral liquidation action existed. | Claude | `dec-000363`; `evt-002682`–`002692`; `run/state/turn_0162.json` |

The engine represents these outcomes through the valid `declare_bankruptcy` action, `CASH_CHANGED` events with `BANKRUPTCY_CASH`/`BANKRUPTCY`, and zero-price creditor acquisitions. There is no separate `PLAYER_ELIMINATED` event type in this run. `GAME_ENDED` is the sole event at terminal index 163.

## Window 1 — Grok, turn 114

### Earlier causal buildup

Grok bought widely but never completed a monopoly or built. Its most important unrealized paths were orange (Tennessee while Claude held St. James and Gemini held New York), red (Kentucky/Illinois while Claude held Indiana), and green (Pennsylvania plus mortgaged North Carolina while Claude held Pacific). The repeated St. James pitches at turns 25 and 29 were based on a mistaken claim that St. James plus Tennessee completed orange; Claude correctly rejected because New York was still required (`trade-0012`, `trade-0013`). A strategically correct red proposal at turn 75—$300 plus Short Line for Indiana—was also rejected (`trade-0027`).

Claude's light-blue hotels caused two major realized shocks. Grok paid $550 at Oriental on turn 79 (`evt-001236`–`001238`). At turn 94, Connecticut's $600 rent forced mortgages of Pennsylvania, Illinois, and Kentucky; Grok then mortgaged Short Line for a buffer (`evt-001607`–`001629`). This survived the debt legally but left only Baltic and Tennessee unmortgaged. Passing Go at turn 109 restored cash to $295, but it did not restore mortgage capacity.

### Five decisions before

| Relative position | Decision | Turn | Action | Relevance |
|---:|---|---:|---|---|
| -5 | `dec-000252` | 113 | Grok drops from Ventnor auction | Preserves $295; Ventnor offers no direct set. |
| -4 | `dec-000253` | 113 | GPT bids $61 | Blocks Gemini yellow; no effect on Grok's liquidity. |
| -3 | `dec-000254` | 113 | Claude drops | Leaves GPT the blocker and preserves Claude's cash. |
| -2 | `dec-000255` | 113 | Gemini drops | Forced by GPT's bid exceeding Gemini's $60 cash. |
| -1 | `dec-000256` | 113 | Gemini ends turn | No rescue or Grok-directed negotiation occurs. |

### Bankruptcy decision and legal proof

The visible pre-state is `run/state/turn_0114.json`: Grok has $295 and lands on Connecticut. The prompt in `decision_started` for `dec-000257` states `owed_amount: 600`, `shortfall: 305`, and only `BALTIC_AVENUE` and `TENNESSEE_AVENUE` as mortgageable. Their canonical mortgage values are $30 and $90. Even both actions would raise cash to $415, still $185 short. No buildings existed to sell. Grok's private report understated Tennessee's mortgage as “~50,” but its conclusion remained correct. The declared bankruptcy is therefore unilaterally unavoidable.

No trade action was legal in the liquidation menu, and no earlier live rescue offer existed. A hypothetical player gift or asset purchase is a negotiated-rescue counterfactual, not a demonstrated path. No branch/oracle claim is made.

At `evt-001887`–`001889`, $295 transferred to Claude and Grok's balance became zero. Seven deeds moved to Claude at `evt-001890`–`001896`, with mortgage state preserved. This completed Claude's red group immediately and green group after unmortgaging.

### Five decisions after

| Relative position | Decision | Turn | Action | Consequence |
|---:|---|---:|---|---|
| +1 | `dec-000258` | 115 | GPT mortgages Ventnor | Raises $130 for pink development. |
| +2 | `dec-000259` | 115 | GPT builds 1/1/1 | Pink reaches 3/3/3. |
| +3 | `dec-000260` | 115 | GPT ends | Leaves only $6 visible at the next pre-state. |
| +4 | `dec-000261` | 116 | Claude unmortgages Illinois | Begins activation of inherited red. |
| +5 | `dec-000262` | 116 | Claude unmortgages Kentucky | Makes all three reds buildable. |

Within the same turn 116, `dec-000263` and `dec-000265` build red to 4/4/4; `dec-000264`/`000266` restore the inherited greens. The creditor transfer, not merely player-count reduction, is the main downstream mechanism.

## Window 2 — Gemini, turn 150

### Earlier causal buildup

Gemini accumulated Atlantic and Marvin but lost Ventnor at the turn-113 auction because its $60 cash made `start_auction` the only legal landing action; GPT bid $61. GPT sold mortgaged Ventnor back for Gemini's maximum feasible $47 at turn 119 (`trade-0032`), completing yellow but leaving no development cash.

Gemini's more consequential engine was dark blue. It bought mortgaged Boardwalk from GPT for $130 at turn 81, won Park Place for $600 at turn 86, unmortgaged Boardwalk, and built one house each at turn 89. The engine never collected a large rent. A $390 North Carolina hit at turn 147 forced sale of both dark-blue houses and mortgage of New York (`evt-002478`–`002489`), leaving $56.

Turn 145 added the entire mortgaged pink group for $175 plus Mediterranean (`trade-0035`), followed by accepting Mediterranean back for zero (`trade-0040`). These holdings increased nominal estate size but not immediate mortgage availability: the pinks and Mediterranean arrived mortgaged. They later transferred to Claude when Gemini failed.

### Five decisions before

| Relative position | Decision | Turn | Action | Relevance |
|---:|---|---:|---|---|
| -5 | `dec-000343` | 148 | GPT offers $275 for Boardwalk | Would provide cash and split dark blue. |
| -4 | `dec-000344` | 148 | Gemini rejects | Prefers keeping monopoly; notes $200 mortgage capacity. |
| -3 | `dec-000345` | 148 | GPT ends | No acquisition occurs. |
| -2 | `dec-000346` | 149 | Claude builds one on each green | Green reaches 3/3/3. |
| -1 | `dec-000347` | 149 | Claude ends | Leaves Gemini facing the developed green corridor. |

The rejected Boardwalk sale is an earlier legal alternative, not a legal action at the bankruptcy prompt. Acceptance would have changed cash and ownership, but whether it would have produced eventual survival requires a branch; it is therefore not proof that bankruptcy was avoidable.

### Bankruptcy decision and legal proof

`run/state/turn_0150.json` records the visible pre-state with Gemini at $56. The `dec-000348` prompt states a $1,000 Pennsylvania rent, $944 shortfall, and exactly three mortgageable deeds: Marvin ($140), Park Place ($175), and Boardwalk ($200). Total unilateral proceeds are $515; cash plus all three would be $571, still $429 short. All other potentially valuable deeds were already mortgaged, and no buildings remained. Bankruptcy was unilaterally unavoidable.

No trade action was legal and no rescue offer was pending. GPT had $277 but no mechanism in the liquidation menu to transfer it. A rescue is thus speculative. Gemini's reported calculation matches the menu exactly.

At `evt-002556`–`002558`, $56 moved to Claude. Twelve deeds moved at `evt-002559`–`002570`, including dark blue, yellow, pink, Water Works, and Mediterranean. The transfer briefly reduced Claude to $225 cash after required mortgage-interest effects captured in the following pre-state, but expanded its ownership dramatically.

### Five decisions after

| Relative position | Decision | Turn | Action | Consequence |
|---:|---|---:|---|---|
| +1 | `dec-000349` | 152 | Claude ends | Heads-up ownership concentration remains. |
| +2 | `dec-000350` | 153 | Claude ends | No asset disposition. |
| +3 | `dec-000351` | 154 | GPT rolls from jail | Fails; remains sheltered. |
| +4 | `dec-000352` | 155 | Claude ends | No change. |
| +5 | `dec-000353` | 156 | Claude ends | Passes Go via Chance-to-Reading route. |

Turn 151 contains no decision because GPT is automatically sent to jail. That non-decision turn is retained in the chronological ledger.

## Window 3 — GPT, turn 162

### Earlier causal buildup

GPT's path was unusually active: 40 proposals, three auction wins, and a developed pink monopoly. The turn-80 $480 Virginia auction completed pink; an immediate $550 Vermont hotel hit at turn 81 forced three mortgages and side-asset sales. GPT nevertheless built pink to 3/3/3 by turn 115. Repeated smaller obligations sold houses, and turn 145's $875 Indiana rent forced sale of all remaining buildings and mortgage of all pinks (`evt-002307`–`002338`).

The accepted turn-145 trade converted the mortgaged pink set into $175 plus Mediterranean, then GPT mortgaged and gave Mediterranean back to Gemini. GPT ended turn 145 with $277 and zero deeds. Subsequent offers to buy dark blues at turn 148 and Boardwalk at turn 159 were rejected. Thus the final thirteen-turn survival stretch had no liquidation assets.

### Five decisions before

| Relative position | Decision | Turn | Action | Relevance |
|---:|---|---:|---|---|
| -5 | `dec-000358` | 159 | GPT offers $200 for Boardwalk | Attempt to reacquire an asset; rejected. |
| -4 | `dec-000359` | 159 | Claude rejects | Preserves ownership concentration. |
| -3 | `dec-000360` | 159 | GPT ends | Retains cash only. |
| -2 | `dec-000361` | 160 | GPT ends | Lands on mortgaged New York; no rent. |
| -1 | `dec-000362` | 161 | Claude ends | No change before GPT's roll. |

### Bankruptcy decision and legal proof

`run/state/turn_0162.json` shows GPT at $213 with no deeds. `dec-000363` states $925 Illinois rent and a $712 shortfall; `available_actions` contains only `declare_bankruptcy`, with empty mortgageable and sellable lists. This is the strongest possible unilateral-unavoidability proof in the artifact contract.

The action transfers $213 to Claude at `evt-002689`–`002691`. There are no property transfers because GPT owns none. The next and final event is `evt-002693` at turn index 163, `GAME_ENDED`.

### After-window limitation

There cannot be five subsequent decisions: `dec-000363` is the final decision in the run. The only subsequent canonical artifact is `evt-002693`. The asymmetry is an endpoint property, not missing review coverage.

## Cross-window mechanism and claim boundary

All three declarations were correct under their visible unilateral menus. Grok and Gemini theoretically had mortgage actions but insufficient total proceeds; GPT had none. Earlier choices plainly shaped exposure—Grok's fragmented estate, Gemini's $600 Park acquisition and refusal to split dark blue, GPT's development/liquidation cycle—but “this earlier action caused an avoidable bankruptcy” would require a declared branch model. The supported single-run conclusion is narrower: Claude's rent engines repeatedly forced liquidation, and creditor transfers then expanded Claude's monopolies, creating a positive-feedback endgame.
