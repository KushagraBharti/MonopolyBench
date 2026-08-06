# GPT-5.6 Sol Pro MonopolyBench research synthesis

Date: 2026-07-28  
Status: initial research pass complete; no follow-up prompt submitted  
Model observed in the conversation DOM: `gpt-5-6-pro`  
Completed-response length: 112,232 characters  
Conversation: <https://chatgpt.com/g/g-p-6a695a6288888191b7bd6afc42ea2b12-monopolybench/c/6a695f12-e6a4-83ea-91df-6e3dfed06552>

## Scope and provenance

This file is a compact, repository-reconciled record of the completed Pro research pass. The complete response remains in the linked ChatGPT project conversation. It is not copied here as benchmark evidence and must not outrank canonical events, actions, decisions, snapshots, replay reports, or frozen hashes.

The task received ten local files: the manuscript, the three analysis guides, and the manual-review, case-study, and integrity reports for Runs 191 and 273. Their byte counts and SHA-256 hashes are in `gpt-5-6-sol-pro_source_manifest_2026-07-28.csv`. Six additional review reports were briefly attached to an empty composer for a possible follow-up, but the follow-up was not sent and the attachments were removed. They are therefore not Pro-task inputs.

The broader eight-game facts in `monopolybench_research_handoff_2026-07-28.md` and `monopolybench_eight_run_ledger_2026-07-28.csv` came from local repository inspection, not a second Pro pass.

## Central scientific recommendation

The current evidence supports a benchmark-methodology paper with deeply sourced mechanism case studies. It does not yet support a model leaderboard or population-level claims about relative model skill.

The eight completed games are valuable as a pilot corpus, but they are not a balanced comparative experiment. Roster versions, seat order, maximum-turn limits, and run conditions are not fully crossed. Descriptive language should therefore remain trace-specific: “in the reviewed traces,” “in this run,” or “the pilot corpus exhibits.” Comparative claims should wait for a fixed roster, independent seed blocks, complete seat rotations, locked prompt/rules/route policy, uncertainty-aware analysis, and an adequately powered design.

MonopolyBench should describe its determinism narrowly and accurately. The engine supports deterministic transition replay conditional on a fixed engine version, engine seed, configuration, player identities, and applied action sequence. That is distinct from deterministic regeneration of model actions. Provider sampling, routing, network timing, and latency are observational metadata and can remain nondeterministic.

## Canonical integrity conclusions

### Run 191

Run 191 is `state_passed_artifact_failed`, not generically “replay clean” and not “pending reconciliation.”

- State replay compared 1,640 events successfully.
- Artifact replay first diverges at event sequence/index 669.
- Event ID: `mock-83265-81ed4937-evt-000669`.
- Decision ID: `mock-83265-81ed4937-dec-000096`.
- The original artifact records `valid=false` and `error=fallback:illogical_after_retry`.
- Replay records `valid=true` and `error=null`.
- The applied fallback action is `reject_trade`.
- There are no missing actions, extra actions, or decision-ID mismatches.

This is a metadata/provenance mismatch around the fallback representation, not evidence that the authoritative engine state diverged. Any paper claim must preserve that distinction.

The manuscript must also distinguish 583 engine decision points from 604 model attempts. The difference includes retries. It must preserve the Run 191 HTTP 503 usage row as missing/null provider usage rather than converting absence into zero.

### Run 273

Run 273 passes both replay layers:

- State replay compared 1,942 events successfully.
- Artifact replay compared 4,102 events successfully.
- There are no missing actions, extra actions, or decision-ID mismatches.

The house-supply episode is scientifically useful as an observed mechanism trace, but the current evidence does not establish a causal claim about alternate actions. At turn 167 the downstream report identifies only a Tier-2 counterfactual candidate, not a completed branch-oracle result.

## Evaluation hierarchy

The paper should replace any blanket “no heuristic oracle” language with four explicit layers:

1. **Layer 0 — canonical observed facts:** engine state, legal-action menus, applied actions, events, usage metadata, and replay results.
2. **Layer 1 — deterministic derived metrics:** accounting/liquidation net worth, cash-flow decompositions, exposure, ownership concentration, trade and auction episodes, and other calculations whose definitions are versioned.
3. **Layer 2 — bounded counterfactual analysis:** legal-liquidity optimization and branch rollouts under a declared continuation policy and exogenous-randomness policy.
4. **Layer 3 — qualitative interpretation:** communication labels, strategic mechanisms, possible deception, and case-study narratives, always with human review and epistemic limits.

This prevents descriptive calculations, counterfactual regret, and qualitative judgment from being presented as if they had the same evidentiary status.

## Statistical design recommended for the next campaign

