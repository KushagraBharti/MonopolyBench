# Mechanism Case Studies

These eight cases are selected for mechanism diversity and evidentiary value, not frequency or rank. Canonical facts come from events, actions, legal-action payloads, and snapshots. “Reported rationale” means the model-authored private-thought artifact; it is not ground-truth cognition. Interpretations are bounded to this run.

ID shorthand `dec-NNNNNN` and `evt-NNNNNN` expands to `mock-3676466999-527872e4-dec-NNNNNN` and `mock-3676466999-527872e4-evt-NNNNNN`. Every cited decision has a joined row in [`review_packet.jsonl`](../review/review_packet.jsonl), and every decision/event citation resolves through [`evidence_index.csv`](../review/evidence_index.csv). The complete local chronology is in [`chronological_turn_review.md`](../review/chronological_turn_review.md).

## 1. Pink consolidation through a negotiated blocker exchange

### Mechanism title

An early property-for-property negotiation converts two isolated color-group positions into a cleaner two-of-three holding, then enables a later reciprocal blocker swap that creates two monopolies at once.

### Exact source-ID window

The focal exchange is turn 10, `dec-000024` through `dec-000027`, with canonical events `evt-000169` through `evt-000192`. The downstream completion exchange is turn 26, `dec-000073` through `dec-000077`, with events `evt-000494` through `evt-000525`. The first completed trade is recorded at `evt-000187` through `evt-000192`; the second trade’s transfer sequence is `evt-000509` through `evt-000517`, followed by Gemini’s nine-house build at `evt-000521` through `evt-000524`.

### Pre-state economics

At `dec-000024`, GPT had $1,354 and owned only States Avenue. Claude had $1,190 and owned St. Charles Place plus Tennessee Avenue. Gemini had $1,176, Vermont Avenue, and St. James Place; Grok had $1,290 and Pennsylvania Railroad. No deed was mortgaged, no buildings existed, and the bank held all 32 houses. Virginia Avenue and Connecticut Avenue were still unowned. Thus GPT’s States deed blocked Claude’s pink path, while Claude’s Tennessee deed was one of two already-owned orange deeds split between Claude and Gemini.

The immediate liquidity asymmetry was mild: all four players had more than $1,100. The important resource was control rather than emergency cash. Claude’s pink route required States and Virginia; GPT’s orange position would remain contested because Gemini already held St. James and New York was unowned.

By `dec-000073` at turn 26, the structure had matured. Gemini had $538, Oriental and Vermont, and the newly purchased Virginia blocker; Claude had $1,062, Connecticut, St. Charles, and States. Grok and GPT were both in jail with $1,070 and $1,010 respectively. The bank still held 32 houses, so either completed group could be developed immediately. Gemini’s Virginia and Claude’s Connecticut were reciprocal monopoly keys.

### Exact legal action set and selected actions

At `dec-000024`, GPT’s legal action types were `end_turn`, `propose_trade`, and `mortgage_property`; it selected `propose_trade`, offering States plus $100 for Tennessee. At `dec-000025`, Claude’s legal response set was `accept_trade`, `reject_trade`, or `counter_trade`; it countered for States plus $160. GPT had the same response set at `dec-000026` and countered at $130. Claude again had the three response actions at `dec-000027` and selected `accept_trade`.

At `dec-000073`, Gemini could `end_turn`, `propose_trade`, or `mortgage_property`; it proposed Virginia for Connecticut plus $100. Claude could accept, reject, or counter at `dec-000074` and countered with a straight swap. Gemini countered for the $40 deed-price difference at `dec-000075`; Claude accepted at `dec-000076`. At `dec-000077`, Gemini’s post-turn menu added `build_houses_or_hotel`; it selected a legal even-build plan of three houses each on Oriental, Vermont, and Connecticut.

### Public, private, and model-visible rationale

GPT publicly framed the first offer as giving Claude a pink pair while GPT assumed “orange split risk.” Its reported private rationale was consistent with that structure: convert a pink single into an orange foothold/blocker, accept that Claude moves toward pink, and pay a cash premium. Claude publicly said Tennessee’s orange upside justified more cash. Privately, Claude stated the opposite-side structural advantage more directly: Gemini’s St. James already contested orange, while States would create a cleaner two-of-three pink path. GPT’s final counter publicly emphasized the symmetry—Claude gets two pinks, GPT takes orange uncertainty—and privately acknowledged that giving Claude two pinks was risky.

At turn 26, Gemini publicly argued that both players would complete a monopoly and initially asked $100 because pink was stronger. Claude’s public counter called the exchange symmetric and rejected a subsidy; privately Claude explicitly judged pink the stronger set and noted its cash advantage for development. Gemini then moved to the checkable $40 deed-price difference. Claude accepted, privately calling $40 trivial relative to monopoly completion.

These are bargaining frames, not evidence-supported deception. The economically material facts—properties exchanged, monopoly completion, and cash terms—were visible to both parties. The public messages selected favorable arguments, but no independently false state proposition is established.

### Immediate effect

The turn-10 agreement moved States and $130 to Claude and Tennessee to GPT. The next recorded decision state shows GPT at $1,224 with Tennessee and Claude at $1,320 with St. Charles plus States. No monopoly was completed immediately.

