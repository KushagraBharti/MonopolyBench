# Independent review of the new feedback and the 12 November manuscript

Reviewer: Opus (xhigh). Date: 14 November 2026.

**Inputs read in full:**
- `inputs/pasted-text-2.txt`: Referee A, "5.5/10" report.
- `inputs/pasted-text-3.txt`: Referee A, comparator follow-up.
- `inputs/inline_feedback.md`: four pieces.
  - The experimental program, called **Ref C** here.
  - The v3 referee report, "4/10", called **Ref B**.
  - Ref B's comparator table.
  - Ref B's liquidation/oracle proposal, called **Ref D**.
- The whole 21-page manuscript: every LaTeX section, the appendix, the rendered cards, and pages 1, 4–7 and 12 viewed as images.
- The integrated handoff, evidence map, integration decisions, final-review decisions, findings/limits and literature notes.

**Process:**
- The 84-file pin matched before review (`pin_check_before.txt`). The after check is in `verification.md`.
- No game, engine execution, replay, policy rollout, search, baseline, provider call or subagent was used.
- Everything below rests on reading source code, original decision/event records and primary literature, plus arithmetic over stored records.
- I did not open any peer folder of this round.
- Where I read and classified model text myself, that is an LLM (Opus) reading. It is not human validation.

---

## 1. Bottom line

The manuscript is careful and honest, and its printed numbers are right. I recomputed:
- the 188-episode partition (62/53/16 with 62/52/14 paid, and 132/56 bound coverage);
- every U\* value;
- all sixteen necessity rows;
- the exact text of all sixteen printed initial fields.

All of them reproduce. My earlier 12 November recomputation of the bargaining tables still applies, because the pinned data are unchanged.

The paper's problem is not accuracy. Once three facts are set beside its central result, the financing result says something narrower and different from what the manuscript implies. The referees each touch these facts, but none of them puts all three together.

1. **Payment success in this engine is mechanically guaranteed for any agent that does not stop.**
   - The engine pays automatically as soon as cash covers the debt.
   - It keeps offering sales and mortgages until none remain.
   - It auto-declares only when nothing is left.
   - In all sixteen necessity states, no hotel/bank-stock restriction can bind.
   - So any policy that keeps choosing listed sales or mortgages pays all sixteen. That includes the configured fallback, as Ref B says.
   - "Fourteen of sixteen paid" therefore measures the *absence of premature stopping*, not route construction.
   - The only discriminating decision is continue-or-stop, and the informative events are the two stops.

2. **Both failed sums equal U0 to the dollar.** Sol's $408 and Gemini's $530 are exactly cash plus all salvage plus the initially listed mortgages. U0 is the total a menu-bounded inventory produces. By the paper's own definition, U0 < D in every necessity state. So the necessity subset is exactly the set of payable states on which a "count what the menu offers" estimate gives the wrong feasibility verdict.
   - Most successful texts pass through that same U0-type total (cash plus current sales and listed mortgages) before adding the released collateral.
   - Several successful provider-returned explanations transiently conclude infeasibility on it.
   - Agents beat the menu-bounded estimate on 14 of the 16 states where it fails. The two failures stop at it.

3. **The "prospective statement" is not prior to the decision it accompanies.** In all eleven private-note cases, the note is an argument of a tool call whose function had already been chosen. In 8 of the 9 sale/mortgage cases, the note also follows the action's own arguments in the emitted call. Corpus-wide in liquidation calls the note follows the action arguments in:

   | Model | Note after action args |
   |---|---|
   | Sol | 81/81 |
   | Grok | 36/40 |
   | Gemini | 56/77 |

   The text is prospective relative to the *menu* (it names collateral not yet offered). It is not prospective relative to the *choice*. The manuscript's sentence "The initial statements below show which resources agents count before choosing whether to proceed" (finance.tex, §3.1) is wrong as written.

**What the evidence supports:**
- Agents value unlisted collateral almost perfectly. Every stated value is right except Sol's $430 for $400 of yellow mortgages.
- Agents usually include released collateral in their first text, and they execute consistently with it.
- About half of the successful texts (5 explicit, 1 tentative) state the dependency itself. The rest give an ordered route (3) or an inclusive total (5). An agent that ignored the rule and simply summed every deed could have written the inclusive totals.
- The two premature stops on payable debts are both inventories that stopped at U0.
- The third payable declaration is a Grok call-level artifact, not a judgment.

This is a real, specific and checkable observation. It is a discovery-scale description of three stop decisions, not a planning result.

**Overall judgment.** I agree with both referees that, as written, this is not a main-track paper at a top ML venue. My reasons are more specific than either report.
- Referee A's central ask, "calibrate with a transparent reactive policy," is largely answerable from the code without running anything. The answer removes the payment rate as evidence.
- Referee B's proposed new headline, "a planted number in the agent's own notes," is weakly motivated by its own facts.
- The experimental program in Ref C ("interfaces centered on current actions cause false infeasibility") is partly contradicted by the discovery data. In G17, Gemini counted two Park Place houses the first menu did not offer for sale, yet omitted only the mortgages those sales release. That points to a rule-specific omission, not generic menu-literalism.
- I disagree with both reviewers on several factual points (§8).

---

## 2. What the paper secures (re-verified this round)

