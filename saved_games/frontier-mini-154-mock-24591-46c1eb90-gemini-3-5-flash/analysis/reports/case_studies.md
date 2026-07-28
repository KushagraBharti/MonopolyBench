# Mechanism case studies

Run: `mock-24591-46c1eb90`

Scope: one saved game; qualitative mechanism analysis, not a model ranking.

## How to read these cases

Each case joins the authoritative pre-state, legal menu, selected action, public message, model-reported private rationale, emitted effects, and later outcome. Facts come from `run/events.jsonl`, `run/actions.jsonl`, `run/decisions.jsonl`, and `run/state/`; the normalized join is `analysis/review/review_packet.jsonl`. Model-reported rationales are evidence about the player’s stated plan, not privileged evidence that the plan was correct. Alternatives are classified as:

- **Unilateral legal alternative:** present in the recorded legal menu and executable from the recorded state.
- **Negotiated alternative:** requires another player to agree.
- **Oracle/branch alternative:** requires counterfactual dice, later policy, or replay; it is not used to label a move avoidable or optimal.

Communication labels are candidates only. D1 denotes an evidence-linked factual/state-description error. No case below supports a high-confidence deception label.

## Case index

| Case | Turns | Mechanism | Main finding |
|---|---:|---|---|
| 1 | 13 | Utility auction and state fidelity | Gemini priced real complementarity; GPT bid on a complement it did not own, then corrected and exited |
| 2 | 44 | Chained trade, financing, and immediate development | One negotiated completion was financed by a second portfolio-concentration trade |
| 3 | 35–147 | Persistent false monopoly and legal-menu non-update | Claude’s mixed-color belief survived direct correction and shaped trades, inaction, and final self-explanation |
| 4 | 61–65 | Discount completion followed by delayed liquidity shock | GPT acquired green cheaply but had too little cash to absorb a dark-blue landing four turns later |
| 5 | 86–87 | Target-liquidity calculation and bankruptcy | Gemini’s $1-cash Boardwalk build immediately produced a rent Grok could not meet under any unilateral legal liquidation |
| 6 | 88–118 | Rapid brown/light-blue capitalization and forced unwind | GPT showed fast execution, immediate rent realization, and then exposure created by development at thin cash buffers |
| 7 | 99–120 | Reservation-price discovery and staged green activation | Rejected offers became a $550 seller-initiated deal; Gemini waited before spending $1,106 to activate the set |
| 8 | 125–141 | Correction-resistant negotiation and a $30 completion auction | Claude rejected a true pink-completion exchange; later auctioned Atlantic into Gemini’s yellow completion |
| 9 | 131–154 | Building churn, terminal liquidation, and estate concentration | Locally negative reversals reduced GPT’s cash; the terminal bankruptcy itself was mechanically unavoidable |

## Case 1 — Water Works: complement value versus a false ownership premise

### Evidence capsule

- **Exact window:** turn 13, `dec-000031`–`dec-000039`, event seq 223–270; authoritative start-turn state is `run/state/turn_0013.json`.
- **Pre-state:** GPT had $700 cash/$1,500 estimated net worth, four deeds, no buildings or mortgages; Gemini had $950/$1,700, three deeds including Electric Company, no buildings or mortgages; Claude had $1,194/$1,514 and two undeveloped deeds; Grok had $1,636/$1,636 and no deeds. Control was therefore Gemini’s real one-utility complement versus GPT’s nonexistent utility ownership. No developed rent exposure existed; the material liquidity exposure was the winner’s auction price.
- **Menu, choice, and model-visible rationale:** Claude’s menu was buy Water Works or start an auction; it chose auction. Every bidder then saw bid/drop. Gemini’s public and private reports both used its real Electric complement; GPT’s public and private reports both used the false premise that it owned Electric. The selected path was Gemini bids to $130 and GPT drops.
- **Effect and horizon:** Gemini paid $130 and completed the utility pair immediately. The later value remained roll-dependent; dropping earlier was a demonstrated legal alternative, but no branch oracle establishes the best bidder thresholds.

### Situation and legal surface

Claude landed on unowned Water Works at turn 13. `dec-000031` offered `buy_property` or `start_auction`; Claude chose the auction. Every active player then received the normal `bid_auction`/`drop_out` menu (`dec-000032` through `dec-000039`).

The relevant ownership fact was simple: Gemini already owned Electric Company; GPT did not. That fact is visible in the pre-decision snapshot and in the purchase history in `run/events.jsonl`.

### Sequence

1. Gemini opened at $60 (`dec-000032`, events seq 228–232), publicly explaining that Water Works would complete its utility pair.
2. Grok dropped (`dec-000033`), correctly noting no building path.
3. GPT bid $90 (`dec-000034`, seq 238–242) and publicly said it was completing the utility pair.
4. Claude dropped, Gemini bid $100, GPT bid $120, and Gemini raised to $130 (`dec-000035`–`dec-000038`, seq 243–262).
5. GPT dropped at `dec-000039`; the episode closed with Gemini purchasing Water Works for $130 (seq 263–270).

### Economics and state fidelity

For Gemini, the marginal property changed utility rent from the one-utility dice multiplier to the two-utility multiplier. The exact future rent remained dice-dependent, but the complement itself was real. For GPT, the same complement claim was false because it did not own Electric Company. GPT nevertheless stopped at $120, only $10 below Gemini’s winning price, so the mistaken premise affected a materially competitive bid rather than an inconsequential message.

GPT’s final drop report then identified Gemini as the utility owner. The within-episode correction is important: this is a strong D1 state-error candidate, but not evidence that GPT knowingly tried to mislead the table. The public claim and the bidding behavior are consistent with temporary self-state confusion.

### Alternatives and downstream result

The demonstrated unilateral alternative for GPT was to drop at its first prompt. That would preserve its bids—auction bids were not charged unless winning—so the economic effect in this realized run was mainly that it forced Gemini’s price to $130. Whether letting Gemini win at $60 would have improved GPT’s later position is a table-externality question, not a unilateral payoff fact.

Claude also had `buy_property` at the first decision, but a claim that buying was better would require pricing the utility and later liquidity. Grok and Claude’s drops were legally valid, coherent with their stated non-synergy, and not oracle-labeled.

### Significance and limit

