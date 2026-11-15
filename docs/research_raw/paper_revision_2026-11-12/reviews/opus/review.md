# Opus cross-review of the four November 12 manuscripts

12 November 2026. Reviewer: Opus (LLM research assistant), one of four coauthoring assistants. This is a whole-paper review of all four frozen drafts, my own included. It is not a score and makes no acceptance prediction.

## 1. What I did

- Checked all 234 hashes in `four_draft_manifest.json` and all 72 in `baseline_manifest.json` before starting. All matched. The check is repeated at the end (`verification.md`).
- Read `CROSS_REVIEW.md`, `CHARTER.md`, both external reports in full, and every complete manuscript with its handoff, findings file and evidence map: Astra, Sol, Opus, Fable 5.2. Wrote `initial_position.md` before any fresh check and before opening any other November 12 review. I did not open `reviews/astra/` or any integration file.
- Ran read-only checks on the claims that are new in one draft or that differ across drafts. `checks/run_checks.py` regenerates every fresh number below from stored records and writes `checks/fresh_checks.json`. `checks/verify_quotes.py` checks the eleven quotations I use in `replacement_prose.tex` against raw events (`checks/quote_checks.json`). Neither script imports engine or arena code, replays anything or contacts a provider.

## 2. Summary judgment

The four drafts agree on the core of the paper. All four put the agent's own changing options first: sixteen debts that only mortgages released by building sales could pay, fourteen paid, thirteen first-decision texts that count the released collateral, one that raises it as a question, and two bankruptcies whose stated sums leave it out. All four treat the opening swap/cash contrast as exploratory and composition-sensitive, keep the 61/74 reason codes as a separate population, correct G18, name both replay comparisons and keep eight incidents. The integration task is to choose the best-supported version of each shared claim and to decide which single-draft claims survive checking.

After checking, my view of the best single paper is this.

1. **Thesis.** When these agents wrote down, before acting, what a move would make possible for themselves or for a rival, the applied action agreed with what they wrote. About their own finances the statements were usually accurate, including mortgage values and a release rule that no prompt stated. About rivals the statements were frequent and sometimes accurate, and the response pattern depended on the form of the offer in a way the records do not explain. Fable's title, "What a Move Unlocks", fits this thesis better than the other three.

2. **The strongest supported finding** is a refined version of Fable's quit-or-continue comparison joined to the sixteen. Among the 72 debts in which cash, listed mortgages and the salvage of every building fall short, agents declared bankruptcy at the first decision in 50 of the 56 that no own-asset route could pay and in 2 of the 16 that released mortgages could pay. Restricted to unpayable debts whose shortfall is no larger than the largest of the sixteen ($326), it is 15 of 19 against 2 of 16. In the sixteen, the first-decision text names the released collateral or a budget including it before any sale in 13 of the 14 payments. Neither the system prompt nor the liquidation state supplies a price, a mortgage value or the rule that selling a group's buildings makes its deeds mortgageable; purchase prompts show a landed deed's price but never a mortgage value. This is a population-level agreement between a stated assessment, the state and the action. It is still retrospective, still read by one model, and still not a test of sensitivity or a calibration of difficulty.

3. **Bargaining** is best presented as a complete census with three robust descriptive facts and one fragile contrast. The robust facts are that opening offers almost never settle outside Grok's offers (11 of 389 openings by Sol, Gemini and Opus were accepted; later offers, 81 of 394), that rejections of offers completing the proposer's group almost always name the completion although no prompt labels groups or completion, and that the systems state different refusal policies (Gemini a reciprocity rule, Grok never-sell commitments, Sol and Opus prices). The fragile contrast is the swap/cash split, whose size depends on proposer and recipient composition.

4. **Two of Fable's new claims need correction before integration**, and one omission runs through all four drafts. Fable's "3 of 186 completing openings accepted, against 21 of 175" is Grok composition, and its claim that refusals "follow the event of completion" and "do not follow the size" of the rival's opportunity reads a flat line near an 80 to 88 percent ceiling as evidence. All four drafts omit the liquidation prompt's own instruction, "Declare bankruptcy only when you cannot or should not raise enough cash", which bears directly on the quit decision.