| Claim | Status | How checked |
|---|---|---|
| 188 episodes; 128 paid, 60 eliminated; 338 liquidation decisions | Confirmed | Episode ledger joined to original decisions |
| U\* for all 188 entries | Confirmed, 0 mismatches | Recomputed from each entry prompt and `contracts/data/board.json` |
| 62/53/16 partition with 62/52/14 paid | Confirmed | Recomputed |
| 132/56 bound coverage at entry | Confirmed | Recomputed |
| All sixteen printed initial fields | Confirmed, character for character after LaTeX normalisation | Compared with the original applied note or the final-attempt provider text |
| Opus refused first attempts contain no hidden text | Confirmed | Checked the raw responses; the selection rule drops nothing |
| Necessity certificate (U0 < D ≤ U\*) | Sound | U0 is an upper bound on what the first menu can reach (S includes all nominal salvage). Any further mortgage requires clearing a group's buildings, and trades are not available in liquidation |
| 14 of 16 paid | Confirmed | Exact 95% interval 61.7–98.4%. Per system: Sol 2/3, Gemini 5/6, Opus 5/5, Grok 2/2 |
| G20 d327: two sales, eight mortgages, $14 left; G20 d291 sequence 275→725→845→955→+70, $25 left | Confirmed | Decision-by-decision cash |
| G7 menu restriction | Consistent with code | A hotel lot is sellable only if the bank holds ≥4 houses; the bank held 0 |

The paper's descriptive bookkeeping is unusually strong, and that should be preserved.

---

## 3. The financing result, re-analysed

### 3.1 Payment success is mechanically guaranteed absent stopping

**Engine semantics (read at HEAD; the engine is identical to run commit `d6808534`):**
- `_resolve_pending_payment` pays automatically whenever `cash ≥ amount`.
- If no mortgageable deed and no sellable building remains, it auto-declares bankruptcy. Otherwise it builds another liquidation menu.
- `_mortgageable_space_indices` excludes any deed whose group has buildings.
- `_sellable_building_space_indices` excludes a hotel lot unless the bank holds ≥4 houses.
- `_validate_sell_plan` checks bank stock and evenness only on the plan's final state. A single bundled plan can therefore sell a hotel together with its four houses even when the menu would not list the hotel.

**The active fallback.** The fallback actually used is `SharedDecisionResolver._fallback_action`, named `finance_before_bankruptcy_v2`. It declares only when neither a mortgage nor a sale is legal. Otherwise it mortgages the first listed deed, or sells one unit of the first listed building.

`LlmRunner._fallback_action` in `llm_runner.py` is a dead duplicate: it is defined, never called, and puts declaration *first* in liquidation. Ref B is right that it is stale code.

**Consequence for the sixteen.** A building lock can bind only through hotels with insufficient bank stock.
- Fifteen of the sixteen entry states contain houses only.
- G20 d327 has two brown hotels with 15 bank houses, so the bank never drops below 7.
- So every maximal never-declare sequence reaches full liquidation, U\*, and the engine pays as soon as cash ≥ D ≤ U\*.

Ref B's "16 of 16 by construction" follows from the menu semantics for these states. It is a counterfactual derived from code, not an executed result, and I ran nothing.

**Where Ref B goes too far.** "Any order of sales and mortgages reaches U\*" is false in general.
- G7 (Opus, d338) is the counterexample in the corpus: nominal $1,310, reachable $440.
- With two or more hotel groups and fewer than eight bank houses, the first hotel sale can exhaust bank stock. Which hotel is sold first then changes the reachable total, so order can matter.
- 26 of the 188 entry states hold hotels; a few have low bank stock (G3 d439/d456 at 0, G7 d318 at 2, G18 d297 at 3).
- My claim is therefore restricted: **for the sixteen, and for every houses-only state, payment success is guaranteed for a non-stopping policy.** I did not exhaustively certify every hotel state among the 131. That would need the search the brief prohibits.

**What this does and does not imply.**

- It does not imply "the task needs no anticipation" (Ref B). The decision to continue at each menu needs a judgment about whether the remaining options can cover the debt. The never-quit loop avoids that judgment only by having no stopping rule. On the 56 above-bound debts it would liquidate everything and then be eliminated. In this engine, that converts buildings the creditor would have inherited intact into half-price cash. It changes the creditor's position, not the debtor's.
- It does imply that the payment rate (14/16, and 128/131) cannot carry evidence of planning difficulty. Ref A's request for a "transparent reactive policy" is partly answered already. A never-quit policy pays every one of the sixteen. A *menu-bounded stopping rule* (declare iff U0 < D) declares on all sixteen, by definition of the subset. The agents sit between those two reference behaviours: they stop on 2.
- The scientifically live quantity is the **stop decision**, as I argued in my 12 November cross-review (quit-or-continue). The evidence is now cleaner.

| Entry region | First-menu declarations | Note |
|---|---|---|
| U0 ≥ D | 1/115 | That one is G12 d249, a Grok call artifact (§3.6) |
| U0 < D ≤ U\* | 2/16 | Both judgment failures |
| U\* < D | 50/56 | 42/48 when the bankruptcy-only menus are excluded |

### 3.2 What the sixteen texts show: the U0 identity, dependency statements and inclusive budgets