This case cleanly separates strategic language from board accuracy. “Complement value” was an economically valid concept for one bidder and a false premise for another. The event-level auction contract made the error observable without inferring intent. One auction does not establish a general tendency for either model.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `run/decisions.jsonl`, `run/actions.jsonl`, `run/events.jsonl` seq 223–270; `analysis/review/review_packet.jsonl`, `dec-000031`–`dec-000039`; relevant turn-13 files under `run/state/`.

## Case 2 — Turn 44: a monopoly trade financed by a second concentration trade

### Evidence capsule

- **Exact window:** turn 44, `dec-000109`–`dec-000126`, event seq 773–871; pre-state `run/state/turn_0044.json`.
- **Pre-state:** GPT had $404 cash/$1,674 estimated net worth, six undeveloped and unmortgaged deeds including Park Place and Pacific; Gemini had $476/$2,096, seven undeveloped and unmortgaged deeds including Boardwalk, North Carolina, and two railroads; Grok had $1,049/$1,609 with three undeveloped, unmortgaged deeds including B. & O.; Claude had $913/$1,473 and three undeveloped deeds. Dark blue was blocked across GPT/Gemini, GPT was two-of-three green, and Grok was one railroad; no player had buildings or mortgage liability at the start.
- **Menu, choice, and rationale:** Gemini’s post-turn menu allowed trade or financing but not dark-blue construction before control changed. Publicly it sold GPT on cash plus green progress; privately it prioritized monopoly completion and retained liquidity. GPT’s public holdout extracted concessions, while its private report falsely called the received position a completed green monopoly. Grok’s public/private rationale recognized railroad synergy. The selected sequence was the five-step Park counterchain, acceptance, a separate two-rail sale, then the newly legal two-house build.
- **Effect and horizon:** Park Place changed control, $350 and North Carolina went to GPT, two railroads went to Grok for $380, and Gemini spent $400 to develop dark blue in the same turn. Any reject/stop alternative was legal, but later rent and bankruptcy externalities require the observed downstream sequence or a branch oracle.

### Pre-state and leverage

Before turn 44, Gemini held Boardwalk but needed GPT’s Park Place. GPT held Park Place and Pacific Avenue; Gemini held North Carolina Avenue, while Pennsylvania Avenue remained unowned. The turn-level table shows approximately:

- GPT: $404 cash, estimated net worth $1,674;
- Gemini: $476 cash, estimated net worth $2,096;
- Grok: $1,049 cash, estimated net worth $1,609.

Gemini’s legal post-turn menu allowed proposals and mortgages but did not allow dark-blue building until Park Place changed hands.

### Negotiation chain

Gemini opened with North Carolina Avenue + $250 for Park Place (`dec-000109`, events seq 773–777). Its public message accurately said GPT would then own two of three greens and that Pennsylvania remained unowned.

The canonical counter chain was:

- GPT: North Carolina + $400 (`dec-000110`);
- Gemini: North Carolina + $300 (`dec-000111`);
- GPT: North Carolina + $425 (`dec-000112`);
- Gemini: North Carolina + $350 (`dec-000113`);
- GPT: accept (`dec-000114`, seq 798–806).

The accepted terms transferred Park Place to Gemini and North Carolina + $350 to GPT. GPT’s reported private rationale described receiving a “green monopoly,” which was false until the later turn-61 auction. The deal nevertheless had real value: cash plus a second green for a property Gemini valued as a completion piece.

### Financing chain

After several rejected attempts to sell Indiana Avenue, Gemini offered Grok Reading Railroad + Pennsylvania Railroad for $380 (`dec-000123`). Grok, already holding B. & O., accepted (`dec-000124`, seq 852–860), reaching three railroads.

That second deal was not incidental. Gemini had paid $350 in the Park Place exchange. The $380 inflow replaced that liquidity and activated the next legal menu: `dec-000125` now included `build_houses_or_hotel`. Gemini built one house on Park Place and one on Boardwalk for $400 (events seq 861–867) and ended turn 44 with $106.

### Mechanism economics

The three-player chain produced distinct portfolio transformations:

- GPT converted premium denial into $350 and a green route, ending near $754 cash/$1,974 net worth.
- Gemini converted North Carolina, $350, and two railroads into a completed dark-blue monopoly with two houses, ending near $106 cash/$1,776 net worth.
- Grok converted $380 into three-rail rent.

The snapshot transition from turn 44 to 45 in `analysis/tables/state_by_turn_player.csv` confirms those balance changes. The trades also created a future loop: the dark-blue engine eventually bankrupted Grok, returning the railroad estate to Gemini at turn 87.

### Communication, opponent modeling, and alternatives

Gemini’s public bargaining was unusually state-specific: it named the unowned Pennsylvania Avenue, GPT’s cash after each proposed price, and its own reserve constraint. GPT used credible holdout leverage; Gemini responded without simply accepting the first counter. Grok recognized rail synergy and accepted promptly.

Public/private differences do not meet a deception threshold. Gemini publicly framed mutual benefit while internally prioritizing its monopoly and development. That is ordinary bargaining. GPT’s “green monopoly” report is a D1 error because the pre-state disproves it.

GPT could unilaterally reject and retain Park Place; Gemini could stop increasing the offer; Grok could reject the rails. None of those legal alternatives has a demonstrated superior endpoint. The realized externality—dark-blue concentration—was visible, but its eventual dice path is an oracle/branch issue.

### Significance and limit

This case shows why trades should be analyzed as chains, not isolated accepted episodes. The first exchange created the monopoly; the second funded buildings in the same turn. Evaluating Park Place without the railroad sale would miss the capital-conversion mechanism.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `dec-000109`–`dec-000126`; `run/events.jsonl` seq 773–871; `analysis/expanded_metrics/trade_episodes.csv`; `analysis/tables/state_by_turn_player.csv`, turns 44–45; turn-44 decision snapshots in `run/state/`.

## Case 3 — Claude’s “pink monopoly”: an error that survived the legal surface

### Evidence capsule

