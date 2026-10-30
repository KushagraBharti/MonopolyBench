# Review of the evaluation pilot and construction recurrence

## Recommendation

The numerical additions pass the checks performed here. I found no high-severity numerical or replay defect. Integrate them as a reference-policy readiness audit and an observational recurrence result, with the two medium corrections below. Neither addition completes the unanswered causal questions about learning, unfamiliar opponents, or general ability. The prospective arms are designs, not execution-ready experiments.

This review is independent of the packet reducer for the recurrence recount: I read all 6,989 original `decision_started`/`decision_resolved` pairs in the twenty canonical `decisions.jsonl` files. For the baseline games I re-executed the package's verifier against all retained actions using the unchanged engine. That is a fresh execution of the verifier, not an independently implemented Monopoly engine. The fixture recount starts from the 130 original scenario JSON files and uses the existing authoritative fixture validator.

## Findings requiring correction

### ER-M1. Corrective request, successful immediate repair, and later recurrence have different denominators

**Severity: medium.** Target: `paper_draft_2026-10-29/sections/recurrence_results.tex`, heading and final paragraph, originally lines 1 and 25. The text says “A corrected response” and “some locally corrected configurations” while the principal 9/50 result conditions on a later request containing feedback. That condition does not require a successful correction.

The original-record recount gives:

| Population | Episodes | Next submitted-build decision observed | Next first build repeats uneven error |
|---|---:|---:|---:|
| Error followed by a recorded corrective request | 54 | 50 | 9 |
| Same population, current decision ends in an applied build | 48 | 44 | 4 |
| Same population, current decision does not end in an applied build | 6 | 6 | 5 |

Thus five of the nine headline recurrences follow an unrepaired decision. The six unrepaired cases are G2 d129 Opus; G4 d136 and d174 Sol; G5 d276 and d278 Sol; and G19 d231 Gemini. G2 d129 has a refusal on the feedback-bearing request. The paper already handles that case correctly, but the section's broader wording should make the distinction throughout.

**Recommended replacement heading:** “Construction-error recurrence after recorded corrective requests.”

**Recommended text:** “Among 54 error decisions with a subsequent request containing the validator feedback, 48 ended in an applied construction action. Forty-four of those have a later submitted-build decision, and four repeat the error. The broader request-exposure population has nine repetitions among fifty observed next submissions.”

These strata are post-observation descriptions, not causal treatment groups. A successful applied build can change the allocation and later opportunity; excluding unsuccessful corrections does not estimate a feedback effect.

Evidence: `canonical_recurrence.json`, `independent_check.py`, and the canonical source paths/line numbers and SHA-256 values retained in that output. All original error/exposure/construction/application fields match the root's packet-derived rows.

### ER-M2. State the same-turn concentration in the paper, not just the result JSON

**Severity: medium.** Target: recurrence prose and table caption. “Next distinct decision” correctly excludes the same-decision retry, but a reader can still interpret “later” as a subsequent turn or a meaningful retention interval. Eighteen of the fifty observed next submissions after a corrective request occur in the same global turn. These mostly represent continued management of the same investment.

| Exposure selection | Same-turn next submissions | Same-turn repeats | Later-turn next submissions | Later-turn repeats |
|---|---:|---:|---:|---:|
| All feedback-bearing episodes | 18 | 1 | 32 | 8 |
| First feedback-bearing episode per player-game | 11 | 0 | 18 | 2 |

**Recommended sentence:** “Eighteen of these fifty next submissions occur in the same global turn; restricting to later turns leaves thirty-two observations and eight repeated errors. For the first-exposure selection, eighteen later-turn observations contain two repetitions.”

This is a sensitivity description, not evidence of durable learning. The next submission is self-selected, states and intended allocations change, and all rows remain nested in twenty games. There is no no-feedback control with equivalent opportunity and no model-weight update.

## Low-severity wording and engineering notes

### ER-L1. “Registered local pilot” is needlessly ambiguous

Target: `evaluation/evaluation_results.tex`, opening paragraph. It calls the work “a small, separately registered local pilot.” The package writes a local protocol copy/hash before execution and correctly disclaims external preregistration elsewhere. I can verify the retained hash agreement and script order; the local filesystem record is not an independently timestamped registration.

Use “a small baseline-only pilot with a locally frozen protocol.” Preserve the adaptive designation on the subsequent fixture-state checks. Do not describe those follow-up checks as prespecified with the first pilot.

### ER-L2. The network hook is an accidental-use guard, not a general isolation boundary

Target: `evaluation/run_offline.py:deny_network`, README and any future execution claims. The hook rejects `socket.connect`, `socket.getaddrinfo`, and `socket.gethostbyname`; it does not cover every possible network mechanism, subprocess, native extension, or datagram operation. I did not attempt a network bypass. The present static runner never creates a provider client, and the configuration loader rejects enabled paid/network flags. The thirteen retained guard tests pass when re-executed in this review folder.

The existing narrow statement “blocks socket connections” and disabled-provider description are adequate for this inspected runner. Do not promote them to a general network sandbox or a functioning paid budget controller. A future provider runner still needs an implemented reservation ledger, contemporary price/token bounds, retry accounting, durable stop behavior, and tests. The JSON gate alone is not that implementation.

## Passed checks

### Original construction records