- Freeze one primary model roster and model-version window.
- Cross complete seat rotations within each engine-seed block.
- Use multiple independent seed blocks, not one seed reused across nominal replicates.
- Lock rules, prompt template, legal-action serialization, identity condition, provider-route policy, and date window before the campaign.
- Predeclare co-primary endpoints and multiplicity handling.
- Report hierarchical uncertainty, cluster by seed block, and include rank probabilities rather than a point leaderboard.
- Define game-horizon, alive-only, and common-horizon AUC variants before looking at results.
- Build canonical eligible denominators for trades, auctions, retries, fallbacks, and communication opportunities.
- Run an 8–12-block blinded calibration campaign, then simulate power/precision under the exact planned analysis model before fixing the final sample size.
- Treat route/date/provider drift as a sensitivity dimension and preserve actual endpoint metadata.

## Counterfactual and oracle requirements

Do not report regret, trade surplus, or “avoidable bankruptcy” as established quantities until the branch-evaluation contract is complete:

- the branch engine accepts the full legal action set;
- the source state and legal-action menu are hashed;
- continuation policies are declared;
- exogenous randomness is controlled or explicitly resampled;
- oracle uncertainty is reported;
- conclusions are tested across multiple continuation policies;
- strong-play fixtures accompany failure fixtures.

For common-random-number comparisons, the preferred design is a counter-based or otherwise branch-stable exogenous RNG schedule. A branch must not consume future randomness merely because one action produces more incidental events.

## Communication-analysis requirements

Claims about deception, collusion, promises, reversals, and epistemic state require opportunity-based denominators and a human-gold validation set. High-risk cases should be double-coded and adjudicated. Any LLM judge should be tested on held-out human labels, with model identity and winner status masked where feasible. Until then, communication findings belong in mechanism-focused case studies, not prevalence tables.

## High-priority mechanism windows

These ranges were highlighted as especially useful for manuscript figures and source-grounded case studies.

### Run 191

- Pink acquisition engine: decisions `000040–000074`, events `000313–000524`, turns 25–26.
- Park Place auction: decisions `000081–000093`, events `000578–000652`, turns 31–32.
- Turn-33 fallback: decisions `000095–000096`, events `000664–000672`.
- Light-blue completion: decisions `000099–000119`, events `000696–000819`.
- Turn-79 consolidation: decisions `000279–000329`, events `001858–002135`.
- Failed improved-property trades: decisions `000386`, `000387`, and `000391`.
- Green development: decisions `000412–000421` and `000427`.
- Grok bankruptcy: decisions `000379–000381` and `000430–000431`; events `002488–002510` and `002839–002855`.
- Gemini bankruptcy: decisions `000369–000473`; events `003111–003124`.
- Claude endgame: decisions `000531–000582`; events `003556–003971`.

### Run 273

- Illinois auction: events `000652–000725`, auction `auction-0003`.
- Kentucky trade: decisions `000157–000160`, events `001061–001079`.
- Vermont retry: decisions `000183–000184`, events `001238–001246`.
- Pink completion and development: decisions `000193–000198`, with later builds through decision `000278`.
- Brown overdevelopment: decisions `000285–000293`, events `002004–002071`, turns 108–109.
- Railroad consolidation: decisions `000307–000308` and `000358–000363`; events `002177–002190` and `002560–002597`.
- New York blocker conflict: decisions `000385–000394`, events `002781–002854`.
- House-lock trade/development: decisions `000395–000422`, events from `002865`, turns 167–180.
- Distress-sale feedback: decisions `000514–000532`, events `003878–004028`.
- Terminal tax: decisions `000536–000539`, events `004059–004101`.

All abbreviated identifiers above must be expanded and resolved against the package evidence index before publication.

## Manuscript stop/go gates

Proceed now with:

- truthful benchmark architecture and replay-methodology prose;
- the four-layer evaluation hierarchy;
- exact Run 191 and Run 273 integrity language;
- descriptive figures whose source table, run ID, replay caveat, and metric definition are explicit;
- mechanism case studies grounded in exact artifact IDs.

Stop before:

- comparative model rankings from the eight pilot games;
- causal regret, trade-surplus, or avoidable-bankruptcy claims without a validated branch oracle;
- deception or collusion prevalence without denominators, human gold, double coding, adjudication, and judge-bias checks.

## Immediate manuscript checklist

- Replace unqualified “deterministic benchmark” language with deterministic engine-transition replay language.
- Use the canonical winner and `state_passed_artifact_failed` status for Run 191.
- State the exact event-669 discrepancy.
- Separate playable turns from terminal-only checkpoints.
- Separate decisions from attempts and retries.
- Trace every token, cost, rent, property, building, liability, and net-worth value to a hashed table row and versioned metric definition.
- Add actual provider/route fields and record omitted temperature or output-token-budget fields as omitted, not inferred defaults.
- Define accounting net worth and liquidation net worth explicitly.
- Explain the split state/artifact replay architecture.
- Version every source hash, generated hash, table, figure, and metric definition used by the paper.

## Interpretation rule

The Pro response is a research aid. Where it conflicts with repository artifacts, the repository's canonical protocol objects and frozen hashes win. Any polished prose adapted from it must be rechecked against source IDs before entering the manuscript.