My classification of the sixteen first texts is an LLM reading with exact evidence. A human coder should check it.

| Category | Episodes | n |
|---|---|---|
| States the dependency (sale enables mortgage) | G1 Grok "Must sell before yellows can be mortgaged"; G2 Sol "Clearing buildings unlocks yellow mortgages"; G5 Gemini "unlock the ability to mortgage"; G8 Gemini "will also unlock Park Place and Boardwalk"; G18 d309 Gemini "which will allow me to mortgage St. Charles Place" | 5 |
| Tentative statement of the dependency | G20 d291 Opus "checking whether mortgaging the pink lots themselves after clearing the houses could close the gap" | 1 |
| Ordered route including released collateral, rule not stated | G4 d270 Gemini "sell my 4 houses … and then mortgage two Yellow properties"; G13 d195 Gemini "sell the house on Boardwalk ($100) and mortgage Park Place ($175)… Selling the house on Boardwalk first"; G18 d313 Grok "still need to mortgage PP or BW afterward" | 3 |
| Inclusive total, no stated dependency | G4 d308, G6 d185, G11 d203, G17 d254 (all Opus provider text); G20 d327 Sol ("Full liquidation should yield $1,414 including cash and all mortgages") | 5 |
| Omission, stopping at U0 | G12 d190 Sol ($408 = U0); G17 d234 Gemini ($530 = U0) | 2 |

**Implications:**

- **"Thirteen state the subsequent mortgages or an aggregate budget including them" is literally true but evidentially mixed.** An agent that simply summed every deed's mortgage value, without knowing the rule, would write the five inclusive totals. Only the five explicit statements, the tentative one, and arguably the three ordered routes separate anticipation of a changed menu from naive totalling.
  - Referee A's "dependency recognition" column is the right correction.
  - My own 12 November reading ("12 explicit, 1 aggregate, 1 tentative, 2 omissions") conflated inclusion with recognition. I withdraw it.
- **Channel matters.** Four of the five inclusive totals are Opus provider text. Opus never had a private-note channel in these games.
- **Values are almost perfectly retrieved, although the prompt supplies none.**
  - Every mortgage and salvage value stated in the sixteen texts is correct except G2's $430 (true $400).
  - G20 d291's comparison is garbled. "$725 short even after…" is the initial shortfall. "$680 … still under the $1000 needed" compares new proceeds with the whole debt. The direction is right (680 < 725, residual $45). Referee A's accounting is exactly right.
  - The binding error in both failures is inventory, not values or arithmetic.
- **The U0 identity.**
  - Both failed sums equal U0.
  - Most successes state a U0-type total or the shortfall left after current sales and listed mortgages, then add released collateral: G1 $126; G2 $283; G5 $674; G11 "$276 without touching the other properties"; G18 d309 $412; G18 d313 "$500 … ~$49 gap"; G13 states M0 = $445.
  - The structure is therefore not "anticipators against reactors". Nearly everyone computes the menu-bounded total; fourteen take a second step and two stop.
- **Execution agreement is high at the specificity stated.** Every success realises its stated route or stops early once the budget suffices.
  - G13 is the most demanding plan in the set. It sells one Boardwalk house, mortgages Pacific, Electric and Indiana (exactly the planned $335) and Park Place, and keeps Boardwalk and Kentucky unmortgaged as planned. That is a genuine route choice under slack (U\* = 1,088 against D = 750).
  - G20 d327, the paper's showcase, has D = U\* − 14. Full liquidation is the only payable end state, so the "$14 prediction" is U\* − D. The case shows exact valuation of 19 assets, and Gemini had computed the same U\* from the opponent's side. It does not show route planning. "An announced budget survives ten actions" is accurate, but it is the least informative success to headline.
  - Two sell actions are bundles, so "ten actions" partly reflects the interface: sales bundle, mortgages do not.

### 3.3 Joint generation and timing

**Private notes come after the choice.**
- For the eleven note cases, the function name precedes the arguments in every stored call.
- In both failures the call is `declare_bankruptcy`, and the infeasibility note is its argument.
- In the nine sale/mortgage cases, the note follows the action's arguments in eight. G18 d313 Grok is the exception.

**The provider text precedes the call.**
- Opus's provider texts are generated before the tool call. Ironically, the five Opus texts are the most temporally prior statements in the set.
- Sol's G12 d190 summary had already concluded bankruptcy, adding "It seems like bankruptcy might transfer property anyway".

**Later actions read the note back.** Subsequent actions are conditioned on the carried note, which is fed back as memory. "Realising an announced budget" is partly consistency with a note the agent rereads. Opus is the exception: recovery responses author no note, so its successes carry no plan forward.

**What the timing does and does not undermine.** None of this makes the texts uninformative. It removes any reading of the note as an independent prediction of the action it accompanies. The defensible temporal claim is the one the related-work section already makes: the text names a resource *before the menu exposes it*.

### 3.4 Both channels, and omission as a common intermediate state

Ref B is right that the selection rule (note when present) hides informative text in the failures.

| Failure | Applied note | Provider-returned text |
|---|---|---|
| G12 d190 Sol | "No legal liquidation can save me." | Same inventory, then "It seems like bankruptcy might transfer property anyway, so declaring insolvency could be the best option without needing further actions." This is a mixed motive: false infeasibility plus indifference. |
| G17 d234 Gemini | "Since I cannot raise $550, I must declare bankruptcy." | Ends: "This won't cover my rent in full, so I will have to start thinking of additional options." It then declares, which reads as premature closure. |

