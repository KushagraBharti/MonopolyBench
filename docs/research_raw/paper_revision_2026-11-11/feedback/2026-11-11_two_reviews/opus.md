# Opus assessment of the two 2026-11-11 referee reports

Opus 5.5 (xhigh), retry after the earlier `parent_not_active` failure. This is an assessment with simple takeaways. It is not a manuscript rewrite, and the manuscript is unchanged.

## Reading and independence

I read every line of `attached_review.txt` (649 lines) and `inline_review.md` (129 lines).

I read the active paper end to end from source:

- `manuscript.tex`, including the abstract
- `introduction`, `setup`, `bargaining`, `liquidity`, `execution`, `discussion` and `appendix`
- every table they input (`opening_table`, `offer_table`, `strata_table`, `debt_rows`)
- all four quotation files and both printed prompts
- `evidence_map.md`

I also looked at the three included figures (`asking_prices.pdf`, `bargaining_conditions.pdf` and `financial_execution.pdf`). `sections/inheritance.tex` exists but is not `\input`. Its G18 text is inlined in `execution.tex`, and I assessed the active version. All 28 hashes in `manuscript_pin.json` match the files I read. For context I also read the integrated `README.md` and `integration_decisions.md`, plus the folder `README.md`.

I did not open `astra.md`, `sol.md`, `fable_5_2.md`, `synthesis_in_progress.md`, `astra_checks.json`, `astra_check_output.txt` or `check_existing_records.py`. Everything below is my own reading and my own arithmetic.

I consulted no primary literature in this pass and opened none of the URLs in either report. The 26-page PDF linked from the attached review is not in the folder, and I did not read it.

All checks were read-only arithmetic over existing records: `integrated/data/offers.json`, `integrated/data/liquidation_episodes.json`, `qa/` outputs, the saved `decisions.jsonl`, `events.jsonl` and replay reports under `saved_games/railway-research-*`, `contracts/data/board.json`, and arena source at the recorded run commits. I ran no engine, replay, game, model call, provider probe, synthetic state or subagent. My scratch scripts live in the session scratchpad, outside the repo. The definitions are given in the text so anyone can reproduce them.

## Bottom line

Both reports are mostly right about what is wrong, and most of their arithmetic reproduces. The inline review's proposer table, its cluster intervals and its 14-of-16 collateral count all reproduce from the owned ledgers. The attached review's G18, replay and tool-choice concerns are real.

The headline swap/cash split is a genuine, direction-consistent regularity. It is weaker and less interpretable than the title, abstract and conclusion state. The finance section has a sharper result than the one it leads with. Most of the needed fixes are within existing records. The fixes the reviewers consider decisive for a main track (a fresh holdout, matched-state tests, a liquidation baseline) are outside the current no-new-evaluation scope. Both reports' venue scores are opinions, and I do not treat them as findings.

## Ranked issues

1. **The headline contrast depends heavily on who proposed the comparator offers, and an interface setting shapes that composition.** Half of the 72 non-completing opening swaps are Grok-authored, and Grok authored 15 of their 17 acceptances. 13 of those 15 come from opening calls that conflict with Grok's own assistant content. At both run-source commits Grok ran with `tool_choice: "required"` (details below). Removing Grok-authored offers leaves 90/108 versus 24/36, a 16.7-point gap whose game-cluster interval includes zero. The abstract quotes only the 30.5-point version. The split was also identified after inspecting the corpus.

2. **The interpretation does not follow from the population result.** The 61/74 reasons come from a disjoint population. In the headline cells themselves, rejections of proposer-only cash bids mention completion and building as often as rejections of proposer-only swaps. Stated reasons therefore cannot explain why only swaps show elevated rejection. The most natural mechanism in the agents' own notes is post-trade building cash. It is not supported by a crude check. "Strategic attention" is undefined. As a result "Bargaining over a Rival's Next Move" names an interpretation the headline contrast cannot carry.

3. **The finance section leads with its weakest statistic and understates its strongest.** 128/131 is a valid partition, but it is close to a ceiling as a difficulty measure: 67 payments take one action and 62 are payable without any sale. The informative subset is the 16 episodes where unlocked collateral was arithmetically necessary. Agents paid 14 and declared bankruptcy in 2. The stated first-decision arithmetic lines up with the outcome in those episodes. The paper's sentence that actions "do not distinguish those mechanisms" is true of actions. It omits that the recorded text distinguishes stated anticipation from its absence, without revealing cognition.

