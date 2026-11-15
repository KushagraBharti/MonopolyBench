# Integration proposal: complete final-paper architecture

Opus cross-review, 11 November 2026. This proposal builds on all four frozen drafts and on the checks in `data/`. The finished prose for the central argument is in `replacement_prose.tex` (compiled to `build/replacement_prose.pdf`). Numbers marked *fresh* come from this review's scripts. The integrated package should regenerate every number from its own scripts, using Fable's `\fact{}` discipline.

## 1. Title

**Withholding a Rival's Monopoly: Defensive Bargaining and Liquidity among LLM Agents in Monopoly**

- *Why this title.* It names the primary regularity (withholding, observed in choices) and its main qualifier (liquidity). It makes no causal or temporal claim.
- *Rejected: Fable's "…Until They Need the Cash".* The guard persists within every cash band at openings, Gemini never releases, and Opus never guards by refusal. See `review.md` §3.9.
- *Rejected: root's "Bargaining over Rivals' Opportunities: LLM Strategy and Economic Execution".* It omits liquidity, the variable the agents name when they release or time a bid, and it splits the paper into two headlines.
- *Rejected: Astra's "Strategic Attention and Economic Execution".* It has the same split.
- *Rejected: Sol's "…bargaining over competitors' future options".* It is accurate but centres attention, which rests more on explanations than on choices.
- *Rejected: my "Guarding the Last Deed".* It carried a categorical-rule mechanism that I withdraw.

Acceptable alternative: "Guarding a Rival's Last Deed: Defensive Bargaining and Liquidity in LLM Monopoly Games."

## 2. Abstract priorities, in order

1. **Setting.** A deed's value depends on who acquires it. Four configured systems, twenty complete four-player games, and 920 responses, each rebuilt from what the recipient saw.
2. **Primary regularity.** Opening requests for the deed that would complete only the requester's group are rejected more often than requests for a deed that completes nothing: 138/187 versus 105/176. The difference holds in every seed block and for every recipient system. It is absent in later offers. Stated reasons name the rival in 61 of 74 refusals of the recipient's own completion (inherited LLM-assisted codes).
3. **Liquidity qualifier.** Cash-poor holders reject every kind of deed request less and counter more, but at openings the extra refusal of completion requests persists in every cash band. Completing deeds that change hands disproportionately come from cash-poor holders: 20 of 43 one-sided sales, 12 of them Opus. Buyers open completion requests to cash-poor holders about twice as often as other requests. Both sides' notes reason about the holder's cash and about what the proceeds can build.
4. **Prices.** Asks are higher for completing buyers in every seller × mortgage cell with enough asks. Same-deed comparisons are mixed (seven rows). No premium is identified.
5. **Finance.** 128 of 131 payable debts are paid. Both standard-condition payable eliminations omit collateral that selling buildings would unlock, which successful payers used in 19 episodes.
6. **Boundaries.** The study is observational, with five seed blocks. Opus plays mostly under provider-refusal recovery. There is no effectiveness reference and no model ranking.

**Not in the abstract:** rent totals, rent-per-landing ratios, the seller build/win split, first-creditor-wins counts, the 56/60 bound, and win counts.

## 3. Architecture and word budget (about 7,000 main-prose words)

| § | Title | Words | Content and sources |
|---|---|---|---|
| 1 | Introduction | 900 | Replacement prose (`replacement_prose.tex` §1). The question, the finding, three contributions, boundaries, and a pointer to the question map. |
| 2 | Setting, information and conditions | 950 | Game rules and the house conventions that matter (Opus Table 1 corrected: auction prompts give the group only). Information surface. Cohort (5 seeds × 4 cyclic rotations). One paragraph each on the Opus recovery condition (exact counts and the prompt difference; full diff in appendix), the Grok channel conflicts, and history misattribution. Units and uncertainty: Fable's "Units, evidence and uncertainty" plus the matched-comparator definition. |
| 3 | Guarding the last deed | 1,500 | Replacement prose §3. Census Table 2 with the neither cell split by deed request. Fig. 1a. Later-offer null. Concessions (matched). Generic counters. Stated reasons. Asks and bids (Fable Fig. prices). Seven same-deed rows referenced to an appendix table. Incidents **G15** and **G2**. |
| 4 | Liquidity sets the terms of release | 1,500 | Replacement prose §4. Table 3 and Fig. 1b. Opening targeting. Refusal-then-sale pairs (Fable Fig. liquidity b, with the under-$100 count added). Composition and prices of completing sales: standard-condition sellers above list, Opus below list. Incidents **G7** (re-centred, as in Fable), **G1**, **G13**, **G20**. |
| 5 | What the positions become | 1,200 | Replacement prose §5. Conversion of trade-completed groups by system, with causes (Fable Table/Fig. conversion; no ratio headline). Debt census with execution quality and the static-lookahead contrast (Fable Fig. debt, annotated). Incident **G12**. Compact G17 contrast. Pre-estate ranks as context. Incident **G18**. |
| 6 | Discussion | 700 | Replacement prose §6. What the agents attend to: public capacity, not hidden beliefs. Attention versus effectiveness. Liquidity as the hinge between strategy and execution. Conditions as part of the environment. Short question-map paragraph with the table in an appendix. |
| 7 | Related work | 450 | Replacement prose §7. |
| 8 | Limitations | 350 | One consolidated section. |
| 9 | Conclusion | 150 | Replacement prose §9. |