Printing both channels for all sixteen cuts both ways. The provider texts of several *successes* show the same menu-bounded inventory before the applied note completes it:
- **G8 Gemini:** only the $100 house and $30 Baltic, then "I need to make a more holistic plan". The note states the unlock.
- **G13 Gemini:** listed mortgages first, then a revised plan.
- **G18 d309 Gemini:** the sale only.
- **G5 Gemini:** explicit revision.
- **G18 d313 Grok:** "I cannot raise enough cash to pay the rent. After selling the buildings, I could mortgage Park Place for $175."

So a transient U0-bounded conclusion is common. What distinguishes the failures is commitment to it.

That observation is more interesting than either "omission" or "menu literalism". It is still a descriptive pattern over provider-surfaced, possibly summarised fields: Gemini `reasoning.text`, Sol/Grok `reasoning.summary`.

### 3.5 Carried-note hypothesis against its counterexamples

**Ref B's facts are correct:**
- Sol's carried notes repeat "$53 cash plus $130 mortgage capacity/reserves" at turns 57, 65, 69 and 73. The turn-57 note explicitly calls them "non-red assets".
- Gemini's turn-68 note keeps "Baltic Avenue unmortgaged as a $30 emergency reserve".
- Four of Opus's five successes had no carried notes. G4 d308 carried ten notes from turns 62–65, 81 turns stale.

**But the inference is weak:**
- $130 is the true mortgage value of Baltic plus Oriental plus Vermont, and $30 is Baltic's. Any agent that correctly prices the listed deeds reuses those figures "to the dollar", whether or not the note steered it. The match is mechanically expected.
- The same reserve frame preceded successes:
  - G13 Gemini carried "$445 in mortgageable non-Dark-Blue properties" and used exactly that figure in a plan that adds released Park Place.
  - G20 d327 Sol carried "$325 idle mortgage capacity" and computed $1,414.
  - G1 Grok's turn-207/209 notes give a "Liq ceiling" that omits yellow mortgages, and Grok still succeeded.
  - G5 Gemini's turn-141 note omits dark-blue mortgages, and Gemini revised.
- With two failures and at least four note-bearing successes that share the frame, the carried-note account is a hypothesis without discriminating support.
- The better-posed version is "a stale inventory frame from a period when the group was developed", not "a planted number steers decisions".
- Ref D's elevation of the "planted number" into the paper's claim is not warranted by the record.

### 3.6 The six above-bound financing starts and G12 d249

The manuscript reports that among 48 above-bound menus offering more than bankruptcy, agents "start financing in six". It does not say who started financing or what their text says.

| Episode | Model | Received call | Note / content / reasoning |
|---|---|---|---|
| G7 d286 | Grok | mortgage Mediterranean | Note concerns an unrelated Atlantic auction. Content is a JSON `declare_bankruptcy` call stating $1,291 < $1,400. |
| G9 d194 | Grok | mortgage Mediterranean (four mortgages over the episode) | Note: "Declare bankruptcy now rather than hand p2 mortgaged deeds first." Content declares. Later notes adopt a strategy of encumbering deeds so "p2 pays the bank 10%". |
| G17 d396 | Grok | sell three light-blue houses | Note calls the sale "forced and insufficient", which is false: declaration is legal. Content declares. |
| G18 d344 | Gemini | mortgage Virginia | Consistent. It mortgages so the creditor must "pay the 10% mortgage transfer fee". |
| G19 d224 | Grok | mortgage Kentucky | Note: "Must liquidate both reds before bankruptcy is valid." That is not a rule of this engine. Content declares twice. |
| G20 d273 | Grok | sell the Illinois house | Note: "Selling first only hands the bank the house at half price … Declare now." Content declares. |

**Findings:**
- None of the six texts claims payment is feasible. Five are Grok calls whose content names `declare_bankruptcy`. In two (G9 d194, G20 d273), the applied note *inside the financing call* says to declare.
- G12 d249 is stronger than the paper says. The applied note inside Grok's `declare_bankruptcy` call reads: "So bankruptcy is wrong. I must not declare … The sell_houses call was the correct action."
- Across all 188 first decisions, the content names a different action from the received call in seven cases, all Grok: the five above-bound starts, G12 d249, and G1 d471, which is benign.
- The paper correctly declines to claim that required tool choice *causes* Grok's conflicts. But G12 d249's note ("I already made the call. The function results aren't back") is strong circumstantial evidence of the mechanism. A paper titled "Stated Plans and Economic Actions" must analyse these divergences, not leave them in one clause. Ref B is right.

### 3.7 Unstated rule variants change what a "false infeasibility" stop means

I verified in code (`_handle_bankruptcy`, `_trade_interest_cost`):
- Bankruptcy to a player transfers deeds with buildings intact and mortgages preserved.
- No interest is charged on inherited mortgaged deeds, whereas trades charge 10% interest.