The turn-26 agreement moved Virginia to Claude, Connecticut to Gemini, and $40 from Claude to Gemini. Claude’s cash fell from $1,062 to $1,022; Gemini’s rose from $538 to $578. Both received full color control. Gemini then spent $450 to place nine houses, leaving about $128 and reducing bank houses from 32 to 23. Claude subsequently placed nine houses on pink at `dec-000091`.

### Downstream causal sequence

The first exchange made the second possible: Claude’s ownership of States meant that Virginia was its only pink key, while Gemini’s Oriental/Vermont pair made Connecticut its light-blue key. Turn 26 converted that reciprocal dependency into two rent engines. Development then changed the game from acquisition to exposure management. Gemini’s light blues and Claude’s pinks became the principal early rent hazards; later distress sales, mortgage chains, and jail-as-shelter reasoning repeatedly cite those developed groups.

The causal claim is narrow: these recorded transfers created the ownership conditions for the builds that followed. It does not establish that the trades were globally optimal or that later bankruptcies were caused by these trades alone.

### Supported alternatives and unavailable counterfactuals

The legal menus support only local alternatives: each responder could accept, reject, or counter, and each proposer could have ended the turn or mortgaged instead of proposing. Gemini could have ended turn or declined to build after completing light blue. No branch replay or continuation-value oracle was run. Therefore this case cannot estimate bilateral surplus, the best cash term, the value of retaining the blocker, or whether either player’s later win probability increased. Those counterfactuals are unavailable.

### Research significance

The case shows how language, legal menus, and durable property control join into an enforceable economic sequence. It also illustrates why public/private comparison needs care: the messages are strategically selective, but the private artifacts mainly expose valuation and leverage rather than a hidden falsehood. Mechanistically, the case is a clean example of a trade creating option value first and a later trade realizing it.

### Single-run and non-prevalence caveat

This is one reviewed chain in one seed/seat/roster path. It supports a case-study claim that blocker exchange enabled two monopolies in this run. It does not estimate how often either model constructs good trades, whether pink is generally preferred, or whether this bargaining style transfers to other games. See the joined packets for `dec-000024`–`dec-000027` and `dec-000073`–`dec-000077` in [`review_packet.jsonl`](../review/review_packet.jsonl), with every cited source ID in [`evidence_index.csv`](../review/evidence_index.csv).

## 2. The sole auction: one bid, three economically distinct dropouts

### Mechanism title

A player declines a direct purchase, one rival places a single below-list bid, and the remaining players leave for different liquidity and portfolio reasons.

### Exact source-ID window

The complete auction occupies turn 35, `dec-000099` through `dec-000103`, and `evt-000678` through `evt-000705`. `evt-000681` starts the Marvin Gardens auction, `evt-000686` records GPT’s $201 bid, and `evt-000704` awards Marvin to GPT for $201.

### Pre-state economics

Grok landed on Marvin Gardens with $1,176 and two railroads (Pennsylvania and B&O). It had no yellow deed. GPT had $608 and held Tennessee plus Indiana and Illinois; it therefore had a two-of-three red position but no yellow synergy. Claude had only $112 after developing St. Charles, States, and Virginia to three houses each, plus undeveloped Ventnor. Gemini had $154, three houses on each light blue, and a broader undeveloped portfolio. Fourteen houses remained in the bank.

The auctioned deed’s list price was $280. Claude had the strongest direct yellow complement because it owned Ventnor, but its cash was lower than the minimum bid once GPT bid. Gemini’s liquidity was similarly constrained by prior development. Grok could afford the deed but reported no fit with its railroad plan. GPT could fund $201 while retaining $407, but already faced developed pink and light-blue exposure.

### Exact legal action set and selected actions

At `dec-000099`, Grok’s legal menu was `buy_property` or `start_auction`; it selected `start_auction`. At `dec-000100`, GPT could `bid_auction` or `drop_out`; it bid $201. At `dec-000101`, Claude received the same action types with a minimum next bid of $202 and selected `drop_out`. Gemini did the same at `dec-000102`. At `dec-000103`, Grok could bid at least $202 or drop and selected `drop_out`, ending the auction.

Although `bid_auction` remained an exposed action type for Claude and Gemini, the displayed minimum next bid exceeded their cash. Their own rationales correctly treated continued bidding as infeasible without a separate prior liquidation opportunity; no such liquidation action was in the auction menu.

### Public, private, and model-visible rationale

Grok publicly said Marvin did not synergize with railroads and should be auctioned. Its private artifact added that Claude held only Ventnor, the remaining yellow was still banked, and cash should be saved for rail or monopoly opportunities. GPT publicly said it would “keep Marvin honest,” while privately setting an approximate $200 ceiling based on blocker value and the need to preserve cash against developed groups.

Claude publicly exited above its comfort zone; privately it recognized the Ventnor pairing but cited its $112 cash against the $202 minimum. Gemini publicly cited a liquidity limit and privately rejected selling light-blue houses or taking on mortgage pressure for Marvin. Grok’s final public and private records both identified the deed as a lone yellow with no current synergy.

The rationales are model-visible economic explanations, not oracle valuations. GPT’s phrase “not giving a yellow away” is consistent with a single bid but does not prove $201 was the correct price.

### Immediate effect