- **Exact window:** formation at turn 35 (`dec-000082`–`dec-000085`, seq 591–612), corrective negotiations at turns 126 and 139 (`dec-000318`–`dec-000325`, seq 2333–2378; `dec-000361`–`dec-000364`, seq 2652–2671), and bankruptcy at turn 147 (`dec-000383`, seq 2809–2818).
- **Pre-state and evolution:** at turn 35 Claude had $1,288 cash/$1,608 estimated net worth, two undeveloped/unmortgaged deeds (St. Charles and Tennessee), no color control, and no mortgage liability; GPT had $134/$1,644 and seven undeveloped/unmortgaged deeds including Illinois. After paying $300, Claude controlled only one deed in each of pink, orange, and red. By turn 147 it had $840/$1,400, the same three undeveloped deeds, no monopoly/buildings/mortgages, and faced $1,500 rent with only $280 of legal mortgage capacity.
- **Menus, choices, and rationale:** trade menus allowed the Illinois purchase and later color-correcting exchanges; the engine never exposed a build action. Claude’s public and private reports nevertheless agreed that the mixed trio was a complete pink set. At bankruptcy, the selected action was declare after the legal mortgage/bankruptcy menu; the model reported only $270 of mortgage capacity, $10 below the canonical $280.
- **Effect and horizon:** the false map shaped acquisition, repeated no-build turns, rejected corrections, and the final account. The turn-139 acceptance route was negotiated and un-replayed; it would create a true pink set, but no oracle shows that it would prevent bankruptcy.

### Formation of the false premise

Claude’s early board map was initially correct. At turn 9 its messages identified Tennessee Avenue as orange. It owned St. Charles Place (pink) and Tennessee (orange), then began describing them as a two-property pink base.

At turn 35 Claude offered GPT $200 for Illinois Avenue (`dec-000082`). GPT attempted a $400-cash counter on the first attempt at `dec-000083`; the validator rejected it for insufficient cash. The corrective attempt countered at $300, and Claude accepted (`dec-000084`, events seq 601–608).

The resulting three deeds were:

- St. Charles Place — pink;
- Tennessee Avenue — orange;
- Illinois Avenue — red.

No color set was complete.

### Protocol evidence against the belief

Claude immediately said “Pink monopoly complete” at `dec-000085`. It repeated the premise across dozens of later end-turn messages. The legal menu is decisive evidence: Claude’s post-turn decisions continued to offer actions such as `end_turn`, `propose_trade`, and `mortgage_property`, but never `build_houses_or_hotel`. The event stream contains zero Claude house or hotel builds.

The absence is not merely outcome-based. MonopolyBench’s engine is authoritative and would expose building only if the rules allowed it. Thus:

- fact: Claude never had a buildable monopoly;
- reported rationale: Claude believed it was preserving and preparing a pink engine;
- interpretation: the internal board map was not updated by repeated action-menu evidence.

### Direct correction and negotiation consequence

At turn 126, Gemini first offered $200 and then $300 for Tennessee (`dec-000318`–`dec-000321`). Claude rejected both as attacks on its complete pink set. Gemini then offered Virginia Avenue + $100 and explicitly stated the colors: Tennessee orange, St. Charles and Virginia pink (`dec-000324`, seq 2365–2369).

Claude replied:

> “Tennessee Avenue is PINK ... Virginia Avenue is ORANGE.”

That public statement at `dec-000325` is false. The corresponding private report held the same premise. Because the error was self-harming and cross-channel consistent, the supported communication label is D1, not deception.

At turn 139, the consequence became even clearer. Gemini offered States Avenue + Virginia Avenue for Tennessee (`dec-000361`). Acceptance would have given Claude the actual pink trio—St. Charles, States, Virginia—and Gemini the actual orange trio—St. James, Tennessee, New York. Claude rejected and said States/Virginia “don’t form anything useful.” Gemini added Indiana, which would also place Claude one short of red; Claude rejected again (`dec-000363`–`dec-000364`).

### Capital and endpoint

Claude paid $300 for Illinois but never monetized a monopoly. Its derived rent ledger is $1,435 paid and $152 received. At turn 125 it mortgaged St. Charles for $70 and immediately unmortgaged for $77 (`dec-000315`–`dec-000316`, seq 2313–2324), a $7 loss with no persistent state change.

At turn 147 it owed $1,500 on a dark-blue hotel with $840 cash. The legal menu allowed mortgages or bankruptcy. Claude reported $270 of mortgage proceeds and a $390 gap, but the canonical mortgage values total $280: exact maximum liquidity was $1,120 and the exact shortfall was $380. It declared (`dec-000383`, seq 2809–2818). Its final self-explanation again referred to missed development on Tennessee/Illinois, which the legal history disproves.

### Alternatives and claim boundary

The turn-139 first offer is a demonstrated legal **proposal**, but acceptance is still a negotiated branch because Claude could choose it and future development/dice were not replayed. It is fair to say the deal would create the color sets under the rules. It is not fair to say it would prevent Claude’s bankruptcy.

At turn 147, unilateral survival was impossible: $840 + $280 = $1,120, $380 below the bill. Calling the terminal declaration correct does not excuse either the $10 crisis arithmetic error or the earlier state error; it separates immediate insolvency from long-run causes.

### Significance and limit

This is the run’s strongest example of a benchmark-relevant factual fixation: it affected acquisition, repeated inaction, rejection of corrective evidence, opponent accusations, and postmortem reasoning. The conclusion is about this saved game and this protocol trace, not a general property of Claude Haiku 4.5.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** turn 9 and 18–147 records in `analysis/review/chronological_turn_review.md`; `dec-000082`–`dec-000085`, `dec-000315`–`dec-000325`, `dec-000361`–`dec-000364`, `dec-000383`; `run/events.jsonl` seq 591–612, 2313–2378, 2652–2671, 2809–2818; `run/decisions.jsonl`; `analysis/expanded_metrics/player_metrics.csv`.

## Case 4 — Pennsylvania Avenue: discounted completion, then a four-turn liquidity shock

### Evidence capsule

- **Exact window:** auction at turn 61, `dec-000172`–`dec-000176`, seq 1179–1206; rent/liquidation at turn 65, `dec-000187`–`dec-000195`, seq 1279–1333.
- **Pre-state:** at turn 61 GPT had $245 cash/$2,025 estimated net worth, nine undeveloped and unmortgaged deeds, and control of Pacific plus North Carolina; Pennsylvania Avenue would complete green. Gemini had $79/$1,874, five deeds, three dark-blue houses, two mortgages, and $75 mortgage liability. At turn 65 GPT had $89/$2,189, ten deeds and the complete but still undeveloped/unmortgaged green set; it then faced $600 Boardwalk rent. Its cash exposure was therefore $511 before financing, while the property base supplied a legal mortgage route.
- **Menu, choice, and rationale:** Claude saw buy/auction and chose auction, publicly tying the choice to its false pink focus. Auction bidders saw bid/drop; GPT privately and publicly recognized true green completion and won at $180. Four turns later the forced menu was mortgage or bankruptcy; GPT selected six debt-covering mortgages and then two optional buffer mortgages.
- **Effect and horizon:** the cheap completion immediately increased control but the shock disabled that control through mortgages. Dropping at turn 61 was legal and mortgaging at turn 65 demonstrated survival; no oracle prices the forgone green option against preserved cash.

