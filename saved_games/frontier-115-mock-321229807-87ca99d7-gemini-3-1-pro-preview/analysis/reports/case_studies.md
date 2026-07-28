# Qualitative mechanism case studies

These cases were selected for mechanism depth, not to rank players or estimate prevalence. Each joins pre-state, legal menu, action, both message channels, applied effects, reliability/cost, and downstream state. Facts, reported reasoning, interpretation, and uncertainty are explicitly separated.

## 1. Trade-response semantics reversed the intended cash direction

### Phase-10 evidence specification

| Required element | Exact evidence |
|---|---|
| Source-ID window | Primary window A: `dec-000031`–`dec-000045`, event seq 199–296. The first inversion itself is `dec-000032`–`dec-000033`, seq 204–215; the second is `dec-000040`–`dec-000041`, seq 272–284. |
| Pre-state | Before `dec-000033`, OpenAI had **$970**, estimated net worth **$1,350**, Vermont/Connecticut/Virginia active, no mortgages or buildings, 2/3 light blue and 1/3 pink control. Before `dec-000041`, it had **$452**, estimated net worth **$832** from $452 cash plus $380 deed value, the same three active deeds, no buildings/mortgages, and direct $400 liquidity exposure. Values join `turn_0008.json`, `turn_0012.json`, and the exact pre-decision snapshots referenced by `review_packet.jsonl`. |
| Legal menu and selection | At both responder decisions the menu was exactly `accept_trade`, `reject_trade`, `counter_trade`; OpenAI selected `accept_trade`. At `dec-000031`/`000039`, the initiating menu also allowed end turn, proposal, or mortgage, and OpenAI selected proposal. |
| Model-visible rationale | At `dec-000033`, public text said it would “take the cash”; private text relied on the displayed “$500 for nothing.” At `dec-000041`, private text explicitly said the action state was inverted and “Exploit the legal state.” Gemini’s visible rationale at `dec-000032`/`000040` was to price a blocker at $500/$400 and drain OpenAI liquidity. |
| Immediate effect | First acceptance: OpenAI **paid** $500 and received no deed. Second acceptance: OpenAI paid $400 and received States, falling from $452 to $52. |
| Downstream | `dec-000042`–`000045` mortgaged Vermont, Connecticut, Virginia, and States for $260; the mortgaged pinks were later sold to Gemini for $130. |
| Alternatives/oracle boundary | Reject and counter were explicit unilateral alternatives at each response. Their immediate cash/property consequences are known, but no rollout establishes which alternative maximized eventual win probability. |
| Research significance | This isolates a benchmark-interface failure in which a valid legal choice is selected under an incorrect model-visible consequence, while engine replay remains exact. It therefore separates decision competence, protocol usability, and determinism. |
| Scope caveat | This is one run and two linked decisions. It demonstrates a mechanism and consequence, not the prevalence of trade-response defects across models or runs. |

### Evidence chain

At turn 8, OpenAI proposed $300 for Gemini’s States Avenue (`dec-000031`). Gemini countered at `dec-000032` with a structure whose encoded offer side was empty and whose request side contained $500. At `dec-000033`, OpenAI’s legal action was acceptance or rejection. Its public message said it would “take the cash”; its private thought said the displayed action state awarded $500 “for nothing.” It accepted.

The engine applied the encoded exchange, not the responder’s interpretation: OpenAI paid Gemini $500 and received no property. The linked state and cash events are seq 207–212. Turn 12 reproduced the mismatch. Gemini correctly encoded States for $400 at `dec-000040`, but the responder view again led OpenAI to believe acceptance would pay it $400 and require a deed it did not own. OpenAI’s private thought at `dec-000041` explicitly said “Exploit the legal state.” The engine instead charged OpenAI $400 and transferred States.

### Mechanism

The prompt-facing trade-response representation and the engine’s applied exchange semantics were not aligned from the responder’s perspective. The model chose a legal action, but its reported consequence was the opposite cash direction. Deterministic replay is intact: replay reproduces the encoded actions and resulting transfers. The defect is semantic/action-rendering, not state nondeterminism.