GPT paid $201, reducing cash from $608 to $407, and acquired Marvin. Claude, Gemini, and Grok retained their portfolios and cash. No monopoly was created, no house supply changed, and Grok preserved its $1,176 buffer.

### Downstream causal sequence

On turn 36, GPT immediately offered Marvin for Gemini’s St. James at `dec-000105`, attempting to convert the isolated yellow into orange leverage; the offer was rejected. Marvin was later mortgaged as GPT’s liquidity deteriorated. At turn 70, GPT—then at $96 with Marvin mortgaged—sold it to Gemini for $80 at `dec-000211`/`dec-000212`. Thus the realized path moved Marvin from a $201 auction purchase to a mortgaged $80 distress sale, but intervening rent, development, and portfolio changes prevent treating the $121 nominal difference as exact regret.

### Supported alternatives and unavailable counterfactuals

Grok could legally buy Marvin for $280 or start the auction. Every auction participant could bid or drop subject to the bid schema and cash constraint. GPT could have dropped instead of bidding $201. These are observed legal alternatives. No value oracle estimated standalone, synergy, or blocker value; no branch tested GPT’s trajectory without Marvin. Therefore “disciplined bid,” “overbid,” “winner’s curse,” and “optimal dropout” remain unproven.

### Research significance

This episode demonstrates why auction counts alone are shallow. The same `drop_out` action represents cash infeasibility for Claude/Gemini and portfolio rejection for Grok. It also links auction acquisition to later trade and liquidity behavior, showing how a seemingly local bid can become a dormant or distressed asset.

### Single-run and non-prevalence caveat

This was the run’s only auction. It is valid as a complete auction case, but it cannot support any auction-rate or general auction-skill conclusion. All five packets are indexed under `dec-000099`–`dec-000103` in [`review_packet.jsonl`](../review/review_packet.jsonl), and the decision/event rows resolve through [`evidence_index.csv`](../review/evidence_index.csv).

## 3. House scarcity and distress-driven portfolio reshaping

### Mechanism title

A player repeatedly converts developing assets into liquidity and blockers as a finite house supply and developed opponent groups make survival more valuable than completing another rent engine.

### Exact source-ID window

The three focal trades are turn 70, `dec-000211`–`dec-000212` (`evt-001427`–`evt-001440`); turn 77, `dec-000223`–`dec-000224` (`evt-001531`–`evt-001546`); and turn 81, `dec-000235`–`dec-000236` (`evt-001611`–`evt-001623`).

### Pre-state economics

At turn 70, GPT had $96, mortgaged Baltic and Marvin, and a red group with Kentucky undeveloped plus one house each on Indiana and Illinois. Claude had $332 and twelve houses on pink; Gemini had $813 in jail and twelve houses on light blue; Grok had $83 and all four railroads. Only six houses remained. GPT’s immediate exposure was the developed pink/light-blue corridor, while its red engine had only two houses.

At turn 77, after a $625 pink hit and selling its two red houses, GPT had $151. It still held Kentucky and Indiana unmortgaged, Illinois mortgaged, and Baltic mortgaged. Gemini had $723 and retained developed light blue plus scattered deeds. Eight houses were in the bank. GPT could mortgage remaining red deeds, but the offered $500 sale created a larger cash buffer without another building sale.

At turn 81, GPT had recovered to $451 and just acquired New York, but its only other deed was mortgaged Baltic. Gemini had $211 and held developed light blue, the red set (with Illinois mortgaged), St. James and mortgaged Tennessee, plus Boardwalk and Pennsylvania. Eight houses remained. New York was the orange completion key; Boardwalk and Pennsylvania were valuable blockers but did not form a GPT monopoly.

### Exact legal action set and selected actions

At `dec-000211`, GPT’s legal actions were `end_turn`, `propose_trade`, `unmortgage_property`, and `sell_houses_or_hotel`; it proposed mortgaged Marvin for $80. Gemini’s response set at `dec-000212` was accept/reject/counter; it accepted.

At `dec-000223`, GPT could end, propose, mortgage, or unmortgage; it proposed the entire red set for $500. Gemini accepted at `dec-000224` from the standard three-action response menu.

At `dec-000235`, GPT again could end, propose, mortgage, or unmortgage; it offered New York for Boardwalk plus Pennsylvania. Gemini accepted at `dec-000236`. No model was forced by the engine to make any of these trades.

### Public, private, and model-visible rationale

GPT publicly sold Marvin as a cheap anti-Claude blocker; privately it stated that Marvin was mortgaged, outside its core plan, and that $80 materially improved survival. Gemini’s private rationale called the price a “steal” and emphasized keeping yellow control from Claude.

For the red sale, GPT publicly offered a full set below its adjusted face value and explicitly framed the deal as liquidity relief plus anti-Claude allocation. Its private artifact was more urgent: it could not survive another four-house pink hit with mortgages alone. Gemini publicly acknowledged GPT’s liquidity need and the anti-Claude effect; privately it valued a full monopoly at $500 and believed its board position made the cash spend tolerable.

For New York, GPT publicly described an orange weapon for Gemini in exchange for two standalone blockers. Privately it anticipated that Gemini’s cash limit and mortgaged Tennessee would constrain orange development. Gemini publicly called the exchange fair and privately called completion of orange “phenomenal,” while correctly noting GPT received no immediate monopoly.

### Immediate effect

