# Findings, limits and objections (Opus draft)

## What I found, ranked by how much weight it can bear

1. **Opening rejection of proposer-completing offers (strongest).** 138/187 (73.8%) vs 152/238 (63.9%) for neither-completing openings. Positive in all five seed blocks (+15.0, +18.9, +5.8, +7.6, +10.8), leave-one-block-out range 8.7–11.3, positive for Sol (+17.1), Gemini (+5.1), Grok (+9.6); Opus −7.1. Without Grok conflict-opened threads +9.7; without Opus on either side +19.0. Offer-level dependence means these are replication-style descriptions, not significance tests.
2. **Concessions on completing bundles are rarely accepted.** 9/58 vs 24/86; 4/42 vs 16/62 without Opus recipients; lower in four of five blocks, but blocks hold 3–19 author-completing concessions.
3. **Distress clears completing sales.** 14/22 completing cash sales had a seller under $100 vs 7/31 other sales; 6/11 vs 4/22 without Opus sellers. Conditions on settlement. Standard distressed sellers still got a median 2.25× list; Opus 0.66×.
4. **Stated reasons name the rival** (inherited LLM-assisted codes): 61/74, κ 0.79; own cost 41/74, κ 0.78. Same-family readers, partial unblinding, 31 of 61 from G1 and G15.
5. **No graded capacity sensitivity**: 75% / 76% / 55% opening rejection by the author's post-trade build cash. Cells differ in price and deed; this is a null on one cut, not proof that capacity never matters.
6. **Asks rise for completing buyers, but unstably**: pooled 1.63 vs 1.08; three of five blocks; single-deed same-seller pairs 5 higher / 1 lower / 1 equal by first ask, only 3 of 7 with complete separation, up to 106 turns apart. Bids show no matching premium (standard 1.13 vs 1.50; Grok strongly reversed).
7. **Development and exposure**: $374 per developed landing vs $20 undeveloped on trade groups; 8 of 9 never-built groups had a mortgaged deed at completion.
8. **Debts**: 188 episodes; 128 paid; 3 of 131 demonstrably payable debts ended in elimination; 102 of 128 paid episodes belong to later-eliminated players.
9. **First estates**: first creditor is already asset leader in 15/20 and wins 18/20; leader wins 15/20; in the five divergent games the creditor wins four. Too few cases to say whether inheritance changes winners.
10. **Null**: opponent standing does not change response rates (67/70/67% opening rejection).

## Objections to the contract or to earlier interpretations

1. **"Same seller/game/deed comparisons are mixed" is right, but the count depends on the statistic.** The contract and Fable's assessment report seven comparisons as 4 higher / 2 lower / 1 equal. With the first ask to each buyer type I get 5 / 1 / 1; restricting to identical mortgage status, 4 / 1 / 1; with complete separation of all asks, 3 of 7. G4 is the swing case (first completing ask $450 mortgaged at turn 152 vs $280 unmortgaged at turn 74; later completing asks fall to $100). The manuscript states the definition and keeps the conclusion "mixed". Integration should fix one definition.
2. **My own earlier assessment was wrong on Sol reasoning tokens.** I wrote that Sol's field was null in 1,292 records. It is present in all 1,991 Sol usage records with 1,296 zeros (Astra was right). I also reported means "where reported" (108/267/281) that came from that error. The manuscript uses 38/254/259/3,589.
3. **The earlier "first management window" development counts (16/17/7/3) and my "by the owner's next turn" counts (16/16/8/4) are different definitions.** I do not print both in the main text; I report eventual building (17/17/12/8 of 17/18/15/13) and exposure, and cite the earlier first-window findings only for the qualitative reasons (Grok deferral notes, Opus defaults).
4. **"Thirty-four records come from G1 and G15" (earlier integrated text) does not reproduce for the 61 agreed rival codes**; I count 31 (G1 21, G15 10). The referee's "34 of the 61" may refer to a different subset. The manuscript uses 31 and says which set.
5. **The contract's request to "keep eight incidents if they earn their place" is met, but seven of eight now involve Grok** (G2 gained Grok's d120 counter). I judged the G2 Grok message essential because it is the clearest buyer-side statement of identity-dependent pricing. Integration may prefer to drop the d120 card to restore six of eight.
6. **The phrase "seller premium" should not return.** The response contrast and the concession contrast are stronger and less composition-sensitive than prices. If the integrated paper leads with pricing, it inherits the block-level instability.
7. **Do not call the stated-reason agreement "validation".** κ between two same-family readers is consistency. I report it with that wording.
8. **The G2 opening bid was a Grok conflict call** (content names `end_turn`, call proposes $200). The earlier text did not say so. It does not change Sol's pricing behaviour, which responds to an offer actually received, but it should be disclosed.

## Limits I did not resolve

- No value reference: I cannot say whether defensive bargaining helped any agent.
- The capacity test uses cash only; mortgage capacity, house stock and timing are not modelled.
- "Asset value" for first-estate standing is a list-price index; a rent-weighted or development-weighted index might rank players differently in G4, G7, G15 and G17.
- The tracker matches snapshots at turn starts; landings are counted from `PLAYER_MOVED` events, which include card moves. Landing counts are therefore arrivals, not dice-only landings.
- Opus's departure from the defensive pattern is inseparable from its response condition.
- I did not rerun any engine witness, replay, Grok channel parser, history-formatter census or semantic coding.

## Things a fresh reviewer should check first

- `data/offers_rebuilt_check.json` (zero field mismatches against the retained ledger).
- `tools/track.py` output (zero mismatches against 3,246 snapshots).
- `qa/quote_checks.json` (31 cards, all true).
- The single-deed pair definitions in `data/extras.json`.