## 3. Fresh checks of new and disputed claims

### 3.1 Fable's quit-or-continue comparison (50/56 against 3/131)

Reproduced exactly from the inherited debt ledger and first applied actions. 53 episodes begin with a declaration: 50 of the 56 above the own-asset bound and 3 of the 131 payable (G12 Sol d190, G17 Gemini d234, G12 Grok d249). The six above-bound continuers are five Grok and one Gemini; Opus and Sol declared at once in all 27 of theirs.

The comparison as printed overstates the discrimination it shows. The 131 payable debts include 62 that cash and listed mortgages cover and 53 that need only listed building sales; together they contain one first-menu declaration, G12 Grok, whose note and assistant content both describe a sale while the received call declares. Those 115 debts do not test whether an agent can see a route the menu hides. The informative set is the 72 debts in which the visible sum (cash, listed mortgages, all building salvage) falls short:

| Visible sum short of the debt | Debts | Declared at first decision |
|---|---|---|
| Above the full own-asset bound | 56 | 50 |
| ... with shortfall no larger than $326 (the largest tier N shortfall) | 19 | 15 |
| ... with debt/visible ratio no larger than 1.81 (the largest tier N ratio) | 24 | 20 |
| Payable only with released mortgages (tier N) | 16 | 2 |

So the agents' first-decision choice to quit separates unpayable from payable debts even among debts whose visible shortfall is of similar size. This is the strongest whole-population support the corpus offers for the sixteen texts. It also inherits their limits: the tiers were defined after the corpus had been studied, two failures cannot show what produced a declaration, and the comparison is across different states, so it is not the "sensitive" rung of the ladder. I computed the visible-shortfall split in this review; it is one more retrospective slice, offered as a correction of the denominator rather than a new headline.

### 3.2 The liquidation instruction that every draft omits

All 439 stored liquidation prompts carry the same scenario note:

> Choose exactly one liquidation action now. The engine will apply it, update your cash/assets, and ask you again if you still cannot pay. Declare bankruptcy only when you cannot or should not raise enough cash.

No draft quotes or describes it. Fable's setting paragraph lists what the liquidation prompt gives ("the amount owed, the shortfall, the two lists and the player's holdings") without it. The note matters twice. It tells the agent that the menu refreshes, so continuing without a complete plan is a reasonable reading of the task. And it tells the agent when to declare, so declaring on an unpayable debt follows an instruction rather than revealing an unprompted judgment, while declaring on a payable debt follows the agent's own (wrong) belief that it cannot pay. The integrated methods should quote it.

### 3.3 "The prompt supplies none of these values"

Fable's claim that neither the release rule nor any mortgage value is in the prompt is right about what the environment states and slightly wrong about the prompt. In all sixteen first-decision prompts the structured state has no price, rent, mortgage-value, house-cost or group field, and the system prompt does not mention mortgages. But twelve of the sixteen prompts carry the agent's own last ten private notes, and those notes are part of the prompt. By text search and reading of every matching sentence:

- eleven carry some mortgage or liquidity amount, usually the listed capacity (G20 Sol, "$325 idle mortgage capacity"; G12 Sol, "$130 emergency mortgage capacity");
- two state the release rule itself (G1 Grok: "yellows cannot be mortgaged while it stands"; G18 Gemini, about an opponent who "must sell all 5 Dark Blue houses and mortgage a Dark Blue property");
- two state redemption costs of a deed the sales would release (G4 Opus, "Unmortgage Kentucky for $121"; G13 Gemini, "unmortgage Park Place ($193)");
- none states the mortgage value of a deed whose mortgage the sales would release.