The Hasbro rules FAQ I fetched states that the new owner of a bankrupt player's mortgaged property must repay or pay 10% "now". The classic rulebook, which I could not text-extract this round, requires buildings to be sold to the bank on bankruptcy to a player. The system prompt states none of these variants: "Your role is not to explain rules or debug the system."

Agents visibly reason about which rules apply:
- G9 d195 Grok: "Standard Monopoly rules say … the new owner must pay 10% interest".
- G19 d224 Grok: "The engine might enforce different rules".
- G18 d344 Gemini acts on the 10% rule.
- G18 d313 Grok, by contrast, reasons correctly that "p1 would inherit built dark blues".

**Implications:**
1. Ref B's "recall misfiring" example (G18 d344) is mostly the opposite. It is accurate recall of a published rule that the engine silently departs from. G19 d224's "must liquidate before bankruptcy" is a genuine false rule.
2. A stop on a payable debt is a feasibility error only if its stated reason is infeasibility, as in both failures' notes. Sol's provider text adds a payoff belief about what bankruptcy transfers. Under undisclosed settlement rules, part of the stop decision is strategic under uncertainty about the rules. Any future false-infeasibility study must disclose the settlement rules, or it confounds a feasibility judgment with a payoff belief.
3. The repository's own `CLAUDE.md` forbids undocumented house rules. The paper documents the variants for readers (§2.1), but agents never saw them.
4. Hotel liquidation during a house shortage is edition-dependent. The current FAQ says a sold hotel is "exchanged for 4 Houses", which matches the engine; older rulebooks allowed selling a group's hotels at once. Ref D's "hotel menu lock" is therefore not simply a bug. The menu/validator asymmetry (§3.1) is the real inconsistency.

### 3.8 The necessity certificate and the middle category

Referee A is logically right: U0 ≥ D does not prove a route without released mortgages, because S is nominal.

Empirically the 53-episode label survives:
- 47 paid without using released collateral, so the observed routes are witnesses.
- G12 d249's audit witness sells pink houses only.
- For the five paid episodes that did use released collateral, I derived no-release routes by hand from the stored entry states, with bank stock checked:

| Episode | No-release route | Why it is realisable |
|---|---|---|
| G3 d228 | Salvage from houses-only groups suffices | Houses only |
| G3 d356 | Salvage from houses-only groups suffices | Houses only |
| G3 d482 | Salvage from non-hotel groups suffices | Light-blue hotel group not needed |
| G3 d461 | Sell 2 red houses, the Boardwalk hotel (bank 6 ≥ 4) and five dark-blue houses: $44 + $750 = $794 ≥ $700 | Bank stock checked |
| G18 d428 | Sell 3 red houses and one orange hotel: $484 + $275 = $759 ≥ $750 | Bank 29 |

These routes are hand-derived from the menu semantics, not engine-validated.

The fix is the caption, not the counts. Say that the middle category is established by observed or derived no-release routes, not by the bound.

### 3.9 Denominators, uncertainty and independence

**Denominators.** Ref B's "16 episodes, 0.2% of the corpus" divides episodes by decisions (16/6,989).

| Comparison | Value |
|---|---|
| Necessity episodes / all financing episodes | 16/188 = 8.5% |
| Necessity episodes / payable debts | 16/131 = 12.2% |
| Liquidation decisions inside the sixteen / all liquidation decisions | 58/338 = 17% |

The small-n point stands; the 0.2% figure is a units error.

**Fisher's test.**
- 2/16 against 1/115 gives two-sided p = 0.039, so Ref B's arithmetic is right.
- Reclassifying G12 d249 as a call artifact gives 2/16 against 0/115, p = 0.014.
- Neither p-value is interpretable. The partition was defined after the two failures were known (Ref B says it suggested the cut). Episodes cluster within agents and games. Three failures cannot support a test.
- The paper should report the descriptive concentration without a p-value.

**Resampling.**
- The intact-block ranges are cluster-bootstrap percentile intervals over five clusters. Ref B is right about the name, and five-cluster bootstraps are known to undercover.
- The paper's disclaimers are honest, but the 95% ranges add almost nothing beyond the five block values and leave-one-out ranges.
- Ref D's call for "mixed-effects with state random effect" would not rescue this. Sixteen states, three failures and five seed blocks cannot estimate variance components.

**Independence.**
- Twenty games are five seeds times four rotations of one roster, with shared trajectories.
- Exposure differs by model: Opus faces 58 financing episodes, Sol 42, Grok 38 and Gemini 50.
- Per-model rates are therefore exposure-confounded descriptions.

---

## 4. Bargaining and conduct

My 12 November recomputation reproduced every bargaining cell, and the pinned data are unchanged.

**New and confirmed issues:**
- **"The cash-bid difference is negative only when pooled" (Introduction) is false.** Grok's within-recipient gap is −0.2 (19/24 vs 27/34). This sentence descends from my own OFR-02 wording ("holds only when pooled"), even though my evidence listed the −0.2. The error is mine.
- **The small-cell rule is inconsistent.** Table 4 suppresses gaps for cells under five, while Figure 2 plots block gaps from neither-cells of 4 and 3. The caption discloses this, but the rule should be uniform.
- **The "all seven cells" asking-price statement includes completing-buyer cells with a single ask.** It is disclosed ("1–17") but weak.
- **What the half amounts to.** After composition correction (30.5 → 16.7, with one block at −23.5), the bargaining half contains a census, a composition-sensitive association, an LLM-coded 61/74 reason count, and eight contextual incidents.
  - None of these is wrong.
  - None connects to the financing result except through the shared word "statement".
  - Referee A is right that the semantic codebook is under-specified.
  - Both referees are right that this half dilutes the paper.
