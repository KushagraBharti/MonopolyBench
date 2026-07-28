# Player Dossiers

These are evolving evidence dossiers, not rankings. Facts, reported reasoning, and interpretation are separated. Counts use all 488 applied decisions; outcomes use the final turn-166 snapshot.

ID shorthand `dec-NNNNNN` expands to `mock-3676466999-527872e4-dec-NNNNNN`; full IDs and source paths are available in `chronological_turn_review.md` and `evidence_index.csv`.

## Claude Opus 4.8

Outcome facts: winner; final cash $1624; 28 final deeds; bankrupt_to=n/a. Decision volume 83, model cost $4.30500500, retries 5, fallbacks 0.

Mechanism ledger: actions `{"accept_trade":2,"build_houses_or_hotel":3,"buy_property":6,"counter_trade":3,"drop_out":1,"end_turn":36,"pay_jail_fine":2,"reject_trade":20,"roll_for_doubles":8,"unmortgage_property":2}`; trade proposals sent 0, received 23, accepted episodes involving player 2; houses built 20; rent paid $1882, rent received $5030. Evidence: `run/actions.jsonl`, `run/events.jsonl`, `analysis/review/review_packet.jsonl`.

Early reported reasoning (first decision): “Pink is a high-traffic, high-ROI group near jail. $140 for a monopoly cornerstone is worth it early. Cash stays at $1360, plenty for flexibility. Start building toward the pink monopoly.”

Late reported reasoning (last decision): “Jail is a safe shelter avoiding GPT's 4 railroads. Rolling is free — if I fail I stay parked (which I prefer). Never pay $50 to walk into rail exposure. GPT ($335) is only live rival; I have $1289 and dominant kill zone. Hold and starve him.”

Interpretation: the dossier supports analysis of adaptation only through the full chronological ledger and cited decisions. It does not infer stable personality from message tone, and public/private difference alone is not labeled deception.

### Evolving dossier

Acquisition and consolidation: bought St. Charles at `dec-000000`, exchanged Tennessee for States+$130 at `dec-000024`–`dec-000027`, and completed pink through the Virginia/Connecticut swap `dec-000073`–`dec-000076`. The sequence is internally consistent with the early pink plan and uses other players' blockers rather than repeated cash bids.

Development and scarcity: built nine pink houses at `dec-000091`, then three more at `dec-000143`. Thereafter Claude repeatedly declined hotels to keep houses out of the bank. After Grok's bankruptcy transferred dark blues, `dec-000434`–`dec-000436` consumed the final eight bank houses and created the terminal Park/Boardwalk zone.

Adaptation: jail choices shifted from cash conservation to rail avoidance as GPT assembled four rails. Negotiation posture also hardened into starving cash-poor rivals (`dec-000402`, `dec-000417`, `dec-000455`). This is competitive refusal, not collusion.

Reasoning caveat: repeated private notes label four-house pink rents as $925/$1,000, while canonical rent events establish $625/$700; later notes call four-house Park $1,100 although the terminal rent is $1,300. These are reported numeric errors. Public messages do not repeat those figures, and engine events—not the notes—determine payment.

## Gemini 3.1 Pro Preview

Outcome facts: bankrupt; final cash $0; 0 final deeds; bankrupt_to=Claude Opus 4.8. Decision volume 118, model cost $1.81197000, retries 1, fallbacks 0.

Mechanism ledger: actions `{"accept_trade":7,"build_houses_or_hotel":2,"buy_property":9,"counter_trade":5,"declare_bankruptcy":1,"drop_out":1,"end_turn":36,"mortgage_property":6,"pay_jail_fine":1,"propose_trade":1,"reject_trade":46,"roll_for_doubles":3}`; trade proposals sent 1, received 53, accepted episodes involving player 8; houses built 12; rent paid $717, rent received $1112. Evidence: `run/actions.jsonl`, `run/events.jsonl`, `analysis/review/review_packet.jsonl`.

Early reported reasoning (first decision): “Early game, need to accumulate as much property as possible to build a monopoly later. Light blues are cheap and effective.”

Late reported reasoning (last decision): “I owe $1300 to Claude, but if I liquidate everything (all 12 houses on light blue for $300, and mortgage the three properties for $160), my max cash would be $901. Since my total liquidity is less than the $1300 owed, I have no choice but to declare bankruptcy.”

Interpretation: the dossier supports analysis of adaptation only through the full chronological ledger and cited decisions. It does not infer stable personality from message tone, and public/private difference alone is not labeled deception.

### Evolving dossier

Acquisition and blocking: bought Vermont, St. James, Boardwalk, and Virginia with explicit blocker logic. The Connecticut/Virginia negotiation `dec-000073`–`dec-000076` completed light blue and led immediately to nine houses (`dec-000077`), later twelve (`dec-000127`).

Portfolio expansion: accepted the red set for $500 (`dec-000223`/`dec-000224`) and New York for Boardwalk+Pennsylvania (`dec-000235`/`dec-000236`), completing orange. Cash and house scarcity kept both new sets mostly undeveloped, so the portfolio's option value did not become equivalent cashflow.

Negotiation policy: repeatedly refused Mediterranean because GPT could consume the remaining eight houses, and explicitly stated at `dec-000254` that full-set properties would not be traded. No later voluntary deal broke a full set. The Pennsylvania purchase at `dec-000397`–`dec-000400` was an anti-Claude block, not evidence of a continuing alliance.

Distress: a turn-128 pink hit required six mortgages while preserving light-blue houses. At `dec-000465`, $441 cash + $300 house sellback + $160 subsequent mortgages totaled $901 against $1,300, proving terminal unavoidability at that decision; earlier-policy avoidability remains untested.