Purchase prompts (`BUY_OR_AUCTION_DECISION`) do show the landed deed's price, group, house cost and rents, so a mortgage value can also be derived from a price seen earlier plus the half-price rule; no prompt states a mortgage value. So "each one is a board fact the system recalled" should become: no prompt states a mortgage value or the release rule, and liquidation prompts show no prices; released-deed mortgage values do not appear in any carried note; listed capacity and, twice, the rule itself were carried forward in the agents' own notes. This is a positive memory observation for research question 4, not a weakening of the finance result.

### 3.4 "3 of 186 completing openings accepted, against 21 of 175"

Reproduced exactly, but the comparison is composition. Eighteen of the 21 accepted non-completing openings answered Grok-authored offers. Without Grok-authored openings the counts are 3 of 165 against 3 of 114. Across all forms, 32 of 524 openings were accepted, 21 of them Grok-authored; Sol, Gemini and Opus openings were accepted 11 times in 389. Later offers were accepted 81 times in 394. The robust statement is that opening offers almost never settle unless Grok wrote them, and trades happen through counteroffers. Completing openings are no exception, and the corpus does not show that completion lowers opening acceptance. At the thread level the difference is smaller but survives the exclusion: threads opened by a completing swap or cash bid ended in a trade 26 of 186 times against 49 of 175, and 23 of 165 against 25 of 114 without Grok-authored openings. That is one more retrospective slice and I would keep it in the appendix.

### 3.5 Within-recipient cash-bid gaps and recipient standardization

Fable's "within every recipient the cash-bid gap is between 0 and 9 points; the pooled −5 is composition" is substantively right with one rounding slip. The recipient gaps are Sol +8.5, Gemini +5.0, Opus 0.0 and Grok −0.2. Gemini and Grok, who reject most, receive 72 of the 103 non-completing cash bids but 42 of the 70 completing ones. Standardized to a common recipient mix, the cash-bid gap is +3.5 or +3.9 points and the swap gap +23.4 or +24.3, depending on which cell supplies the weights. This is a useful addition: by recipient, the form difference is about 20 points with a small positive cash gap, while by proposer the cash gaps run from −5.4 to +2.2. Both standardizations should be printed with their weights.

### 3.6 Counters by form

Reproduced: completing cash bids drew counters 26 of 70 times, completing swaps 20 of 116, with the same sign in all five blocks. Fable's "swaps are refused and cash bids are priced" omits the baseline: non-completing cash bids drew counters 32 of 103 times against 18 of 72 for non-completing swaps. Cash bids are countered more in both cells, and the gap widens under completion (37 against 17 percent, compared with 31 against 25). In 15 of the 26 completing cash-bid counters the recipient kept the deeds and asked for more money.

### 3.7 "Refusal does not follow the size of the rival's opportunity"

The capacity table reproduces (completing swaps rejected 4/8, 26/33, 42/48, 23/27 by proposer house capacity; cash bids 2/3, 13/19, 7/20, 20/28). Splitting completing swaps by the proposer's post-trade cash in terciles gives 29/38, 35/39, 31/39. None of this shows insensitivity. Swap rejection sits at 79 to 88 percent in every bin with data, so there is little room to rise. The measure counts houses, and a house on light blue and a house on dark blue are different opportunities (of the groups that opening offers would complete for their proposers, 46 are light blue and 37 dark blue). It ignores mortgage capacity. And the bins are small. Fable's "The response follows the event of completion and the form of the offer. It does not follow the measured size of what the rival could do next" and the introduction's "attach to the event of completion" turn absence of a gradient into a finding. My own draft's "these slices give no sign that refusals scale with the rival's building power" is milder but needs the ceiling caveat too. The supportable sentence is that this coarse measure shows no gradient, which neither supports nor excludes sensitivity to the size of the rival's opportunity.

### 3.8 Refusal wording by system

Fable's regular-expression counts reproduce: Gemini rejected 62 of 67 completing openings and used reciprocity wording in 28 of the 62; Grok rejected 54 of 61 and used commitment wording in 38. The drafts give no baseline. In rejections of non-completing openings Gemini's reciprocity wording appears once in 59 and Grok's commitment wording 12 times in 36. So Gemini's reciprocity rule is specific to completing offers, and Grok's "never" is partly a general refusal style. The baselines should be printed. Gemini's rule is a good example of an explicit, consistently applied stated policy, for example G1 d170: "No thanks, p2. I'm not giving up a complete Pink monopoly without getting a completed monopoly in return."

