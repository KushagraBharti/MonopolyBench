# Executable artifact review

The original runner can issue a false impossibility certificate. Its graph enumerates atomic sales, although the unchanged engine accepts some bundled sales that cannot be decomposed into those atomic moves. I reproduced this failure outside the historical census. The coordinator added a guard during this review, and my bounded recheck confirms that the revised runner refuses this case. The 126 historical results survive the correction.

I found no additional failure in the frozen population, historical prefixes, upper-bound certificates, three payment witnesses, or construction multiset checks. These conclusions concern the selected twenty-game corpus and the stated local interventions. They do not establish evaluator accuracy or future survival.

## Reviewed versions

I wrote `initial_position.md` before inspecting the implementation and did not read earlier reviewer reports. I used the source cohort manifest only to verify the selected game paths. The original runner hash is `7d5b01f7ff4447dd17a982268f4533dfc9b12bfb071571c7c0b3cd092e7ea4a0`. The original ZIP hash is `9d825ce485f2ed9d9a98a70e373b7e34182be5461e67bfe8e77bd42e9551c840`.

The coordinator changed the live artifact while I reviewed it. I preserved the original ZIP, extracted it under `portable_original/`, and verified that its runner, tests, and README match my initial hashes. The reproducers use this preserved version. The separate fix recheck targets live runner hash `6fd0b059d7bc9a5a96c7fbc5ffb38948eaebabf0b9677a84da7a7076b4b1fb3a`. The review is therefore explicit about which code failed and which code passed the correction check.

## High-severity finding: atomic search can falsely certify impossibility

Original `run_audit.py` lines 168 to 178 generate only one-building sales and single mortgages. Lines 219 to 248 call exhaustion of that graph an impossibility result. `check_elimination` then exposes it as `exhaustive_financing_impossibility` for the broader own-sales-and-mortgages intervention.

The engine's `_validate_sell_plan` checks bank house inventory and evenness after the complete plan, at engine lines 2854 to 2862. It does not impose the atomic search's intermediate stock restrictions. Thus the graph can omit accepted actions.

The executable counterexample has a debtor with no cash, one house on each Brown deed, and a hotel on each Dark Blue deed. Another player holds thirty houses across three complete groups, so all 32 houses and both hotels are accounted for. The debtor lands on that player's Illinois Avenue with three houses. The unchanged engine computes rent of 750. Atomic financing sells the two Brown houses and mortgages the two Brown deeds, yielding at most 110. Hotel sales never appear in the atomic menu because bank house inventory never reaches four. The search exhausts six states and issues an impossibility certificate.

At the initial decision, however, `sell_houses_or_hotel` is offered because the Brown houses are sellable. The engine accepts one plan that sells the Park Place hotel, its four replacement houses, the Boardwalk hotel, and its four replacement houses. The complete plan returns house inventory to its starting value, raises 1,000, pays the 750 debt, and leaves 250. The validator returns no errors and the engine emits the payment event. This is an accepted legal action under the unchanged benchmark engine, regardless of whether the engine's sale semantics match an external interpretation of Monopoly.

Run `PYTHONDONTWRITEBYTECODE=1 python3 docs/research_raw/paper_adversarial_2026-10-29/round2/certificates/adversarial_checks.py` from the repository root with Python 3.10 or newer. `adversarial_results.json` contains the false six-state certificate and the accepted payment witness. This fixture is synthetic, with internally consistent inventory and rent. It is not one of the recorded games.

The coordinator's fix refuses negative graph certification whenever an expanded state offers a building-sale action. This is a sound way to avoid the demonstrated incomplete enumeration. It leaves such cases unresolved instead of claiming that atomic exhaustion proves the broader claim. `recheck_fix.py` confirms refusal of the counterexample while the valid bundled sale still pays. All 126 historical result objects remain equal apart from the added graph-scope description, and all twenty replay digests remain equal.

## Why the historical G7 certificate survives

At G7 decision 339 the exact offered action names are `mortgage_property` and `declare_bankruptcy`. There is no `sell_houses_or_hotel` action. I submitted a bundled hotel-and-house sale directly to the validator at that prefix. It rejects the action with `Action not legal for decision` before considering its plan.

