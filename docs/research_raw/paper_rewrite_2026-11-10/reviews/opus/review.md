# Opus whole-paper review of the four independent drafts

Reviewer: Opus xhigh (Claude Opus 5.5). This is a full-scope cross-review by a named coauthor. I did it personally, with no subagents.

## 1. Scope and order of work

I read all four complete papers before forming a view: Astra (`manuscript.tex`, `main.tex`, `conduct.tex`, `discussion.tex`, `appendix.tex`), Sol (`manuscript.tex`, `conduct.tex`, `temporal_discussion.tex`, `appendices.tex`), my own Opus draft (every file in `sections/`, including generated tables and quote macros) and Fable 5.2 (every file in `sections/`, including `generated_tables.tex` and `quotes_supplement.tex`). I also read each handoff, evidence map, figure note, literature note and initial position. I then ran read-only checks on retained ledgers and canonical decision prompts and wrote `initial_position.md`. Only after that did I open `reviews/astra/`. Sections 5 and 6 respond to Astra's report. Where Astra changed my mind, I say so.

New checks I performed (scripts and outputs in `checks/`) are listed in `verification.md`. In brief:

- (a) First-window construction access for the nine never-legal groups, from canonical prompts and the engine's buildable and redemption rules. This is arithmetic, not an executed witness.
- (b) Offer cash against board list prices, with robustness splits.
- (c) A reproduction of the counter-content, cash-poor, thread-position and route tabulations.
- (d) The Grok content-versus-received-name breakdown.
- (e) Primary-source abstract checks of eight cited papers.
- (f) The 272 baseline hashes and 81 draft hashes, all unchanged.

Every engine-executed result in every draft (payment witnesses, the G7 search, the 61/63 reachable multisets, replay, prompt reconciliation) is inherited from the 29 October audit. Neither I nor any of the four authors re-executed those in this round.

## 2. Central thesis I propose for the integrated paper

In a four-player economy where a bankrupt player's buildings pass intact to its creditor, a deal's value depends on what it lets each party build and on who receives the estate if someone fails. Twenty complete games by four configured LLM systems show three connected things:

- **Bargaining is organized around color-group completion.** Responses differ by who would complete. The difference persists within opening bids and within later offers, and in three of four responding configurations.
- **Completion becomes income only through a gated chain.** The links are a construction option on the menu, the owner's financing choices and a valid encoded action. Failures occur at each link and are distributed very unevenly across configurations.
- **Estates move productive assets during play almost as often as trades do and concentrate them.** Agents argue explicitly about who will inherit.

The evidence is observational. It describes these dependencies and shows agents attending to them. It does not identify the effect of a rival's completion, a message, a default or the inheritance rule.

This is close to the thesis of all four drafts. The improvement I argue for is in what each link is allowed to claim.

## 3. Strongest evidence, ranked

1. **The joint-completion response census, stratified by thread position and responder.** Author-only offers are rejected 159/289 and recipient-only offers 38/140. Opening bids are rejected more everywhere, and 187 of the 289 author-only offers are opening bids against 51 of the 140 recipient-only offers. Within position the gap shrinks but keeps its direction: 138/187 versus 31/51 among opening bids, and 21/102 versus 7/89 among later offers. By responder, the rejection contrast holds for Sol (31/83 v 3/30), Gemini (63/76 v 15/31) and Grok (62/78 v 14/37). It fails for Opus (3/52 v 6/42), which counters instead. Fable found the position split. I reproduced it. It is the most important robustness addition in any draft, and Astra's review does not mention it.
2. **Execution access as a separate stage.** The 63/43/9/4/4/3 first-window partition, the 34/42 entry-buildable subset, the 663 END partition with 573 unverified residuals, and the 61/61 Opus multisets reachable after reordering (inherited).
3. **Current-debt finance.** 56 eliminations below the generous bound, three payable with distinct mechanisms, one hotel-locked at \$440 reachable of \$1,310 nominal (witnesses inherited). Plus the successful G20 and G16 liquidation contrasts.
4. **Nonterminal inheritance.** 52 estate completions during play against 63 trade completions. Eventual winners own 45 of the 52 against 18 of 63, receive 35 of 40 nonterminal estates and 202 of 227 nonterminal estate deeds. Only 14 of the 52 estate groups collect rent (\$11,472), against 51 of 63 trade groups (\$57,378). Estates arrive late and concentrate holdings more than they generate income during play.
5. **Seven contextual incidents** whose stakes are the same dependencies: rival construction capacity (G15, G2), solvency and estate framing (G13), creditor withdrawal (G18), financial denial (G20), premise correction with settlement (G19) and a speech/action conflict at a payable debt (G12).