- All 6,989 canonical decisions were read. The independent reducer reconstructs initial prompts for the first attempt rather than treating the packet's `initial_prompt_ref` marker as a payload. No initial prompt contains the exact corrective error, so the marker does not bias the exposure counts here.
- Parsed construction submissions occur in 422 decisions. Uneven-operation errors occur in 114 decisions. Error counts by configuration are Opus 61, Sol 29, Gemini 19, Grok 5.
- The three supplied episode totals reproduce exactly: 114/109/63, 54/50/9, and 31/29/2 for episodes/observed next submission/repeated error.
- The comparison against all 6,989 packet-derived rows finds zero differences in construction submission, uneven error, corrective-request exposure, or applied action.
- There are two malformed parsed construction attempts in the full population. Neither is the next-submission endpoint of an error episode. Every nonrepeating first construction submission at the observed next decision is marked valid; there is no malformed-action masking of recurrence in this result.
- No case has a construction name in plural parsed calls but not the singular parsed call used by the reducer.
- Applied construction is kept separate from a submitted call. In the exposure population, 47 of 50 next decisions eventually apply a build, whereas 41 of 50 first submitted builds are valid. A corrective retry at that next decision explains the distinction.
- No links cross player or game. The six supplied recurrence tests pass, including a feedback-removal mutation. Absence of a later submitted build is not recoded as successful repair.
- Sixty Opus episodes have an error only after the refusal-consumed retry. The one Opus feedback-bearing episode G2 d129 is a refusal. This is not comparable feedback opportunity across configurations.

### Retained baseline pilot

- Re-execution reproduces all 20 retained action streams, all 179,816 events, all decision objects, and all final snapshots. Total actions are 19,494.
- Nineteen runs end at the evaluator's 1,000-decision observation limit; one run, `mixed-r3-73002`, terminates after 494 applied decisions with builder winning. Every censored summary has null winner fields. There is no net-worth winner imputation.
- No generated live action fails validation; the runner halts on such a failure and contains no repair/fallback branch. Zero trade proposals and 44 construction actions are confirmed from retained action counts.
- Two repeated runs match the original compressed actions, events, decisions, final snapshot and summary bytes. Run identity is preserved, which matters because random-policy choices include decision identity. Rotations are not matched policy-randomness interventions.
- All 174 protected source hashes match. Current `engine.py` and the historical executable-audit ZIP member are byte-identical at SHA-256 `122edf5f16db0c4b8e0bd475ded73bf70a2b08065304d0517b8f8e2c98d63e0d`.
- This validates the engine file identity, not equality of the whole historical and new configured experiment. The pilot uses baseline policies, two chosen seeds, a synthetic run identity, and an external observation limit. The prose preserves that distinction.

### Static fixtures and score definitions

- The original 130 fixtures reproduce 75 rejected choices among 780 policy–scenario pairs. Policy-specific rejected counts are 16 always-buy, 8 auction-aggressive, 23 builder, 8 cash-conservative, 8 no-trade, and 12 random-legal.
- All eleven failed supplied reference actions reproduce. I inspected their original ownership, building, bank and trade records. The failures include genuinely wrong owners, already-owned purchase/auction targets, an incomplete or split-owned developed group, a developed-deed trade, and a hotel sale requiring four houses where only two exist. None of these reference failures depends solely on demanding standard total inventory conservation.
- The specified static checks reproduce 55 flagged fixtures: 55 house-stock discrepancies, six split-ownership groups, ten inconsistent debt shortfalls, one hotel-stock discrepancy and two developed-group mortgage flags. These overlap. All 68 fixtures passing both limited screens reproduce.
- A synthetic stock intervention need not be an invalid task. The package's conditional phrase “under standard stock-conservation” and its intervention caveat are essential and should remain. A displayed bank count is an explicit numerical condition, but standard reachability and the rationale for intentionally changing conservation still need to be declared. Do not call all 55 unusable or all 68 valid capability tests.
- The keyword count is 128/130; median fraction of rubric points is 0.1578947 and maximum is 0.2574257. Forty-one fixtures produce identical action names and arguments across the six policies. Keyword scoring is an expression measurement unless separately validated as strategy quality.
- Fixture tests run the authoritative validator on reconstructed public state plus the supplied pending menu. They do not generate a complete menu from a reachable prefix or execute a future continuation. The proposed interpretation correctly stops at conditional legality.

## Which unanswered questions this work closes

The completed additions answer two bounded questions: whether a particular encoding error recurs at an observed later submission, and whether the existing fixture/policy library is ready to support a capability evaluation. They strengthen evaluation validity and the distinction between immediate correction and later behavior.

They do not measure model adaptation caused by feedback, beliefs about opponents, strategic value/regret, transfer to unfamiliar opponents, or a relationship between general and multi-agent intelligence. They also do not isolate skill from chance in the historical LLM cohort. The twenty new games contain no LLMs. Calling all eleven agenda questions empirically completed on the strength of these additions would be incorrect.

The future arms are useful design sketches with targets, controls, units and holdout concepts. They are not execution-ready. Missing pieces include the adjudicated task population, executable intervention code, model roster, randomized assignment, sample-size/precision calculations, finalized endpoints and estimators, model/provider invocation, current cost bounds, a working budget ledger, and tests of treatment validity. The adaptation and framing arms additionally require explicit versioned model-facing conditions. A spending approval would remove one prerequisite, not all of them.

## Review limits and artifacts

This review did not query any provider, run a new model game, alter a fixture, or modify shared paper/engine/prompt sources. It did not render or compile the final integrated manuscript. It did not independently implement engine rules or prove all fixtures reachable/unreachable. The candidate reference-action failures were examined in source, but no strategic optimality labels were supplied.

The initial system `python3` evaluation import failed because it lacks `httpx`; the documented repository environment `python/.venv/bin/python` ran the checks successfully. This is not a package defect because the reproduction instructions specify that environment.

Review artifacts are `independent_check.py`, `canonical_recurrence.json`, `packet_comparison.json`, `check_evaluation.py`, `evaluation_reexecution.json`, `guard_tests.json`, `repeat_comparison.json`, and `checks.json`. Shared files may change after this review. Hashes in `checks.json` identify the inspected revision.