Bankruptcy anchor: `mock-3676466999-527872e4-dec-000465` at turn 150; the legality and liquidity proof is reviewed in `bankruptcy_windows.md`.

## Grok 4.3

Outcome facts: bankrupt; final cash $0; 0 final deeds; bankrupt_to=Claude Opus 4.8. Decision volume 80, model cost $0.47997485, retries 1, fallbacks 0.

Mechanism ledger: actions `{"accept_trade":4,"buy_property":3,"counter_trade":5,"declare_bankruptcy":1,"drop_out":1,"end_turn":31,"mortgage_property":6,"reject_trade":26,"roll_for_doubles":2,"start_auction":1}`; trade proposals sent 0, received 31, accepted episodes involving player 5; houses built 0; rent paid $2511, rent received $600. Evidence: `run/actions.jsonl`, `run/events.jsonl`, `analysis/review/review_packet.jsonl`.

Early reported reasoning (first decision): “No properties to build/mortgage/trade usefully. Just paid rent, early game, best to end turn and wait for opportunities. No benefit in proposing trades with limited holdings.”

Late reported reasoning (last decision): “No liquidation options remain; cash $274 vs $625 owed. Bankruptcy inevitable. Claude wins.”

Interpretation: the dossier supports analysis of adaptation only through the full chronological ledger and cited decisions. It does not infer stable personality from message tone, and public/private difference alone is not labeled deception.

### Evolving dossier

Strategic identity: rail concentration is unusually stable from Pennsylvania Railroad `dec-000019` through B&O acquisition `dec-000085`, Short Line `dec-000180`, and Reading `dec-000200`. Public and private accounts consistently value house-independent $200 rent.

Blocker/liquidity tension: Park Place at `dec-000338` blocks GPT dark blue but lowers cash to $86. Virginia rent then forces mortgages on all rails and Park (`dec-000341`–`dec-000345`), eliminating the income engine Grok had protected.

Adaptation rather than silent breach: Grok twice says it will keep the rails (`dec-000350`, `dec-000362`) but later accepts $450 at `dec-000385` under severe liquidity pressure, then buys Boardwalk for $500 at `dec-000387`. The changed state is public and the reversal is disclosed; it is not labeled deception.

Terminal state: Grok enters turn 134 with $274 and two mortgaged dark blues. The legal menu at `dec-000428` contains only bankruptcy; no liquidation source can close the $351 shortfall.

Bankruptcy anchor: `mock-3676466999-527872e4-dec-000428` at turn 134; the legality and liquidity proof is reviewed in `bankruptcy_windows.md`.

## OpenAI GPT 5.5

Outcome facts: bankrupt; final cash $0; 0 final deeds; bankrupt_to=Claude Opus 4.8. Decision volume 207, model cost $15.31713600, retries 7, fallbacks 0.

Mechanism ledger: actions `{"accept_trade":1,"bid_auction":1,"build_houses_or_hotel":1,"buy_property":9,"counter_trade":9,"declare_bankruptcy":1,"end_turn":41,"mortgage_property":17,"pay_jail_fine":2,"propose_trade":106,"reject_trade":1,"roll_for_doubles":3,"sell_houses_or_hotel":1,"unmortgage_property":14}`; trade proposals sent 106, received 0, accepted episodes involving player 13; houses built 2; rent paid $2950, rent received $1318. Evidence: `run/actions.jsonl`, `run/events.jsonl`, `analysis/review/review_packet.jsonl`.

Early reported reasoning (first decision): “Try to pick up Vermont at a modest premium; light blues are cheap to complete/develop if I later land Oriental/Connecticut. Don’t overpay early.”

Late reported reasoning (last decision): “Shortfall is $965; even mortgaging all four railroads raises only $400, so survival is impossible. Declare now rather than hand over extra cash through pointless liquidation.”

Interpretation: the dossier supports analysis of adaptation only through the full chronological ledger and cited decisions. It does not infer stable personality from message tone, and public/private difference alone is not labeled deception.

### Evolving dossier

Negotiation breadth: GPT initiates all 107 trade proposals and repeatedly searches for orange, red, brown, green, dark-blue, or railroad completion. Early flexibility produces useful deals; after turn 85 the same search increasingly repeats despite counterparties' stable completion-risk objections, supporting a bounded fixation finding.

Material trades: States+$130 for Tennessee (`dec-000024`–`dec-000027`), B&O+$130 for Indiana (`dec-000084`/`dec-000085`), Short Line for $250 (`dec-000176`–`dec-000180`), red sale for $500 (`dec-000223`/`dec-000224`), New York for Boardwalk+Pennsylvania (`dec-000235`/`dec-000236`), four rails for $450 (`dec-000384`/`dec-000385`), and the two-step $220 brown consolidation (`dec-000444`–`dec-000449`).

Capital allocation: emergency mortgages after pink hits are often necessary, but Boardwalk is mortgaged and unmortgaged in the same turn twice (`dec-000257`–`dec-000259`, `dec-000367`–`dec-000369`), paying interest without an intervening roll. This is a concrete churn cost. The late choice to keep four rails live is coherent because they are the only $200 income path.

Reliability and terminal proof: seven of GPT's decisions use corrective retry, mainly illegal attempts to trade built properties; every final action is valid and no fallback occurs. At `dec-000487`, $335 plus all four $100 rail mortgages equals $735, below $1,300 Park rent, so bankruptcy is terminally unavoidable at that decision.

Bankruptcy anchor: `mock-3676466999-527872e4-dec-000487` at turn 165; the legality and liquidity proof is reviewed in `bankruptcy_windows.md`.

