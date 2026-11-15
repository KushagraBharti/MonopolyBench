# Independent whole-paper assessment — Astra

14 November 2026. Written before reading Sol, Opus or Fable's assessments. This reviews both attachments, all four inline pieces, the complete final November 12 manuscript, its active tables and appendices, and the earlier integration decisions. No new evaluation was run. Evidence checked in this pass is distinguished below from retained results.

## Judgment

The reviewers are right about the central scientific problem: the paper does not yet establish a new explanation of agent behavior, a calibrated capability measurement, or an effective intervention. Repeatedly finding a more interesting subset of the same twenty games cannot supply those missing results. Our previous rounds improved factual accuracy and presentation; we too readily treated that improvement as resolution of the contribution problem.

They are wrong to equate this with an absence of evidence, to treat every success as trivial and every failure as model incompetence, or to treat the latest proposed experiment as an already established discovery. The corpus contains useful observations of resource assessment, conditional knowledge, bargaining and execution. The question is what those observations warrant. A controlled financing study is a plausible next project, not a result already earned by this paper and not automatically novel.

The most defensible current observation is specific: **agents often identify collateral that a sale will release, but recognizing that dependency, calculating a complete budget, issuing a matching action and reaching payment are separable accomplishments.** The records contain positive and negative examples of each separation. This is more informative than either “14 of 16 proves planning” or “a reactive policy could pay, therefore the text tells us nothing.” It remains an observational finding in a familiar, strongly scaffolded task.

I would preserve the present paper as a coherent discovery study and stop changing its central claim after each review. Under the standing no-new-evaluations rule, we can improve its measurement and release it honestly; we cannot promise a main-conference contribution through another rewrite. If that rule changes later, the right investment is a small, discriminating study after reference-policy and task calibration, not an automatic hundred-game expansion.

## 1. What the finance record actually establishes

I independently joined the 188 retained episode entries to original decision records and reconstructed their initial resource sums from holdings, menus and board values. All upper bounds match. There are 128 payments and 60 eliminations. The sixteen necessary-collateral entries and fourteen payments reproduce. The three retained legal payment witnesses, the G7 reachability result and full replay reports were not rerun.

The useful denominators are sixteen of 188 financing episodes (8.5%), or sixteen of 131 demonstrated-payable episodes (12.2%). The referee's 0.2% divides episodes by all game decisions. That mixes units and says little about the importance of a terminal financial decision. Small sample size is a real limitation; this particular percentage is not a good argument for it.

The sixteen include thirteen successful initial responses that identify additional collateral or a budget containing it, one tentative response, and two declarations following incomplete totals. I read both the applied private note and the provider reasoning field, plus assistant content where available, for every one. I agree with the broad 13 + 1 + 2 recognition reading. I do not agree that it establishes thirteen accurate financial assessments or fourteen fully specified plans.

Examples distinguish the constructs:

| Record | What the text and action support | What they do not support |
|---|---|---|
| G20 d327, Sol | A $1,414 resource total precedes a ten-action payment sequence leaving $14 | Ten actions do not establish deep search or optimal asset preservation |
| G2 d216, Sol | Recognizes yellow mortgages after sales and reaches payment | Its $430 mortgage estimate is $30 too high; dependency recognition is not numerical accuracy |
| G20 d291, Opus | Raises future pink mortgages as a possibility and subsequently uses one | Its comparison confuses proceeds with total available cash; the passage is not a correct complete budget |
| G12 d190, Sol | Both fields omit released red collateral; the applied action declares | The provider field also mentions transferring property, so the passage is not exhausted by a single numerical sentence |
| G17 d234, Gemini | The note totals only $530 and declares on a $550 obligation | The provider field ends by considering additional options, rather than making the same categorical impossibility statement |
| G12 d249, Grok | The text identifies a payable route while the applied call declares | This is not the same omission mechanism as the two necessary-collateral failures |

For G20 d291, the arithmetic matters to the scientific label. Cash is $275; debt is $1,000. Building sales plus initially available mortgages yield $680, producing a $955 balance and a $45 remaining shortfall. The response compares the $680 proceeds with the full debt and also reuses the original $725 deficit. It then considers additional mortgages and succeeds. This is positive evidence for dependency recognition alongside imperfect accounting, not an embarrassing aside to hide or the main story of the paper.