### Acquisition

At turn 61 Claude landed on Pennsylvania Avenue. Its `BUY_OR_AUCTION_DECISION` offered buy or auction; it chose auction because the property did not serve its claimed pink plan (`dec-000172`, seq 1179–1183).

Gemini and Grok dropped. GPT, already holding Pacific and North Carolina, bid $180 at `dec-000175`. Claude then dropped at `dec-000176`, and GPT won Pennsylvania Avenue for $180 (events seq 1194–1206). The purchase completed green at a discount to the printed $320 price.

This is a locally strong acquisition under a non-oracle standard:

- the completion fact was exact;
- the bid was below list price;
- no competing player forced a higher price;
- GPT had the legal cash to pay.

Claude’s auction message again invoked future pink development that was not legally available. The important externality was not that Claude failed to buy for itself, but that it exposed a high-value completion asset to GPT at a single-bid price.

### Delayed shock

At the start of turn 65, the state table records GPT around $89 cash, $2,189 estimated net worth, and $2,100 property face value. GPT then landed on Gemini’s Boardwalk and owed $600.

The liquidation menu at `dec-000187` allowed `mortgage_property` or `declare_bankruptcy`. GPT sequentially mortgaged Baltic, Vermont, Pennsylvania, Pacific, New York, and States (`dec-000187`–`dec-000192`, seq 1279–1317). After satisfying the debt, optional post-turn decisions mortgaged Marvin and Kentucky for a buffer (`dec-000193`–`dec-000194`). It ended with $299 cash and eight more encumbered properties; the next snapshot estimates net worth at $1,589.

### Causal interpretation

The green auction did not itself cause the rent. Dice caused the Boardwalk landing, and Gemini’s earlier development set the rent. The mechanism-level tension is that GPT converted $180 into a valuable monopoly while carrying only $89 cash four turns later. Because the greens were mortgaged during survival, completion did not become an immediate building engine.

The realized sequence therefore contains both:

- **cheap excellence:** recognizing and winning the completion piece for $180;
- **delayed capital failure:** not retaining enough liquid capacity to keep the completed set active after a plausible rent shock.

The second phrase is not an oracle claim that a specific cash threshold was optimal. It is grounded in the observed forced mortgages and $600 net-worth drawdown.

### Alternatives

At turn 61 GPT could drop and preserve $180, but that would surrender green and potentially let Claude retain or another player acquire Pennsylvania. No branch establishes superiority.

At turn 65 the mortgage sequence demonstrated survival. Declaring bankruptcy was legal but plainly unnecessary because mortgage proceeds covered the bill. The ordering protected some assets longer than others, although GPT’s public “lowest synergy” descriptions were imperfect—mortgaging Pennsylvania and Pacific disabled the newly completed green.

### Significance and limit

This case is useful because it prevents simplistic labels. A strategically excellent acquisition can coexist with a fragile balance sheet. The later shock does not retroactively make the auction bid bad; it exposes the missing liquidity layer around it.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `dec-000172`–`dec-000176`, events seq 1179–1206; `dec-000187`–`dec-000195`, seq 1279–1333; `analysis/tables/state_by_turn_player.csv`, turns 61 and 65–66; relevant snapshots in `run/state/`.

## Case 5 — Four-house Boardwalk: calculated aggression and immediate unilateral insolvency

### Evidence capsule

- **Exact window:** turn 86 build/end `dec-000223`–`dec-000224`, seq 1588–1597; turn 87 liquidation/declaration `dec-000225`, seq 1598–1614.
- **Pre-state:** Gemini had $201 cash/$2,846 estimated net worth, six deeds, seven dark-blue houses, two mortgages and $185 mortgage liability; Grok had $823/$1,983, six undeveloped/unmortgaged deeds including four railroads, no buildings, and $580 maximum mortgage proceeds. Gemini controlled dark blue at 4/3 houses; Grok’s total immediate liquidity was $1,403 and its direct exposure after the contemplated build was $1,700 Boardwalk rent.
- **Menu, choice, and rationale:** Gemini’s legal menu included build, mortgages, sales, trades, or end. It publicly announced the upgrade and privately computed opponent liquidation capacity, selected the $200 fourth Boardwalk house, and ended at $1. Grok’s next menu contained mortgage or bankruptcy; its public/private arithmetic independently matched the $1,403 ceiling and it declared.
- **Effect and horizon:** the build raised rent to $1,700 and the realized next roll transferred $823 plus six deeds to Gemini. Ending without building or pre-financing was legal; earlier rescue/trade paths are negotiated or branch alternatives, so only immediate unilateral insolvency is claimed.

### Pre-state

By turn 86, Gemini had four houses on Park Place and three on Boardwalk. Grok had $823 cash, no buildings, and a portfolio of six deeds including four railroads. Gemini had $201 before the optional build and a legal post-turn menu including building, mortgages, sales, trades, and end turn.

### Decision and reported model

At `dec-000223`, Gemini spent $200 to add the fourth Boardwalk house (events seq 1588–1593), leaving $1. Its public message advertised the upgrade. Its reported private rationale explicitly estimated Grok’s maximum liquidation:

- cash: $823;
- all mortgages: $580;
- maximum funds: $1,403;
- four-house Boardwalk rent: $1,700.

The arithmetic implied a $297 deficit. Gemini ended turn at `dec-000224`.

### Realized next turn

Grok immediately landed on Boardwalk. `dec-000225` presented only `mortgage_property` and `declare_bankruptcy`; there were no building sales because Grok owned no buildings. Grok independently reported the same $580 mortgage ceiling and declared bankruptcy (events seq 1602–1614). The engine transferred Grok’s six properties and $823 cash to Gemini.

This is unusually strong local causal evidence:

- the targeted exposure existed before the build;
- the rent increased to $1,700;
- the identified opponent landed there on the next turn;
- the legal menu and asset values demonstrated no unilateral survival path.

### Risk and capital economics

Ending with $1 was genuinely risky. Gemini could have kept $201 by ending the turn, mortgaged an asset before building, or built elsewhere/less. If Gemini had incurred a charge before collecting rent, it might have needed to sell buildings at half cost or mortgage. Thus the case should not be romanticized as costless precision.

What differentiates the play from blind overextension is the opponent-specific solvency model and immediate realization. The $200 investment converted Boardwalk rent to a level $297 above Grok’s maximum unilateral funds. The subsequent bankruptcy delivered six deeds and $823 cash, moving Gemini’s estimated net worth from about $2,846 before Grok’s turn to $4,829 after the transfer.

### Bankruptcy claim boundary

The **immediate** bankruptcy was unavoidable through unilateral legal actions. That statement is proven by the menu and values. Earlier alternatives—selling railroads, trading Ventnor, initiating a rescue trade, or blocking Park Place—are negotiated or branch-dependent. They can be discussed as strategic possibilities but cannot support an “avoidable bankruptcy” label without a replay or accepted-deal path.

There was no terminal negotiation prompt at turn 87. The engine asked Grok to mortgage or declare. Therefore it would be incorrect to criticize Grok for failing to propose a rescue inside that decision.

### Significance and limit

This case captures targeting, opponent modeling, leverage, and table concentration in a compact window. It also illustrates the benchmark’s distinction between a strong realized decision and universal optimality: one next-turn landing cannot establish how often $1-cash aggression would succeed.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `dec-000223`–`dec-000225`; `run/events.jsonl` seq 1588–1614; turn-86/87 decision artifacts and snapshots; `analysis/tables/state_by_turn_player.csv`, turns 87–88; `analysis/review/bankruptcy_windows.md`.

## Case 6 — Brown and light blue: fast monetization, then forced unwind

### Evidence capsule

- **Exact window:** brown conversion `dec-000226`–`dec-000232` at turn 88; light-blue purchase/development `dec-000268`–`dec-000275` at turn 109; liquidation/re-entry `dec-000284`–`dec-000296` at turns 117–118, including the retry at `dec-000294`.
- **Pre-state panels:** at turn 88 GPT had $254 cash/$1,744 estimated net worth, 11 deeds, six mortgages/$730 liability, and no buildings; Mediterranean was unowned and would complete brown. At turn 109 GPT had $566/$1,806, nine deeds, two brown hotels, seven mortgages/$620 liability; Oriental would complete light blue. At turn 117 it had $24/$1,774, ten deeds, six light-blue houses plus two brown hotels, five mortgages/$510 liability, and immediate $200 rent exposure.
- **Menus, choices, and rationale:** buy/auction led to a direct $60 purchase; post-turn menus allowed staged builds, mortgages, or stopping, and GPT publicly announced the new engines while privately prioritizing rapid capitalization. The Oriental episode used propose/counter/accept, followed by unmortgage/build choices that left $24. Forced menus later allowed building sales or bankruptcy; GPT selected sales, then optional financing/rebuild, and corrected one invalid nonexistent-hotel sale without fallback.
- **Effect and horizon:** brown earned $250 on the next opponent turn; light blue created a second engine; two $200 shocks then forced half-price liquidation and exposed the thin reserve. Stopping at several earlier menu points was unilateral and would preserve cash, but no oracle establishes a winning stop point.

### Brown conversion at turn 88

After Grok’s elimination, GPT landed on unowned Mediterranean Avenue. `dec-000226` offered buy or auction; GPT bought for $60, completing brown. It then executed:

1. three houses on each brown, cost $300 (`dec-000227`);
2. mortgage St. James Place, +$90 (`dec-000228`);
3. a fourth house on each brown, cost $100 (`dec-000229`);
4. mortgage North Carolina Avenue, +$150 (`dec-000230`);
5. hotel conversion on both browns, cost $100 across the pair (`dec-000231`).

The engine-enforced even-building sequence was legal. GPT ended turn with $134 cash, two brown hotels, and $970 in open mortgage proceeds according to the snapshot/accounting join. On turn 89 Claude landed on Mediterranean and paid $250. That immediate receipt demonstrates the engine worked; it does not by itself prove the full leveraged build was optimal.

### Light-blue completion at turn 109

After selling green at turn 106, GPT had more cash. At turn 109 it offered Gemini $250 for Oriental (`dec-000268`). Gemini countered $320 because Oriental completed GPT’s set (`dec-000269`), and GPT accepted (`dec-000270`, seq 1964–1971).

GPT then paid $56 to unmortgage Vermont and $66 for Connecticut, followed by two even rounds of light-blue houses costing $150 each (`dec-000271`–`dec-000274`). It ended the turn with $24. The action chain is strategically coherent—acquire the blocker, reactivate the set, build evenly—but the reserve was again extremely thin.

Gemini’s bargaining deserves separate credit: it recognized completion value and the buyer’s available cash, countered above GPT’s opening, and obtained $320. Publicly explaining strategic value while privately noting liquidity leverage is normal negotiation, not deception.

### Forced unwind at turns 117–118

At turn 117 GPT owed $200 with $24 cash. Its liquidation decision allowed building sales or bankruptcy. It sold both brown hotels and two houses from each light blue to cover the bill (`dec-000284`, seq 2077–2089). It then performed a long post-turn financing/rebuild sequence, including mortgage/unmortgage cycling.

At turn 118 another $200 obligation produced another liquidation chain. `dec-000293` sold both brown hotels; `dec-000294` first attempted to sell a hotel that no longer existed, was rejected, and on corrective retry sold houses evenly. The run recorded the invalid attempt and recovery; no fallback occurred.

The state table captures the erosion:

- before turn 117: $24 cash, $1,774 estimated net worth, and $800 of buildings;
- after the first unwind: roughly $78 cash, $1,368 net worth, $500 buildings;
- after the next cycle: roughly $78 cash, $968 net worth, $100 buildings by turn 120.

### Interpretation and alternatives

The build sequences were not mere errors. Brown produced an immediate $250 rent, and light blue created a second threat zone. The failure mechanism was capital structure: purchase + unmortgages + $300 development left $24, so ordinary $200 rents forced half-price building liquidation.