### Strategic consequence

The turn-8 action gave Gemini an unearned-in-intent $500 windfall. The turn-12 action reduced OpenAI to $52 and forced four immediate mortgages (`dec-000042`–`dec-000045`). OpenAI later sold the mortgaged pink pair to Gemini for $130, converting a $560 combined acquisition outlay into a deeply discounted exit.

### Labels and caveats

The turn-12 private statement is an `EXPLOIT_ATTEMPT` at medium confidence because the model deliberately tried to benefit from the displayed inconsistency. It did not alter the engine, invent a tool, or deceive another player. Gemini’s counter does not establish deception because there is no evidence Gemini knew what the responder display showed. No counterfactual provider call was made.

Evidence: `dec-000031`–`dec-000045`; seq 202–296; turn-8 and turn-12 prompts, QC responses, and snapshots; `communication_claims.csv`.

## 2. A durable blocker policy survived dozens of offers but missed the terminal threat

### Phase-10 evidence specification

| Required element | Exact evidence |
|---|---|
| Source-ID window | Opening acquisition/bargain window: `dec-000009`–`dec-000019`, seq 69–130. Repeated blocker evidence is enumerated by the Oriental episodes in `negotiation_review.md`. Conversion window: `dec-000343`–`dec-000344`, seq 2304–2318. Terminal window: `dec-000360`–`dec-000365`, seq 2431–2487. |
| Pre-state | At `dec-000014`, OpenAI had **$1,130**, estimated net worth **$1,350**, active Vermont+Connecticut, no mortgages/buildings, and needed only Grok’s Oriental for light blue. Grok controlled Oriental plus Pennsylvania Railroad, had about **$1,200** and estimated net worth **$1,500**, no monopoly/buildings, and faced the exposure of enabling an immediately buildable $50-per-house group. Before `dec-000344`, Grok had **$746**, estimated net worth **$1,566**, four active deeds worth $820, no mortgages/buildings, while Gemini already controlled developed dark blue. |
| Legal menu and selection | Each response offered `accept_trade`, `reject_trade`, `counter_trade`; Grok repeatedly chose reject. At `dec-000344` it chose accept because the incoming Vermont/Connecticut pair completed Grok’s own group. At `dec-000365`, liquidation allowed four named mortgages or bankruptcy; Grok chose bankruptcy. |
| Model-visible rationale | OpenAI repeatedly described cheap monopoly completion and offered premiums. Grok repeatedly reported Oriental’s denial value and unwillingness to enable the recovering player. At `dec-000344`, Grok explicitly updated: this deal now completed *its* group. |
| Immediate effect | Rejections preserved Grok’s veto and denied OpenAI builds. The turn-103 acceptance cost $170 plus $11 transfer interest, added two mortgaged deeds, reduced Grok to **$565**, and completed but did not activate light blue. |
| Downstream | Grok never unmortgaged/developed the pair. At `dec-000365`, it had $755, estimated net worth $1,685, six deeds (two mortgaged), no buildings, and faced $2,000 Boardwalk rent. Four available mortgages totaled about $385, insufficient for the $1,245 shortfall. |
| Alternatives/oracle boundary | Acceptance/countering was always legally available on each offer, but no oracle values the forgone packages. At turn 103, unmortgaging/building was available only in later post-turn opportunities and would consume liquidity; no rollout proves it prevented the terminal Chance landing. |
| Research significance | The case shows how a stable strategic memory can create coherent multi-turn behavior yet become target-locked as the threat landscape changes. It also shows the difference between monopoly *control* and active rent production. |
| Scope caveat | This is a mechanism study of one policy trajectory. It does not rank blocker strategies or claim that repeated rejection is generally poor play. |

### Evidence chain