The only financing edge mortgages Oriental Avenue and triggers bankruptcy at cash 440 against debt 750. The graph has one nonterminal state. Unlike the synthetic counterexample, no offered sale action can admit an omitted bundle. Declaring bankruptcy cannot pay the debt and therefore does not need to be a financing edge. The historical negative certificate is valid for the current debt and current legal menu. It says nothing about earlier management decisions, trades, help, future turns, or eventual outcomes after a different history.

## Independent historical verification

I reran the original runner and reproduced all 50,918 canonical events. Its output equals the saved original `results.json` as a complete JSON object. I also ran the original ZIP after extraction into the review directory with an explicit Python 3.14 interpreter and obtained the same result.

I independently reread the canonical game files. All eighty recorded source-file hashes match, all twenty copied action files are byte-identical, every frozen event hash matches its canonical event, and every frozen config field equals the corresponding original field. The seven vendored Python source files and board JSON are byte-identical to their canonical counterparts. These 88 files also match their hashes at the end of the review.

The case list has 126 unique case IDs. The 60 elimination markers match the original bankruptcy event census, including the marker's player, the preceding response decision, and its declared/automatic label. The 66 default cases equal the full set of original `decision_resolved` records with `fallback_used`, and all applied `end_turn`. The attempt fields and recorded plans match their source records. Every start/resolution line hash matches. Every case prefix ends at the correct requested decision and matches both the original prefix count/digest and the freshly replayed engine snapshot. The source cohort manifest contains the same twenty game paths; this does not establish that those games were selected prospectively or represent all saved games.

The results are 56 upper-bound impossibility certificates, one G7 graph certificate, and three legal payment witnesses. I independently recomputed all estate upper bounds and replayed every action and event in the three witnesses. Each witness contains the actual pending debt's amount and payment reason, and the debtor is not bankrupt at its endpoint.

For construction, all seventy well-formed target encodings fail as submitted. Sixty-three target attempts execute after atomic expansion and ordering; seven cost more than current cash. One attempted target is malformed and 61 attempts have no parseable target. At decision level, 63 of 66 defaults have a reachable recorded target, and all 66 have some legal construction. For every successful target I independently compared the original per-deed/per-kind counts, the reordered plan, the emitted construction events, and the cash debit. No purchase was lost or substituted.

## Proof and implementation limits tested

The upper bound is valid for these fixed rules and the stated intervention. A house sale converts one half-cost building level into cash. A hotel sale converts level five to level four and returns one half-cost level. A mortgage converts the clear deed's half-price capacity into cash. None increases their sum. Every relevant building price is even, so grouping sales does not create rounding income. Dropping sale-order and stock constraints enlarges the budget, which makes `U < debt` a sufficient negative certificate. The counterexample does not defeat this bound because its U exceeds its debt. Across all 60 historical elimination prefixes, I executed 139 offered atomic successors, comprising 42 sales and 97 mortgages. The potential never increases.

State deduplication omits counters, other-player cash, and pending debt context. In one local search, the debt and static board data remain fixed until the endpoint, and the successor menu depends on the debtor's cash, ownership, building/mortgage states, and bank stock that the key retains. I tested a three-mortgage commuting graph without deduplication: ten nonterminal paths collapse to seven states, and matching keys have matching action menus and pending payments. This supports the fixed-debt use; it does not make the key suitable for pooling states across debts or continuing after payment.

`payment_in` is a live-execution convenience, not a standalone verifier of supplied certificates. A fabricated `CASH_CHANGED` event for a BUILD debit equal to the debt passes that predicate. The checked financing branches cannot generate a BUILD debit, and I verified the actual debt reason in all three historical witnesses. I found no false historical payment certificate. Reusing this predicate on arbitrary event lists would require stronger provenance and debt matching.

The construction ordering is incomplete in general. This artifact records unresolved ordering failures instead of negative certificates when cash is adequate. In this census its seven well-formed failures exceed current cash, so their negative conclusion follows from cost and the no-extra-financing intervention. I also tested rejection of boolean, float, zero, negative, and string counts and an unknown deed.

## Evidence status

The case population, retrospective targets, source identifiers, and original expected outcomes were inherited. My new work recomputed replay equality, source linkage, certificate execution, event-level construction preservation, the counterexample, and the bounded fix check. The eight bundled tests passed before the new counterexample, so their success alone was insufficient evidence of solver soundness.

No canonical file, original engine, prompt, or shared artifact was edited by this reviewer. All reviewer writes stayed in this directory. No model/provider calls or network requests were made. `verification.md` lists commands and evidence files. `findings.json` records the material failure and its rechecked correction.
