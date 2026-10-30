# Temporal extension: bounded adversarial review

## Recommendation and scope

The three medium clarifications below are now resolved in the temporal source package after messages to the parent. I re-read the updated prose and re-ran original-source comparisons; the final source pin verifies 117 distinct witness decisions. No high-severity count, quotation, or source-identity defect was found. The strongest results are the distinction between a stated policy and a later actual opportunity, the G16 note/action conflict at that opportunity, and the G9 multi-stage target. They are useful evidence for Q2, Q4, Q5 and A, but do not complete theory-of-mind accuracy, causal memory, durable learning, or global strategic-value measurement. This is not approval of an unseen final integrated PDF.

I read the two scoped fields for all 240 sampled records, together with the original coder's compact tags. This was an independent adversarial reading, **not a blind second coding pass**. I did not create a second full semantic-label ledger or estimate inter-rater reliability. I inspected all eight named landing policies and independently re-extracted their subsequent actual purchase opportunities through game end from original canonical decision/action files. I checked the original 107 witness decisions and the final expanded 117 distinct decisions in the retained landing, longitudinal, and forecast witnesses against action text, menu, cash, holdings, bank stock, event records, field hashes and line references. All comparisons matched.

The review script imports none of the temporal reducer's functions. It uses the source paths in the retained extraction to read original files. It does not independently implement Monopoly or run the engine. Original source hashes and inspected extension hashes are in `source_checks.json`; reviewed record details are in `original_endpoint_context.json`. I did not compile or visually inspect the final integrated paper.

## Medium findings

### TEMP-M1: G17 d241's one-house choice is not a one-house feasibility ceiling — resolved in source

Target: `temporal_results.tex`, paragraph beginning “The distinction also matters for immediate plans.”

The phrase “a later changed state supports only one added house at d241” suggests that only one purchase was feasible. The canonical record says something narrower: d241 applies one Oriental house, and d242 ends with another reserve explanation. The d242 legal menu still lists `build_houses_or_hotel`. Its note explicitly rejects additional Vermont/Connecticut houses on a liquidation calculation, which the paper already identifies as omitting unlocked light-blue mortgages. The record cannot support a one-house feasibility ceiling merely because one house was applied.

**Replacement:** “At a later changed state, d241 applies one Oriental house, followed by a reserve-based END at d242. Both explanations omit unlocked light-blue mortgage capacity, so the chronology establishes revision rather than an improved financial calculation.”

This preserves the real revision between the d236 mortgage-and-three-houses plan and the d237 END without upgrading a stated reserve preference into an engine constraint.

Original sequence: G17 p4, d236 cash 24 mortgages North Carolina; d237 cash 174 ends with the three-house capacity available in the menu; d241 cash 374 builds Oriental once; d242 cash 324 ends with construction still offered. Source references and complete fields are retained in `original_endpoint_context.json`.

### TEMP-M2: Follow the G17 rival-build forecast to the actual management opportunity, rather than stopping after two jail decisions — resolved in source

Target: `temporal_results.tex`, opponent-assessment paragraph, and `forecast_endpoints.json` G17d000228.

The current version correctly states that the rival's next two decisions are jail rolls and does not claim that the forecast was proved false. Nevertheless, stopping there is an arbitrary short horizon when the protocol's purpose is actual-opportunity analysis. The original stream provides a complete, stronger endpoint without speculation.

- Grok p4 predicts at d228 that p1 will outbid its $99 ceiling and still build.
- P1 outbids at d231 with $100. Grok d232 faces minimum $101 with $99 cash, so its withdrawal respects its own cash ceiling.
- P1's next decisions are jail rolls d238, d243 and d252. A trade response occurs at d246.
- At d253 p1 mortgages Marvin to pay the jail fine. It then sells houses and mortgages Indiana at d254–256 to pay the ensuing rent.
- P1's first actual post-auction management is d257, with $63 cash and **no construction action in the menu**. The later d261/d264 management menus also contain no construction. P1 is eliminated at d267.