The paper needs a matrix with distinct columns for stated feasibility, dependency recognition, inventory completeness, numerical values, arithmetic, proposed route, first applied action and final payment. “Uncertain” and “not stated” must be legitimate labels. Otherwise the study turns a loose semantic success criterion into an apparent reasoning score.

### The six unsuccessful financing starts change the interpretation

I read all channels for all six episodes in which an agent starts financing despite a debt exceeding the generous total-asset bound. They are not six cases of believing an impossible debt payable.

| Entry | Initial applied action | Relevant text |
|---|---|---|
| G7 d286, Grok | Mortgage | Provider field recognizes insolvency; assistant content names bankruptcy; applied note concerns an earlier purchase |
| G9 d194, Grok | Mortgage | Private note, provider field and content favor declaring |
| G17 d396, Grok | Building sale | Provider field and content recognize insolvency and name declaring |
| G19 d224, Grok | Mortgage | Provider field and content favor declaring; applied note asserts an unsupported liquidation requirement |
| G20 d273, Grok | Building sale | Private note and other text favor declaring |
| G18 d344, Gemini | Mortgage | Correctly recognizes insolvency but describes imposing a mortgage-transfer fee that this engine does not charge |

All five Grok cases involve disagreement between applied calls and other response text. Gemini's case concerns a mistaken consequence of liquidation, not inability to compare available funds with debt. These cases belong in a paper about statements and actions because they separate correct infeasibility assessment, incorrect beliefs about consequences, and response-resolution failure.

This is also why a census should not code “continues financing” as optimism or “declares” as an infeasibility belief. The historical objective permits declaring when financing is undesirable, and the engine accepts declarations while payment remains possible. Read the stated justification and the action contract separately.

## 2. The fallback criticism is substantive, but its scope must be proved

The active shared decision resolver mortgages a listed deed first, otherwise sells a listed building level, and declares when neither financing action is available. The unused legacy helper in `llm_runner.py` is not the operative policy. The engine and resolver files are identical between the two collection commits.

Code inspection and the sixteen entry portfolios provide a strong structural argument for the referee's claim on this subset. Fifteen contain houses and no hotels. Selling a maximum-developed property preserves evenness, increases bank house stock and eventually clears a group; mortgages then become available and increase cash. The remaining entry, G20 d327, has two brown hotels and fifteen bank houses, enough for both four-house exchanges even before other house sales return stock. Thus these entries do not exhibit the hotel-stock obstruction discussed elsewhere. Under the recorded rules, a continuing legal cash-raising policy has no apparent need to infer the future collateral in advance.

This is a source-based argument, **not a measured 16/16 baseline result**. I did not execute the fallback. It strongly undercuts a claim that payment itself demonstrates prospective planning. It does not negate the observation that some initial texts already identify the later resource.

The stronger blanket statement “any order reaches U*” is unsafe outside a specified class. Hotel menus depend on bank houses, while the plan validator accepts some bundled plans based on their resulting state. The G7 obstruction demonstrates why a nominal resource total and the actual legal transition system must be distinguished. A claim covering all 131 payable states needs either a proof covering those states and the real menu semantics or an executed reference policy. Neither should be invented in a review.

There is a related issue in the paper's three-tier partition. Let U0 be cash plus all building salvage plus initially listed mortgages. U0 below the debt establishes that initially unlisted collateral is necessary, provided payment is feasible. U0 at or above the debt does not by itself prove a legal route avoiding that collateral. The middle tier should be described as **nominally sufficient without adding released mortgages**, unless an actual restricted route or structural proof is supplied. Five payments in that tier actually use released mortgages. Their use is not evidence of necessity, but their classification as unnecessary also needs more than the generous sum.

The appropriate question is consequently twofold: can the agent assess the reachable resources, and does its stopping decision allow a simple execution scaffold to finish? Route quality is a third question. Combining them into “planning ability” hides the distinction the data could usefully reveal.

## 3. Memory is a credible hypothesis, not yet a mechanism

The $130 in Sol's G12 failure and $30 in Gemini's G17 failure appear in their delivered carried notes. I checked those notes. The figures were not arbitrary false numbers: $130 describes currently available non-red mortgages while preserving the developed red group; $30 describes Baltic's available mortgage. Both are correct components under the conditions in which they were recorded.