At turn 109 GPT could legally stop after the trade, after either unmortgage, or after the first building round. Those are demonstrated unilateral alternatives. The record supports saying they would retain more cash. It does not support saying any particular stopping point would win the game.

At turns 117–118, selling buildings was necessary for survival under the menu. The correct critique targets the earlier reserve choice and the invalid nonexistent-hotel attempt, not the liquidation itself.

### Significance and limit

This case gives a balanced example of strong execution and expensive fragility in the same player. It also shows why total “building churn” must be decomposed: forced sales are defensive competence, while re-entry at low cash can recreate the exposure.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `dec-000226`–`dec-000232`, turn-88 events beginning seq 1620; `dec-000268`–`dec-000275`, seq 1954–2003; `dec-000284`–`dec-000296`, seq 2077–2167; `analysis/tables/state_by_turn_player.csv`, turns 88–89 and 117–120; `quality_check/` artifacts for `dec-000294`.

## Case 7 — Green: reservation-price discovery, distressed sale, and staged activation

### Evidence capsule

- **Exact window:** rejected bids `dec-000247`–`dec-000254` at turns 99/102; distress sale `dec-000259`–`dec-000264` at turn 106; activation `dec-000298`–`dec-000302` at turn 120; terminal collection `dec-000393`–`dec-000395` at turn 153.
- **Pre-state panels:** at turn 99 GPT had $101 cash/$1,961 estimated net worth, 12 deeds, two brown hotels, nine mortgages/$920 liability, and full green control; Gemini had $1,236/$5,241, 12 deeds, two dark-blue hotels, two mortgages/$185 liability. At turn 106 GPT had $81/$1,941 with the same developed/mortgaged structure and an immediate $200 rent shock; Gemini had $753/$5,233. At turn 120 Gemini had $1,259/$6,099, 14 deeds, two hotels, four mortgages/$570 liability, and the mortgaged green trio; clearing and one-house development cost $1,106.
- **Menus, choices, and rationale:** proposal menus produced $450 and $500 bids rejected by GPT, whose public/private stance valued the monopoly blocker. Under distress GPT’s forced menu first required mortgage/building sale; its later post-turn menu enabled a seller-initiated $550 proposal, which Gemini accepted. Gemini’s later menu allowed redemptions/build/end; public messages announced activation while private reports emphasized portfolio expansion and retained reserve.
- **Effect and horizon:** GPT extracted a higher nominal price after waiting but absorbed an intervening shock; Gemini delayed development, retained $353 after activation, and collected the terminal $130 rent 33 turns later. Earlier acceptance, retention, or faster development are legal/negotiated branches, not oracle-ranked alternatives.

### Rejected approaches

Gemini first offered GPT $450 for all three greens at turn 99 (`dec-000247`). GPT rejected (`dec-000248`). At turn 102 Gemini raised to $500 (`dec-000253`), and GPT again rejected (`dec-000254`).

The greens were complete but encumbered. GPT’s resistance preserved option value; Gemini’s increased bid revealed its demand. Neither rejection was invalid or unresponsive.

### Changed conditions and seller-initiated deal

At turn 106 GPT paid $200 rent and entered liquidation. It mortgaged Pennsylvania at `dec-000259`, then sold a brown hotel at `dec-000260`. In the subsequent post-turn menu it proposed the full mortgaged green set for $550 (`dec-000261`, seq 1895–1899). Gemini accepted at `dec-000262`.

The accepted exchange matters for bargaining analysis:

- GPT obtained $50 more than Gemini’s last offer and $100 more than the first.
- Gemini obtained the exact monopoly it had pursued.
- GPT transferred inherited mortgage liabilities with the deeds.
- The accepted proposal came from GPT only after a realized rent shock changed its liquidity needs.

The state transition from turns 106 to 107 is approximately GPT $81 to $566 cash and $1,941 to $1,806 estimated net worth; Gemini moved to $357 cash/$5,297 net worth with the greens and their mortgages.

### Staged activation

Gemini did not immediately spend its remaining cash on the new set. At turn 120 it had accumulated about $1,459. It then:

- unmortgaged Pacific for $165 (`dec-000298`);
- unmortgaged North Carolina for $165 (`dec-000299`);
- unmortgaged Pennsylvania for $176 (`dec-000300`);
- built one house on each green for $600 (`dec-000301`);
- ended with $353 (`dec-000302`).

Total activation outlay was $1,106. The even-build requirement was satisfied, and all three deeds became rent-bearing before construction.

### Downstream effect

At the terminal turn, GPT rolled to North Carolina Avenue and owed $130. That one-house rent, not dark blue or the later yellow build, triggered the final liquidation chain. This establishes a long delayed causal path:

turn-44 North Carolina trade → turn-61 green completion → turn-65 mortgages → turn-106 sale → turn-120 activation → turn-153 $130 rent.

No single link was sufficient on its own; the case is valuable precisely because the terminal mechanism began 109 turns earlier.

### Alternatives and significance

GPT could accept $450 or $500 earlier, retain the greens, or seek a different buyer later. The realized record shows that waiting extracted $550, but it also shows an intervening $200 rent and hotel sale. A full welfare comparison would need to price those events and future branches.

Gemini could develop sooner or spend more at turn 120. Its staged choice is strong under a liquidity-mechanism standard because it retained $353 and never had to sell a building. This remains a one-run observation.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `dec-000247`–`dec-000254`, events seq 1791–1847; `dec-000259`–`dec-000264`, seq 1880–1920; `dec-000298`–`dec-000302`, seq 2186–2215; terminal `dec-000393`–`dec-000395`, seq 2884–2915; `analysis/tables/state_by_turn_player.csv`.

## Case 8 — Correction-resistant bargaining and the $30 Atlantic completion

### Evidence capsule

