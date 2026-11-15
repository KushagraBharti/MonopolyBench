# Evidence map

Each row says what a claim in the manuscript rests on and how it was established for this draft.

Status words:

- **Recomputed**: rebuilt in this round from raw `decisions.jsonl` or `events.jsonl` by a script in `tools/`, and asserted by `tools/08_verify.py`.
- **Source read**: derived by reading engine source at the run commits. Nothing was executed.
- **Author reading**: one LLM author read stored text. Not human annotation.
- **Inherited**: taken from the 12 November package or the 14 November reviews and not redone here.

## Financing

| Claim | Evidence | Status |
|---|---|---|
| 188 financing episodes, 128 paid, 60 eliminated, 338 decisions | `tools/01_episodes.py`. Episodes are grouped by player, turn, amount, creditor and reason. Outcome comes from the bankruptcy event emitted by the last decision | Recomputed. Agrees with the 12 November ledger on all 188 rows |
| $51,997 paid through 180 mortgages and 89 sale calls; 67 one-action and 61 multi-action payments; no fallback in a first action or a payment | `tools/02_finance.py` | Recomputed |
| U0 and U* for every entry | `tools/01_episodes.py` from recorded holdings, the first menu and `contracts/data/board.json` | Recomputed |
| 131 payable debts | 128 payments plus three declarations with a stored legal payment sequence | 128 recomputed. The three witnesses are inherited from the engine audit stored with the 12 November package. Not rerun |
| 62/53/16 partition, 62/52/14 paid | `tools/02_finance.py` | Recomputed |
| Middle row: 47 paid without a released mortgage, 1 stored sale-only witness, 5 with a route that avoids released mortgages | Routes from `tools/01_episodes.py`; the five arguments in Appendix C | 47 recomputed. Witness inherited. The five arguments are source reads from recorded holdings, reached independently by Sol, Opus, Astra and me on 14 November. Not executed |
| G7 Opus: bound $1,310 against $750, no sale offered, $440 reachable | Entry state and menu from raw records; Opus's own "$440" in its provider field | Entry state, menu and text recomputed. That no later menu could reach payment is inherited from the stored restricted search |
| Continued valid financing pays in all 131 payable entries | Appendix B | Source read plus recomputed premises. Complete ownership and evenness hold in 131 of 131. Coverage 108, 12, 9, 2. The first three conditions are mine from 14 November. The fourth is Astra's argument, which I re-derived, extended to bundled sale plans and checked against the recorded stock. No policy was run |
| Engine, resolver and board files identical at both run commits and in the working tree | `git rev-parse <commit>:<file>` against `git hash-object <file>` | Checked in this round |
| 132 episodes with the bound covering the debt and 56 without; first-action declarations 3 and 50; 8 forced menus; 6 financing starts on unpayable debts | `tools/02_finance.py` | Recomputed |
| 43 of 48 unpayable first responses state the exact full bound, proceeds or gap; 2 itemize; 3 state the listed-only total | `tools/03_stated_totals.py`; five non-exact responses read directly | Number match recomputed. The five direct readings are author readings of short texts quoted in Appendix F |
| 37 first responses face building-locked collateral; 32 count or raise it, 5 stop at the listed-only total | 16 necessary-collateral responses plus 21 unpayable ones with U0 below U* | Recomputed counts on top of the tier coding |
| Tiers 5, 3, 5, 1, 2 for the sixteen | `tools/coding.py`, with evidence spans asserted verbatim by `tools/07_tables.py` | Author reading. Opus and I reached the same five-way split independently on 14 November. Astra re-read the five inclusive cases and agreed. Agreement among model readers, not human validation |
| Every stated asset value correct except Sol's $430; seven responses contain a full-bound figure; three stated remainders met | Sixteen full fields against board values and routes | Author reading for values. Number match recomputed for totals and remainders |
| Two false budgets equal U0 exactly ($408, $530) | Notes against recomputed U0 | Recomputed |
| Stored audit pays both with $38 and $180 to spare | Engine audit stored with the 12 November package | Inherited |
| Selective financing: 28 of 30, 46 of 52, 122 of 128, 119 of 128 | `tools/02_finance.py` and `tools/08_verify.py` | Recomputed. Descriptive. No search and no optimum |
| Nine named-action conflicts in 338 financing decisions, all Grok; Grok's content names an action in 27 | `tools/04_corpus.py` | Recomputed. The check can see a conflict only where content names an action |
| What each channel says in the nine departures | Appendix G and `supplement/nine_departures.json` | Text extracted in this round. The descriptions in section 5 are author readings |
| Carried notes of the sixteen | `tools/coding.py`, spans asserted against the stored prompt | Author reading |
| Published rules in Table 1 | Hasbro instruction sheet, PDF text read locally on 14 November | Read by me at the primary source |
| Engine rules in Table 1 | `_handle_bankruptcy`, `_mortgageable_space_indices`, `_sellable_building_space_indices`, `_validate_sell_plan`, `_resolve_pending_payment` | Source read in this round |