A possible mechanism is therefore **reusing a conditional resource inventory as if it were the total after the condition changes**. That is a more precise hypothesis than “a wrong number in memory caused bankruptcy.” The same figures can also be reconstructed directly from the current menu. Their repetition does not identify the source of the later omission.

Counterexamples are informative. G13 Gemini carries a $445 non-dark-blue figure and then adds newly available Park Place finance. G20 Sol carries a $325 idle-mortgage figure and constructs a much broader $1,414 budget. G5 Gemini revises a prior incomplete inventory when facing the debt. Four of five Opus successes lack authored carried notes, but that contrast is inseparable from configuration, recovery and state exposure.

The existing records therefore support a conditional-inventory hypothesis and examples of both persistence and revision. They do not estimate a memory effect, prove anchoring, or establish learning. Removing notes would change factual information, context length and history simultaneously. Planting a reserve instruction would change preferences; planting a false factual total would change beliefs. Those are different experiments and must not be silently combined.

## 4. Text is an observable report, not a privileged cognitive trace

The private note and first action are arguments in one response. Calling the note “prospective” is justified relative to later menu states and actions; it is not a separately elicited forecast that temporally causes the first action. Provider reasoning fields have different provenance and may be summaries. Their order in a response does not establish a causal mental sequence.

The current private-note-first selection rule is explicit and reproducible, but it can hide disagreement in the very cases being interpreted. Print or link both fields for all sixteen, and preserve their identities. An annotation should be able to record “private note asserts insufficiency; provider field considers further options; call declares.” Forcing one unified belief would discard evidence.

Two same-family model readings are useful consistency checks, not independent human validation. A human reference would improve the semantic measurement, but sixteen records are not automatically twenty minutes of work: definitions, channel handling, ambiguous budgets, independent annotation and disagreement resolution take care. We cannot manufacture human annotation or authorship. Model-assisted reading can remain clearly disclosed in a descriptive paper.

A full 188-entry statement/action analysis would address an actual coverage gap. Extracting all fields is feasible and has been done in my scratch analysis; I have not assigned semantic labels to all 188. The codebook should be fixed before that expansion, include the six contrary cases, and treat silence as missing evidence. This would broaden descriptive coverage, not create an independent confirmation set.

## 5. Bargaining remains scientifically relevant, but it cannot carry a causal title

The full form-by-completion table, proposer stratification and resampling sensitivity are improvements. The headline swap contrast is still exploratory and strongly affected by proposer composition and Grok's response condition. Removing Grok-authored offers reduces the gap, with uncertainty spanning zero. A pure-cash comparison with a wide interval is not evidence of no effect. Nor can the 61/74 reason labels explain that contrast: they describe a different selected population.

Retain what the evidence directly shows: offers, counteroffers, stated rival consequences, blocking policies, selective presentation, permitted bluffing and financial-denial appeals. These are observable features of strategic interaction. Whether they were optimal, persuasive, adaptive or effective requires other comparisons.

The buyer-specific price cases are useful qualitative illustrations of externalities. Seven retrospectively selected pairs, including a singleton cell and a mortgage-status mismatch, cannot establish a general completion premium. The economic theory provides a reason to examine whose opportunities a transfer changes; it does not turn one selected episode into an equilibrium test.

I would retain the eight incidents in the complete release, with a shorter main-text selection if the venue demands it. I would not automatically delete them to make the paper fit a new financing thesis. The user asked for multi-agent science. An observational economy paper and a future focused diagnostic are different legitimate products; choosing the second does not make the first's evidence worthless.

## 6. Inference cannot repair the design, but it is not pointless

Twenty games are not categorically insufficient for a paper. Li et al. use twenty runs for a different measurement, with a defined population, classifier validation and a model tailored to their question. Our five shared-seed blocks and cyclic ordering support a narrower design. Same-seed games do not necessarily experience the same subsequent random outcomes when actions change draw consumption.

The current whole-block bootstrap is a real empirical bootstrap. Enumerating 3,125 ordered samples, only 126 distinct weight vectors, does not make it mathematically meaningless. Five blocks nevertheless provide weak information about a population of new blocks; the procedure also does not correct exploratory subgroup selection. Resampling games and resampling games within blocks represent different assumptions. None should be selected because it produces a preferred interval.