- **Grok's channel conflicts appear on both sides of bargaining.** They affect 13 of the 15 Grok-authored accepted neither-completing swaps and 7 of Grok's 28 acceptances. The opening-swap contrast is partly an interface phenomenon. The paper says so in its own words.

The eight incidents are carefully sourced; I re-traced them on 12 November. Their scientific role is illustration. Keeping all eight in the main text is a human decision about emphasis that conflicts with focus.

---

## 5. Novelty and literature

Full sources, versions and access depth are in `literature_matrix.md`. My reading:

- **Action reachability is established.**
  - ACPBench (AAAI 2025) defines Action Reachability as whether an action "can be made applicable from the given state through some sequence of actions". It is single-turn question answering over natural-language renderings of PDDL, not an acting agent.
  - ACPBench Hard (ICLR 2026, per arXiv comments) adds generative versions with validation algorithms.
  - The present paper does not claim that construct as new and must not in any future framing.
- **False impossibility is established.**
  - The o1 PlanBench evaluation (arXiv 2409.13373 v1) reports that "11.5% of instances are incorrectly claimed to be impossible" on Randomized Mystery Blocksworld (0% on Blocksworld), alongside 100 deliberately unsolvable instances.
  - Occurrence of false infeasibility is not novel. What may be distinctive is narrower: false infeasibility about one's *own* resources, in naturally reached multi-agent states, with a sound arithmetic certificate, legal witnesses, and an irreversible voluntary stop. I make no novelty claim from absence.
- **Interactive versus whole-plan generation.** AutoPlanBench (Stein, Fišer, Hoffmann, Koller; arXiv 2311.09830) compares ReAct-style interactive action choice with plan generation and notes difficulty with dead-end domains.
- **Menu sensitivity.** "The Menu Is an Execution Prior" (arXiv 2609.09395, "Accepted to EMNLP 2026 Main") constructs pre-execution tool menus with producer-before-consumer ordering. I could not confirm the claimed same-candidate order ablation from the abstract. Its menus are fixed before execution and do not model runtime unlocking or giving up.
- **Verifiers.** LLM-Modulo (ICML 2024 position paper) establishes verifier-in-the-loop framing. A solver supplying routes would be an assisted condition, not a contribution.
- **Recitation.** Reasoning or Reciting (NAACL 2024) establishes default-versus-counterfactual comparisons. The present paper's release rule is the standard one, so it cannot separate recall from reasoning. It already says so.
- **Statement–action gaps.**
  - "Unpropagated refutation" (ICML 2026 atomic-chess work, 200 prior-conflicting positions, rule stated in the system prompt) names an agent submitting a move it has just refuted.
  - "Do LLM Agents Execute the Plans They Declare?" (arXiv 2609.38108, preprint) studies declared-plan adherence.
  - Grok's within-call note/function contradictions (§3.6) are an instance of the same family. They are not a new phenomenon.
- **Memory and branching.**
  - ACL 2026 "How Memory Management Impacts LLM Agents" documents error propagation from stored experiences.
  - MafiaScope (arXiv 2607.10645 v3) offers counterfactual replay branches from saved states. I could not verify the "672-game" figure.
  - Any future carried-note or replay study must cite both.

---

## 6. Economic comparators