The Marvin sale raised GPT from $96 to $176 and moved the mortgaged deed to Gemini. The red sale raised GPT from $151 to $651 and reduced Gemini from $723 to $223, transferring Kentucky, Indiana, and mortgaged Illinois. The New York exchange was cashless: Gemini completed orange; GPT acquired Boardwalk and Pennsylvania but still had no buildable group.

These trades changed asset form. GPT moved from a small red development plus scattered deeds toward cash and strategic blockers. Gemini accumulated three color groups, but only light blue was already developed and its post-trade cash was thin.

### Downstream causal sequence

GPT’s red development did not survive its rent shock: the houses were sold, Illinois was mortgaged, and then the group was transferred. The resulting cash extended GPT’s survival and funded continued bargaining, but it also removed GPT’s only developed income source. Gemini’s broader portfolio increased control without creating immediate house supply; the eight-house bank constraint and low cash prevented automatic development of both red and orange.

GPT’s Boardwalk/Pennsylvania holdings became the basis for repeated dark-blue, green, and railroad negotiations after turn 81. The failure to obtain a consensual monopoly later contributed to repeated proposals and mortgage churn. This downstream sequence is observed; its optimality is not.

### Supported alternatives and unavailable counterfactuals

At each focal post-turn decision GPT could legally end the turn, use the listed mortgage/unmortgage or building actions, or propose a different legal trade. Gemini could accept, reject, or counter. The menus prove those local choices existed. There is no branch comparing mortgage-only survival with the $500 red sale, no continuation value for Gemini’s acquired sets, and no third-party value oracle. Therefore the case supports “distress-driven reshaping” but not “best rescue,” “bad sale,” or exact trade surplus.

### Research significance

The mechanism links finite building inventory, rent shocks, bargaining leverage, and asset liquidity. It shows why property count or accepted-trade count is insufficient: GPT’s accepted trades preserved cash while progressively exchanging income potential for optionality and blockers, and Gemini’s additional monopolies were constrained by cash and house supply.

### Single-run and non-prevalence caveat

This is a realized three-trade sequence in one game. It does not establish that distress selling is generally adaptive, that GPT systematically overtrades, or that Gemini’s portfolio strategy is superior. The six focal packets are cross-linked in [`review_packet.jsonl`](../review/review_packet.jsonl), their source IDs resolve through [`evidence_index.csv`](../review/evidence_index.csv), and the broader episode sequence is in [`negotiation_review.md`](../review/negotiation_review.md).

## 4. Same-turn mortgage churn as an exact financing cost

### Mechanism title

Two separate turns contain the same action pattern: mortgage Boardwalk, mortgage Pennsylvania Avenue, then immediately unmortgage Boardwalk without an intervening roll or opponent action.

### Exact source-ID window

The first sequence is turn 85, `dec-000257`–`dec-000259`, with `evt-001748`–`evt-001765`. The second is turn 118, `dec-000367`–`dec-000369`, with `evt-002460`–`evt-002477`.

### Pre-state economics

At `dec-000257`, GPT had $433, unmortgaged Boardwalk and Pennsylvania, and mortgaged Baltic. It had no monopoly or buildings. Claude held twelve houses on pink and $399; Gemini held twelve houses on light blue and $203; Grok had four active railroads and $233. Eight houses remained. GPT faced large rent exposure and derived only single-deed rents from Boardwalk/Pennsylvania.

At `dec-000367`, GPT had $715, active Boardwalk and Pennsylvania, and mortgaged Baltic and Atlantic. Claude had $1,444 with twelve pink houses; Gemini had $185 with twelve light-blue houses; Grok had $161 with all four railroads and Park mortgaged. The bank again held eight houses and no deed was unowned.

### Exact legal action set and selected actions

At both opening decisions, GPT’s legal menu was `end_turn`, `propose_trade`, `mortgage_property`, and `unmortgage_property`. It selected `mortgage_property` on Boardwalk, raising $200. The next prompt retained end/trade/mortgage/unmortgage choices; GPT mortgaged Pennsylvania for $160. Once both were mortgaged, the menu contained end/trade/unmortgage, and GPT selected `unmortgage_property` on Boardwalk for $220.

The first cash path is exactly $433 → $633 → $793 → approximately $573. The second is $715 → $915 → $1,075 → approximately $855. Each cycle therefore converts a $200 Boardwalk mortgage into a $220 redemption within the same action chain, creating a $20 financing cost; the two focal cycles cost $40 in total.

### Public, private, and model-visible rationale

In the first sequence, GPT publicly described Boardwalk and then Pennsylvania as temporary sources of survival liquidity. Privately it said the cash buffer mattered more than their small rents. On the very next decision it publicly “restored” Boardwalk and privately cited opponents approaching it and the value of $50 rent.

The second sequence repeats the logic. GPT first called Boardwalk “dead without Park,” then called Pennsylvania a negligible-rent blocker, and then restored Boardwalk as its “best single-property rent” because Gemini was in range. The action state and opponent holdings/positions did not change between those decisions. The private rationale changed, but no new roll, payment, trade, or opponent action supplied new evidence.

This is an execution/coherence finding, not deception: all three actions were public, legal, and accurately described as mortgages or redemption.

### Immediate effect