The binomial interval for 14/16 and Fisher comparison of 2/16 against 1/115 can be reported only as exploratory calculations under stated assumptions. They do not address repeated systems, related states, post hoc selection or the different mechanism of the third failure. The exact population counts are stronger than a p-value that invites a broader interpretation than the design supports.

For future work, the independent unit is a state family, not each repeated call or debt variant. Repeated requests estimate response variation on those states. Fresh families are needed to test a claim selected from the discovery corpus. A mixed-effects model with too few families is not a substitute for replication.

## 7. The novelty objections largely hold, but the comparators are not flawless

Primary-source checks confirm established work on action reachability, false impossibility judgments, interactive execution versus plan generation, tool-menu ordering, external verification, counterfactual rules, saved-state probing and memory error propagation. We should cite and differentiate these constructs, not rename them as discoveries. The literature matrix records exact sources and access depth.

Several comparisons need correction:

- AgentMonopoly v2's paper reports 140 games across its four designs; the inline report's 120 is a different repository-based count that was not reconciled. Temperature zero does not guarantee complete reproducibility. An instruction against contradictory messages does not prove conflicts cannot occur.
- FinBoardBench's fixed opponents and thinking comparison are useful design choices. Its judge labels are not an optimal value reference, and small thinking cells do not establish a null effect.
- Vending-Bench's $63,000 figure is a proposed good strategy estimate, not a demonstrated strong human reference. Epoch's direct audit found serious environment and unequal-context problems. It is not a gold standard against which all of our disclosures count as unusual defects.
- AutoVend provides a meaningful rule-based reference and a local pricing metric. It uses three repeats in one frozen world; that is replication of responses, not broad world coverage. Its local pricing regret is not total business optimality.
- Li et al.'s validation is meaningful but limited: the primary paper describes single-annotator validation and component audits, not human ground truth for every classification. Its twenty-run observational design does not identify causality either.
- Atomic chess's “unpropagated refutation” is a finding in a paper with a different title, not itself a universal diagnosis of our Grok channel mismatches. The causal path from response fields to executed actions differs.

The closest open opportunity is not “the first planning failure in Monopoly.” It is a precise relationship between **resource availability, initial feasibility assessment, stopping and eventual execution**, with independently verified states and a selective comparison. Whether this is sufficiently new remains open. A few unsuccessful literature searches cannot certify novelty.

## 8. How I would judge the proposed research program

The long first proposal is substantially better than the final confident pitch. It distinguishes representation from added assistance, assessment from execution, positive from negative states, and a pilot from confirmation. Its central question is explicitly a hypothesis. The final pitch instead writes a result in advance: frontier agents fail a fifteen-line task and a planted number steers them. Neither part has been measured under the proposed conditions.

The proposed local objective — pay whenever legally possible — is valuable because it makes premature termination an error. It changes the original game objective. That change must be explicit. Optimal liquidation should be defined against that local objective, not presented as optimal Monopoly play.

Three reference levels serve different purposes: a feasibility verifier establishes whether payment is possible; a transparent reactive policy calibrates the execution scaffold; a cost-minimizing planner measures a chosen preservation objective. They should not be called one oracle. A sound negative certificate must reflect the actual legal interface; a timeout remains unknown. The initial resource upper bound is not automatically the reachable maximum.

Restoration-cost regret is a plausible local metric, but it needs a precise accounting definition. Rebuilding costs, recovered sale cash, mortgage principal, redemption interest, rounding and terminal state all matter. Paying principal is not itself an irreversible loss if the corresponding borrowed cash has been accounted for. A local restoration metric also ignores forgone rent, group position, bankruptcy inheritance and future strategic value. Failure to pay should be reported separately, rather than assigned an arbitrary finite regret that can dominate an average.

I favor a minimal pilot after this calibration, if newly authorized. Start with explicit rules and primitive values, a fixed local objective, and independent assessment and execution instances. The first useful comparison is whether the model's assessment and its execution agree. Then test one representation or memory hypothesis, with impossible controls and comparable additional-call controls. Do not launch every proposed arm simultaneously.

