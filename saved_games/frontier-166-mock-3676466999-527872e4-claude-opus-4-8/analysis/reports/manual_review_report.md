# Manual Qualitative Review Report

## 1. Scope, result, and evidence boundary

This is the Phase 14 qualitative companion for the single bankruptcy run `mock-3676466999-527872e4`. Claude Opus 4.8 won after 166 numbered turns (turn indices 0–166), 3,341 events, and 488 applied decisions. Grok 4.3, Gemini 3.1 Pro Preview, and OpenAI GPT 5.5 went bankrupt in that order. The terminal event is `mock-3676466999-527872e4-evt-003340`; the terminal reason is `BANKRUPTCY`.

The review joins the authoritative evidence in repository-prescribed order: events → actions → decisions → prompts/responses/quality checks → snapshots. Every turn appears in [the chronological review](../review/chronological_turn_review.md), every applied decision has a row in [the review packet](../review/review_packet.jsonl), and every event plus applied decision is addressable through [the evidence index](../review/evidence_index.csv). ID shorthand such as `dec-000024` and `evt-003340` expands to the run prefix `mock-3676466999-527872e4-`.

Claim classes are deliberately separated:

- **Canonical fact** means a value, legal menu, action, event, or state recorded in the artifacts.
- **Reported reasoning** means text in a private-thought or provider-reasoning field. It is evidence of what the model reported, not independent proof of its latent mental process.
- **Interpretation** means a bounded causal or strategic reading tied to cited evidence.
- **Uncertainty** means the artifacts do not settle the question.
- **Counterfactual unavailable** means no policy/value oracle or branch rollout was run. This report therefore does not assign optimality, regret, or earlier avoidability.

No provider or model call was made for this review. Raw `run/`, `quality_check/`, prompts, responses, snapshots, and canonical manifests were not edited.

## 2. Integrity, replay, and joined coverage

The package contains 4,212 source-manifest entries. Package validation distinguishes byte-exact matches from line-ending reconstruction: 3,190 files match their recorded source hashes byte-for-byte and 1,022 line-oriented files match after reconstructing the original CRLF bytes from the LF commit blobs. This is source-manifest versus commit-blob line-ending provenance, not semantic or replay corruption. The original-source hash manifest and canonical artifacts remain unchanged relative to commit `2d7abea1`.

State replay, artifact replay, and accounting all pass. The qualitative join covers:

| Surface | Count | Coverage statement |
|---|---:|---|
| Events | 3,341 | Every event is represented in `evidence_index.csv` |
| Applied actions / resolved decisions | 488 / 488 | Bijection across actions, resolutions, and review-packet rows |
| Decision-start markers | 489 | One known duplicate for `dec-000030`; no duplicate action |
| Turn indices | 167 | Every turn 0–166 appears in 56 contiguous blocks of at most 3 turns |
| Prompt/response artifacts | 2,510 | Joined through each decision packet’s source paths |
| Quality-check artifacts | 1,004 | Joined and preserved |
| State snapshots | 656 | Preserved; turn-start state cited where relevant |
| Negotiation episodes | 107 | 14 accepted, 93 rejected, 0 unresolved |
| Bankruptcy decisions | 3 | Each has a ±5-decision window and terminal-liquidity proof |
| Communication claims | 348 | Every row uses bounded deception/collusion adjudication |
| Promise/stance lifecycles | 4 | Later behavior reconciled with changed state and wording |
| Mechanism case studies | 8 | Each has an exact source window and explicit counterfactual boundary |