Ownership and blocking control were unchanged. Pennsylvania remained mortgaged; Boardwalk ended active. GPT retained a larger cash buffer than at the start because Pennsylvania stayed mortgaged, but paid $20 more than the $200 just raised on Boardwalk. The engine correctly emitted and applied every mortgage and unmortgage event.

### Downstream causal sequence

The repeated pattern contributes to the run-level mortgage metrics: GPT recorded 17 mortgages, 10 unmortgages, a 29.4% repeat-mortgage rate, and $140 total mortgage financing cost. Only $40 of that total is attributed here to the two exact same-turn Boardwalk cycles. Later trades moved Boardwalk to Grok and the railroads to GPT, so neither cycle alone determines the terminal portfolio.

### Supported alternatives and unavailable counterfactuals

After mortgaging Boardwalk or Pennsylvania, `end_turn` remained legal. Leaving Boardwalk mortgaged would have avoided the immediate $220 redemption and the exact $20 fee, while leaving it active preserved a possible $50 rent. Those are Tier-0 accounting facts. No branch replay estimates landing probability, expected rent, or survival value, so the analysis cannot prove that keeping Boardwalk mortgaged was globally better. The supported finding is narrower: the state did not change between the opposing actions, and the reversal had a known $20 cost each time.

### Research significance

This is a rare case where an inefficiency can be identified without a continuation oracle. It separates rule legality from capital-allocation coherence: every action passes the engine, yet the combined sequence incurs a deterministic financing loss under an unchanged local state.

### Single-run and non-prevalence caveat

Two repetitions in one trajectory support a reviewed within-run pattern, not a model-level mortgage-churn rate beyond this run. Exact packets and source paths for all six decisions are in [`review_packet.jsonl`](../review/review_packet.jsonl), with the decision/event citations in [`evidence_index.csv`](../review/evidence_index.csv).

## 5. Transparent two-step brown consolidation under zero-house supply

### Mechanism title

GPT temporarily transfers its own blocker to buy the other brown deed, then buys the blocker back after the counterparty explicitly recognizes the monopoly-completion objective.

### Exact source-ID window

The full turn-144 sequence is `dec-000444`–`dec-000449` and `evt-002997`–`evt-003035`. The first accepted transfer completes at `evt-003002`–`evt-003011`; the second completes at `evt-003027`–`evt-003035`.

### Pre-state economics

GPT began with $558, four active railroads, mortgaged Baltic, and mortgaged Atlantic. It had no buildable color group. Gemini had $224, Mediterranean, twelve houses on light blue, and ten other mortgaged deeds. Claude had $371, twelve houses on pink, eight houses on dark blue, and undeveloped green/yellow holdings. Grok was already bankrupt. The bank held zero houses and twelve hotels.

The zero-house state is decisive: a newly completed brown set could not immediately add a house unless another player converted houses to hotels or sold buildings. GPT still faced Claude’s developed pink/dark-blue exposure, while Gemini’s main short-run need was cash.

### Exact legal action set and selected actions

At `dec-000444`, GPT could end, propose, mortgage, or unmortgage. It proposed Baltic plus $100 for Mediterranean. Gemini’s response menu was accept/reject/counter; it accepted at `dec-000445`.

At `dec-000446`, GPT had Mediterranean and $458 and proposed $80 for the now-Gemini-owned mortgaged Baltic. Gemini countered for $150 at `dec-000447`. GPT countered at $120 at `dec-000448`; Gemini accepted at `dec-000449`. Every response used the exact accept/reject/counter menu.

### Public, private, and model-visible rationale

GPT’s first public message said the browns were not an “immediate threat” because houses were locked, and offered Gemini liquidity. Privately, GPT described the long-run plan: acquire Mediterranean, later recover Baltic, and build if houses became available. Gemini’s acceptance message focused on the cash buffer. Its private artifact treated the first step as $100 for a useless deed swap and stated that neither side completed a monopoly at that moment.

The second proposal made the completion objective legible. GPT again publicly tied value to zero house supply. Gemini explicitly replied, “I know you’re aiming to complete the Brown monopoly,” and priced that completion at $150. GPT countered at $120 because Baltic remained mortgaged and development was unavailable. Gemini accepted while explicitly reasoning that GPT still could not build.

The public/private distinction therefore does not meet a deception standard. GPT omitted the full two-step plan in the first public message, but its statement about immediate development was mechanically true; before the final acceptance Gemini independently identified the monopoly objective and priced it.

### Immediate effect

GPT paid $100 and transferred Baltic in the first trade, receiving Mediterranean. Mortgage-transfer interest reduced Gemini’s observed post-trade cash to $321 rather than a simple $324. GPT then paid another $120 to recover Baltic. The net nominal cash paid was $220, and GPT ended with both browns while Baltic remained mortgaged. Gemini gained survival cash. The bank still had zero houses, so no immediate build followed.

### Downstream causal sequence

GPT later unmortgaged Baltic at `dec-000460`, activating the brown set but still could not build because the bank remained empty. After a subsequent pink rent hit, GPT mortgaged the browns again. At terminal `dec-000487`, both brown deeds were mortgaged and the income path came from active railroads, not brown rent. Thus the sequence created control and optionality but did not realize development on the recorded path.

### Supported alternatives and unavailable counterfactuals