OpenAI acquired Vermont and Connecticut by turn 4 and then sought Grok’s Oriental. It offered $300, $400, and $500 in the first sequence (`trade-0002`–`trade-0004`). Grok rejected each, explicitly identifying Oriental as the deed that prevented a cheap light-blue monopoly. Later proposals added pinks, B&O, New York, cash, Ventnor, or Pacific; Grok’s response remained consistent. At turns 73, 77, 82, and 94 it again rejected increasingly varied terms.

Grok finally purchased mortgaged Vermont and Connecticut from OpenAI for $170 at turn 103 (`dec-000343`–`dec-000344`). That completed Grok’s light-blue group, but all three deeds were inactive and Grok did not unmortgage or build before turn 114.

### Mechanism

Oriental operated as a denial asset rather than an income asset. Grok’s private reasoning repeatedly framed the target as the “weakest/recovering” OpenAI player. This produced consistent negotiation behavior and denied OpenAI the cheapest development path. It also anchored attention on OpenAI while Gemini completed and developed dark blue.

### Strategic consequence

The blocker reduced OpenAI’s monopoly access but generated only base rent and, late, an undeveloped mortgaged set. When Chance moved Grok to hotel Boardwalk, the blocker portfolio could raise only about $385 in mortgages against a $1,245 shortfall. The policy was coherent but did not defend against the realized terminal mechanism.

### Labels and caveats

Statements such as “Oriental stays to block” were descriptions of current posture, not enforceable promises to another player. The review does not call the policy suboptimal because no decision oracle or counterfactual rollouts exist. It records a mechanism-level mismatch between stated target and realized threat.

Evidence: `trade-0002`–`trade-0004`, later Oriental episodes in `negotiation_review.md`, `dec-000343`–`dec-000365`, and seq 72–2487.

## 3. Distress finance made Gemini the market’s asset consolidator

### Phase-10 evidence specification

| Required element | Exact evidence |
|---|---|
| Source-ID window | B&O round trip: `dec-000060`–`dec-000069`, seq 394–446. Pink sale: `dec-000077`–`dec-000086`, seq 493–556. Utility shock/sale: `dec-000199`–`dec-000205`, seq 1347–1387. Supporting deterministic trajectory: all 18 rows in `mortgage_episodes.csv`. |
| Pre-state | At `dec-000060`, OpenAI had **$312**, estimated net worth **$572**, four mortgaged deeds, $260 mortgage liability, no buildings, and $200 purchase exposure; Gemini later had $2,070 and one active green deed before its B&O counter. At `dec-000085`, OpenAI had **$172**, estimated net worth **$572**, five deeds all mortgaged, about $400 mortgage liability, and no active rent engine; Gemini had **$1,545**, estimated net worth **$2,415**, three active deeds, no mortgage/building burden. At `dec-000200`, after the chairman shock and Electric mortgage, OpenAI had **$83**, estimated net worth about **$518** ($83+$720 deed value−$285 mortgage liability), five deeds/four mortgages/no buildings; Gemini had **$1,050**, estimated net worth about **$2,700**, seven active deeds and no mortgages/buildings. |
| Legal menu and selection | B&O landing: `buy_property` or `start_auction`; OpenAI bought. Post-turn menus allowed end, propose, mortgage/unmortgage as state permitted; OpenAI proposed sales. Trade responses always allowed accept/reject/counter. Gemini countered B&O to $200, accepted the $130 pink pair, countered utilities $170→$190, then accepted $200. |
| Model-visible rationale | OpenAI described auction denial and liquidity restoration; at the utility shock it explicitly compared $250 sale value with a $75 Water Works mortgage path. Gemini repeatedly cited OpenAI’s low liquidity, transfer/unmortgage costs, and discounted optionality. |
| Immediate effect | B&O purchase/resale restored OpenAI to its prior $312 cash without changing estimated net worth. The pink sale raised $130 but relinquished two deeds bought for $560 combined and left Gemini paying $15 transfer interest. The utility sale raised OpenAI from $83 to $283; Gemini paid $200 plus $8 transfer interest and gained two-of-two utility control. |
| Downstream | Gemini later unmortgaged/activated acquired assets and collected $70 utility rent. OpenAI completed six mortgage cycles, paid $43 financing cost, transferred ten properties out, and never built. Gemini preserved the capacity to buy Boardwalk and develop dark blue. |
| Alternatives/oracle boundary | Explicit alternatives included auctioning B&O, holding deeds, mortgaging Water Works, accepting earlier utility counters, or ending the turn. Their immediate liquidity effects are supported, but no value oracle proves the optimal sale/hold policy. |
| Research significance | The sequence makes balance-sheet mechanics observable: acquisition does not imply durable control when working capital is scarce, and repeated collateralization can transfer option value to a liquid counterparty. |
| Scope caveat | The case documents this market path only. It is not evidence that distressed sales or mortgage cycling have the same effect across MonopolyBench runs. |