## Corpus and conditions

| Claim | Evidence | Status |
|---|---|---|
| 50,918 events, 6,989 decisions, 8,679 attempts; decisions by system; wins 8, 7, 3, 2 and by seat 7, 7, 3, 3 | `tools/04_corpus.py` | Recomputed |
| 1,604 first-attempt refusals and one later; all first attempts refused in games 5 to 20; no recovery attempt refused; one refusal message | `tools/04_corpus.py` | Recomputed |
| One standard system prompt across 6,989 decisions and one recovery prompt across 1,604 attempts | `tools/07_tables.py` hashes every stored system prompt | Recomputed |
| Grok content names an action in 1,068 decisions and a different one in 139 | `tools/04_corpus.py` | Recomputed |
| Provider field present in 287, 1,316, 1,560 and 1,662 final responses; field types | `tools/04_corpus.py` | Recomputed |
| Grok required tool choice, others automatic | 12 November package, which checked saved request files | Inherited |
| Seeds, commits and folders in Table 18 | `cloud/job.json` of each saved game and `data/game_map.json` | Recomputed from stored job records |
| Cost of USD 141.39 | 12 November package | Inherited |
| Replay comparisons passed for all twenty games | Stored replay reports | Inherited. No replay run |

## Bargaining

| Claim | Evidence | Status |
|---|---|---|
| 920 responses, 113/394/413; 526 threads; styles by system | `tools/05_bargaining.py` | Recomputed |
| Opening table by form and completion | `tools/05_bargaining.py`, completion classified from holdings in the response prompt | Recomputed. Matches the 12 November table in every cell |
| 95/116 against 37/72; 90/108 against 24/36; 93/112 against 26/43; cash bids 42/70 against 67/103 | `tools/05_bargaining.py` | Recomputed |
| Block bootstrap ranges and leave-one-block-out ranges | All 3,125 ordered resamples enumerated | Recomputed |
| Grok wrote 36 of 72 neither-completing swaps, 15 of 17 acceptances, 13 from conflicting calls; 7 of Grok's 28 acceptances named another action | `tools/05_bargaining.py` | Recomputed |
| 79 of 111 counters keep the bundle and improve cash | `tools/05_bargaining.py` | Recomputed |
| 74 recipient-completing rejections with legal acceptance | `tools/05_bargaining.py` | Recomputed population |
| 61 of the 74 cite a consequence for the rival | Two model readings from the 12 November package | Inherited. Not human-validated |
| Fourteen resistance-to-settlement histories; six matched price pairs | 12 November package | Inherited |

## Incidents

Every quotation is extracted by `tools/06_quotes.py` and checked against its stored field and against the PDF text by `tools/08_verify.py` (47 quotations).