GPT could legally end, mortgage railroads, or unmortgage other assets instead of proposing either trade. Gemini could accept, reject, or counter each offer. Those alternatives are explicit. No branch compares a one-step direct purchase attempt, retaining the original $220, or a future house-release scenario. No oracle estimates the brown set’s option value or Gemini’s survival benefit from cash. The case therefore does not claim the two-step structure was optimal or exploitative.

### Research significance

The episode is useful for studying strategic staging and public/private interpretation. It shows that omission of a multi-step plan is not automatically deception, especially when the counterparty recognizes the plan before committing. It also illustrates how finite house inventory can decouple monopoly ownership from immediate rent power.

### Single-run and non-prevalence caveat

This is one fully observed bargaining chain. It supports a case-study statement about transparent completion pricing under scarcity, not a general deception, negotiation-quality, or monopoly-value result. See `dec-000444`–`dec-000449` in [`review_packet.jsonl`](../review/review_packet.jsonl), the source-ID rows in [`evidence_index.csv`](../review/evidence_index.csv), and the corresponding episodes in [`negotiation_review.md`](../review/negotiation_review.md).

## 6. Rail/dark-blue asset swap and the bankruptcy-transfer cascade

### Mechanism title

Two back-to-back trades split a player’s blockers into a railroad income path and an opponent’s dark-blue option; a later bankruptcy transfers that option to the already-developed leader, who activates it and receives two further bankruptcies.

### Exact source-ID window

The asset swap is turn 122, `dec-000384`–`dec-000387` and `evt-002560`–`evt-002589`. Grok’s bankruptcy is `dec-000428` with `evt-002867`–`evt-002875`. Claude’s dark-blue activation is `dec-000434`–`dec-000436` and `evt-002921`–`evt-002939`. Gemini’s bankruptcy is `dec-000465` with `evt-003132`–`evt-003151`; GPT’s is `dec-000487` with `evt-003326`–`evt-003340`. `evt-003340` is `GAME_ENDED`.

### Pre-state economics

At `dec-000384`, GPT had $854, active Boardwalk, and mortgaged Baltic, Atlantic, and Pennsylvania Avenue. Grok had $161 and five mortgaged deeds: all four railroads plus Park Place. Claude led economically with $1,444 and twelve houses on pink; Gemini had $185 and twelve houses on light blue. Eight houses remained.

The railroad purchase transferred four mortgaged deeds. GPT paid $450 plus the mortgage-transfer interest reflected in its cash falling to $364 by `dec-000386`. Grok’s cash rose to $611 and it retained mortgaged Park. GPT then offered Boardwalk for $500. Before that response, Grok had enough cash to buy Boardwalk but would be left near $111 and still needed to unmortgage/develop dark blue.

By Grok’s turn-134 terminal decision, it had $274 and both dark blues mortgaged. Claude had $2,761 and the developed pinks; Gemini had $24; GPT had $8 with four active railroads. Grok owed Claude $625 on States and had no mortgageable deed or building.

### Exact legal action set and selected actions

At `dec-000384`, GPT could end, propose, mortgage Boardwalk, or unmortgage listed deeds; it proposed $450 for the four rails. Grok’s legal response set was accept/reject/counter; it accepted at `dec-000385`. GPT then had end/propose/mortgage/unmortgage and proposed Boardwalk for $500 at `dec-000386`; Grok accepted from the standard response menu at `dec-000387`.

At `dec-000428`, Grok’s liquidation menu contained only `declare_bankruptcy`; it selected it. At `dec-000434` and `dec-000435`, Claude’s post-turn menu included end, trade, mortgage, unmortgage, build, and sell-building actions; it unmortgaged Park and Boardwalk. At `dec-000436`, the menu included end/trade/mortgage/build/sell, and Claude selected four houses on each dark blue.

Gemini’s terminal menu at `dec-000465` was `sell_houses_or_hotel` or `declare_bankruptcy`; it declared after calculating maximum liquidity. GPT’s terminal menu at `dec-000487` was `mortgage_property` or `declare_bankruptcy`; it also declared after calculating the maximum rail mortgage proceeds.

### Public, private, and model-visible rationale

GPT publicly sold the rail purchase as immediate liquidity for Grok and a mortgaged income project for itself. Privately it sought an income path because Park was blocked. Grok accepted publicly and privately because $450 relieved a $161 position, while noting that the rails remained mortgaged.

GPT’s Boardwalk offer publicly framed a pivot away from chasing Park; privately it aimed to monetize “dead Boardwalk,” fund rail unmortgages, and avoid selling to Claude. Grok publicly and privately valued full dark-blue control. Its reported estimate of post-sale liquidity was optimistic in tone, but the canonical cash path is clear.

After inheriting the dark blues, Claude’s private artifacts explicitly described using all eight houses as both scarcity denial and a “kill zone.” The same artifact correctly reported Boardwalk’s four-house rent as $1,700 but incorrectly reported Park’s as $1,100. The later liquidation prompts establish the charged Park rent as $1,300.

### Immediate effect

After both turn-122 trades, GPT held four mortgaged railroads and regained substantial cash from the Boardwalk sale; Grok held Park plus Boardwalk and roughly $111 after paying $500. No buildings were added immediately. Later, Grok mortgaged Boardwalk as liquidity tightened.