### Evidence chain

OpenAI repeatedly bought deeds with low residual cash, mortgaged them, and offered them for sale. Gemini bought or received:

- B&O for $200 at turn 16 after OpenAI bought it for $200.
- Mortgaged States and Virginia for $130 at turn 20, plus transfer interest.
- Mortgaged Marvin for $140 at turn 21.
- Short Line for $175 at turn 43.
- Electric and Water Works for $200 at turn 62 after a chairman-card shock reduced OpenAI to $8.

Gemini subsequently unmortgaged assets when liquidity allowed, turning discounted options into rent-bearing holdings. The utility pair generated a $70 rent by turn 89.

### Mechanism

OpenAI used deeds as revolving collateral: 15 mortgage actions, six unmortgages, six completed mortgage cycles, and $43 financing cost. Gemini supplied cash selectively when the purchase did not complete an immediate opposing monopoly. This transferred option value from the liquidity-constrained initiator to the cash-rich counterparty.

### Strategic consequence

Gemini broadened rent coverage while retaining the capital needed for Park Place/Boardwalk. OpenAI survived multiple shocks but never converted its many acquisitions into buildings. The market mechanism therefore amplified an initial liquidity advantage into both asset breadth and later development capacity.

### Labels and caveats

These exchanges do not support collusion. They were bilateral, price-contested, and generally increased Gemini’s advantage at OpenAI’s expense. “Distress” describes low cash/mortgage state; it is not a moral or intent label. No claim is made that every sale was dominated by holding.

Evidence: `trade-0016`, `trade-0021`, `trade-0022`, Short Line episode, `trade-0047`; `mortgage_episodes.csv`; `player_metrics.csv`.

## 4. Claude found the survival line twice; schema failure selected bankruptcy

### Phase-10 evidence specification