| Incident | Facts checked against raw records in this round | Inherited |
|---|---|---|
| 1. G13 d195 selective route | Note, provider field, route deed for deed, $28 left, slack | None |
| 2. G20 budgets | Both notes, ten calls, $700 and $665, $14 left | None |
| 3. G15 refusal | Cash $333 and $730, both offers, both refusals, elimination at turn 81 to Gemini | That Sol never completed either group (not stated in the main text) |
| 4. G2 pricing | Bids, asks, cash $845, the "nine houses" note, Opus's ceiling, the later reversal at $17 | None used in the main text |
| 5. G7 timed bid | Sol's $84, the three offers and replies, five mortgages, four houses, the earlier $600 bluff | Later rents and the outcome (not stated in the main text) |
| 6. G13 solvency pitch | Cash $35 and $1,926, pitch, counter, note, provider fields, payment, elimination at turn 150 on a $200 debt to Sol | The 5/36 miscount (not stated) |
| 7. G19 correction | Proposal, note, content naming `end_turn`, reply, execution | None |
| 8. G20 appeal | Appeal, Grok's note, build, mortgages, offer, refusal | Opus's later cash offers |
| 9. G18 withdrawal | Bids, refusal, renewal with reservation, invocation, withdrawal, cash $49 | That a second $750 rent caused the fall to $49 |

## Literature

Access depth for each source cited. "Mine" means I opened the source on 14 November, in the review round or in this round.

| Source | Depth | Used for |
|---|---|---|
| Hasbro instruction sheet | PDF text read locally, six pages, relevant sections in full (mine) | Table 1 |
| ACPBench, AAAI 2025 | HTML through a summarizing fetch, most of the paper; arXiv page rechecked in this round for authors and venue (mine) | Action reachability exists as a task; single-turn |
| ACPBench Hard, ICLR 2026 | HTML through a summarizing fetch; arXiv page rechecked in this round (mine) | Generative versions with validators |
| PlanBench, NeurIPS 2023 | PDF text read locally around search hits (mine) | Context for the next row |
| Valmeekam, Stechly and Kambhampati 2024 | Unsolvable-instances section through a summarizing fetch (mine); Table 3 read by Sol and Astra | 11.5% false unsolvability in one obfuscated domain |
| Stein et al., AutoPlanBench, ICAPS 2025 | HTML through a summarizing fetch; arXiv page rechecked in this round (mine) | Whole-plan against step-by-step action choice |
| Yao et al., ReAct, ICLR 2023 | Known from prior reading. Not reopened | Interleaved reasoning and action |
| Yan, Lin and Wang, EMNLP 2026 | PDF text read locally, 14 pages, Table 6 (mine); ACL Anthology page rechecked in this round | Same candidates, changed order, changed success |
| Wu et al., NAACL 2024 | Abstract pages (mine) | Counterfactual task variants |
| Xiong et al., ACL 2026 | Abstract page; rechecked in this round for authors and pages (mine) | Experience following and error propagation |
| Oota et al. 2026 | Project page on 14 November; arXiv abstract page in this round (mine) | Declared planning structure often not kept. Preprint |
| Co and Konuganti 2026 | ICML virtual-site page with abstract, rechecked in this round (mine) | Agent reasons a move violates the rule, then submits it. Workshop poster. Paper text not read |
| Turpin et al. 2023; Lanham et al. 2023 | Retained from earlier rounds. Not reopened | Explanations need not reflect what drove the output |
| AgentMonopoly | HTML through a summarizing fetch, two passes (mine). Rules file and engine code read by Opus and Sol, not by me | Elimination at negative cash |
| FinBoardBench | HTML through a summarizing fetch, two passes (mine); Appendix C.3 checked by Astra | Rules require mortgaging or selling houses when short of cash; no analysis of that phase |
| Vending-Bench | HTML through a summarizing fetch (mine) | Named only as the base of the Arena study |
| Li et al. 2026 | Abstract and first 100,000 characters of the HTML (mine) | Classifies all 2,583 emails |
| Lewis et al. 2017; He et al. 2018 | Abstract pages, read by Astra and Sol in earlier rounds. Not opened by me | Negotiation with explicit utilities |
| NegotiationArena | Abstract page, read by Sol. Not opened by me | Defined negotiation scenarios |
| Guhe and Lascarides 2014 | Read by Sol, who found that embargo recipients always comply. Not opened by me | The sentence in section 7 is Sol's reading |
| Jehiel, Moldovanu and Stacchetti 1996 | Abstract and opening, read by Sol. Not opened by me | Identity-dependent externalities |

No claim in the paper depends on a search for absence. Section 7 says we could not determine whether FinBoardBench permits bankruptcy on a payable debt, and makes no priority claim.