## 4. Major objections to each draft

### Astra

Astra has the shortest architecture, the most careful incident readings (G13 "bought immediate liquidity without preventing the later event", G18 reliance and dishonesty limits) and the right appendix correction table. Objections:

- **No position or responder stratification of the headline table** (`main.tex` 101–125). The pooled 55% v 27% is presented as the result. The Opus exception and the position composition are missing. Astra concedes the configuration part in its own review (A1).
- **"Recipients consequently do not respond to incoming cash alone"** (`main.tex` 119). The cash median is the price of the deed being bought. The completing side receives a deed in 429 of 429 one-sided offers. Astra self-flags this (A1). I agree, and add the list-price evidence in section 6.
- **The abstract says "nine never become buildable"** (`manuscript.tex` 11). The body says "never buildable during that window", but the abstract drops the window. Eleven of the 20 unbuilt groups are built later, and seven of the nine could have been financed into construction from the owner's own assets (my check). Use "offered no construction in that window".
- **The reasons paragraph omits that 36 of the 74 coded rejections are "both" offers**, where accepting completes the writer's group too. Rival-consequence language is close to mechanical there.
- **Minor:** the G20 d97 content is a mortgage (`mortgage_property` in the conflict ledger). "Financing/building" should read "a mortgage".

### Sol

Sol has the clearest continuous economic argument, the best prose discipline and the most careful finance and inheritance language. It has the fewest new findings. Objections:

- **Pooled cells only.** Sol "omit[s] unverified consistency across games/blocks/configurations" (handoff). That was prudent before checks existed. Now that Fable's and my splits are reproduced, a paper with only pooled cells understates the configuration heterogeneity and overstates the pooled contrast.
- **"despite a median \$200 transfer toward the recipient"** (`manuscript.tex` 127) has the same cash-direction framing problem. "Offers most often induce counters" should read "receive counters" (Astra S1).
- **"The earlier payment purchases time"** (`conduct.tex` 16) implies a purchased survival duration. Sol's next sentence ("does not establish that purchasing time had no value") reinforces rather than removes the causal reading.
- **"Validated ontology" for Empty Commitments and "causal order"** (`temporal_discussion.tex` 27, 35). Both need narrowing (Astra S1).
- **The G20 boycott reading** ("direct evidence of a participant trying to regulate bilateral cash flows according to a third-party competitive objective") is a fair description, but it should attribute the objective to Gemini's public text.

### Opus (my own draft)

Opus contributes the counter-content table (reproduced by me and by Astra), per-responder and seed-block tables, the G2 and G11 incidents with verified delivery, the menu-only financing column, and the provenance table. Its errors are listed in `findings.json` (OPR-01, 03, 06–18, 25, 28, 29, 33). The serious ones:

- **Opus first-window shortfall misattributed** (abstract, introduction item 2, conclusion). "Most of the shortfall comes from engine defaults" and "lost most of its development" are false. The eight Opus non-builds are five never-legal windows and three defaults.
- **Selection presented as a finding.** The abstract, introduction item 4, the discussion paragraph "Conduct audits can start at pressure points" and the conclusion all say conduct concentrates near solvency and inheritance in transcripts that I selected partly for stakes.
- **"Refuse or price."** Counters raise the counterer's cash in every completion cell (135/164 even in "neither"). My own list-price check shows no buyer-side markup for completion. "Price" is not established. The defensible claim is conditional: among counters to author-only offers, 92 of 111 keep the author's completion, and 79 of the 88 that keep only it change nothing but cash, upward (Astra's refinement).
- **The G2 note's "nine yellow houses" error is quoted without comment.** \$520 buys three \$150 houses. The same incident says Sol "collects no rent" on the yellows. It collects \$44 of undeveloped rent and no developed rent (OPR-33, found while drafting the replacement card).
- **Smaller errors:** G20 d97 "building" should be "mortgage". "Every text channel" contradicts the action in G12 and G19, but the public message carries the applied call. "15 identical arguments" should be 15 parsed objects equal and 5 literal. "Refusal recovery used in 1,605 decisions" should be 1,604 recovery chains. "Displayed options understated finance" should say the mortgage subtotal does, since sales are on the menu. "Sound allocation … earns nothing". "No probability forecasts". The first sentence asserts deployment while citing simulations. The Cosentino summary lacks its information condition.
- **Length:** 9,500 words, 43 pages, first result on page 7.

### Fable 5.2

Fable has the most new and useful existing-data analysis: thread-position stratification, the Grok-conflict join to negotiation counts (64 of 136 openings), route-by-winner and terminal splits, the seed-block observations, the never-legal row table and the new G15 incident. It also has the most overstated headlines:

- **"No list price asks for this premium … The systems price the completion itself, on both sides"** (`bargaining.tex` 16, abstract, conclusion). This is not supported (see section 6, item 2).
- **"Nine could not legally be built on … properties of the purchase", and "17 of 20 trace to the terms of the acquisition or the response path"** (`development.tex` 40, 48, abstract). This is contradicted by my arithmetic check. G14 Grok had \$602 against \$193 redemption plus a \$200 house. G16 Grok had \$523 against \$111 plus \$100. Seven of nine reach redemption plus a house using the owner's other mortgages. Grok's own notes defer redemption. The category mixes inability with owner deferral.
- **"Opus … lost most of their early value"** (introduction 18, development 75, conclusion 3). False, as in my draft.
- **"Estates complete 121 groups against 63 by trade" / "Bankruptcy moves more property than trade"** (abstract, introduction 14, heading). Sixty-nine of the 121 are terminal. Fable's own body and conclusion use 52, so the abstract contradicts the body.
- **"Completing deeds change hands mainly when their holder is short of cash"** (abstract, `bargaining.tex` 101, conclusion). 21 of 48 is not "mainly", and Opus is the seller in 13 of those 21.
- **"The protection bought lasted 43 turns"** (`insolvency.tex` 84). This turns a later bankruptcy into a purchased survival duration.
- **Literature:** Cattle Trade's abstract says strategic coherence "is associated with rank more strongly than spending volume or any single subskill", not "coherent spending predicts rank". Shah et al. report rigid anchoring at extremes, not concession "too readily".
- **"The order of these figures matches the order of wins."** Gemini's rent (\$26,070) exceeds Sol's (\$20,818), while Sol wins more.
- **Rent by configuration as a main exhibit** invites a ranking. It is confounded by survival and landings.
- **Minor:** the G1 Boardwalk note's "\$220" redemption is the standard-rule figure, but this engine charges \$221 on a \$200 principal. Flag it in the card.

## 5. Where I agree with Astra's all-four review

I agree with F1, F3, F4, F6, F7, F8, F9, F10 and O1–O9 substantially as written, and with A1, S1 and P1. Astra independently reached my OPR-01, OPR-09, OPR-13, OPR-14 and OPR-15 on my own draft, and its counter join (79/88 pure cash repricings) improves my table. Its proposal to put the nonterminal inheritance comparison in the headline is right. So is its dissent against "mostly", "sound", "lost value", "premium", "protection lasted" and "only delays".

I also changed one decision after reading Astra. My initial position put G7 in the main text and G2 in the appendix. I now favor G2 in the main text with the arithmetic error flagged, and G7 as a one-sentence contrast plus an appendix card. G2 contains a bluff that did not settle (Opus's "final" \$450 below a private \$475), rival-capacity reasoning with a visible arithmetic error, a reversed trade 24 turns later and an estate transfer to the winner. G7 adds only a cleaner settled bluff. Astra's argument contributed to this change. I would revert to G7 if length forces G2's chain to be cut, because a G2 card without its arithmetic flag and outcome is worse than G7.

## 6. Explicit dissent from Astra

1. **The position split belongs in the headline result.** Astra's review lists Fable's contributions as conditions-to-construction, the Grok conflict join and inheritance. It does not mention the thread-position stratification, which is the most consequential correction to the bargaining headline in the whole set. Astra's proposed bargaining section ("response population and heterogeneity, actual counteroffer changes, stated rival consequences, exploratory seller-cash association") has no slot for it. The pooled 55% v 27% is about half composition. The integrated table must show opening and later offers.
2. **"The completing side usually pays net cash" should not be presented as a finding.** Astra's F2 keeps it as "correct and useful". The completing side receives a deed in all 429 one-sided offers, so it pays for the same reason any buyer pays. The informative comparison is with list price, and it cuts against a completion premium:

   | Offer type | Median cash / list price |
   |---|---|
   | Pure cash bids for a deed completing the bidder's group (n=134) | 1.32× |
   | Bids in non-completing purchases (n=178) | 1.38× |
   | Same two groups, unmortgaged deeds only | 1.57× v 1.50× |
   | Same two groups, opening bids | 1.40× v 1.36× |
   | Same two groups, later offers | 1.31× v 1.43× |
   | Sellers' asks for a deed completing the buyer's group (n=93) | 1.63× |
   | Non-completing asks (n=117) | 1.08× |
   | Same two groups, unmortgaged deeds only | 2.31× v 1.82× |
   | Same two groups, later offers | 2.21× v 1.85× |

   Buyer bids show no consistent completion markup. Seller asks are higher in every split, and most of the pooled gap reflects composition. The defensible statement is: "Cash usually flows to the side giving up the completing deed, as in any purchase. Relative to board prices, bids for one's own completion were not higher than other bids. Asking prices for a recipient-completing deed were somewhat higher than other asks in every split we examined. None of these contrasts holds price, position and portfolio fixed." The 373/429 figure can stay in an appendix table for orientation, not in the abstract.
3. **Never-legal windows need the financing arithmetic, not only a scope caveat.** Astra's F5 says the nine are "not nine demonstrated impossibilities". That is right but too weak. Two were affordable from cash at the window's first decision, seven of nine with the owner's own other mortgages, and only two (G15 Opus, G20 Opus) were not. The integrated text should say so with its basis (arithmetic under the engine's buildable and redemption rules, not an executed witness). It should treat Grok's four never-legal windows, where its notes defer redemption, as stated deferrals. This moves the development narrative from "execution-layer loss" toward "execution failures plus owner deferrals plus genuine illiquidity". That is more interesting and more accurate.
4. **Volume versus concentration in the inheritance headline.** Astra argues that 52 estate completions and 227 deeds transferred during play "against 63 trade completions and 207 traded deeds" is the main result. I agree on population, but the volume comparison should not lead. Fourteen of the 52 estate groups collect any rent, against 51 of 63 trade groups, so estates arrive late and are mostly realized as concentration. The concentration contrast leads: 45/52 against 18/63 winner-owned, 35/40 nonterminal estates to the eventual winner, and first estate to the eventual winner in 18 games. It is winner-conditioned and stated once as such.
5. **Rent totals in the development exhibit.** Astra would integrate rent with the development figure. Per-configuration rent on trade groups (\$20,818 / \$26,070 / \$5,930 / \$4,560) tracks survival, landing and wins, and invites a ranking that Fable's own "matches the order of wins" sentence then has to retract. Keep the totals in the appendix. If anything goes in the main text, use one sentence: groups built in the first window collected \$53,810 against \$3,568 for the other 20, with 11 of those built later and exposure unequal.

## 7. Incidents: G2 and G15 against G7 and G11

- **G15 (Fable, new).** Grok refuses a swap three times, the last with \$250 added. Its public and private reasons concern Sol's ability to build first. Sol's note counts on the same asymmetry. The state matches the notes: Sol has \$730 and Grok \$333, Gemini holds three houses on each orange (checked by me in the d168 prompt), and the note arithmetic (\$830, \$233, \$600) is correct. All four public messages reached the counterparty (Astra's check). Outcome: Grok is the first eliminated, 18 turns later, and its blockers pass to Gemini, which wins. This is the best main-text answer to the first research question's own example. It is a four-player state with checkable reasons and a third-party estate outcome. Its limits: refusing is not shown to be correct, and Grok's "5+ yellow houses immediately" is a capacity claim, not a forecast that was tested.
- **G2 (Opus).** Price reasoning about rival capacity (with an arithmetic error), a failed bluff and a reversal, construction without rent and inheritance by the winner. It is valuable as the one chain that touches all four results. Its risk is a narrative reading that the reversal was a mistake. Remove the "shows the whole chain studied here" sentence and the introduction vignette.
- **G11 (Opus; Fable appendix).** A two-player endgame. The refuser is far ahead, so refusing its own completion costs little. It is better as an appendix contrast with the false-premise correction.
- **G7.** The clean settled bluff. One sentence in the G2 reading and a full appendix card.

The main seven become G15, G2, G19, G20, G13, G18 and G12. G3, G7, G11, G4, G6, G12 d195 (rejected label), the G1 Boardwalk note and the G20 d1 disclosure go to the appendix.

## 8. All-section recommendations

`integration_proposal.md` gives the full architecture and keep/cut/rewrite decisions. `replacement_prose.tex` gives finished text. Headlines:

- **Title and abstract.** Remove every count that is either mechanical (373/429) or terminal-inflated (121, 54/60). Lead with the stratified bargaining contrast, the execution partition, 56/3/1, and nonterminal concentration. One sentence states the conditions.
- **Introduction.** One question, three results, scope. No G2 vignette. No claim that agents already act for firms without a deployment source.
- **Setup.** Sol's prose, Fable's configuration table with a "departure from standard path" column, exact refusal-chain counts (1,604 recovery chains; G2 d129 exception), and the Grok conflict breakdown (60 end→propose, 22 build→end, 11 buy→auction, 6 reject→accept, plus 7 where the content named bankruptcy and the call financed instead, and 1 the reverse). The prompt norms are quoted once.
- **Measurement.** Units, ledgers, bound and witness and guarded search, arithmetic access checks, channels, coding identities (the 74-rejection and 240-sample codings were done by GPT-6 Astra instances), and incident selection.
- **Bargaining.** Position-by-cell table, responder rejection line, styles table with conditions, counter content (with 79/88), the cash-to-list paragraph, reasons (61/74; 36 of the 74 are "both"), initiation with the Grok join, an exploratory cash-poor sentence, and the G15 and G2 incidents.
- **Development.** Window table with an "ever built" column. Never-legal explained by arithmetic. END census, reachable multisets, recovery table and two valid holds. No "lost value".
- **Debt and inheritance.** Finance figure, four-case table, mechanisms kept distinct, the G12 incident, a route figure with the terminal bar separated, concentration and late arrival, and trajectories without survival durations.
- **Conduct.** G13, G18, G20 and G19 with Astra's and Sol's readings, edited for the G20 d97 fact.
- **Temporal.** Fable's or Sol's compact version: G16 plan lost at the call, G9 target realized, and recurrence by feedback exposure.
- **Related work.** The narrowed comparator claims from the literature checks.
- **Discussion.** Corrected implications for economic-agent evaluation, one merged question map, and A–C paragraphs including Fable's seed-block observations without "the dice decided".
- **Limitations.** One section (Sol's, plus the arithmetic-access and list-price caveats).
- **Appendices.** Evidence tables, extra incidents, provenance by author, and the readiness pilot.

## 9. Three likely rejection reasons for the best integrated paper

1. **A descriptive case study with no identified effect.** Twenty games, five seeds, one roster and no manipulation. The headline contrast changes by about half under one stratification, so a referee will ask what else it would lose under price, deed and state controls the design cannot supply. Incidents are purposive. A venue that wants generalizable capability claims may see a careful log analysis without a transferable result.
2. **Harness conditions dominate the configuration comparisons.** Opus is refused on the first attempt in 1,604 of 1,696 decisions. It answers 162 of 189 offers in the action-only condition and loses its private memory. Grok's content and calls disagree in 139 decisions, including 64 of its 136 thread openings. 2,054 of 6,989 initial prompts (29%) contain misattributed trade history. A referee may conclude that cross-configuration differences in rejection, construction and defaults measure the harness more than strategy, and that the cohort should be rerun before analysis. We cannot answer that without new runs, which are outside scope.
3. **Semantic and selection validity, and incremental novelty.** Rival-consequence coding and the temporal sample were done by LLM instances from families that overlap the evaluated systems, with a partly unblinded second reader and no human labels. The same coauthor models chose the incidents. AgentMonopoly, FinBoardBench, the Arena study and DECE already cover Monopoly, financial board games, state-grounded communication and configured-system evaluation. A referee may judge the connected account an incremental contribution.

## 10. My strongest dissent

The four drafts and Astra's integration plan still let *signed cash medians and pooled completion cells* carry the bargaining claim, and they let *never-legal windows* stand for inability. Both choices make the paper sound more decisive than its evidence. The position split and the list-price comparison show that much of the apparent rival-completion premium is composition. The redemption arithmetic shows that much of the apparent illiquidity is owner deferral. The integrated paper should lead with the stratified contrast and the corrected execution partition, even though the story becomes less striking. If it does not, the first careful referee will make these two corrections and the paper's credibility on everything else will suffer.

This review does not establish that the integrated paper will be accepted or is free of error. It records the faults I found and the limits that remain.