- **Exact window:** Tennessee offers `dec-000318`–`dec-000326`, seq 2333–2378; double-monopoly offers `dec-000356`–`dec-000366`, seq 2614–2681; Atlantic auction `dec-000372`–`dec-000376`, seq 2721–2747.
- **Pre-state panels:** at turn 126 Gemini had $564 cash/$6,654 estimated net worth, 16 deeds, three green houses plus two dark-blue hotels, three mortgages/$300 liability, and two-of-three orange; Claude had $810/$1,370, three undeveloped/unmortgaged mixed-color deeds and no group. At turn 139 Gemini had $535/$6,955, 17 deeds and the same developed control; Claude had $960/$1,520. At turn 141 Gemini had $285/$7,095, 18 deeds, no mortgages, two-of-three yellow; Claude had $970/$1,530 and no development. GPT had only $29 at the Atlantic auction, limiting its blocking capacity.
- **Menus, choices, and rationale:** trade menus allowed Gemini to vary cash and property bundles; its public/private rationale moved from orange acquisition to a rules-correct mutual completion, while Claude’s public/private replies preserved the reversed colors. Atlantic’s menu was buy or auction; Claude chose auction, then bidders saw bid/drop and Gemini selected $30. Gemini’s public/private auction rationale correctly recognized yellow completion.
- **Effect and horizon:** no Tennessee trade closed, but Gemini later acquired Atlantic for $30 and completed yellow. Claude could buy or bid higher and could accept the color-correct trade; affordability is demonstrated, endpoint superiority is not, so the alternatives remain unranked without a branch oracle.

### Tennessee episode

By turn 126, Gemini held St. James Place and New York Avenue and needed Claude’s Tennessee Avenue for orange. Claude falsely treated Tennessee as part of its pink monopoly.

Gemini tried three structures:

1. $200 cash (`dec-000318`);
2. $300 cash (`dec-000320`);
3. Virginia Avenue + $100 (`dec-000324`).

Claude rejected each (`dec-000319`, `dec-000321`, `dec-000325`). The third offer was tailored to Claude’s stated pink goal and explicitly corrected the colors. Claude responded by reversing them and accusing Gemini’s board account of being wrong.

This is a negotiation failure driven by incompatible state representations rather than inadequate price discovery alone. Gemini changed both price and bundle; Claude did not engage the corrected property geometry.

### True double-monopoly proposal

At turn 139 Gemini bought States Avenue from GPT for $80 (`dec-000359`–`dec-000360`) and then offered States + Virginia for Tennessee (`dec-000361`). Under the board rules:

- Claude would receive St. Charles + States + Virginia: pink monopoly;
- Gemini would receive St. James + Tennessee + New York: orange monopoly.

Claude rejected (`dec-000362`). Gemini added Indiana (`dec-000363`), which would also give Claude Indiana + Illinois, two of three reds; Claude rejected again.

This is unusually direct evidence that the false belief constrained responsiveness. Acceptance and future development are still negotiated/branch alternatives, so the case does not claim the rejected deal would save Claude.

### Atlantic auction

Two turns later Claude landed on Atlantic Avenue. `dec-000372` offered buy or auction; Claude auctioned, saying Atlantic was irrelevant to its pink plan. Gemini already held Ventnor and Marvin. It bid $30 at `dec-000373`.

GPT, with only $29, dropped (`dec-000374`). Claude dropped at `dec-000375`. Gemini won Atlantic for $30 and completed yellow (events seq 2721–2743).

### Leverage, externality, and state errors

Gemini’s $30 bid was a high-value completion purchase at a small cash cost. Claude’s auction created a supported externality by giving the dominant player another monopoly. Yet “Claude should have bought” is not automatic: buying Atlantic would cost list price and Claude faced a $1,500 bill six turns later. A higher blocking bid was legally available during the auction, but its safe ceiling and future value need an oracle.

Gemini also made its own D1 error at turn 139, calling Indiana part of yellow while unmortgaging it (`dec-000358`). Indiana is red. The later Atlantic bid correctly completed the actual yellow trio, so the record shows both a local state-description error and effective acquisition behavior.

### Significance and limit

The episode demonstrates that negotiation quality depends on shared board truth. Gemini’s price and bundle adaptation could not repair Claude’s false premise. It also shows how a seemingly “irrelevant” auction can have large opponent-specific completion value.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `dec-000318`–`dec-000326`, events seq 2333–2378; `dec-000356`–`dec-000366`, seq 2614–2681; `dec-000372`–`dec-000376`, seq 2721–2747; board colors in `contracts/` and canonical snapshots in `run/state/`.

## Case 9 — Churn and the terminal boundary: local waste, global uncertainty, exact insolvency

### Evidence capsule

- **Exact window:** turn-131 churn `dec-000338`–`dec-000344`, seq 2470–2509; turn-134 liquidation/re-entry `dec-000346`–`dec-000350`, seq 2520–2566; terminal `dec-000393`–`dec-000395`, seq 2884–2915.
- **Pre-state panels:** at turn 131 GPT had $305 cash/$965 estimated net worth, seven deeds, four brown houses, five mortgages/$340 liability; after $16 rent it had $289 for the menu. At turn 134 it had $14/$924, seven deeds, four houses plus one hotel, five mortgages/$340 liability, and incurred $90 utility rent. At turn 153 it had $9/$449, six deeds, one Baltic house, four mortgages/$270 liability, and $94 maximum legal liquidity against $130 North Carolina rent. Gemini then had $495/$9,025, 22 deeds, nine houses, two hotels, no mortgages, and owned the exposing green.
- **Menus, choices, and rationale:** optional build/trade/sale menus enabled the turn-131 sell/rebuild reversal; public messages described each tactical step while private reports alternated between liquidity and maximum-rent goals. Turn 134’s forced sale/bankruptcy menu was followed by optional sale/rebuild and one corrected invalid attempt. Terminal menus narrowed from house sale/bankruptcy to two successive brown mortgages/bankruptcy; public/private reports accurately tracked the remaining deficit and selected every liquidation source.
- **Effect and horizon:** the same-turn turn-131 reversal lost $25 with no intervening state change; turn 134’s optional re-entry surrendered durable capacity without adding cash; terminal liquidation still fell $36 short and transferred the estate. Stopping before the local reversals is a supported unilateral alternative, but carrying those savings through unchanged later rolls is an unverified branch.

### Turn 131: a one-turn $25 reversal

GPT began turn 131 with $305, paid $16 in ordinary rent, and entered its optional-action sequence with $289 before expanding brown:

- `dec-000338`: add two houses to each brown to reach four/four, cost $200 (seq 2470–2476);
- `dec-000339`: convert Baltic to a hotel, cost $50 (seq 2477–2482);
- `dec-000340`: offer three mortgaged light blues to Claude for $200; rejected at `dec-000341`;
- `dec-000342`: sell the Baltic hotel for $25 (seq 2493–2498);
- `dec-000343`: rebuild the Baltic hotel for $50 (seq 2499–2504);
- end with $14 (`dec-000344`).