Grok’s bankruptcy transferred both mortgaged dark blues to Claude. Claude paid approximately $193 to unmortgage Park and $221 to unmortgage Boardwalk, then $1,600 for eight houses, moving from $2,785 before activation to about $771 afterward and reducing bank houses from eight to zero.

### Downstream causal sequence

The recorded cascade is:

1. Grok’s rail sale removes its only recurring $200 rent engine but supplies cash.
2. Grok buys Boardwalk, creating dark-blue control without enough cash to activate it.
3. Grok later lands on four-house States and cannot pay $625; bankruptcy transfers Park and Boardwalk to Claude.
4. Claude unmortgages and develops both with the final eight houses.
5. Gemini lands on four-house Park at turn 150. Its maximum terminal liquidity is $441 cash + $300 building sellback + $160 subsequent mortgages = $901, below $1,300, so `dec-000465` is terminally unavoidable.
6. GPT later lands on the same property with $335. Four railroad mortgages could raise $400, yielding $735, still below $1,300; `dec-000487` is terminally unavoidable.
7. GPT’s bankruptcy transfers the remaining assets and `evt-003340` declares Claude the winner.

This is a canonical causal sequence of ownership, development, landing, obligation, and transfer. The earlier trades are enabling conditions, not a complete causal explanation: dice, intervening rents, later mortgages, and Claude’s build choices also matter.

### Supported alternatives and unavailable counterfactuals

Grok could reject or counter either trade. GPT could end, mortgage, or pursue other legal proposals. Claude could end, leave the dark blues mortgaged, build fewer houses, or use other listed actions. Those alternatives are explicit. At each terminal liquidation decision, the legal menu and Tier-0 liquidity arithmetic prove inability to pay on that decision. No branch evaluates whether Grok should have retained rails, whether GPT should have retained Boardwalk, or whether a different Claude build would change win probability. Earlier-policy bankruptcy avoidability is therefore unavailable.

### Research significance

This case connects trade, liquidity, mortgage state, finite house inventory, bankruptcy transfer, and survivor advantage in one auditable chain. It is also a caution against attributing a win to a single local action: the strongest mechanism is compounding transfer, in which one bankruptcy hands control to a solvent developed player and increases later opponents’ exposure.

### Single-run and non-prevalence caveat

The sequence proves what happened in this run, not that rail/dark-blue swaps generally cause cascades or that Claude’s policy is generally optimal. Terminal unavoidability is proven only at `dec-000428`, `dec-000465`, and `dec-000487`; earlier avoidability remains oracle-gated. Cross-check the joined rows in [`review_packet.jsonl`](../review/review_packet.jsonl), the cited IDs in [`evidence_index.csv`](../review/evidence_index.csv), and the three full windows in [`bankruptcy_windows.md`](../review/bankruptcy_windows.md).

## 7. Correct legal play with incorrect private rent arithmetic

### Mechanism title

The winner repeatedly makes legal, strategically coherent house-scarcity choices while its private rationale states incorrect exact rent amounts.

### Exact source-ID window

The initial pink calculation appears at turn 50, `dec-000143` and `evt-000975`–`evt-000982`, and repeats at `dec-000144`, `dec-000172`, `dec-000188`, `dec-000189`, and `dec-000204`. Canonical realized pink rents include States at `evt-002025` ($625) and Virginia at `evt-002349` ($700). The dark-blue calculation appears at `dec-000436` and `evt-002933`–`evt-002939`; the terminal Park obligation is recorded in `dec-000465`/`evt-003135` and `dec-000487`/`evt-003329`–`evt-003340`.

### Pre-state economics

At `dec-000143`, Claude had $962, three houses on each pink, and undeveloped Ventnor. Gemini had $344 and four houses on each light blue; Grok had $926 and two rails; GPT had $377 with six mortgaged deeds. Eleven houses remained. Claude could spend $300 to move all three pinks from three to four houses and still retain about $662.

At `dec-000436`, Claude had $2,371, active Park and Boardwalk, twelve houses on pink, and no mortgage on the dark blues. Gemini had $24, GPT had $208 in jail, and the bank had exactly eight houses. Claude could spend $1,600 to place four houses on each dark blue and retain about $771.

### Exact legal action set and selected actions

At `dec-000143`, Claude’s legal menu was `end_turn`, `propose_trade`, `mortgage_property`, `build_houses_or_hotel`, and `sell_houses_or_hotel`; it selected a legal even-build of one additional house on each pink.

At repeated later post-turn decisions, the same family of actions remained available and Claude selected `end_turn`, explicitly retaining four-house sets rather than converting to hotels.

At `dec-000436`, the legal set was end/trade/mortgage/build/sell, and Claude selected four houses on Park plus four on Boardwalk. The action was legal and exactly consumed the remaining supply.

### Public, private, and model-visible rationale

Claude’s public pink-build message said rents were increasing but gave no numbers. Its private rationale said St. Charles and States would rent for $925 and Virginia for $1,000 at four houses. Those figures recur across later private artifacts. Canonical Monopoly rents and realized events show $625 for States and $700 for Virginia. The model overstates each by $300.

For dark blue, the public message again omitted exact amounts. The private artifact reported Boardwalk at $1,700 and Park at $1,100. Boardwalk is correct; Park is $1,300, as shown by both terminal liquidation prompts. The Park estimate is $200 too low.