4. **G18 is misframed.** No Opus text in d421–461 mentions inheritance, the estate or a creditor. Only Opus and Sol remain at that point, so Sol's elimination ends the game. The estate Opus "inherits" is the terminal one, and the paper itself says terminal transfers have no later earning opportunity. The clause "explicitly stated inheritance-related motive" is unsupported. The incident does not belong in a subsection about estates as an acquisition route.

5. **Documentation gaps that matter for reproducibility.**
   - The replay sentence describes only the weaker of two stored modes.
   - The tool-choice setting is omitted even though it bears on issue 1.
   - The seed list, run map and entry point are absent from the PDF.
   - The paper uses "inherited" without saying which procedure produced what.

6. **Scope and presentation.**
   - Eight incidents are given equal weight.
   - Figure 2A's labels sit next to the wrong series.
   - "Absent for pure cash bids" asserts a null the data cannot support.
   - Revision-speak appears in the paper body.
   - The main text runs about 18 pages.
   - The byline is a placeholder.

   None of these changes the science, but together they make it look weaker.

7. **The secondary results are correctly hedged but over-allocated.**
   - The same-deed asks give 4/1/1.
   - The 14 resistance-to-settlement histories are selected on eventual settlement, and the paper does not state that they pair the first earlier refusal or counter.
   - The exposure summaries compare medians only.

   They can stay as context but should not be headline claims.

## Proposer composition and post-hoc selection

Opening swaps, rejected/received, by proposer, from `offers.json` with the integration's form definition:

| Proposer | Completes proposer only | Completes neither | Gap |
|---|---|---|---|
| Sol | 44/50 | 9/11 | +6.2 |
| Opus | 42/50 | 15/23 | +18.8 |
| Grok | 5/8 | 13/36 | +26.4 |
| Gemini | 4/8 | 0/2 | n too small |
| All | 95/116 | 37/72 | +30.5 |

This matches the inline review exactly.

- **Composition.** Grok authored 36 of the 72 comparator swaps and 15 of their 17 acceptances. 29 of the 36 Grok-authored comparator swaps, and 13 of its 15 accepted ones, come from opening calls whose assistant content names a different action. The 15 accepted Grok-authored comparator swaps transfer a net $4,020 of board list value to recipients. That is a narrower population than the inline review's $4,700 figure, which covers all accepted openings.
- **Standardization.** Weighting the within-proposer gaps by cell size gives about 18 points (18.1 and 18.4 under two weightings). Excluding Grok-authored offers gives 90/108 versus 24/36, +16.7 points.
- **Game-cluster bootstrap.** I resampled 20 games, 5,000 replicates, 95% percentile intervals:
  - all swaps: +30.5 [+13.8, +47.9]
  - cash bids: −5.0 [−22.9, +10.0]
  - swaps without Grok authors: +16.7 [−1.6, +38.3]

  These match the inline review's intervals to within rounding. Games share seeds within blocks, so even these intervals are optimistic.
- **Direction.** The sign is positive in every proposer stratum and in seven of the nine author–recipient pairs where both cells are observed. The one reversal (Sol→Opus) has a single comparator offer. The paper's existing sensitivity (excluding conflict openings, 93/112 versus 26/43) keeps the direction in four of five seed blocks. The direction is consistent. The magnitude is not, and a single headline percentage hides that.
- **Tool choice.** `tool_choice_for_model` returns `"required"` for `x-ai/grok-4.7` and `"auto"` otherwise. That holds at both recorded run-source commits, 42f85183 and d6808534. The docstring says it was meant to make Grok "invoke a tool, not describe one." I confirmed this from source at those commits, not from per-request records, because `prompt_payload_raw` does not store `tool_choice`.
  - G19 d135 shows what this setting can produce. The applied note says "Abort this trade. Do not send it." The content names `end_turn`, but a trade went out.
  - I cannot establish that forced tool choice caused the 139 conflicts. It is a plausible mechanism and must be disclosed, because those offers supply most of the comparator's acceptances.
- **Forking paths.** The paper discloses that the split emerged during cross-review. The path ran from the old author-only versus recipient-only comparison, to a deed-request comparator, to the form split, to the conflict exclusion. Each step was reasonable, but none was specified before the corpus was inspected. Recomputing the split, as Astra did, validates the arithmetic, not the regularity.
- **Other cells.** The table also omits cells that support the thesis. Opening swaps completing both parties are rejected 34/48. Non-swap offers that would complete only the recipient's group are rejected 29/45. Base rejection rates for openings are high almost everywhere, driven by Gemini and Grok as recipients. The comparator's 51% is the outlier, and its low rate is largely Grok-authored.