| Comparator | What I verified | Bearing on this paper |
|---|---|---|
| AgentMonopoly (arXiv 2610.29330 v2 and code) | Paper: 140 games, 4 series, 8 open-weight local models, 5 seeds, temperature 0. Repo README table: 120 games, a disagreement inside their own materials. Engine: immediate elimination at negative cash, no sell-building action. `agent.py` loads `rules.json` into the system prompt; the rules include "You CANNOT mortgage a property if ANY property in its color group has houses". The prompt forbids public messages contradicting the action. | Referees are right that it has no debt-rescue phase. Ref D is right that its agents receive rules, including the release rule. |
| FinBoardBench (arXiv 2605.27896 v1) | Monopoly has a **fund-raising manager** with mortgage, sell-building and bankruptcy actions, the last described as "when recovery is impossible". DeepSeek V4 Pro judges trade quality, with no human validation reported. Up to five action-execution failures before a forced fallback. Thinking-mode table sums to about 4/36 against 10/36 wins (cells garbled in extraction). | "Liquidation is where you're ahead" is true against AgentMonopoly but **not** against FinBoardBench: multi-step fund-raising is not unique. What may differ is MonopolyBench's *voluntary* declaration on payable debts. Without it, premature stopping cannot be observed. |
| Vending-Bench (arXiv 2502.15840 v1) | 9 models plus one human (5 hours, day 67); 5 runs per configuration; 2,000-message cap; capital/fee/memory variation; larger memory performed worse; r = 0.167 between sales stopping and memory filling. | Ref D's "10 models" is wrong (9 plus human). The rest is right. |
| Vending-Bench 2 (Andon page) | One year; ~$63k reference built from assumptions ($206/day × 302 days ≈ $62.2k); "±" not defined as SE. Lists Gemini 4 Argon (#5), GPT-6 Sol (#4) and GPT-6.1 Sol (#6). Grok 4.7 and Opus 5.5 are not visible in the top 10. | Ref D's "external capability axis available today" is at most half available. Epoch's review rates VB2 "Flawed" (unequal usable context, exploitable environment; exploits not seen in the two official traces inspected). |
| Arena communication study (arXiv 2608.14825 v3) | 2,583 emails, 20 runs, 13 models. Mixed-effects logistic regressions and run-level cluster bootstrap. Judges from three families. "Hand-labelled set" is 50 emails labelled by one author who also wrote the codebook. Prompt check is term-level on 52/58 readable payloads. No venue on arXiv. | Both referees describe it accurately in kind. Ref D's "NeurIPS 2026" is unverified. Its own validation is weaker than "hand-labeled set" implies. |
| AutoVend (arXiv 2610.36980 v2) | 5 agents, 20 sites, 180 days, 3 runs per LLM in one frozen world; newsvendor baseline. Only GPT-6.1 Sol beats it, in all three runs. Conditional pricing regret holds site, assortment and inventory fixed. | Referee A's description is accurate. The lesson (a reference policy) applies, but for the sixteen the never-quit reference's outcome is derivable from code. |

---

## 7. What the proposed interventions identify

Details and costs are in `recommendations.md`. In brief:

- **Replay of saved first-decision requests (Ref B, "$40").**
  - Arithmetic: historical mean cost per priced attempt was Opus $0.029, Sol $0.009, Gemini $0.011 and Grok $0.033. 480 calls per model gives about $39. That is a historical figure, not a quote.
  - Estimand: P(action at the first menu | that exact saved context), under today's provider version. This is the right estimand for stop decisions.
  - It is **not** "every model on identical states". Each saved request contains one model's own first-person notes and history. Opus's standard requests were refused 100% after G4, so its arm must use the recovery prompt, a different condition. Identifiers may now route to different weights.
- **Notes stripped / planted reserve.** Estimand: the within-state effect of the carried history on first-menu declaration. A planted number is identifiable only if it differs from the true listed-mortgage value. The historical reuse is uninformative because they coincide.
- **Rule stated, values supplied.** These target different errors. Values are already almost perfect in the sixteen texts, so a values arm tests a hypothesis the data already weaken. A rule arm must also state the bankruptcy-settlement rules, or it confounds feasibility with payoff beliefs (§3.7).
- **Counterfactual rule.** This changes the engine, creates a new benchmark version, and must be stated to agents (the Wu et al. paradigm). It is the only design here that separates recall from rule-following.
- **Reactive policies and verifier.** For houses-only states, both outcomes follow from code. Running them adds engine confirmation and certifies hotel/bank-stock states, nothing more. The informative reference is a menu-bounded *stopping* rule, which reproduces both failures by construction.
- **Minimum-restoration-cost "regret" (Ref D).** It assumes:
  - the agent intends to rebuild;
  - bank stock will allow rebuilding;
  - no time value, foregone rent or dice exposure;
  - group identity and position have no strategic value;
  - the redemption premium is exactly 10%, whereas the engine's float ceiling adds $1 on five principals;
  - surplus cash raised beyond D is not a loss.

  It is a chosen local objective, not an optimum of the game. Calling it "regret" reintroduces the value judgement the paper rightly avoids. It is useful only if labelled as "excess liquidation under objective X".
- **Validation games handing liquidation to a solver.** Payable-state stops were 3/131 here, so 20 games would yield almost no events. The estimand is also confounded by game dynamics.

---

## 8. Agreements, disagreements and reviewer contradictions

**I agree with:**
- **Referee A:**
  - modest insight;
  - the 9/0/2 + 4/1/0 channel table;
  - the dependency-recognition column;
  - the G20 d291 accounting error;
  - one-way necessity logic;
  - "ten actions ≠ ten planning decisions";
  - "negative only when pooled" is false;
  - the codebook gap;
  - settlement selection;
  - the abstract denominator ("connects all 920 … and 188 … to … prospective statements" suggests statements were coded across both populations; they were examined for 16 and 74).
- **Ref B:**
  - the joint tool call;
  - fallback 16/16 for these states;
  - both failure channels;
  - the six above-bound starts and their content conflicts;
  - "reproducible result" is wrong wording;
  - the inconsistent small-cell rule;
  - references dropped 16 → 12 (Vending-Bench, NegotiationArena, Cattle Trade and three others removed; Hasbro and PlanBench added);
  - artifacts are not in the repository (origin/main is at the 29 October commit; the package is untracked);
  - titles have changed with each round.

**I disagree with:**
- **"The task needs no anticipation" (Ref B).** Routing needs none; stopping needs a feasibility judgment.
- **"Any order reaches U\*" (Ref B).** False in general (§3.1).
- **"Recall misfiring" (Ref B).** G18 d344 is correct recall of a published rule the engine departs from.
- **The planted-number headline (Ref D).** Its own counterexamples and the value coincidence undercut it.
- **"0.2% of the corpus".** A units error.
- **"Cite at least 40 references".** A quota.
- **"Every model faces identical states".** False (§7).
- **"Fix the hotel menu lock".** Edition-dependent.
- **"Liquidation is where you're ahead".** Not against FinBoardBench.
- **Ref C's interface hypothesis as the motivated question.** G17 shows extrapolation beyond the menu for sales but not for mortgage release.
- **Referee A's priority on running a reactive policy for the sixteen.** The code already answers it. A stopping-rule reference is the informative variant.

**Contradictions between reviewers:**

| Point | One reviewer | Other reviewer | My finding |
|---|---|---|---|
| AgentMonopoly game count | 140 (Referee A) | 120 (Ref D) | Paper says 140; repo README table says 120. Both are quoting real sources. |
| Resampling | "Handled candidly" (A) | "Bootstrap under another name, not inference" (B) | Both partly right. |
| Calibration | Calibration needs a run (A) | Result asserted without one (B) | The code supports B for these states. |
| Whether the texts show anticipation | Referee A: "The prospective evidence is real … dismissing all fourteen successes as mere menu following would now be unfair" | Ref B: "The task needs no anticipation" | Both are partly right, about different decisions. Nine texts state the dependency (five explicit, one tentative) or an ordered route (three); payment itself needs no anticipation; stopping does. Ref B's "no fourth draft moves the score" is not a contradiction, because its later rewrite advice assumes new data. |
| What the paper should be about | "Premature termination" as the possible thesis (C) | "Liquidation scored against a computed optimum" (D) | These are different estimands: stop decision versus route cost. The first is supported by the discovery data; the second is not, since route quality is barely observable when D ≈ U\* or when agents stop early once paid. |

---

## 9. Which critiques change my own prior assessment

1. **Dependency recognition versus inclusion (Referee A).** This changes my 12 November "12 explicit" reading to 5 explicit + 1 tentative + 3 ordered + 5 inclusive.
2. **The fallback point (Ref B), confirmed in code.** I previously treated 14/16 as positive evidence of execution through a dependency. I now treat payment success as uninformative about route construction, and the result as being about the stops.
3. **The joint tool call (Ref B), plus my argument-order check.** This withdraws any prediction reading of the notes. It also shows a sentence in the integrated text, which I passed in final review, to be wrong.
4. **"Negative only when pooled."** This is my error, introduced through OFR-02. Separately, my OFR-03 explanation (every leave-one-out sample keeps blocks 1–2) was wrong, as Astra noted.
5. **Unchanged.** Referee A's 5.5/10 tone, Ref B's 4/10 and Ref D's proposals do not change my view that this paper should stay descriptive, and that no new headline should be drafted before new data exist.

---

## 10. Strongest dissent

Against the reviewers, the prior team and the paper alike: **the 14-of-16 payment rate, the "ten-action" G20 case and the "13 statements" count should not be presented as the result.**
- The rate is guaranteed for any non-stopping agent.
- The G20 route is forced.
- The count mixes recognition with inclusion.

The result is three stop decisions on payable debts:
- two inventories that stopped at exactly the menu-bounded total, one of them with a mixed strategic motive;
- one Grok call that contradicts its own note.

Around them is a population of agents who mostly compute the same menu-bounded total and then go further, with near-perfect valuations.

That is worth reporting honestly. It is not worth 21 pages. Neither referee's new thesis (interface-induced false infeasibility; planted-number steering) should be adopted without fresh, authorised data. Both are partly contradicted by the existing records.

---

## 11. What remains scientifically unresolved

- Whether the two stops reflect a stable propensity, or single draws from a broad response distribution. Each state was sampled once.
- Whether the stops are feasibility errors, payoff beliefs under undisclosed settlement rules, or both. Sol's provider text mixes them.
- Whether inclusive totals reflect knowledge of the release rule.
- Whether carried notes matter. No manipulation exists, and the historical numbers are confounded with true values.
- Whether Grok's within-call contradictions are caused by required tool choice. G12 d249 is suggestive; there is no ablation.
- Whether hotel/bank-stock states contain order traps among the 131. Settling this needs search.
- Bargaining: whether any rival-development association survives a change of both proposer and recipient composition. No value reference exists.
- External validity: four configurations, one roster, five seeds, and one provider/harness era with an Opus refusal regime.

---

## 12. What should stay in the present paper (if revised without new data)

**Keep:**
- The 188-episode census and the 62/53/16 partition, with the middle category justified by witnesses.
- All sixteen texts, with **both channels**.
- The two failures, with their U0 identity and both channels.
- G13 as the route-choice example, and G20 d291 annotated.
- The never-quit property stated plainly, with its hotel caveat.
- The joint-generation caveat.
- A paragraph on the six above-bound starts and G12 d249 as Grok call conflicts.
- Disclosure that agents were not told the bankruptcy-settlement rules, which differ from the published ones.
- The bargaining census and composition table.

**Fix:**
- The abstract's denominator.
- "before choosing whether to proceed".
- "reproducible result".
- "negative only when pooled".
- The small-cell rule.
- The Table 2 caption.
- Restore the dropped references, and add the planning and statement-action literature at the depth actually read.

**Move or shorten:** Most bargaining analysis and the incidents to an appendix or a companion paper. This is a human decision.

**Do not add:**
- Any p-value.
- Any "premature termination" or "planted number" thesis.
- Any accuracy score.
- Any claim of human validation.