**Replacement:** “The outbid occurs. Before the rival's next management, jail exit and rent require liquidation; its first actual management at d257 has no build action, and no later build menu occurs before elimination at d267. Thus later construction is not observed, but the trace supplies no comparable opportunity at which to score a deliberate failure to build. It also does not settle the original conditional financing proposition.”

The claim combines behavior and capacity, and has no specified deadline. The absence of later construction can be reported directly, while avoiding a false belief or strategic-choice label. `source_checks.json` independently records the three management endpoints and the absence of any build menu; complete source records are retained in the context file.

### TEMP-M3: G3 d207's first stock endpoint occurs before any opponent can act — resolved in source

Target: `temporal_results.tex`, G3 d207 sentence, and `forecast_endpoints.json` G03d000207.

The current wording reports the correct stock endpoint and properly disclaims the opponents' financing bounds. It still leaves out a decisive timing fact. P1 has just rolled doubles at event 1486 (2+2, turn 81). Following d207 END, p1 immediately rolls again at event 1494 (6+5, turn 82) and reaches Short Line/d208. No opponent has acted between the forecast and that first stock endpoint. Three houses remaining there is therefore not a test of the rivals' restraint or affordable construction.

The later d213 own-management endpoint also has three houses after opponents have acted. This is an observed outcome, but does not validate the claim that p2 could buy at most one or that p3/p4 could buy none under all legal financing sequences.

**Replacement:** “At G3 d207, three bank houses remain at the next own management after crossing yellow, but a doubles roll places that endpoint before every opponent action. Stock remains three at d213 after opponents have acted as well. Neither observation validates the claimed bounds on their legally financeable construction.”

The exact event block is `g03_doubles_endpoint_events.json`. This context is especially useful as a negative control against interpreting an apparently successful stock prediction as opponent modeling.

## Low-severity reporting notes

### TEMP-L1: The semantic screen is exploratory, and its final categories are broader than the initial protocol

The initial protocol describes a prospective plan with specified condition and endpoint; the final codebook deliberately expands P to a broad forward-looking passage, including the G20 d324 affordance-only borderline case. Likewise R includes references to feedback or rejection without separately establishing the earlier belief and exposure for all 25 records. This refinement is documented and defensible for exploratory screening. It should not be called a prespecified executable-plan inventory or a census of actual revisions/learning.

The present main text's “forward-looking own-action passages,” “prospective opponent capacity or outcome passages,” and “explicit correction or feedback references” are adequate. Preserve the single-reader designation and avoid shortening those to “59 plans,” “36 correct opponent predictions,” or “25 adaptations.” No separate numerical correction is needed.

### TEMP-L2: Improve copyable typography in the new prose

Several joins read `turn29`, `to60`, `event 1277` and `event1279`. Use “turn29” only in a code identifier; prose and native table cells should read “turn29” with an explicit TeX nonbreaking space (`turn~29`) and similarly `event~1277`. The required semantic separation is low priority but prevents accidental run-together labels in the PDF.

## Checks that passed

### Sample and source identity

- Exactly 240 unique sample rows and 240 ledger rows. Every sample decision matches the original phase-2 `public_unflagged_sample.jsonl`; selection rank and eligible-pool count match.
- Twelve decisions per game, three per player-game, sixty per configured model. Selection was from a public-unflagged pool, not a 200 ordinary/40 notable sampling design.
- All 240 applied actions, args, public/private field values and field hashes match original `actions.jsonl`. Menus, actor, turn, cash and holdings match original `decisions.jsonl`.
- Fifty-three private fields are absent; all are Opus. No selected action is an engine default. Absence is retained rather than interpreted as no planning.
- Ledger counts reproduce P = 59, O = 36, R = 25. These are recounts of the original coder's labels, not independently validated prevalence estimates.
- Every P row has an endpoint disposition and every non-P row lacks one. The 8 landing rows, 19 illustrative chronologies and 32 unscorable rows partition 59. Illustrative endpoint selection is explicitly not random, and no pooled adherence rate is reported.