My judgment is to keep the split as an exploratory, direction-consistent regularity. Show all three composition versions side by side with descriptive cluster intervals, and stop calling the cash-bid contrast "absent."

## The semantic-code population mismatch

The attached review is correct. The 61/74 codes cover all rejections of offers completing the recipient's group: 27/38 recipient-only and 34/36 both-party. The headline compares proposer-only with neither. These populations are disjoint. The bargaining section's transition ("The agents' stated reasons connect that pattern to economic consequences") claims a link the codes cannot provide. The discussion section admits as much, so the paper contradicts itself.

I ran one crude check on the headline cells themselves, using the recipient's public message plus applied note. It is a regex, a single analyst's one pass, and not a semantic coding.

| Cell (rejections) | Completion or blocking terms | Building terms |
|---|---|---|
| Swap, proposer-only | 93/95 | 83/95 |
| Swap, neither | 30/37 | 21/37 |
| Cash bid, proposer-only | 42/42 | 35/42 |
| Cash bid, neither | 57/67 | 26/67 |

When recipients reject a proposer-only offer, they cite the completion and the rival's building in nearly every case, whatever the offer form. The form split lies in how often they reject, not in what they say when they do. This makes the attached review's point stronger. The reasons show expressed concern under both forms, and they cannot be the explanation of the swap/cash difference.

I also checked two alternative mechanisms within the headline cells:

- **Immediate own benefit, crudely measured by board list value.** Proposer-only swaps offer recipients more net list value than comparator swaps (median +$170 versus +$80; 89% versus 69% non-negative). Cash bids are similar across cells (+$65 versus +$70). A "reject low-value offers" rule therefore does not explain the swap gap in list-value terms. List value omits complementarity and blocking value, and blocking value is the construct at issue, so this only narrows the alternative explanation.
- **Post-trade building cash**, which G2 and G15 notes suggest. Proposer-only cash bids leave the proposer slightly more house capacity than swaps do (median 4.96 versus 4.04 houses). Cash-bid rejection falls as proposer cash rises (17/20 below $300, 17/31 at $300–599, 8/19 at $600 or more). The mechanism is not supported.

These two checks are themselves post hoc slices. I report them to show the mechanism is open, not to propose adding them as findings.

## Necessary collateral: 14 of 16 versus 19 uses

I recomputed the own-asset bound at each first debt menu. It is cash, plus half the building cost for every level, plus the mortgage value of every unmortgaged deed. My figure matches the stored `upper_bound` in all 188 episodes. Results:

- 56 eliminations exceed the bound. Four do not: G7 Opus (menu-restricted), G12 Sol, G12 Grok and G17 Gemini.
- 67 of 128 payments take one action.
- 62 of 128 are payable from cash plus first-menu mortgages, with no sale.
- 114 of 128 are payable from cash, all building salvage and first-menu mortgages.
- The median debt among paid episodes is 0.36 of the bound.

The inline review's descriptive claims reproduce.

**Necessary-unlock set.** Necessity means that cash plus all salvage plus first-menu mortgages falls short of the debt, while the full bound covers it. This holds in 16 episodes: 14 paid and 2 declared (G12 Sol d190, G17 Gemini d234). By system, Gemini paid 5 of 6, Sol 2 of 3, Opus 5 of 5 and Grok 2 of 2.

**The 19 uses.** The paper's 19 unlocked-collateral payments split into 14 where the unlock was necessary and 5 where it was optional. The optional ones are four G3 Gemini episodes (d228, d356, d461, d482) and G18 Sol d428. The 19 is a legitimate count of repeated behavior. The 14/16 contrast is the one that connects successes to the two failures.

**First-decision text in the 14 paid necessary episodes.** In my single reading, 13 state the unlocked mortgages before acting. The text is the applied note for Sol, Gemini and Grok, and provider-returned reasoning for Opus under recovery. G20 d291 (Opus) raises it as an open check ("checking whether mortgaging the pink lots themselves after clearing the houses could close the gap"). G5 d263 Gemini reasoning makes the same omission as the failures, then corrects itself within the same response.

- The inline review's "all 14" is slightly generous. "13 explicit, 1 tentative" is what I can support.
- Both failures declare at the first decision. Each sum includes only the listed mortgages.

