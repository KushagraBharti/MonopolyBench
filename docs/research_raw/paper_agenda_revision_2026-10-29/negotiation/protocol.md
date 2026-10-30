# Negotiation and collective-flow protocol

This protocol is fixed before computing the new extension's outcomes. It extends the existing twenty-game cohort and changes no game or model input. Prior aggregate counts are reconciliation targets, not exclusion rules.

## Populations and units

1. A negotiation thread begins at each canonical `TRADE_PROPOSED` event and ends at its matching accepted or rejected event. Preserve every thread, including immediate rejection and repeated approaches to the same pair.
2. An offer opportunity is each initial proposal or counteroffer followed by a response. Reconstruct its author from the actor of that event and use the next response actor as recipient. Never infer bundle direction from the thread initiator or the formatted memory sentence.
3. Mechanical offer consequences are calculated from the authoritative delivered state at the response decision and the currently pending bundles. Count color groups completed or broken for each party, the cash transferred and mandatory mortgage-transfer charges, and the immediate holdings. These are accounting consequences, not utility, fairness, optimum, or predicted effects on winning.
4. Report negotiation activity per thread, response per received offer, and model/game strata. Report both global decision/turn elapsed time and actual actor opportunities when defined. Repeated threads remain distinct; pair-level summaries expose concentration rather than merging them into inferred negotiations.
5. A directed flow edge connects the recorded payer/transferor to recipient for trade cash, paid rent, and inherited property. A trade of several deeds is one settlement but several deed-transfer edges. Bankruptcy cash is estate transfer, not paid rent. Bank flows remain separate from player-player flows.

## Prespecified questions

- How often do threads settle, and how often does settlement follow counters or counterparty-authored terms?
- Is mechanically completing the recipient's own color set sufficient for accepting an offered exchange? Report all received offers and all response types, including cases where both parties complete, only the recipient completes, or neither completes.
- What immediate cash and completion changes accompany actual settlements? How concentrated are bilateral dealings and realized rent/estate transfers?
- Do observed repeated approaches or collective flow patterns establish a coalition? They do not by themselves; this extension will not turn network density or keywords into a collusion label.

## Validation and limits

Reconcile canonical events, actions and decision records. Require one complete response path per offer and one terminal outcome per thread. Validate bundle ownership and transaction cash against actual settlement events. Check source hashes, state/ownership reconstruction, and outlying rows manually. Include synthetic mutations that must make invariants fail.

The unit of uncertainty is not an individual dependent offer. Report exact finite-cohort counts and game/configuration breakdowns, not nominal IID significance. The design has five seed blocks and fixed configurations. Semantics such as deceptive intent, generosity, coalition membership, or reason for rejecting a deal require a separate annotated population and are not inferred here. Effects of communication, alternative trades, or opponent policies are not identified. Source observations are downstream analysis only.

## Stated-reason extension

After the mechanical census and before reading this subset's texts, define a closed semantic population: every direct rejection of an acceptance-legal offer that would newly complete at least one recipient color group. Read each applied public message and private note. Code explicit stated considerations only, with a short supporting span; multiple codes are allowed. Categories are rival completion/development/funding, own cash/price/affordability, retained assets or income, timing or conditional policy, and no applicable explicit reason. A stated consideration is neither a verified factual proposition nor a causal explanation. Do not infer preference from a missing note, do not force classification, and report channel availability. This is a single model-assisted coding pass subject to independent review, not human gold-standard annotation or a validated corpus-wide intent classifier.