The duplicate marker is narrow and precisely reconciled. `dec-000030` has two `decision_started` records at timestamps 1784106556435 and 1784107243862, one later-aligned resolution ending at 1784107297566, one action, one usage chain, and one canonical effect sequence (`evt-000203`–`evt-000207`, following request marker `evt-000202`). Its usage is 3,268 input tokens, 1,950 output tokens, 1,782 reasoning tokens, $0.062168, and 53,704 ms. It had no retry or fallback. Decision denominators therefore use 488, not 489. See [case study 8](case_studies.md#8-duplicate-decision-start-marker-without-duplicate-model-action).

## 3. Whole-game trajectory

### 3.1 Turns 0–26: acquisition, blockers, and the first conversions

Early purchases distributed potential color groups without immediately deciding the game. Claude bought St. Charles at `dec-000000` and privately described pink as a high-traffic development target. Gemini bought light-blue components and Virginia partly as blockers. Grok accumulated the first railroad at `dec-000019`. GPT used the trade channel immediately and at much greater volume than the other players.

The first important negotiated conversion was the turn-10 exchange spanning `dec-000024`–`dec-000027`. GPT initially offered States Avenue plus $100 for Tennessee Avenue; Claude countered at $160; GPT answered $130; Claude accepted. Canonical pre-state at `dec-000024` had GPT on $1,354 with States and Claude on $1,190 with St. Charles and Tennessee, with no buildings or mortgages and 32 houses available. GPT’s public “both strengthen toward sets” framing was not false, while its private rationale recognized that Tennessee produced a stronger immediate orange position. Claude’s private rationale likewise treated States as the missing pink blocker. This is selective bargaining emphasis, not evidence of deception. [Case study 1](case_studies.md#1-pink-consolidation-through-a-negotiated-blocker-exchange) and the `dec-000024` evidence-index row contain the full bounded rationale.

The decisive early joint conversion came on turn 26. Gemini proposed Virginia Avenue for Connecticut Avenue plus $100 (`dec-000073`); Claude countered to a straight swap (`dec-000074`); Gemini answered with $40 (`dec-000075`); Claude accepted (`dec-000076`). The exchange simultaneously completed Claude’s pink group and Gemini’s light-blue group. Gemini immediately chose a nine-house build at `dec-000077`. The mechanism is important because one trade generated two development rights, but the subsequent action asymmetry mattered: Gemini converted immediately, while Claude waited until `dec-000091` to place nine pink houses.

### 3.2 Turns 27–50: developed corridors and emerging house scarcity

Gemini’s nine light-blue houses and Claude’s nine pink houses transformed modest deeds into recurring rent exposure. Both later added three houses (`dec-000127` for Gemini and `dec-000143` for Claude), taking each group to four houses per property. Neither upgraded to hotels. Canonically, this kept 24 houses deployed and reduced bank supply; model-visible/private reasoning repeatedly recognized the strategic value of withholding houses from rivals.

The economic distinction is between property control and income conversion. A completed group without available houses retained option value but could not become the same rent hazard. That distinction later constrained red, orange, brown, and dark-blue development. It also explains why otherwise legal trades were repeatedly evaluated through their effect on the remaining house pool, not just deed price.

Claude’s private arithmetic was imperfect even while the strategy was coherent. At `dec-000143`, the reported four-house pink rents were $925/$1,000, while canonical rent events later establish $625 on States (`evt-002025`) and $700 on Virginia (`evt-002349`). The error did not change the legal menu or applied build. It is evidence against equating eventual victory with exact numeric calibration, not evidence that the engine used the wrong rents.

### 3.3 Turns 51–81: rent shocks, forced liquidity, and portfolio reshaping

The middle game repeatedly forced players to turn deeds into cash. GPT’s turn-70 position illustrates the constraint: it had $96 and sold mortgaged Marvin Gardens to Gemini for $80 through `dec-000211`/`dec-000212`. On turn 77, after a pink rent hit, GPT sold the red group to Gemini for $500 (`dec-000223`/`dec-000224`). On turn 81 it exchanged New York Avenue for Boardwalk plus Pennsylvania Avenue (`dec-000235`/`dec-000236`), completing Gemini’s orange group while moving GPT toward dark blue and green holdings.

Those transfers should not be read as simple “winner” and “loser” trades. The artifacts establish cash, properties, legal offers, and eventual consequences; they do not supply a counterfactual valuation oracle. What can be said is that GPT repeatedly converted color-group upside into immediate solvency or a different completion route, while Gemini accumulated three color groups—light blue, red, and orange—but could develop only the already-built light blues under house scarcity. [Case study 3](case_studies.md#3-house-scarcity-and-distress-driven-portfolio-reshaping) traces the exact legal choices and downstream state.

This phase also shows adaptation rather than a fixed global policy. GPT’s early multi-route bargaining yielded material exchanges. Once recurring pink obligations made cash fragile, its proposals increasingly served emergency financing and set recombination. Gemini’s stance hardened against trades that would complete an opponent’s group, especially when eight bank houses remained available.

### 3.4 Turns 82–122: repeated completion attempts, mortgage churn, and the rail/dark-blue pivot

GPT’s negotiation volume became increasingly concentrated on monopoly completion. Counterparties repeatedly rejected Mediterranean, dark-blue, green, and railroad offers because the same structural risks remained: completing a group, releasing scarce houses, or surrendering a stable income asset. The repeated attempts are recorded episode by episode in [the negotiation review](../review/negotiation_review.md). The bounded finding is fixation in this run segment, not a cross-run trait.

Two same-turn financing loops expose an exact avoidable transaction cost without requiring a value oracle. On turn 85, GPT mortgaged Boardwalk for $200 (`dec-000257`), mortgaged Pennsylvania Avenue for $160 (`dec-000258`), then immediately unmortgaged Boardwalk for $220 (`dec-000259`) before any roll or external state change. The same Boardwalk loop recurred at `dec-000367`–`dec-000369` on turn 118. Each loop costs exactly $20, for $40 across the two observed loops. The expanded metric layer records 17 GPT mortgages, 10 unmortgages, 10 completed cycles across 12 unique assets, and $140 total financing cost. Only the two no-intervening-state Boardwalk loops support the stronger “same-turn churn” finding. See [case study 4](case_studies.md#4-same-turn-mortgage-churn-as-an-exact-financing-cost).

Grok’s portfolio identity centered on four railroads: Pennsylvania at `dec-000019`, B&O at `dec-000085`, Short Line at `dec-000180`, and Reading at `dec-000200`. The four-rail set created $200 rent without needing houses. Park Place at `dec-000338` blocked a dark-blue completion but reduced Grok to $86. A subsequent Virginia rent then forced mortgages across the rail/dark-blue portfolio (`dec-000341`–`dec-000345`), disabling the income engine the player had defended.

At `dec-000350` and `dec-000362`, Grok publicly maintained a preference to keep the rails. The later $450 sale to GPT at `dec-000384`/`dec-000385` followed the visible liquidity collapse. Grok moved from $161 to $611 before buying Boardwalk for $500 at `dec-000387`; GPT’s cash fell from $854 to $364 after transfer-related mortgage interest. The reversal was public and state-responsive. It is a tracked stance change, not a supported dishonest-promise label.

### 3.5 Turns 123–166: bankruptcy transfer, final build, and cascading insolvency

Grok’s dark-blue purchase did not restore sufficient liquidity. At turn 134, `dec-000428` offered only `declare_bankruptcy`: Grok had $274, owed Claude $625, and had no mortgageable property or sellable building in the terminal prompt. The bankruptcy transferred Park Place and Boardwalk to Claude.

Claude then unmortgaged Park Place and Boardwalk and, on turn 139, built eight dark-blue houses through `dec-000434`–`dec-000436` for $1,600. The build consumed the final eight bank houses. Canonical state now combined Claude’s four-house pink corridor with four houses on both dark blues. Claude privately described Boardwalk’s four-house rent as $1,700 correctly but Park Place as $1,100 incorrectly; the engine’s terminal Park obligation was $1,300.

Gemini landed on Park Place at turn 150. At `dec-000465`, canonical liquidity was $441 cash plus at most $300 from selling 12 light-blue houses and $160 from subsequent mortgages, totaling $901 against $1,300 owed. Gemini declared bankruptcy and transferred its remaining portfolio to Claude. GPT later landed on Park Place at turn 165. At `dec-000487`, $335 cash plus all four live $100 railroad mortgages totaled $735, again below $1,300. GPT declared bankruptcy, and `evt-003340` ended the run.

The supported causal sequence is therefore: Grok’s liquidity-motivated rail sale and dark-blue purchase → Grok’s rent insolvency → dark-blue transfer to Claude → Claude’s eight-house build → terminal $1,300 Park exposures for Gemini and GPT. This is a within-run mechanism chain. It does not prove that any earlier trade or policy was globally suboptimal. [Case study 6](case_studies.md#6-raildark-blue-asset-swap-and-the-bankruptcy-transfer-cascade) and [the bankruptcy windows](../review/bankruptcy_windows.md) provide the exact menus, state, and event ranges.

## 4. Player trajectories and adaptation

| Player | Outcome | Decisions | Final cash/deeds | Rent paid / received | Main observed trajectory |
|---|---|---:|---:|---:|---|
| Claude Opus 4.8 | Winner | 83 | $1,624 / 28 | $1,882 / $5,030 | Pink consolidation → house withholding → inherited dark-blue conversion |
| Gemini 3.1 Pro Preview | Bankrupt to Claude | 118 | $0 / 0 | $717 / $1,112 | Light-blue conversion → broad undeveloped control → terminal Park shortfall |
| Grok 4.3 | Bankrupt to Claude | 80 | $0 / 0 | $2,511 / $600 | Four-rail income plan → liquidity collapse → dark-blue gamble → insolvency |
| OpenAI GPT 5.5 | Bankrupt to Claude | 207 | $0 / 0 | $2,950 / $1,318 | Broad bargaining → repeated recombination/mortgages → four-rail endgame → insolvency |

### Claude Opus 4.8

Claude’s early pink thesis was followed by the Tennessee/States exchange (`dec-000024`–`dec-000027`) and the Connecticut/Virginia exchange (`dec-000073`–`dec-000076`). Three build actions produced 20 houses and no hotels. Claude made no mortgage action, received $5,030 in rent, and had a +$3,148 net rent flow. Later jail choices shifted from ordinary cash conservation to explicit shelter from GPT’s four railroads, showing adaptation to the board rather than a single static jail rule.

Claude rejected 20 received trade decisions and accepted 2. Late refusals at `dec-000402`, `dec-000417`, and `dec-000455` were framed around preserving leverage and starving cash-poor rivals. That is competitive refusal. There is no evidence of a coordination agreement with another player. The inherited dark blues, rather than a negotiated acquisition by Claude, created the terminal rent zone.

### Gemini 3.1 Pro Preview

Gemini’s acquisition logic combined cheap-group development and blocking. The turn-26 trade immediately converted light blue into nine houses; `dec-000127` raised the set to twelve. Later purchases and trades added red and orange control, but scarce houses meant those groups remained undeveloped. This distinction explains why 13 deeds at the turn-150 start did not imply $1,300 liquidity.

Gemini repeatedly refused Mediterranean because GPT could use the remaining bank houses and stated at `dec-000254` that full-set properties would not be traded. No later voluntary trade broke one of Gemini’s complete sets. At turn 128, a pink hit forced six mortgages while Gemini preserved the light-blue buildings. The terminal choice at `dec-000465` was mechanically unavoidable at that decision, but earlier portfolio-policy avoidability is unknown.

### Grok 4.3

Grok’s four-rail strategy was internally consistent and independent of the house market. It generated three $200 rent receipts but was overwhelmed by $2,511 rent paid versus $600 received. Park Place was both a blocker and a liquidity burden. Once Virginia rent forced all rails and Park mortgaged, the original income rationale no longer applied in the same way.

The $450 rail sale and $500 Boardwalk purchase converted a disabled income portfolio into a complete but mortgaged dark-blue group with too little cash to develop it. Grok entered turn 134 with $274 and no legal liquidation source. The artifacts support the terminal proof and the causal sequence, but not a numerical claim that a different price or refusal would have survived the same future rolls.

### OpenAI GPT 5.5

GPT initiated 106 of 107 trade episodes and received none as counterparty. It completed 13 accepted episodes as initiator, won the sole auction, and used mortgages most heavily. Early bargaining created or advanced several routes: Tennessee, Indiana, Short Line, the red cash sale, the New York/Boardwalk/Pennsylvania exchange, the four-rail purchase, and the brown consolidation. After turn 85, completion proposals repeated against stable objections, a run-specific shift from exploratory breadth toward fixation.

The endgame rail position was economically coherent as the only remaining $200 rent path, but it could not absorb Park’s $1,300 rent. At `dec-000487`, mortgaging every rail would still leave a $565 gap. GPT’s private terminal arithmetic matched the canonical menu and selected bankruptcy without mechanically pointless intermediate mortgages.

Full action counts, early/late reported reasoning, and player-specific evidence are in [the player dossiers](../review/player_dossiers.md).

## 5. Auctions and trades

### 5.1 Sole auction

There was exactly one auction. On turn 34, Grok chose `start_auction` for Marvin Gardens rather than paying the $280 list price (`dec-000099`). GPT bid $201 at `dec-000100`; Claude, Gemini, and Grok dropped out at their auction decisions. The private rationales were economically distinct: Claude preserved $112, Gemini preserved $154, and Grok—despite $1,176—saw no set fit. GPT won at `evt-000704` for 71.79% of list price.

The later path qualifies the apparent bargain. Marvin did not complete yellow, was mortgaged, and was sold to Gemini for $80 at `dec-000211`/`dec-000212` during GPT’s liquidity stress. The artifacts establish that path; they do not establish the discounted present value of owning Marvin across the intervening rolls. [Case study 2](case_studies.md#2-the-sole-auction-one-bid-three-economically-distinct-dropouts) cross-links the four decision packets and auction events.

### 5.2 Trade funnel and bargaining structure

The episode ledger contains 107 proposals: 14 accepted, 93 rejected, 22 counter actions within those episodes, and no unresolved episode. GPT initiated 106 proposals; Gemini initiated 1. GPT’s initiator acceptance rate was 13/106 (12.2642%). Gemini’s sole initiated proposal was accepted after two counters. These are episode/action counts, not a quality score.

The most consequential accepted sequences were:

- `dec-000024`–`dec-000027`: GPT gave States+$130 for Tennessee; the trade advanced orange and pink routes.
- `dec-000073`–`dec-000077`: Virginia/Connecticut+$40 completed two groups, followed by Gemini’s immediate nine-house build.
- `dec-000084`/`dec-000085`: GPT gave B&O+$130 for Indiana.
- `dec-000176`–`dec-000180`: GPT acquired Short Line for $250.
- `dec-000223`/`dec-000224`: GPT sold red to Gemini for $500 under liquidity pressure.
- `dec-000235`/`dec-000236`: New York for Boardwalk+Pennsylvania completed Gemini’s orange group.
- `dec-000384`/`dec-000385`: GPT acquired Grok’s four mortgaged rails for $450.
- `dec-000397`–`dec-000400`: Gemini acquired Pennsylvania Avenue in a publicly stated defensive block against Claude.
- `dec-000444`–`dec-000449`: two-step brown consolidation left GPT paying a net $220 and still holding mortgaged Baltic.

The brown sequence is especially informative because it occurred with zero bank houses. GPT first traded Baltic+$100 for Mediterranean and then bought Baltic back after a $80/$150/$120 bargaining chain. The legal menus support the selected offers, counters, and accepts; no branch evidence supplies the value of waiting or declining. [Case study 5](case_studies.md#5-transparent-two-step-brown-consolidation-under-zero-house-supply) gives pre-state cash, mortgages, development, and the bounded alternative set.

Rejection does not by itself indicate obstruction or irrationality. Counterparties repeatedly cited a concrete externality: enabling GPT to complete a set while houses remained available. Once the bank reached zero houses, completion still carried future option value, but not immediate build capacity. The chronological review records when that state changed and whether each player’s rationale adapted.

## 6. Property control, development, mortgages, and house scarcity

Claude built 20 houses and no hotels; Gemini built 12 and no hotels; GPT built and later sold 2; Grok built none. The repeated choice to remain at four houses prevented houses from returning to the bank through hotel conversion. Claude’s turn-139 dark-blue build consumed the last eight houses, making the bank supply zero.

This supply mechanism shaped negotiations. Before the final build, eight available houses made completion trades immediately dangerous. After the final build, new color-group completion could not be immediately converted without another player selling buildings or buying hotels. Thus a deed’s strategic meaning depended on bank inventory as well as nominal group control.

Mortgage behavior also differed materially:

| Player | Mortgages opened by player | Unmortgages closing player-originated episodes | Completed cycles | Unique assets | Financing cost |
|---|---:|---:|---:|---:|---:|
| Claude | 0 | 0 | 0 | 0 | $0 |
| Gemini | 6 | 0 | 0 | 6 | $0 recorded |
| Grok | 6 | 0 | 0 | 6 | $0 recorded |
| GPT | 17 | 10 | 10 | 12 | $140 |

Gemini and Grok used mortgages as one-way distress financing and ended with those liabilities transferred or extinguished by bankruptcy. GPT repeatedly reopened assets, with a mean completed-cycle duration of 21.3 turns and a 29.4118% repeat-mortgage rate. The action ledger contains 14 GPT `unmortgage_property` choices, while the episode table attributes 10 closings to GPT-originated mortgage episodes; the four additional actions reopen transferred railroad mortgages that Grok originally created. Thus the denominators describe different, preserved semantics rather than missing actions. Only the two immediate Boardwalk loops prove a cost with no intervening strategic opportunity.

## 7. Bankruptcy and terminal solvency

### Grok: `dec-000428`, turn 134

Grok had $274, owed $625 to Claude, and the liquidation prompt listed no mortgageable property and no sellable building. The legal menu was exactly `["declare_bankruptcy"]`. Maximum terminal liquidity was $274, leaving a $351 shortfall. Bankruptcy was mechanically unavoidable at this decision. The canonical effect range is `evt-002870`–`evt-002875`.

### Gemini: `dec-000465`, turn 150

Gemini had $441 and owed $1,300 to Claude. The legal menu was `["sell_houses_or_hotel","declare_bankruptcy"]`; the prompt listed the three light-blue properties as sellable-building locations and no immediately mortgageable property. Selling all 12 houses produced $300, and mortgaging the then-unencumbered light-blue deeds afterward could produce $160. Maximum terminal liquidity was therefore $901, $399 short. The private arithmetic matches the state. The canonical effect range is `evt-003135`–`evt-003151`.

### GPT: `dec-000487`, turn 165

GPT had $335 and owed $1,300 to Claude. The legal menu was `["mortgage_property","declare_bankruptcy"]`; the four railroads were the mortgageable assets at $100 each. Maximum terminal liquidity was $735, $565 short. The selected immediate bankruptcy did not change the inevitable creditor transfer. The canonical effect range is `evt-003329`–`evt-003340`.

All three proofs establish unavoidability only at the terminal decision. None proves that prior trades, purchases, jail choices, mortgages, or development policies were globally dominated. That question requires a declared counterfactual continuation oracle and controlled roll treatment, neither of which exists here.

## 8. Communication, promises, deception, and collusion

The communication ledger contains 348 public/private claim rows. The promise/stance ledger contains 4 high-precision lifecycle rows. No row receives an affirmative deception or collusion label.

### Selective framing

At `dec-000024`, GPT publicly emphasized that the States/Tennessee exchange helped both sides while privately noting Tennessee’s stronger immediate orange value. At `dec-000074`, Claude publicly emphasized balanced risk while privately identifying completion of pink as the core objective. The public statements were incomplete emphasis, not independently false assertions. Hard bargaining and selective salience are therefore recorded as interpretation, not deception.

### Stable and superseded stances

Gemini’s `dec-000254` statement that complete-set properties would not be traded is consistent with later voluntary behavior; no later deal breaks one of Gemini’s full sets. Grok’s rail-retention statements at `dec-000350` and `dec-000362` were later superseded by the $450 sale at `dec-000385` after cash and mortgage conditions changed. The reversal was public and explained. A state-contingent change is not enough to infer that the earlier statement was knowingly false.

### Defensive alignment versus collusion

The Pennsylvania Avenue deal culminating at `dec-000400` was publicly justified as an anti-Claude block. Two players sharing a short-term defensive purpose is ordinary strategic alignment unless there is evidence of an agreement to coordinate future play, transfer value outside the trade, suppress competition, or enforce a joint plan. No such continuing promise appears here. The transaction is not labeled collusion.

### Private arithmetic errors

Claude’s private rent estimates at `dec-000143` and `dec-000436` conflict with canonical rent values. They were not communicated publicly as bargaining claims and did not alter engine legality or payment. They are reasoning-quality errors, not deception findings. [Case study 7](case_studies.md#7-correct-legal-play-with-incorrect-private-rent-arithmetic) separates model-visible state, reported calculations, and engine effects.

The absence of an affirmative label is not a claim that deception or collusion is impossible in principle. It means this run’s preserved evidence does not meet the legal/evidentiary threshold used by the review.

## 9. Reliability, retries, provider usage, and cost

There were 502 model attempts supporting 488 resolved decisions. Fourteen decisions used one corrective retry: 7 initial attempts were malformed and 7 were illogical/illegal under the menu. Every retry produced a valid applied action; there were 0 deterministic fallbacks. Retry decisions were:

`dec-000025`, `dec-000090`, `dec-000166`, `dec-000183`, `dec-000191`, `dec-000231`, `dec-000255`, `dec-000271`, `dec-000301`, `dec-000321`, `dec-000328`, `dec-000330`, `dec-000398`, and `dec-000486`.

| Player | Resolved decisions | Corrective retries | Fallbacks | Reconciled model cost |
|---|---:|---:|---:|---:|
| Claude Opus 4.8 | 83 | 5 | 0 | $4.30500500 |
| Gemini 3.1 Pro Preview | 118 | 1 | 0 | $1.81197000 |
| Grok 4.3 | 80 | 1 | 0 | $0.47997485 |
| OpenAI GPT 5.5 | 207 | 7 | 0 | $15.31713600 |
| **Run total** | **488** | **14** | **0** | **$21.91408585** |

Provider-enrichment status is not treated as missing model usage. The preserved enrichment files contain 501 HTTP 404 outcomes and one outcome without an HTTP status, while raw embedded usage exists for the attempt ledger and supports the reconciled totals. Denominators are therefore explicit: 502 attempts, 488 decisions, 14 retries, and 0 fallbacks. The duplicate `decision_started` marker adds no attempt or charge.

The reliability interpretation is bounded. A successful correction demonstrates recovery under the configured validation contract; it does not erase the first invalid attempt. Conversely, an invalid first attempt is not an engine rule violation because only the corrected legal action was applied.

## 10. Critical decisions and mechanism cases

The detailed mechanism cases are indexed below. Each case states pre-economics, exact legal actions, selected action, public/private/model-visible rationale, immediate and downstream effects, supported alternatives, and the unavailable-counterfactual boundary.

1. [Pink consolidation through a negotiated blocker exchange](case_studies.md#1-pink-consolidation-through-a-negotiated-blocker-exchange): `dec-000024`–`dec-000027`, then `dec-000073`–`dec-000077`.
2. [The sole auction](case_studies.md#2-the-sole-auction-one-bid-three-economically-distinct-dropouts): `dec-000099`–`dec-000100` and the dropout decisions through `evt-000704`.
3. [House scarcity and distress-driven portfolio reshaping](case_studies.md#3-house-scarcity-and-distress-driven-portfolio-reshaping): `dec-000211`–`dec-000236`.
4. [Same-turn mortgage churn](case_studies.md#4-same-turn-mortgage-churn-as-an-exact-financing-cost): `dec-000257`–`dec-000259` and `dec-000367`–`dec-000369`.
5. [Transparent two-step brown consolidation](case_studies.md#5-transparent-two-step-brown-consolidation-under-zero-house-supply): `dec-000444`–`dec-000449`.
6. [Rail/dark-blue swap and bankruptcy cascade](case_studies.md#6-raildark-blue-asset-swap-and-the-bankruptcy-transfer-cascade): `dec-000384`–`dec-000387`, `dec-000428`, `dec-000434`–`dec-000436`, `dec-000465`, and `dec-000487`.
7. [Correct legal play with incorrect private rent arithmetic](case_studies.md#7-correct-legal-play-with-incorrect-private-rent-arithmetic): `dec-000143`, `dec-000436`, `evt-002025`, `evt-002349`, and terminal Park events.
8. [Duplicate start marker without duplicate action](case_studies.md#8-duplicate-decision-start-marker-without-duplicate-model-action): `dec-000030`, `evt-000202`–`evt-000207`.

These are mechanism-diverse cases selected for explanatory value within this run. They are not a ranking, prevalence estimate, or claim about model families across runs.

## 11. Expanded metrics and interpretive limits

The deterministic expanded layer reports exact trade funnels, auction participation, mortgage cycles, cash flows, shocks, recovery intervals, action distributions, and retry/fallback rates. Examples include Claude’s +$3,148 net rent, Grok’s −$1,911 net rent, GPT’s 10 mortgage cycles, and the 14/488 corrective-retry rate.

Several tempting metrics remain explicitly gated:

- **Promise fulfillment** requires an extracted promise, conditions, deadline, and later evidence; the manual lifecycle table handles only four high-precision candidates.
- **Deception** requires a supported contradiction plus evidence of strategic intent. Public/private difference is not enough.
- **Negotiation quality** requires contextual leverage and outcome assessment; acceptance rate alone is not quality.
- **Long-horizon agency** is discussed as a trajectory only where multiple cited decisions support adaptation or fixation.
- **Optimal-decision rate and regret** require a declared policy/value oracle or counterfactual rollouts.

No ranking or prevalence claim is made from these single-run measures.

## 12. Review surfaces and reproducibility map

- [Chronological turn review](../review/chronological_turn_review.md): every turn and decision in ≤3-turn blocks, with analyst synthesis and live dossier deltas.
- [Player dossiers](../review/player_dossiers.md): evolving four-player evidence dossiers.
- [Bankruptcy windows](../review/bankruptcy_windows.md): exact terminal menus, state, ±5-decision windows, and liquidity proofs.
- [Negotiation review](../review/negotiation_review.md): all 107 proposal episodes and every counter/accept/reject outcome.
- [Evidence index](../review/evidence_index.csv): 3,829 rows covering every event and applied decision.
- [Review packet](../review/review_packet.jsonl): 488 joined decision records with legal actions, selected action, rationale, effects, costs, and source paths.
- [Promise lifecycle](../review/promise_lifecycle.csv): four bounded commitment/stance candidates.
- [Communication claims](../review/communication_claims.csv): 348 claim rows with no-label D/C adjudication.
- [Case studies](case_studies.md): eight full mechanism narratives.
- [Expanded metrics report](../expanded_metrics/expanded_metrics_report.md) and [definitions](../expanded_metrics/metric_definitions.md): exact numeric tables and semantic gates.
- [Integrity report](integrity_report.md), [coverage report](coverage_report.md), and [package validator](../quality/validate_package.py): provenance, completeness, replay, archive, and hash checks.

## 13. Claim boundaries and open issues

1. **No earlier-bankruptcy avoidability claim.** Terminal liquidity is proven; alternative prior policies are not evaluated.
2. **No optimality or regret claim.** No oracle or branch rollout exists.
3. **No trade-surplus claim.** Accepted price, later cashflow, and eventual ownership are observed, but counterfactual continuation values are not.
4. **No affirmative deception or collusion label.** Selective framing, private errors, defensive alignment, and changed stances do not independently meet the threshold.
5. **No cross-run prevalence claim.** Every mechanism and reliability rate belongs to this one 166-turn run.
6. **Provider enrichment remains unresolved but bounded.** Enrichment retrieval failures do not invalidate raw embedded usage; both statuses are preserved.
7. **One duplicate start marker remains canonical evidence.** It is not removed or normalized away; denominators reconcile it explicitly.
8. **Source-manifest line endings require provenance-aware validation.** The CRLF-to-LF distinction is byte-level materialization history, not semantic divergence.
9. **Private reasoning is self-report.** It can reveal stated calculations and objectives but cannot prove latent intent.
10. **House scarcity is a supported mechanism, not a full causal attribution.** Rolls, rent hits, transfers, and liquidity jointly produced the terminal ordering.

## 14. Overall qualitative finding

This run is best explained as an interaction among early blocker exchange, scarce-building conversion, repeated liquidity shocks, and bankruptcy transfers. Claude’s pink plan became a durable rent engine without mortgages; Gemini converted light blue early but could not monetize later color control under scarce houses; Grok’s house-independent railroad strategy collapsed after rent forced the portfolio mortgaged; GPT’s unusually broad trade search produced real assets but later narrowed into repeated completion attempts and costly refinancing. Grok’s bankruptcy then transferred an undeveloped dark-blue set to the only player with enough cash to activate it. Claude’s eight-house build converted that transfer into two terminal $1,300 Park obligations, eliminating Gemini and GPT.

The strongest research value is mechanistic rather than comparative: legal menus constrain what can be claimed, state-contingent communication must be separated from dishonesty, private numeric confidence can coexist with incorrect rent arithmetic, and a duplicate telemetry marker need not imply a duplicate model action. Those conclusions are exhaustively sourced for this run and intentionally stop short of rankings, prevalence, or unsupported counterfactual judgment.
