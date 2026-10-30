# Final integration review of the research-agenda revision

## Recommendation and scope

The inspected manuscript is an honest report of the work performed. It has become a broader empirical study of execution and interaction, with an explicit question-to-measurement contract. It does **not** establish that the full eight-question agenda and broader questions A/B/C have been empirically solved. In particular, the paper correctly leaves causal learning, unfamiliar-opponent transfer, general strategic value, and the general-to-multi-agent capability relationship unmeasured. The prospective appendix is labelled as unexecuted designs, not new results.

No high-severity numerical or scientific-overclaim defect was found in the inspected integration. Two medium wording clarifications and several low editorial fixes would improve the final version. The medium findings concern the interpretation of already-supported counts, not a request for more experiments.

I read all fourteen requested manuscript/status files in full and retained their source hashes in checks.json. I also inspected the current validation, methods and economic-results passages needed to check integration, and the three fresh specialist reports. I compared the displayed numbers and claims to those reports and retained exports. I did **not** rerun the canonical-game census, engine replay, fixture validator, semantic coding, or paid experiments. Those checks are inherited from named specialist work, not claimed as another independent replication here. I did not build or inspect the final integrated PDF.

## Medium findings

### INT-M1. Define applied-build repair locally wherever the new recurrence ratio appears

Targets: sections/recurrence_results.tex, final paragraph; sections/discussion.tex, the Q5/Q8 paragraph; question_status.md, Q5.

The new text correctly separates a corrective request from a decision that ends in an applied build. It then calls the latter an "applied construction repair" or "applied-build repair." A reader entering through the new section can infer that the intended purchase allocation was repaired. The earlier economic-results section explicitly establishes otherwise: successful construction retries preserve the original multiset in 20/25 Sol, 6/18 Gemini and 5/5 Grok cases. A valid smaller or differently allocated build is not exact recovery of the original target.

This does not change the independently checked 48 episodes / 44 observed next submissions / four repetitions. It changes the interpretation of the conditioning event. Add a sentence directly after introducing the 48 applied-build decisions:

> Here, repair means that the decision ends in some legal construction; it does not require the original purchase multiset to be preserved.

In the discussion and status ledger, prefer "after a decision ending in an applied build" over "after an applied construction repair." Retain the same-turn count and the 5/6 recurrence after decisions without an applied build. These are observational strata, not treatment effects.

Evidence checked here: the integrated recurrence text, the existing exact-multiset recovery paragraph in economic_results.tex, and the recurrence specialist's 48/44/4 versus 6/6/5 recount in reviews/evaluation_recurrence/checks.json. I did not independently re-execute those rows.

### INT-M2. Make the G14 brown target unambiguously per property

Target: sections/temporal_results.tex, paragraph beginning "The records contain sustained, realized targets as well as revisions."

The text says "G14 d145 states a brown four-house target." The verified target and endpoint are four houses on **each** brown deed, eight houses total, with $619 after completion. The existing economic-results section calls this an eight-house target. The shorthand therefore makes the new temporal result appear inconsistent with the earlier construction analysis.

Replace the phrase with:

> G14 d145 states a target of four houses on each brown deed, and three later building decisions in the same turn reach it, leaving $619.

The temporal specialist independently checked d145 through d149 and reports 4/4. This integration review relies on that source check and verifies consistency between the two manuscript passages.

## Low findings and optional cuts

### INT-L1. Link the new longitudinal exhibits from the relevant result paragraphs

The three labels fig:temporal-target, fig:temporal-opportunity and fig:temporal-revision appear only at their definitions. The appendix label app:temporal-exhibits likewise has no main-text reference. Add figure references to the G9, G16 and auction-limit paragraphs, or one introductory sentence directing the reader to Appendix app:temporal-exhibits. These exhibits are useful and should not be discoverable only by reaching the appendix.

### INT-L2. State the two baseline studies' different starting states together

The validation section reports nineteen of twenty earlier **prefix continuations** terminating before a 20,000-decision cap. The new readiness subsection reports nineteen of twenty baseline-only **new games** censored at 1,000 decisions. Both statements are qualified and internally consistent, but the inverse fractions are easy to misread as conflicting accounts of one experiment.

Add to the new pilot protocol paragraph:

> Unlike the historical-prefix continuations above, these pilot games start from the initial board and use the separate 1,000-decision observation limit.

Use that wording only if the initial-board condition is confirmed from the runner or its retained initial settings. The existing pilot report describes new full games, but this review did not reopen all initial snapshots. This is a clarity suggestion, not a new empirical check.

### INT-L3. Use the applied-response level consistently in the headline negotiation sentence

The negotiation specialist recommended "the applied responses comprise 34 acceptances, 113 counters and 74 rejections." The integrated section currently uses passive "34 are accepted" wording, followed later by an explicit warning about content/tool disagreement. The present sufficient-condition claim is valid for configured systems. Naming applied responses at first use would make that interpretation harder to lose when the sentence is quoted. This is especially appropriate because some of the paper's best cases show that received actions need not express a channel-consistent plan.

### INT-L4. Tighten repetition without removing the result boundaries