**What this supports.** In the episodes where it matters, the stated feasibility arithmetic and the agent's choice agree. Stated inclusion of unlocked collateral goes with sustained liquidation and payment. Stated omission goes with an immediate declaration. On the attached review's ladder this is expressed concern, accurate assessment and action consistency, at the episode level.

**What it does not support.** The text does not show internal computation. It does not show that a reactive policy would fail. And n is 16 with 2 failures, found post hoc by a reviewer.

The failure mode is also clearer than "a specific planning boundary." Both failures are premature voluntary stops based on an incomplete feasibility sum, not errors partway through a sequence. A policy that never declares while any financing action is listed would not make this error. Whether such a policy would reach payment under the even-sale and bank-house constraints is unexecuted. The paper must not claim it, and the inline review's "pays 131 of 131" has no score until someone runs it.

## G18 motive

The attached review is right, and the problem is larger than it says.

- **What the texts say.** I searched every Opus text field in G18 d421–461 for inherit, estate, bankrupt, creditor, bust and elimin. The fields were public message, note, assistant content and provider reasoning. The only hits are "bankrupt" in the sense of survival:
  - d438: "would likely go bankrupt soon anyway... giving them $450 mainly just extends the game"
  - d446: "push p1 toward bankruptcy"
  - d455 and d457: "funding them just delays the inevitable"

  The d442 withdrawal explanation, which the paper paraphrases, cites prolonging a nearly bankrupt rival and development cost. No span mentions receiving the estate.
- **The game state.** At d421, Gemini and Grok are already bankrupt. With only Opus and Sol left, Sol's bankruptcy ends the game. The motive the texts state is to deny the last opponent survival cash, which is about winning. Opus's eventual "inheritance" is the terminal estate. `execution.tex` itself says terminal transfers have no subsequent earning opportunity.
- **Earlier text.** At d431, the decision where Opus publicly renews "My Pacific offer still stands," its returned content already says it "didn't raise my Pacific offer, since extra cash now would only help p1 last longer." The survival-denial concern was in Opus's returned text before the withdrawal.

**Fix.** Delete "with an explicitly stated inheritance-related motive." Describe the withdrawal as accompanied by a stated objection to financing a nearly bankrupt last opponent. Note that the game is two-player at that point, and move the incident out of the estate subsection or flag it as terminal. Keep the attached review's point that Opus redeems its greens before bidding again.

G13 is the paper's real inheritance case. The seller's public message says "gpt inherits the yellows in bankruptcy," and the buyer's returned text repeats it. The abstract's "anticipated inheritance" should rest on G13, not G18.

## Replay wording and interface configuration

**Replay.** All 20 stored `replay_report.json` files show `status`, `state_status` and `artifact_status` as passed, with equal canonical hashes. There are two modes:

- **Artifact mode** applies `canonical_event_lines` over the full event stream. `excluded_event_types` is empty, and the compared count equals the total (3,529 events for G1).
- **State mode** drops `LLM_DECISION_REQUESTED`, `LLM_DECISION_RESPONSE`, `LLM_PRIVATE_THOUGHT` and `LLM_PUBLIC_MESSAGE`, and renumbers `event_id`, `seq` and `ts_ms` (1,649 compared events for G1).

The full-stream comparison can match because the runs use a synthetic clock (`start_ts_ms` 0, `ts_step_ms` 250).

The earlier draft described artifact mode, and the current appendix sentence describes state mode only. Both are true. The current wording undersells the evidence by implying equality required removing identifiers and timing. The fix is to name both modes and cite these report fields. No rerun is needed. These reports date from 25–26 October and are inherited executions, not new ones.

**Interface configuration.** Restore a compact table covering the following:

- tool choice by system (Grok `required`, the others `auto`)
- the corrective retry
- action-only refusal recovery
- the deterministic fallback policy (`finance_before_bankruptcy_v2`)
- the named fallback model that was never invoked

Figure 2's caption says Sol, Gemini and Grok have "standard response policy throughout." That should say what is actually shared: no action-only recovery. Grok's interface differs.

**Refusal category.** The inline review says one direct API call would settle the refusal category. That call would be a provider probe, which this scope forbids. It would also need a direct vendor client, which `CLAUDE.md` forbids. I inspected one saved refused attempt. It has `finish_reason: content_filter`, `native_finish_reason: refusal` and the ToS refusal text, and no `stop_details`. The current "unconfirmed" wording is defensible. It could be tightened to say that the message names the ToS restriction and the gateway response exposes no structured category.

## Where the reports disagree, and my judgment