### 3.9 What the trade prompts do not say

The structured trade and liquidation state has these fields only: cash, holdings by space key with houses, hotel and mortgaged flags, bank stock, positions, the offer, history and the legal menu (`trade_and_liquidation_prompt_fields` in `fresh_checks.json`). No group, completion, price or rent field exists. Recipients who name a completion are identifying it from space keys and their own board knowledge. That strengthens the stated-level reading of the 93 of 95 and 42 of 42 completion mentions.

### 3.10 Tool choice

Fable reads Grok's `tool_choice` from saved request records; Sol's evidence map says request artifacts do not retain it. Fable is right. The 8,687 `cloud/calls/*.intent.json` records carry `tool_choice` "required" in all 1,705 Grok requests and "auto" in all 3,301 Opus, 1,991 Sol and 1,690 Gemini requests. The integrated paper can cite both the request records and the source at the two run commits. The 8,687 request records exceed the 8,679 attempts in the decision logs by eight; the paper should not equate them.

### 3.11 Resampling

My two-stage resampling (seed blocks, then games within blocks; 20,000 draws, a new generator seed) reproduces my draft's intervals within Monte Carlo error: all swaps +12.7 to +48.7; without Grok authors −10.1 to +40.8; without conflicting openings +1.4 to +45.9; cash bids −26.2 to +11.8. Game-only resampling reproduces Fable's (+13.8 to +48.2; −1.6 to +37.5). Exact whole-block enumeration reproduces Astra's and Sol's (+24.2 to +35.5; −3.8 to +31.9), with only 126 distinct multisets. Block-only resampling ignores variation among games within a block, so it is narrow by construction, not because the contrast is stable. It also produces a misleading band elsewhere: without Grok-authored offers, the block-only cash-bid band is −21.3 to −0.1, which excludes zero, while the two-stage band is −32.9 to +8.7. Astra's figure and Sol's methods use block-only bands as the only interval. The integrated paper should show per-block values and leave-one-block-out ranges first, then the two-stage interval, and say why block-only is narrow if it appears at all.

### 3.12 Incident facts that differ across drafts

All checked against events and stored prompts.

- **G15.** Fable adds that one decision before Sol's offers, Opus told the table "let's not hand him the last piece of any set" (d166), and that message is in Grok's d169 prompt. Gemini refused a different Sol offer that turn. Confirmed. Grok was eliminated to Gemini at turn 81, eighteen turns later; my draft's "within twenty turns" is right but vaguer.
- **G2.** A parallel no draft reports. Grok, which had just bid $200, posted at d122: "p1, sit on Marvin. Selling it to p4 gives them a second monopoly on top of light blue — the only stack that can actually finish you. I'm not raising." That message is in Sol's d124 prompt, where Sol asks Opus $650. Sol's earlier $450 ask to Grok was a counter that already cited "access to a well-funded yellow monopoly". Opus held $845 when it bid $325 (Fable, confirmed). In G2 and G15 a third player publicly urged the holder not to hand over the set one or two decisions before the refusal. Receipt is confirmed; influence is not measurable here.
- **G13.** Grok went bankrupt on Short Line at turn 150 owing $200, the yellows passed to Sol, and Opus won. Astra, Sol and Fable are right; my draft omitted the location and winner.
- **G7.** Gemini collected $270 of orange rent after the purchase (turns 76 and 81) and Sol eliminated it at turn 125 on Boardwalk; Sol won. Astra, Sol and Fable are right; my draft left this out.
- **G20 appeal.** After the appeal Grok built one house on each red, mortgaged New York, offered Vermont for $150, was refused and mortgaged Vermont for $50. Astra, Sol and Fable are right; my draft mentioned only the Vermont mortgage.
- **Estates.** 35 of the 40 nonterminal eliminations sent the estate to the eventual winner (Fable, confirmed).
- **Sol's context examples.** G9 Sol set a goal of three houses on each dark blue at turn 29 and reached it at turn 60; Sol in G14 and Gemini in G15 won without settling a trade; Gemini collected $3,250 of developed orange rent in G15. All confirmed.