The eight-question list appears in the introduction, the methods table and the opening discussion synthesis. The table and discussion do different jobs and should remain. The introduction can shorten its list to one sentence pointing to the table. The discussion's future-design paragraphs partly repeat the prospective appendix. Keep its normative-contract rationale and cite the appendix for implementation details. This is an optional length improvement, not a claim that any required question is missing.

Also correct the stale source comment at the top of negotiation_extended.tex: "Semantic counts are one / model-assisted readings" is grammatical debris from integration. The economic-results closing sentence says "The social analysis next asks" although two new sections now intervene. Use "The social analysis later asks" or remove "next."

## Coverage assessment

| Question | Current answer status in the manuscript | Integration verdict |
|---|---|---|
| Q1 strategy | Observed tradeoffs, refusal under own completion, local feasibility and execution. | Supported at the declared scope; not optimal-policy evidence. |
| Q2 opponent modeling | Prospective statements and selected public-capacity/action endpoints. | Honest partial answer; no private-belief calibration or theory-of-mind score claimed. |
| Q3 negotiation/deception | Complete mechanical threads plus qualified reason coding and contextual transcripts. | Strong descriptive coverage; causal influence, fairness and latent deception prevalence remain open. |
| Q4 plans/memory | Fixed-sample field reading, all prospective-row dispositions, explicit opportunity endpoints and sustained targets. | Useful behavioral evidence; no aggregate planning-success or causal memory score. |
| Q5 adaptation | Revision examples and recurrence after recorded feedback, with censoring and same-turn distinctions. | Observational answer only; durable or feedback-caused learning is not claimed. |
| Q6 economics/risk | Construction/receipt accounting, accessible finance, local certificates and inherited assets. | Strong local/mechanical coverage; no ex ante risk-adjusted value or regret claim. |
| Q7 collective behavior | Typed transfer networks, nonterminal concentration and documented coordination. | Partial descriptive answer; ordinary interdependence is not labelled collusion. |
| Q8 validity/generalization | Replays, source checks, mutation tests and a reference-readiness audit. | Internal measurement checks are substantial; external generalization remains untested. |
| A skill versus strategic language | Source-linked text/action/opportunity disagreements and positive follow-through. | Supported case-level distinctions; no validated monitoring score. |
| B general versus multi-agent capability | Independent axis and held-out design requirements stated. | Explicitly not empirically answered. No result is fabricated from the four-model cohort. |
| C skill versus luck/weak opponents | Specific error and transfer mechanisms, dependence cautions and cross-play design. | Partial local evidence; no causal outcome decomposition or opponent-adjusted ranking. |

The table is a review of scope, not a new numerical completeness scale. A professional paper can report these completed analyses and unresolved targets honestly. It cannot call the entire scientific agenda completed merely because every row has prose.

## Integration checks that passed

- The twenty historical LLM games, twenty baseline pilot games, two exact repeat runs, and earlier twenty prefix continuations are distinguished. Pilot games are not pooled into the 6,989-decision cohort.
- The negotiation totals agree with the specialist's independently implemented census: 526 threads, 920 responses, 918 acceptance-legal opportunities, and 221 recipient-completing offers with 34/113/74 responses. The table totals exclude one rejected and one countered offer without a legal acceptance action.
- The 61 common positive semantic labels are presented as agreement between model-assisted readings, with disagreement and accidental exposure disclosed. Broader categories are not quietly promoted to validated motive prevalence.
- The 54/50/9 and 31/29/2 recurrence counts are separated from 48/44/4 applied-build cases. Same-turn continuation and the 8/32 later-turn count are stated. No randomized feedback effect is inferred.
- The temporal screen uses 59 forward-looking passages, 36 opponent-capacity/outcome passages and 25 correction/feedback references, not 59 executable plans or 25 learning events. The 53 missing private fields and filtered sample are explicit.
- The G3 doubles timing and G17 complete rival-opportunity suffix corrections appear in the integrated temporal text inspected here. G16 is interpreted as an applied note/action conflict, not intentional abandonment or deliberate deceit.
- Pilot findings agree with the specialist report: 19,494 decisions, 179,816 events, 19 censored games, zero live invalid actions and zero trade proposals. Static 75/780 rejections are not reported as live-policy failure rates.
- Eleven invalid reference actions, 55 conditional state flags and 68 limited-screen candidates have distinct meanings. The paper does not call all flagged fixtures unusable or all screened candidates validated capability tasks.
- The future appendix uses unexecuted language. The limitation paragraph lists missing tasks, interventions, roster, precision and outcomes. No paid budget is mistaken for a complete experimental design.
- Abstract, introduction and conclusion remain about audited execution and interaction. They do not promise a causal capability–alignment curve or a ranking that the study does not estimate.

## Limits

The final PDF, layout, bibliography, full old economic/social sections, package rebuild and all original source calculations are outside this bounded review. The applicable older economic and validation passages were read only where needed for integration. I did not independently validate comparator literature or semantic ground truth. Review reports can change after the source pin; checks.json identifies the files I read. All writes are confined to this integration review's findings.md and checks.json. No shared manuscript, outline, canonical artifact, prompt, engine, game or provider call was changed.