| Topic | Attached review | Inline review | My judgment |
|---|---|---|---|
| Headline split | Credible, informative, needs the immediate-benefit alternative addressed | Forking path, composition-contaminated, half its size by proposer | Inline arithmetic reproduces. The direction holds, the magnitude does not. Both are partly right, and the inline review is closer on magnitude. |
| 128/131 | Valid denominator, not circular | Ceiling effect | Both are true. Keep it as a partition. It is not difficulty evidence. |
| Unlocked collateral | Asks when it was necessary | Answers 14/16, says the notes distinguish mechanisms | 14/16 reproduces. The notes show stated anticipation in 13 plus 1 tentative, not mechanism. |
| Liquidation baseline | Recommends one and warns against assuming the outcome | Asserts a loop "pays 131 of 131" | The attached review's stance is correct. The inline review's claim is an unexecuted prediction with no score. Either way it is forbidden in this scope. |
| Inference | Warns that big regressions do not fix endogeneity | Runs clustered bootstraps and logits | Report simple descriptive game-cluster intervals and stratified tables. Skip causal models. |
| G18, replay, tool choice | Raises all three | Silent | Raised correctly. G18 is worse than stated. Replay is resolvable from stored reports. |
| Refusal | Not raised | "Unconfirmed for no reason" | Current wording is defensible. The proposed remedy is out of scope and against policy. |
| Authorship | Not raised | Calls the placeholder byline fatal | It must be resolved before submission. It does not show that no human contributed. |
| Theory | Not raised | JMS cited, not used | Fair but minor. G13 fits an identity-dependent externality, and at most one stated hypothesis belongs in the discussion. |
| Next step | Matched-state tests, local baseline, prospective confirmation | $140 holdout, rollouts, 100 games | Both are good science and both are outside current scope. Cost estimates are not facts. |
| Scores and venues | 5/10, 3/6 | 4/10, venue table | Opinions. Not used here. |

## Checked versus inherited evidence

Checked by me in this pass, read-only:

- The four headline cells, the both-party (34/48) and recipient-only (29/45) cells, and the proposer table.
- Grok's share of comparator swaps and of their acceptances, and the overlap with conflict openings. The conflict-opening list itself came from Astra's earlier script output.
- Within-proposer and within-pair directions, plus the game-cluster intervals.
- Tool choice from source at both run commits.
- The recomputed own-asset bound (188/188 match), the 56/4 split of eliminations, 67/128, 62/128, 114/128 and the median debt-to-bound ratio of 0.36.
- The 16-episode necessary set, the 19 = 14 + 5 split, and first-decision texts in all 16.
- Player status in G18 and an Opus text search over d421–461.
- All 20 stored replay reports and their mode definitions.
- One saved refusal record.
- Figure 2A label placement.
- The pairing rule in `check_offer_forms.py` (the first earlier refusal or counter).
- The crude keyword, list-value and building-cash slices.

Inherited and not checked by me:

- The 61/74 semantic codes and their LLM-reader agreement.
- The three historical payment witnesses and the G7 menu search. I checked only that the bound arithmetic places these cases within the bound.
- The 66 construction defaults and the 61 reorderable Opus allocations.
- The full count of 139 Grok channel conflicts.
- The Opus refusal count of 1,604.
- Rental exposure and first-estate lead counts, the price ledger, the cost and token fields.
- That the stored replay executions themselves were correct.

The evidence map in the paper should label each claim the same way. In the main text, "inherited" should be replaced by the name of the procedure and the stored report.

## What stays

- The complete 920-response census and the full 188-episode partition. These are the paper's most defensible assets.
- The swap/cash split, kept as an exploratory regularity with all composition versions displayed. It should not be the title.
- The 16-episode necessary-collateral contrast, with the 19 uses as context and G20's $14 sequence as its worked example. That example should note the offsetting $25 error and separate execution length from dependency depth.
- G15, the clearest refusal of one's own monopoly, with checkable cash figures. G13, the genuine inheritance pitch with selectively presented collateral. G19, the correction without rejection. The rest move to the appendix.
- The response-condition disclosures, which are a finding in their own right. Provider policy and harness settings (refusal recovery, forced tool choice) change the population of offers that other agents face. In a multi-agent benchmark the measured object is the interacting configured systems, not the four underlying models.
- The separation of terminal from nonterminal estates, which G18 should also follow.

## Remedies inside existing records, and what is forbidden

Allowed now. These are text, table and figure edits, plus read-only arithmetic on existing records.

