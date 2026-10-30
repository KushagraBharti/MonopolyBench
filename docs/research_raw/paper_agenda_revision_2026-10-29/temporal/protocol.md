# Prospective statements and subsequent behavior

## Frozen design

This extension studies Q2, Q4, Q5 and A with recorded statements and subsequent behavior. It does not test latent beliefs, optimal planning, causal memory effects or learning across games.

The parent sample is `core_review/public_unflagged_sample.jsonl`: 240 decisions, three SHA-ranked records per player per game from the public-unflagged pool. A later ordinary/notable review label is an outcome, not a sampling stratum. This study freshly codes all 240 records. An initial proposed reduction to 80 rank-one rows was withdrawn at the parent's request before any behavioral field was opened. The complete sample supports a descriptive sample study, not corpus prevalence or model ranking.

## Text and units

The primary unit is a sampled decision. Read the full selected applied action's public message and private note, including empty or synthetic fields. Provider summaries and assistant content are not part of this primary semantic coding; named channel conflicts are recorded separately from the retained complete conflict audit. Missing private notes are not negative evidence of plans or opponent models.

The statement unit is a complete proposition or linked plan with an exact quote and field. A sampled row receives a manual note even when no statement qualifies. Automated scripts extract fields and follow events; they do not assign semantic truth, intent or deception labels.

Code these overlapping categories:

- `plan`: a prospective own action or target beyond the already-applied immediate choice, with specified condition and endpoint. Vague preferences are retained as `preference`, not counted as executable plans.
- `opponent_prediction`: a falsifiable statement about another player's later action, achievable action or future economic state. Feasible-action forecasts and behavior forecasts are distinct. Incentive descriptions without an observable prediction are `opponent_assessment`.
- `factual_claim`: a definite state, rule, arithmetic or affordance statement relevant to the decision. Recorded source availability and any mechanical test are separate from its semantic classification.
- `revision`: an explicit acknowledgment, correction or change relative to identified earlier information. Mere changed action, retry repair or state-driven liquidation is not learning.
- `none`: no eligible prospective statement or revision in the scoped fields. This does not assert no internal planning.

For every qualifying statement retain speaker, target, condition, horizon, quote, channel, source pointer and hash. Distinguish testable claims from unscorable preferences and private-state attribution. A statement may combine categories; decision-level category counts must not be added as disjoint totals.

## Follow-up and outcomes

Use subsequent canonical decisions and events in the same game. An own-plan follow-up must identify an actual legal opportunity for the stated step, or record that none arose. Stop at the explicit horizon; if absent, use the next own actual management window for an immediate-management plan and the end of the game for an acquisition target, while marking this analyst-defined endpoint. Conditions can fail, the state can change, the target can be achieved, the plan can be revised, or the record can remain unscorable. Do not score all noncompletion as plan failure.

For an opponent forecast, test feasibility at the relevant actual decision state separately from whether the opponent chose the action. An impossible-action claim is not validated because the actor later failed to act. Behavioral forecasts require a specified observable target and horizon. Statements about beliefs, wants or private intent lack a gold-standard truth label here.

For revision, identify the earlier source, delivered feedback if recoverable, and a later comparable opportunity. Report recurrence descriptively. Do not infer learned policy from one correction or compare learning between configurations with unequal feedback/notes.

## Verification and reporting

Generate extraction and follow-up tables with canonical source references, field SHA-256 and event/decision IDs. Assert 240 unique manifest IDs, 240 selected, twelve rows in each of 20 games, three per player-game, and no duplicate semantic rows. Verify quoted spans against retained full fields. Keep source-checked examples distinct from complete sample statistics. Report counts with the actual text-availability denominator and no confidence intervals that pretend decisions are independent.

The study is exploratory, fixed before opening this extension's selected text, but the project previously reviewed these games. It is not preregistered or blind to all prior findings. Primary coding is one model-assisted reader, with any parent review reported separately. No paid calls, new game, engine/prompt change or causal intervention is part of this extension.