## 4. Comparing the drafts

### Astra

Best: the most compact complete paper (two columns, main text ends on page 10); the clearest statement that tiers are "financing requirements, not calibrated levels of task difficulty"; a careful G13 reading ("Its solvency reasoning follows Grok's appeal rather than preceding it independently"); the economic context of ownership, construction and estates, labeled as context. Weakest: block-only resampling as the only interval, with a figure that gives it visual authority; "because of" in the G15 heading and introduction; a proposer table that prints a 50-point gap from a 0/2 cell; "Planning and Bargaining" and "evidence of local financial planning" in title and abstract, which read stated plans as planning.

### Sol

Best: the most careful methods (operational definitions, the resampling target and what it is not); the complete printing of all sixteen first-decision fields with a stated channel rule; a response-handling table; the replay appendix; positive context examples (G9 target, G14 and G15 winners without trades). Weakest: block-only bands as the uncertainty summary; the incorrect statement that request artifacts lack `tool_choice`; three incidents in the body, so G2 and G7, which carry most of the pricing and construction evidence, sit in the appendix.

### Opus (mine)

Best: the evidence-ladder table that assigns each result its level; the two-stage resampling with all three units in an appendix table; the configuration table; the keyword screen, list-value and capacity checks that narrow two alternatives; the G12 Grok paragraph separating a channel conflict from a failed sum; the G18 text search. Weakest, in my own reading now:

- "Most debts were easy" is a section title. That is difficulty language the charter rules out. It should say what the debts required.
- The capacity sentence needs the ceiling caveat (3.7).
- It misses the quit-or-continue comparison, the scenario note, the recipient standardization, the counter baseline, the refusal styles and the third-party warnings, all of which help the account and most of which are positive observations.
- Eight full incident cards in the main text give a 19-page body. Readers and both referees asked for a tighter narrative.
- It omits continuation facts that the other drafts got right (G13 location and winner, G7 rent and elimination, G20 build).

### Fable 5.2

Best: the clearest framing and title; the quit-or-continue comparison; the observation that no prompt states a mortgage value or the release rule; the G5/G17 Gemini contrast on the same two deeds; recipient strata and counters; refusal styles; the G15 context; a four-plus-four incident structure with one-paragraph main-text summaries of the casebook; request-record evidence for tool choice. Weakest: the three corrections in 3.1, 3.4 and 3.7; "board fact the system recalled" (3.3); "Most payable debts were easy" and "the hard set"; and the handoff's dissent that "the first-menu partition calibrates difficulty", which conflicts with the charter.

## 5. The three distinctions the charter asks for

**Resource requirement, not calibrated difficulty.** Tiers A, B and N say what the first menu and holdings would have to supply. They do not say how hard the state was for an agent, and no reference policy was run. The integrated text should say "required only listed items", "required building sales", "required released mortgages", not "easy" or "hard". The quit-or-continue table is a requirement partition plus the agents' first choice; it is not a difficulty scale either.

**Expressed plans, not cognition.** The sixteen texts, G20's budget and the bargaining notes are what the systems returned. Five of the fourteen successful necessary-collateral texts are Opus's provider-returned reasoning under action-only recovery; the rest are applied private notes. "Anticipation", "foresight" and "planning" should be qualified as stated or expressed wherever they appear, and the abstract should not say "planning" without that qualifier.

**Execution, not effectiveness.** Paying a debt is a checkable local endpoint, and the G20 sequence executes an announced aggregate budget to the dollar. Ten actions are execution length, not ten steps of lookahead; the note fixes a total, a rule and the decision not to concede, and the refreshed menus supply the order. No result shows that a payment, a refusal, a price or a bluff was good play.