1. Report the full form × completion table and the proposer rows. Put three composition versions side by side, with descriptive game-cluster intervals and stated caveats. Replace "absent" with "no corresponding increase."
2. Rewrite the 61/74 transition along the lines the attached review suggests. State plainly that reasons do not explain the form split.
3. Define strategic attention using the attached review's five levels, and tag each result with the level it reaches.
4. Lead the finance section with the 16-episode contrast. Report the difficulty descriptors (67, 62, 114, 0.36). Describe the two failures as first-decision declarations based on an incomplete feasibility sum.
5. Correct G18 as described above.
6. Name both replay modes, and add the configuration table with tool choice.
7. Restore the seed list, the G1–G20 run map, the source commits and an entry-point command.
8. State the first-resistance pairing rule. Fix Figure 2A's labels. Show unique games and threads, or drop the n=1 cell in Figure 1.
9. Cut the main-text incidents to about three, and delete the revision-speak ("This revision uses saved records," "They cannot supply a retrospective explanation...").
10. Rescope the title and abstract to match items 1–4.

Forbidden in this scope. List these as future work, not as results.

- A reactive or greedy liquidation policy run on stored debt states (engine execution).
- Matched-state tests of rival opportunity (synthetic states and model calls).
- A fresh holdout or preregistered replication, and scaling to 100 games.
- Scripted rollouts or baseline-only games to provide a value reference.
- A provider probe for the refusal category.
- Re-running replay. This is also unnecessary, because the stored reports suffice.

A decision for the user: human annotation of the 74 rejections and the 16 notes. It executes nothing, but it is new measurement, and the 2026-10-29 scope decision excluded new controlled evaluations of any kind. If it is not done, the paper should keep saying the codes are LLM-read and unvalidated.

## Strongest dissent

The swap/cash split should not be the paper's headline or title. This dissents from the current manuscript, from Fable's cross-review thesis as I understand it from my memory notes, and in part from the attached review, which treats the split as the credible result to build on.

The case against it, in the data:

- It was found post hoc.
- Its magnitude falls by roughly half once proposer composition is accounted for, and that interval includes zero.
- Most of its comparator acceptances come from offers that Grok's own content disowned, under a forced-tool-choice setting the paper does not disclose.
- The reasons recipients give are the same under both offer forms.
- The most natural mechanism, the rival's post-trade building cash, does not hold up.

"Bargaining over a Rival's Next Move" therefore names an interpretation that the population result cannot carry. Two things hold up without new evaluations. One is the expressed concern found in the census and incidents. The other is the 16-episode contrast, where stated assessments of how one's own actions change the future menu match what the agent then did.

My recommendation is to make the paper an observational account of when expressed assessments of changing options, one's own and a rival's, correspond to actions. Finance would anchor it, and the bargaining census would be described as expressed concern with a form-dependent, composition-sensitive rejection pattern.

The finance contrast has weaknesses of its own. It is also small (16 episodes, 2 failures) and was also surfaced by a reviewer. Its main advantage is that necessity is fixed by the rules' arithmetic rather than by an analyst's choice of comparator.

Under the no-new-evaluation scope, the achievable gain is correctness and honest scoping, not a stronger claim. The paper should be written for that.

## Summary

- **What reproduces.** The inline review's proposer table, cluster intervals, ceiling descriptors and 14/16 necessary-collateral count all reproduce from existing records. The attached review's G18, replay and tool-choice concerns are real.
- **The headline.** The swap/cash split is direction-consistent but composition-sensitive (30.5 points overall, 16.7 without Grok-authored offers, with that interval including zero). It is post hoc and unexplained, because stated reasons are the same across offer forms. Keep it as exploratory, not as the title.
- **Finance.** 128/131 is a valid partition but not difficulty evidence. The informative result is 14 of 16 necessary-unlock episodes paid. Stated first-decision arithmetic lines up with the outcome: 13 explicit and 1 tentative inclusions, and 2 omissions, both followed by immediate declarations. This is evidence about stated assessment and action, not about cognition.
- **G18.** The inheritance motive is unsupported. The game is two-player and the estate is terminal. The stated motive is denying survival cash to the last opponent.
- **Replay.** Both stored modes passed in all 20 games. Name them both. Also disclose `tool_choice: "required"` for Grok.
- **What is out of scope.** Every remedy needed for a stronger claim (baseline, matched states, holdout) is a forbidden evaluation in this scope. Everything else is an edit within existing records.