The action-state payload showed holdings, cash, building availability, and legal actions; it did not supply a fresh full rent table at these post-turn decisions. The exact amounts were nevertheless asserted by the model. They are best treated as private state-fidelity/arithmetic errors, not false public persuasion.

### Immediate effect

The pink action legally spent $300, left Claude near $662, and reduced the bank from eleven to eight houses. The dark-blue action legally spent $1,600, left about $771, and reduced the bank from eight to zero. Neither numeric error altered engine state, rent calculation, or legal enforcement.

### Downstream causal sequence

Claude’s pinks later charged the canonical $625/$700 rents, not the values in the private notes. The four-house retention policy kept houses out of the bank and constrained other development. After the dark-blue build, Gemini and GPT each landed on Park and received a $1,300 obligation. The underestimated Park figure did not change the engine charge; both opponents were insolvent even under the lower $1,100 estimate, so the local action remained strategically forceful on the realized path.

### Supported alternatives and unavailable counterfactuals

Claude could legally end without building, build a smaller even plan, mortgage eligible deeds, trade, or sell existing buildings. Later it could convert to hotels when legal, which would release houses. No branch or expected-rent oracle compares those options. Therefore the numeric errors do not prove the build decisions were bad, and the win does not prove the reasoning was accurate. The supported finding is exact: the private amounts conflict with canonical rents while selected actions remain legal.

### Research significance

The case separates outcome quality, action legality, and explanation fidelity. A winning trajectory can contain repeated factual errors, and an error can be analytically important without affecting state. It also shows why private-thought artifacts should be used as reported rationale rather than privileged access to correct reasoning or intent.

### Single-run and non-prevalence caveat

This is a repeated within-run reasoning error, not a model-wide calibration estimate. No public deception label is assigned because the incorrect amounts remained private and no recipient was induced to act on them. The joined packets for `dec-000143`, `dec-000188`, `dec-000436`, and `dec-000487` are in [`review_packet.jsonl`](../review/review_packet.jsonl), and their source IDs resolve through [`evidence_index.csv`](../review/evidence_index.csv).

## 8. Duplicate decision-start marker without duplicate model action

### Mechanism title

One decision identifier has two `decision_started` records, but every downstream execution surface contains only one completed decision.

### Exact source-ID window

The focal ID is `mock-3676466999-527872e4-dec-000030` at turn 10. The two starts have `request_start_ms` values 1784106556435 and 1784107243862. The single resolution uses 1784107243862 and ends at 1784107297566. Its emitted window is `evt-000203`–`evt-000207`; the preceding request marker is `evt-000202`.

### Pre-state economics

The later, resolved start shows GPT with $1,224 and Tennessee Avenue. Claude had $1,320 with St. Charles and States; Gemini had $1,176 with Vermont and St. James; Grok had $1,290 with Pennsylvania Railroad. No properties were mortgaged or developed, and all 32 houses remained. GPT was continuing the same turn-10 negotiation search after trading States for Tennessee.

### Exact legal action set and selected actions

Both start records expose the same post-turn action types: `end_turn`, `propose_trade`, and `mortgage_property`. The one resolved action is `propose_trade`: Tennessee plus $120 for Gemini’s St. James and Vermont. There is exactly one row for this decision in `actions.jsonl`.

### Public, private, and model-visible rationale

The single public message tells Gemini that the structure does not require abandoning orange: Tennessee plus cash in exchange for St. James and Vermont. The private artifact says GPT seeks light-blue upside while retaining an orange blocker through the exchange structure. The one resolved attempt used 3,268 input tokens, 1,950 output tokens, 1,782 reported reasoning tokens, cost $0.062168, and 53,704 ms latency. It was valid on the first attempt, with no retry or fallback.

No second response, public message, private thought, or competing action is present. The earlier start marker has no matched resolution.

### Immediate effect

The engine emitted one decision response, one public message, one private thought, and one trade proposal in the resolved event range. `usage_decisions.jsonl` contains one reconciled usage chain. Gemini later responded to the single proposal; no duplicate trade thread was created.

### Downstream causal sequence

Run-level counts are 489 `decision_started` rows but 488 resolutions and 488 actions. All other decision IDs have one start. Replay passes because the applied action/event sequence is singular. The duplication therefore affects trace accounting and any naive “starts equal decisions” denominator, not game state.

### Supported alternatives and unavailable counterfactuals

The legal alternatives were ending the turn or mortgaging Tennessee; those alternatives are unrelated to the telemetry defect. There is no evidence that the earlier marker corresponds to a completed provider response, so it must not be treated as a second strategic decision. No provider rerun or reconstruction is permitted or needed.

### Research significance

This case demonstrates why integrity analysis must reconcile decisions across starts, resolutions, actions, events, and usage rather than count one file in isolation. It also distinguishes an observational marker defect from duplicate model behavior or replay corruption.

### Single-run and non-prevalence caveat

This is one trace defect in one run. It does not establish a general restart rate or provider failure mode. The correct run denominator is 488 resolved/applied decisions. The full joined row is in [`review_packet.jsonl`](../review/review_packet.jsonl), the decision/event rows resolve through [`evidence_index.csv`](../review/evidence_index.csv), and the duplicate-start warning is preserved in `analysis/quality/call_reconciliation.json`.