### Landing policies

I read all 240 fields with the operational subset in mind. The eight enumerated rows are a defensible narrow set of named-deed policies contingent on landing or sight: G2d161; G3d16; G4d126; G5d103; G6d36/d37; G9d119; G16d103. Other acquisition goals in the sample lack that explicit trigger or make additional vague resource conditions. This is a qualitative inclusion judgment, not a semantic oracle.

Independent full-game opportunity search reproduces six no-opportunity rows, G2d161→d256 Mediterranean purchase, and G16d103→d159 Virginia auction. The two G6 statements share one player-game and are not independent episodes. A deed acquired by another route is not recoded as an own bank-purchase opportunity. The codebook excludes G6d37's unspecified “better open set” from the named-target list.

G16d159 is particularly clear: Grok p1 has $371, Virginia costs $160 and `buy_property` is available. The applied note says buying at list is the only way to finish pink, while the applied action is `start_auction` and the public message falsely reports the set closed. Gemini p4 bids $380 at d162; assignment occurs following d164 at event 1277 and auction end 1279. The paper correctly treats this as execution/record disagreement, without identifying deliberate abandonment or deceptive intent.

### Principal chronologies

- G9d64 begins at one house on each dark blue and cash $27, targeting three each. D67 adds Boardwalk's second house; d102 adds Park Place's second; d162 mortgages Connecticut; d163 adds the third on each. D164 confirms 3/3 and cash $17. Global turns 29→60 give 31 increments. Intervening transactions, rolls and financing prevent a causal memory interpretation.
- G14d145 applies the first brown layer; d146–148 add three more layers in the same turn 61. D149 confirms 4/4 and $619. This is eventual allocation attainment, not evidence that the original rejected within-decision plan was preserved or that durable learning occurred.
- G20d99's next-Vermont-mortgage plan is followed first by a $150 sale offer at d100, refusal at d101, mortgage at d102 and END/cash $157 at d103. Next-action and same-turn-endpoint consistency differ, as the text says.
- G20d40's $235 cap is not exceeded: the observed later bids are $230 and $232. D42 explicitly tightens the limit to $230; d44 acknowledges exceeding that newer limit by $2; d46 withdraws at next minimum $234. No conclusion about whether the revision improves value follows.
- G17d162 gives an approximate $400 cap; d166 raises it to $460 and bids $410; d169 raises it to $530 and bids $500. D172 drops because minimum $551 exceeds cash $545. These are genuine textual revisions under changing bids, not a measured learning gain.
- G2d161's rival auction outcome is correctly forecast from public cash limits; it is not a test of private-belief inference.
- G19d220 is followed by no made/received offer before elimination. The claimed refusal is therefore never elicited. Later estate receipt does not retrospectively validate it.
- All 117 distinct final retained witness decisions match original menus, action fields, events and references. Short quoted spans in the three exhibits match the original fields inspected here.

## Remaining limits

No engine branch, model query, new game, production change or shared-manuscript edit was performed. I did not recompute the finance maxima cited from prior audits; I checked that their omission-related qualification is compatible with the original notes and menu. I did not read provider summaries or assistant content for this review, and do not validate the separate named-content-conflict detector. The same-record applied note/action conflicts are independently visible. I did not reconstruct every narrative judgment in the 32 unscorable rows into an exhaustive counterfactual analysis. I did inspect their texts and stated endpoint exclusions, and none is silently counted as a failed plan.

These additions strengthen a professional empirical paper by defining what a record can answer. They do not by themselves establish calibrated opponent beliefs, optimal strategy, causal learning, benefit from memory, or generalization across opponents. Those remain prospective evaluation targets.