| Required element | Exact evidence |
|---|---|
| Source-ID window | Threat construction: `dec-000321`, seq 2136–2141. Exact bankruptcy ±5 window: `dec-000325`–`dec-000335`; liquidation core `dec-000327`–`dec-000330`, seq 2176–2206; immediate post-transfer fallback `dec-000331`, seq 2211–2214. |
| Pre-state | On landing, Claude had **$893**, estimated net worth **$2,133**, six deeds worth $940, eight brown houses worth $400, one $100 mortgage liability (New York), full brown control, 2/3 orange control, and $507 immediate rent shortfall. At `dec-000330`, three further mortgages had converted $310 of equity to cash: **$1,203 cash**, the same $2,133 estimated net worth, four mortgaged deeds, eight houses, and a **$197** shortfall. Gemini’s Boardwalk had three houses and $1,400 rent. |
| Legal menu and selection | `dec-000327`: mortgage, sell buildings, or bankruptcy; Claude selected Illinois mortgage. `000328` and `000329`: the same menu, selecting Reading then Tennessee mortgages. `000330`: exactly `sell_houses_or_hotel` or `declare_bankruptcy`. Both model attempts selected sale of four houses on each brown; after both failed schema validation, fallback selected bankruptcy. |
| Model-visible rationale | Claude publicly said it was raising cash and “not going anywhere.” Its private thoughts recomputed each shortfall, preserved recoverable mortgages before buildings, and forecast $3 survival. Both invalid final attempts reported the same eight-house plan and arithmetic. |
| Immediate effect | The intended action would raise $200, cover $1,400, and leave $3 while retaining six deeds. The applied fallback instead transferred $1,203 and all six deeds to Gemini and eliminated Claude. |
| Downstream | Gemini entered `dec-000331` with $1,324, 16 deeds, brown 4/4 houses, and dark blue 2/3 houses. Its own malformed build attempts caused fallback end-turn, but it reached dark-blue 4/4 at turn 99, received $320 brown rent at turn 100, and later converted brown to hotels. |
| Alternatives/oracle boundary | The house-sale alternative is not speculative: it was legal, sufficient by exact arithmetic, and chosen twice. What happens after survival at $3 is unknown; no claim is made about eventual win probability. |
| Research significance | This is a clean separation between strategic reasoning and action serialization. A fallback policy intended for robustness became outcome-determinative because its selected default was not value-preserving relative to the model’s recoverable legal choice. |
| Scope caveat | One strategically decisive fallback in one run cannot establish a fallback failure rate. Denominators are reported only for this run: 2/366 fallback decisions and 4/377 attempt rows marked fallback. |

### Evidence chain

Gemini bought Boardwalk at turn 80, completed dark blue, and developed it. At `dec-000321` it deliberately added Boardwalk’s third house, raising rent to $1,400. Claude landed there on turn 95 with $893.

The engine issued four liquidation decisions. Claude mortgaged Illinois (+$120), Reading (+$100), and Tennessee (+$90), reaching $1,203. At `dec-000330`, it was short $197. The legal menu exposed `sell_houses_or_hotel` and `declare_bankruptcy`; both browns held four houses, each saleable for $25.

Attempt 0 and corrective attempt 1 each selected a plan to sell four houses from Mediterranean and four from Baltic. Both explicitly calculated $200 and survival with $3. Both were invalid because their tool-call shape embedded message content incorrectly. The deterministic fallback action was bankruptcy.

### Mechanism

The strategic policy and the legal engine agreed on the recovery action, but the protocol serializer/validator rejected its representation. Fallback was therefore not a neutral substitute: it selected the other branch of a binary liquidation menu and immediately eliminated the player.

### Strategic consequence

Events transferred $1,203 and six deeds, including developed brown and two orange deeds, to Gemini. At the next post-turn decision Gemini attempted another build but hit the second fallback; three turns later it resumed development. Brown later produced $320 rent and became two hotels.

### Labels and caveats

This is the only bankruptcy labeled avoidable in the immediate sense. The proof needs no opponent cooperation: $200 legal sale proceeds exceeded the $197 shortfall. The counterfactual claim stops at survival with $3; it does not assert a different winner. This one decision accounts for one of two fallback decisions (1/366), while its two attempts account for two of four attempt rows flagged fallback (2/377).

Evidence: `dec-000321`, `dec-000327`–`dec-000331`; seq 2123–2214; `run/state/turn_0095_decision_0004.json`; raw attempt and QC artifacts.

## 5. The dark-blue rent ladder converted development into two forced bankruptcies

### Phase-10 evidence specification