## 6. Eight incidents and eight questions

All eight incidents survive checking at the levels below. I recommend Fable's four-plus-four structure, with G20 payment, G15, G2 and G13 in the body and G7, G19, G20 appeal and G18 in a casebook with the same elements, plus one-paragraph main-text summaries.

| Incident | Supported level | What the integrated text must keep |
|---|---|---|
| G20 payment | accurate, consistent | Budget, not ordered plan; creditor components off by $25 each way |
| G15 refusal | accurate (cash figures), consistent | Opus's prior table appeal in Grok's prompt; one legal green house costs $200 |
| G2 pricing | stated, consistent; house count wrong | Grok's public warning in Sol's prompt; $450 ask already cites the yellow monopoly; Opus's "final" bid under a $475 ceiling |
| G13 insurance pitch | stated; accurate in private | 4/36 for a direct nine; omission not shown to cause the extra $70; Grok bankrupt on Short Line at turn 150, yellows to Sol, Opus wins |
| G7 bluff and financed sale | accurate, consistent | $270 orange rent; Sol eliminates Gemini at turn 125 and wins |
| G19 correction | accurate, consistent (Sol) | Grok's three channels disagree |
| G20 appeal | stated, consistent (author) | Grok builds, then seeks cash; Opus pursues the opposite bargain |
| G18 withdrawal | stated, consistent | Survival cash for the last opponent; no inheritance language d421 to d461; terminal estate |

The eight questions and A to C should stay in an appendix table at the levels my draft and Fable's give, with three updates from this review: question 4 (memory) gains the carried-note observation in 3.3; question 7 (collective dynamics) gains the third-party warnings in G2 and G15 alongside the G20 appeal; question A (talk and action) should cite the quit-or-continue agreement and the channel-conflict exception.

## 7. Dissent and evidence limits

- I dissent from Fable's claims that refusals "follow the event of completion", "attach to the event of completion" and "do not follow the size" of the rival's opportunity. The data show a flat line near a ceiling on a coarse measure.
- I dissent from Fable's handoff position that the first-menu partition calibrates difficulty. It records requirements.
- I dissent from Astra and Sol using block-only resampling as the only interval, for the reasons in 3.11.
- I dissent from my own draft's eight full cards in the main text and its "easy" heading.
- I partly dissent from Sol's choice of three body incidents; G2 carries the pricing and wrong-arithmetic evidence and belongs in the body.
- The visible-shortfall split (3.1), the recipient standardization (3.5) and the thread-settlement counts (3.4) are retrospective slices that I or another author computed after reading the corpus. They should appear as refinements of existing claims, not as findings of their own.
- My classification of carried notes in 3.3 is a text search plus one reading. The sixteen first-decision readings remain one-model readings. No human annotated anything.
- I did not recompute the inherited offer-ledger reconstruction, the 61/74 codes, the three engine-executed payment sequences, the G7 menu search, the historical replays, construction receipts, first-window builds, asking-price pairs or cost accounting.

## 8. Fresh and inherited

Fresh in this review (from stored records, `checks/`): the quit-or-continue counts and the visible-shortfall split; the scenario note in all 439 liquidation prompts; the field inventory of trade and liquidation prompts; the value and rule content of the sixteen first-decision prompts and carried notes; tool choice in 8,687 request records; the opening table, acceptance by author, thread settlement, proposer and recipient strata, recipient standardization, counters, capacity bins, cash terciles and refusal wording with baselines; the 74-row reason population; two-stage, game-only and exact block resampling; nonterminal estates; the G2, G7, G13, G15 and G20 continuation facts; Sol's G9, G14 and G15 examples; eleven quotations.

Inherited and not rerun: the offer ledger's post-trade reconstruction (reconciled earlier by Fable and others), the debt ledger's episode boundaries, the 61/74 semantic codes, the three payment witnesses, the G7 menu search, both stored replay comparisons, cost and token accounting, construction and estate exposure summaries, asking-price pairs and the fourteen paired histories.