The sixteen historical states can diagnose response variability and implementation issues. Repeating them thirty times does not confirm a hypothesis selected from them. Fresh state families, interleaved conditions, model version logging and consistent recovery remain necessary. New debts on the same portfolio are related variants; changing quantities while preserving old notes creates contradictions. Cross-model probes also need consistent player identities and histories.

Removing the reasoning request, fixing house rules, changing tool choice and adding values are sensible candidate setup changes, but doing all of them before a contrast changes many variables. Freeze and document the new setup. An unchanged-harness holdout tests reproducibility of the old configured systems; a corrected-harness study answers a different question.

The proposed replay-probe costs are not reliable budgets. Execution contains multiple calls and retries; historical costs include varying lengths, caches, refusal handling and model prices. Spend should be estimated from an authorized pilot, not an average call multiplied into a promised result. An arbitrary forty-reference target and predicted acceptance score add no scientific discipline.

## 9. What should stay, and what should change in the current paper

Keep the complete populations, the sixteen-case inventory, the positive G20 budget-to-payment sequence, both omission failures, the contrasting Grok declaration, and economically informative bargaining trajectories. Preserve response-condition disclosures in one accessible place. Preserve source-linked artifacts and the distinction between authorized public deception and instruction violations.

Change the scope of the headline from a general capability claim to a precise observational claim. Add the six contrary financing cases and both channels. Separate accurate resource recognition from accurate budget calculation. Rename tiers where only a bound is available. Keep the subgroup bargaining results as exploratory, with full denominators and composition. Expand related work around the actual constructs instead of adding citations by quota.

The current package is untracked locally while its artifact paragraph points readers to repository paths. That is a real release blocker, independent of research novelty. It should be packaged and published in a dedicated release when authorized, with a manifest, build command and source-to-result map. The byline must identify accountable humans; an unresolved byline does not prove that the human contributed nothing. Anonymous submission and named preprint are different release modes. Venue limits must be checked for the chosen track and year rather than applying one generic nine-page rule to every venue.

Do not fill the abstract with every caveat or every fault. State the positive observation, its population and the key setup condition. Put the remaining limits where they explain the result. Conversely, moving limits to the end must not leave a stronger title or abstract than the evidence supports.

## 10. The original questions remain the right map of coverage

| Question | What this corpus can contribute | What it cannot establish |
|---|---|---|
| Strategic reasoning | Stated rival consequences and applied bargaining policies | Optimality or a general strategic score |
| Opponent modeling | Explicit beliefs and expectations about particular opponents | Calibration, theory of mind or unfamiliar-opponent transfer |
| Negotiation and cooperation | Complete response accounting and selected tactics | Causal persuasion, welfare or fairness |
| Long-horizon planning | Particular maintained policies, revised inventories and multistep execution | General long-horizon capability or memory benefit |
| Adaptation | Contextual revisions and recurrence | Feedback-caused learning |
| Economic decisions and risk | Local resource feasibility and realized finance | Globally rational prices, investment or risk-adjusted strategy |
| Collective behavior | Transfers, concentration and coordination appeals | Unprompted emergence or functioning collusion from isolated appeals |
| Evaluation validity | Documented configuration conditions and attribution limits | General validity of a new auditing method |
| A: strategic language versus execution | Both aligned and contradictory recorded examples | Internal reasoning or causal faithfulness |
| B: general versus multi-agent capability | A possible comparison question for future matched measurements | A separate capability axis from four unequal configurations; an external business score alone does not resolve it |
| C: skill versus luck | Seed/seat patterns and concrete mechanisms | A causal decomposition of winning |

“Not established” is a legitimate answer to a research agenda. It should not become a repeated substitute for a contribution. The paper's job is to explain the findings it does have and say clearly where the agenda continues.

## Strongest dissent and revised position

My strongest dissent from our prior process is that we kept changing the paper's headline while leaving the measurement question unresolved. My strongest dissent from the referees is their proposed certainty: neither a reactive baseline, a planted-number manipulation, an exact local objective nor a new citation list guarantees a novel or accepted paper.

The immediate scientific task is to define which observable claim we want to measure and confront its counterexamples. The existing evidence is strongest when it distinguishes financial inventory, stopping and executed action. It is weakest when those are compressed into a broad claim about LLM reasoning. The review should end with that decision, not with another speculative title or a promise of perfection.