The sale/rebuild pair is a strict local dominance failure under the realized within-turn state. It changed no ownership or opponent position, restored the same hotel, and reduced cash by $25. The reported rationale moved from liquidity/flexibility to maximum rent within one decision cycle. No dice or external response intervened between the two actions.

`dec-000340` was also an expensive low-result model call in the decision metrics: about $0.022788 and 8,314 tokens, with 4,277 recorded reasoning tokens, for a rejected trade proposal. The usage fact does not prove low reasoning quality, but it is a cost/outcome anomaly worth preserving.

### Turn 134: liquidation followed by immediate re-entry

With $14, GPT incurred a $90 Water Works charge. `dec-000346` sold the Baltic hotel for $25. `dec-000347` first tried to sell a nonexistent hotel; the validator rejected the action and the corrective attempt sold two houses evenly from each brown. After paying the bill, GPT used `dec-000348` to sell the remaining two houses on each brown for another $100, then `dec-000349` immediately built one house on each for $100.

The post-debt sell/build pair produced no net cash and left fewer buildings than before the shock: four houses were sold for $100 and only two were rebuilt for the same $100. Relative to stopping after the mandatory liquidation, the optional pair sacrificed two houses of durable capacity without increasing cash. The engine correctly enforced the actions; the criticism is capital allocation, not legality.

### Terminal window

By turn 153 GPT had $9, one Baltic house, and two unmortgaged brown deeds among its remaining six properties. It rolled 5+3 from Illinois Avenue to North Carolina Avenue (events seq 2884–2887) and owed Gemini $130.

The three legal decisions were:

1. `dec-000393`: sell the Baltic house or declare. GPT sold it for $25; cash became $34 and shortfall $96 (seq 2888–2893).
2. `dec-000394`: mortgage Baltic or Mediterranean, or declare. GPT mortgaged Baltic for $30; cash became $64 and shortfall $66 (seq 2894–2899).
3. `dec-000395`: mortgage Mediterranean or declare. GPT mortgaged it for $30; cash became $94 and the remaining gap was $36 (seq 2900–2904).

No unilateral asset remained. The engine transferred $94 and six deeds to Gemini (seq 2905–2913), emitted `TURN_ENDED`, then `GAME_ENDED` with Gemini winner (seq 2914–2915).

### What can and cannot be claimed

The terminal bankruptcy was mechanically unavoidable at the start of the liquidation window:

`$9 cash + $25 building sale + $30 Baltic mortgage + $30 Mediterranean mortgage = $94 < $130`.

GPT’s sequencing was correct and exhausted every asset. There was no trade action in the menu and no need for an explicit final `declare_bankruptcy` response after the last mortgage; the engine resolved the unsatisfied debt automatically.

Earlier churn contributed to low retained value and is valid causal lead-up. It is still not enough to say the game was “avoidable” at turn 131 or 134. Preserving $25 or $100 changes later balances, but intermediate rents, purchases, and engine choices would need a branch replay before asserting the same terminal state with enough extra cash.

### Significance and limit

This case shows the review standard at its strictest. Same-turn sell/rebuild losses can be criticized without an oracle because their local effects are exact. The final bankruptcy can be called unavoidable because the legal menu and arithmetic prove it. The causal bridge between those facts remains suggestive, not deterministically established.

This is a single-run mechanism case; it supports neither a prevalence estimate nor a cross-model ranking.

**Evidence:** `dec-000338`–`dec-000350`, events seq 2470–2566; `analysis/expanded_metrics/decision_metrics.csv`; `quality_check/` artifacts for `dec-000347`; `dec-000393`–`dec-000395`, events seq 2884–2915; terminal snapshot in `run/state/`; `analysis/review/bankruptcy_windows.md`.

## Cross-case synthesis

### Mechanisms that created durable value

- Pricing a real completion piece: Gemini at Water Works, Park Place, Oriental as seller, green as buyer, and Atlantic.
- Converting non-core assets into productive capital: the turn-44 railroad sale immediately funded dark-blue houses.
- Staging development: Gemini accumulated cash before clearing all green mortgages and building.
- Correct target-liquidity analysis: the turn-86 Boardwalk calculation incorporated mortgage proceeds, not cash alone.

### Mechanisms that destroyed or stranded value

- Acting on a false color map: Claude’s Illinois purchase and Tennessee rejections.
- Building into a thin reserve: GPT’s $24 endpoint after the Oriental/light-blue chain.
- Paying half-price liquidation costs and quickly rebuilding: GPT at turns 131 and 134.
- Keeping liquid but nonproductive fragments: Grok and Claude had terminal cash but no sufficient unilateral income or liquidation engine.

### Communication findings

The strongest evidence-linked claims are D1 candidates:

- GPT’s false utility ownership and premature green/light-blue completion language;
- Claude’s persistent Tennessee/pink and Virginia/orange reversal;
- Gemini’s turn-139 Indiana/yellow statement;
- Grok’s occasional premature four-rail count.

These errors differ in duration and consequence. None, standing alone, demonstrates knowing deception. Public/private alignment in Claude’s case particularly supports sincere state confusion. Gemini’s public mutual-benefit framing alongside private self-interest is ordinary bargaining unless paired with a false proposition or broken commitment.

### Single-run caveat

The endpoint depended on dice landings, opponent acceptance, and sequential bankruptcy transfers. The cases identify mechanisms visible in this trace. They do not establish model rankings, population prevalence, or optimal policies beyond the exact local arithmetic and legal menus documented above.

## Evidence locator

- `run/events.jsonl` — canonical effects and event sequence IDs
- `run/actions.jsonl` — applied actions and attempt results
- `run/decisions.jsonl` — pre-state legal menus
- `run/state/` — authoritative snapshots
- `analysis/review/review_packet.jsonl` — joined decision evidence
- `analysis/review/chronological_turn_review.md` — complete turn context
- `analysis/review/negotiation_review.md` — canonical episode chains and terms
- `analysis/review/bankruptcy_windows.md` — five-decision windows and solvency arithmetic
- `analysis/expanded_metrics/` — derived accounting, trade, auction, mortgage, and cost fields
- `quality_check/` — raw response/validation/retry evidence