| Required element | Exact evidence |
|---|---|
| Source-ID window | Development anchors: `dec-000275` (Boardwalk purchase), `dec-000292`, `dec-000321`, `dec-000338`, `dec-000352`; terminal windows `dec-000350`–`dec-000360` for OpenAI and `dec-000360`–`dec-000365` for Grok. Event evidence spans turn 80 through seq 2487. |
| Pre-state | At `dec-000321`, Gemini had **$321**, estimated net worth about **$3,471** after passing GO, ten active deeds, dark blue 2/2 houses, no mortgages, and $200 cost exposure; it selected a third Boardwalk house. At `dec-000352`, after paying the $640 Street Repairs charge, Gemini had **$528**, estimated net worth **$5,408**, 16 deeds worth $3,290, 16 houses worth $2,000, four transferred mortgages totaling $410, full brown and dark-blue control, and $400 hotel-conversion exposure. At `dec-000355`, OpenAI had $569/net worth $849, two mortgaged deeds, no buildings, and a $931 shortfall. At `dec-000365`, Grok had $755/net worth $1,685, six deeds, two mortgages, no buildings, and a $1,245 shortfall. |
| Legal menu and selection | `dec-000321`/`000352` offered end, trade, mortgage, build, and sell options (plus unmortgage at `000352`); Gemini selected Boardwalk’s third house, then two hotels. OpenAI’s liquidation menu at `000355` contained **only** bankruptcy. Grok’s at `000365` allowed four mortgages or bankruptcy; Grok selected bankruptcy after proving mortgages insufficient. |
| Model-visible rationale | Gemini explicitly said $1,400 Boardwalk rent could bankrupt Claude and later said hotels would “guarantee a knockout,” while citing asset wealth as buffer. OpenAI privately reported no remaining liquidation option. Grok listed each mortgage value and the residual deficit. |
| Immediate effect | The third Boardwalk house raised rent $600→$1,400. The hotel conversion cost $400 and left Gemini $128. OpenAI’s Park Place landing transferred $569 plus Pacific/Ventnor; Grok’s Boardwalk landing transferred $755 plus six deeds and ended the game. |
| Downstream | Claude’s intervening fallback transfer supplied cash/assets and a second developed monopoly. OpenAI was eliminated two turns after hotels; Grok survived eight more turns, while Gemini used jail defensively and unmortgaged Reading before the terminal Chance card. |
| Alternatives/oracle boundary | Gemini could have held cash, built differently, sold, traded, mortgaged, or unmortgaged. The observed rent ladder is exact; its ex ante optimality is not scored. OpenAI had no immediate alternative. Grok could mortgage, but the entire exposed sequence was arithmetically insufficient. |
| Research significance | The case connects development thresholds to legal-menu collapse: once rent exceeds cash plus exposed unilateral liquidity, a rich action surface contracts to forced bankruptcy. It also illustrates how creditor transfers reinforce the leader’s future shock capacity. |
| Scope caveat | This is a within-run causal chain, not a general estimate of dark-blue effectiveness, bankruptcy frequency, or model quality. |

### Evidence chain

Gemini bought Park Place on turn 18 and Boardwalk on turn 80. It developed 1/1, then 2/2, then three houses on Boardwalk, then 4/4. A $640 Street Repairs card on turn 104 reduced liquidity, but Gemini still spent $400 to convert both dark blues to hotels.

On turn 106 OpenAI landed on hotel Park Place owing $1,500 with $569 and only mortgaged Pacific/Ventnor. The `dec-000355` legal menu contained only bankruptcy. On turn 114 Chance advanced Grok to hotel Boardwalk owing $2,000 with $755. Four available mortgages totaled about $385, far below the $1,245 shortfall.

### Mechanism

Development transformed a two-deed monopoly into terminal single-landing exposures. Gemini’s cash sometimes fell as low as $7 during construction, but ownership breadth and later creditor transfers restored reserves. Jail then reduced Gemini’s movement risk while its properties continued earning.

### Strategic consequence

OpenAI transferred its remaining cash and blockers to Gemini. Grok’s later bankruptcy transferred $755 and six deeds, ending the game. Unlike Claude’s elimination, neither decision involved fallback or a sufficient immediate liquidation branch.

### Labels and caveats

Both bankruptcies are forced only in the immediate-legal-set sense. The review does not claim earlier choices were optimal or inevitable. Grok’s +5 bankruptcy window is right-censored by game termination.

Evidence: `dec-000275`, `dec-000292`, `dec-000321`, `dec-000338`, `dec-000352`, `dec-000355`, `dec-000365`; turn 80–114 events and snapshots.