Incident narration (about 1,600 words) is included in the section budgets.

## 4. Figures

**Main text**

1. **Fig. 1, "Guard and liquidity"** (new; `assets/fig_guard_liquidity.pdf`). (a) Matched opening rejection by seed block and recipient. (b) Openings by holder cash band, completion requests versus other deed requests, standard-condition and all holders. This is the economic and behavioural lead figure.
2. **Fig. 2, "Release"** (Fable `fig_liquidity` (b) plus my draft's `distress` panel). Holder cash at first refusal and at sale for the 14 pairs, marking the 8 under $100. Seller cash and price/list for completing cash-only sales, coloured by condition.
3. **Fig. 3, "Asks and bids by buyer position"** (Fable `fig_prices`, unchanged).
4. **Fig. 4, "What trade-completed groups became"** (Fable `fig_conversion`). Caption states that rent per landing mostly reflects the rent schedule. Sol's or my lifecycle chart goes to the appendix.
5. **Fig. 5, "Debt episodes"** (Fable `fig_debt`). Add markers for the 19 paid episodes that used unlocked collateral and label the two static-menu failures.

**Appendix:** the seven same-deed rows (Sol `same_deed`, adding first-ask markers and turn gaps); pre-estate ranks (Sol `pre_estate`); every trade-completed group (Fable `fig_timeline`); refusal time bins.

## 5. Tables

**Main text**

- **T1:** configured systems and response conditions (my Table 2 plus Fable's notes column).
- **T2:** offer census, completion cell × stage, with "neither" split into deed-requesting and non-deed-requesting rows (`replacement_prose.tex`).
- **T3:** openings and later offers by holder cash band × request type, for standard-condition and all holders (`replacement_prose.tex`).
- **T4:** trade-completed groups by system: count, mortgaged at completion, post-trade cash, first-window build, ever built, landings per 100 turns, and the causes of no first-window build.
- **T5:** debt episodes by system: paid, multi-action, used unlocked collateral, payable eliminations, bound below debt, menu lock.

**Appendix**

- Joint recipient × stage × cell table.
- Seller × mortgage × stage price cells (Sol).
- Same-deed rows with both estimands and turn gaps.
- Concessions by cell, matched.
- Seller conversion with player-game counts and the held-group stratum.
- Pre-estate positions (Fable or Opus, with the timing note).
- Usage and cost.
- Prompt diff, refusal message and time bins.
- Tool descriptions and board fields by phase (Fable).
- Definitions and reconciliation (Fable).
- Question map.

## 6. Eight main incidents (about 22 cards)

All quotation IDs below were re-verified in this review against canonical `decisions.jsonl`: file hash, field hash and exact span (`data/quote_spotcheck.json`; G2 d119 checked separately).

| # | Incident | Section | Cards | Mechanism | What the reading must say |
|---|---|---|---|---|---|
| 1 | **G15** Refusing one's own monopoly | 3 | `g15-d169-refusal-note`, `g15-d174-sweetener`, `g15-d175-final-refusal`; inline `g15-d176-wait-note` | Guard against a rival's construction timing; terms revised to the objection | Grok refuses its own completion three times. Its $600 is a full green layer, not the minimum build. Sol's closing note states a buyer-side timing rule ("reassess … when opponents need cash"). The later loss does not score the refusal. |
| 2 | **G2** One deed, two buyers, two prices | 3 | `g2-d119-note`, `g2-d124-price`, `g2-d128-note` | Identity-dependent asks; resale route; proceeds priced by what they fund | Sol prices a third party's resale option and its own use of the proceeds ("Mortgage reserves mean I need not sell cheaply"; "no monopoly to develop with the proceeds"). The "nine houses" arithmetic is wrong. The roles reverse at Opus's $17. |
| 3 | **G7** A liquidity-timed bid and a construction-financing sale | 4 | `g7-d42-final`, `g7-d42-ceiling`, `g7-d141-timed-bid`, `g7-d142-ask-note` | Authorised bluff that settled; buyer times its bid to the holder's $84; seller prices by own build path | The bluff settles and nothing isolates its effect. The same holder that refused while liquid sells the rival's completing deed at 3.5× list once it has houses to fund. |
| 4 | **G1** A completing deed sold at a quarter of list | 4 | `g1-d306-offer`, `g1-d309-accept-note` | Distress release under recovery; buyer reasons about the alternative estate | The Opus side has no note, because of recovery. Grok pays above its own ceiling because bankruptcy would hand the deed to the leader. The low price is the Opus distress pattern (0.66× list, n = 8), not the standard-condition pattern (2.25×, n = 6). |
| 5 | **G13** Distress used as a bargaining position | 4 | `g13-d250-insurance`, `g13-d252-floor`, `g13-d252-omission` | Omitted collateral; estate insurance | The omission appears in the returned provider explanation, while the applied note names Ventnor. Opus echoes the estate frame but not the claimed limit. 5/36 is not the single-roll 4/36. The record does not show the omission moved the price. |
| 6 | **G20** Denying a rival's construction cash | 4 | `g20-d96-appeal`, `g20-d101-refusal` | Collective liquidity denial; mixed follow-through | One appeal and its author's follow-through; Opus offers Grok money "for more red houses"; no cartel. |
| 7 | **G12** A payable debt ends in a contradictory bankruptcy | 5 | `g12-d249-note`, `g12-d249-public` | Route found; incompatible applied call | The note finds a five-sale route. Content names a two-house sale that falls short. The call declares bankruptcy. The record does not show which channel reflects intent. |
| 8 | **G18** A standing offer withdrawn as the seller weakens | 5 | `g18-d420-note`, `g18-d431-assurance`, `g18-d442-withdrawal`, `g18-d442-explanation` | Seller's liquidity rule; buyer's estate expectation; unenforced assurance | Sol states "only sell … for a major liquidity swing". Opus withdraws once Sol has $49 and bids lower later. No insincerity or reliance is established. |

**Compact contrasts in the main text (not counted among the eight):**

- **G19** in §3 or §4, two short quotations (`g19-d135-public`, `g19-d136-public`). The recipient corrects a false colour claim and accepts the terms. This keeps competent correction in the main text, as the brief requires.
- **G17** in §5, one quotation (`g17-d234-public`). A payable bankruptcy from the static-menu error hands Park Place and Boardwalk with five houses to the last-placed player, who wins.

**Disclosure:** Grok appears in seven of the eight incidents (all except G18). Its separate content and call channels make conflicts observable. The incidents estimate no rate.

## 7. Question map (main-text paragraph plus appendix table)

| Question | Evidence (integrated paper) | Not measured |
|---|---|---|
| 1. Strategic reasoning | Matched opening refusal of completion requests, all blocks and recipients; recipients refuse their own completion with stated rival reasons | Optimality, regret, exploitability |
| 2. Opponent modelling | Buyers open completion requests to cash-poor holders about 2× as often (20/169 versus 9/160 without Opus); notes on rival build capacity, resale and estates | Calibrated beliefs about hidden information |
| 3. Negotiation, cooperation, deception | Full response census; generic cash repricing; matched concessions; authorised bluff, omission, correction, withdrawal, denial appeal | Persuasion effects, surplus, fairness, deception prevalence |
| 4. Planning and memory | Unlocked collateral used in 19 paid episodes versus the static-menu lookahead failure in both standard payable eliminations; G9 target (inherited); Opus note condition | Memory benefit; plan-completion rate |
| 5. Adaptation and learning | Revised terms within threads; holders' responses change with own cash; uneven-build recurrence (inherited) | Feedback-caused learning; unfamiliar-opponent transfer |
| 6. Economic decisions and risk | Asks by buyer position; liquidity and release; 128/131 payable debts; building-preserving liquidation (2/68) | Value of any price or reserve; risk-adjusted return |
| 7. Collective dynamics | G20 denial appeal; creditor succession; five discordant first-estate games | Coalition stability; coordination effects |
| 8. Validity | Recipient-view rebuild; matched comparators; block and recipient replication; explicit conditions | Model ranking; repaired-interface performance |
| A. Talk versus action | Stated release rules that match population patterns; G12 channel conflict; G2 arithmetic error with correct concern | General relation of explanation quality to play quality |
| B. General versus multi-agent | No measure of general capability | Any relationship |
| C. Skill versus chance | Seat and seed patterns; first creditors usually already led; G17 | Causal shares of skill and chance; counterfactual winners |

## 8. What to cut or move

- Out of the main text: rent totals, the $57,378 and $53,810 figures, and the 3.0× rent-per-landing ratio. Estate deed totals go to one context sentence. The 56/60 bound goes to the debt figure caption.
- Per-number caveats: state once in Limitations.
- Detail moved to appendices: prompt, usage, Grok parsing, history-formatter counts, redemption rounding, the G7 menu-lock mechanics, uneven-build denominators.
- My draft's capacity table: appendix only, labelled exploratory.
- Sol's long conditions appendix: merge with Fable's definitions and reconciliation tables.

## 9. Integration process notes

- Port `tools/cross_checks.py`, `tools/liquidity_openings.py`, `tools/concessions_matched.py` and `tools/unlock_check.py` into the integrated analysis, and regenerate their numbers as `\fact{}` values.
- Use Fable's quote generator for every card. Keep G2 d119 from the Opus manifest.
- Treat the matched comparator, cash bands and windows as post hoc descriptive cuts, labelled as such once in §2. Show all cells.
- Human byline: left to the project owner. LLM roles are disclosed in an appendix.
