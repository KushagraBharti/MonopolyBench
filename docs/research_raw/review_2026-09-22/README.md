# Research and implementation review — 2026-09-22

MonopolyBench has substantial reusable infrastructure and an unusually inspectable
exploratory corpus. The next campaign should follow a bounded correctness and
measurement pass. The September two-paper direction is coherent, but current
implementation and evidence do not yet establish its two proposed contributions.

This review examined the active roadmap, historical protocols, manuscript source,
saved-game integrity records, engine/arena/telemetry/microbench code and tests,
campaign controls, and selected current primary sources. It ran the checks below
and additional unpaid probes. It is not a complete line-by-line code audit, a fresh
human adjudication of every behavioral episode, or a clean-machine reproduction.
No game/provider generation calls were made and no frozen source artifacts were
rewritten. Source baseline: `c370c87c`; the September roadmap edits were already
uncommitted when review began. This directory contains review evidence only.

## What is established now

| Surface | Fresh evidence or bounded status |
| --- | --- |
| Contracts | `bash scripts/verify.sh` passed contract examples, board, and micro catalog validation. |
| Python lint | Wrapper passed Ruff. |
| Python type checking | Wrapper failed at `tui.py:402,406`: `msvcrt.getwch` unavailable in the platform's type definitions. |
| Python tests | Explicit engine/API/arena/telemetry/microbench invocation: **193 passed in 27.91 seconds**. |
| Frontend | `npm run lint` and `npm run build` passed; nonblocking large-chunk warning. No live UI interaction audit was performed. |
| Saved replay | Fresh read-only replay: **8/8 state, 7/8 full event stream**. R191 first mismatch remains index 669. |
| Action reconciliation | All eight games have matching unique started-decision/applied-action ID sets and unique applied actions. R166 and R172 each contain a duplicated start marker already disclosed by their integrity reports. |
| Baseline action legality | All six implemented baselines passed existing legal-action validation on all 130 micro fixtures: **780 checks**. This is not engine reachability, optimality, or full-game policy validation. |
| Prompt preservation | Existing preservation tests passed with the suite. The historical 12-fixture exact-history proof was read, not freshly regenerated. |
| Manuscript | Current `.tex` hash matches `paper/final_build_manifest.json`. Its listed PDF and anonymous supplement ZIP are absent at the recorded paths in this checkout. No PDF rebuild or visual review was performed. |

Reproduce the test invocation from `python/`:

```bash
uv run --frozen pytest packages/engine/tests apps/api/tests packages/arena/tests packages/telemetry/tests packages/microbench/tests -q
```

Reproduce additional probes from `python/`:

```bash
uv run --frozen python ../docs/research_raw/review_2026-09-22/probes.py --out /tmp/monopolybench-review-probes.json
```

[probe_results.json](probe_results.json) preserves this review's results;
[probes.py](probes.py) preserves the method. Some probes intentionally call private
helpers or use synthetic data and are labeled accordingly. They do not replace
public-path regression tests for subsequent fixes.

## Priority findings

Severity here means impact on the proposed research, not an assertion that a
published claim or paid campaign has already been corrupted.

| Priority | Finding | Evidence and consequence | Proposed next action / affected surfaces |
| --- | --- | --- | --- |
| Before new games | Bankruptcy behavior differs materially from the cited rules | `engine.py:2909–2978` transfers buildings intact to a player creditor, does not collect the associated mortgage-transfer interest, and returns bank-creditor properties to unowned status without queuing their immediate auctions. This changes asset windfalls, rent exposure, and house inventory. | Establish the intended ruleset; implement/test conformance or explicitly version and explain deviations. Engine, events, replay compatibility, documentation, and relevant case interpretations. |
| Before reusing campaign runs | Run identity and resume checks are incomplete | Changing `max_trade_exchanges` to 1 leaves all smoke-plan run IDs and resume keys unchanged. `_completed_run_exists` accepts eleven empty files. `write_campaign_plan` rewrites campaign plans before reuse checks. | Bind reuse to complete treatment/configuration/source hashes, verify contents and completion, and preserve immutable manifests. Arena, campaign contracts, recovery tests. |
| Before reporting micro capability | Micro scores reward wording and use incomplete cash accounting | All 130 scenarios award 10–30% of normalized points for keyword mentions/nonempty messages. Text-only edits changed 14 builder-action labels. `_cash_after_action` accounts for purchases, bids, and jail fines, but ignores build/trade/mortgage cash changes. | Version downstream scoring, report action quality separately from rationale-text features, validate cash accounting against engine transitions, obtain independent judgment for subjective preferences. Microbench, metric schemas/reports, tests. |
| Before ranking models | Existing rank and uncertainty outputs do not implement the proposed estimands | `_rank_players` ranks by final wealth/cash and assigns distinct ranks to complete ties in insertion order; it does not rank bankrupt players by survival. Campaign CIs resample individual scalar game outcomes without seed blocks. | Freeze placement/tie/censoring rules and implement matched block-aware analysis. Telemetry, campaign analysis, tests. |
| Before spending | The configured campaign budget is not a strict within-game ceiling | `run_campaign` checks `should_stop_for_budget` before execution and after a full game; the runner receives no campaign ceiling. The historical-max estimate is absent before the first run. | Define approved bounded overshoot or implement accounting checks/reserves before further calls. Preserve partial cells and missing usage. Arena/accounting/campaign tests. |
| Before paper-facing aggregates | Missing data can become zero | `_leaderboard_payload` feeds costs and other nullable metrics through `_number`, whose fallback is 0.0. | Preserve missing values and report coverage with each statistic; keep operational dashboard summaries distinct from paper tables. Arena/telemetry. |
| Before claiming reusable validation | Full-event replay is narrower than full-package integrity | Replay reads events, actions, and run configuration; it does not validate snapshot, prompt, decision-log, or manifest contents. R166/R172 duplicates pass full-event replay. | Add a corruption-detection matrix assigning each artifact defect to its validator. Keep existing state/full-event distinctions. |
| Before social prevalence/model claims | Independent behavioral validation remains incomplete | The calibration manifest reports 0/3 independent human coders, no adjudication, no passed calibration. The 24 packets are a development set, not a prevalence sample. | Adapt the existing codebook to the new questions; complete judge/evidence-challenge records and the chosen human validation/negative-audit workflow. Analysis only. |
| Before release | Verification and reproduction have avoidable gaps | Both wrappers omit microbench tests; Mac mypy currently fails; recorded paper outputs are missing locally. | Repair verification, include microbench, document/rebuild release outputs, validate the reproduction recipe. Tooling/docs/paper artifacts. |

### Bankruptcy is a scientific issue

The exact booklet cited in the manuscript, [Hasbro 00009](https://www.hasbro.com/common/instruct/00009.pdf),
requires buildings to be sold back at half cost on bankruptcy to another player,
requires mortgage-transfer interest, and auctions property surrendered to the bank
(classic rules, PDF page 8). The current code behaves differently.

The synthetic helper probe gave a debtor $5, two brown houses, and a mortgaged
railroad. The creditor received $5 and retained both houses; bank house inventory
stayed at 30. This checks the transfer handler, not an entire playable trajectory.
The existing `test_bankruptcy_on_rent_transfers_assets` also explicitly expects the
creditor's cash to increase only by the debtor's $5 despite a mortgaged deed.

The exploratory manuscript describes a declared ruleset and carefully limits
external validity. That helps, but does not substitute for an explicit deviation
table. Historical paths remain valid descriptions of this implementation. Changing
the engine does not retroactively change those paths; keep the old compatible
implementation and version the next cohort. Audit which mechanism cases depend on
inherited development before using them as evidence of classic Monopoly strategy.

### Measurement must distinguish constructs

The micro wording probe held each builder action and its arguments fixed, blanked
the two text fields, then inserted rubric terms and a generic public message.
Fourteen labels changed: seven acceptable-to-preferred, seven bad-to-acceptable.
This does not show real models intentionally gaming the rubric. It demonstrates
that the scalar mixes action selection with easily satisfied textual features.

The cash helper also returns $700 after a $200 build in the dark-blue fixture,
where direct accounting gives $500. Both exceed that fixture's $150 threshold, so
that example establishes a wrong cash calculation, not an observed threshold flip.
The next scorer audit should test threshold crossings and all applicable action
types. Human review is needed for strategic preferences, not for arithmetic.

Six legal baseline policies are already available. Their names should not be treated
as quality guarantees: `builder` and `always_buy` accept every legal trade response;
several proposal paths construct empty offers. Random legal action selection also
uses constructed arguments rather than a uniform draw over every legal parameter
combination. Use these as documented reference policies and verify intended
contrasts before adding new ones or calling one an economic-competence baseline.

The rank helper's synthetic equal-wealth players, bankrupt at turns 1, 100, and 50,
receive ranks 1, 2, and 3 in insertion order. These are wealth-based ordinal ranks,
not finishing placement. Decide whether tied wealth should remain tied and whether
Paper B instead needs elimination-order placement. Do not silently reinterpret old
`final_rank` fields.

## Assessment of the two papers

### Paper A: credible foundation, missing validation results

The strongest contribution is the ability to connect legal opportunity, selected
action, fallback/retry, state consequence, and artifact provenance in one economic
trajectory. The eight-game corpus already supplies diagnostic examples: interface
failure near insolvency, conversion of trades into development, and finite-inventory
effects. The split between state replay and observation provenance is useful.

Paper A needs results showing that the instrument measures what it claims:
rule-conformance/deviation coverage, corruption detection, independently checked
metric calculations, known contrasts among reference policies, and representative
model experiments. Passing tests and artifact volume alone do not supply this.

The existing July manuscript is more mature than a skeleton: audited claims, exact
corpus totals, limitations, case evidence, and a sealed source hash already exist.
Preserve it as the exploratory manuscript. Reuse its evidence contract and bounded
cases; reshape its central result around validation for the new Paper A. The
recorded PDF/ZIP being absent here is a reproduction gap, not proof they never
existed. The Apache license and citation file already exist.

### Paper B: coherent questions, not yet a separate empirical result

The current eight games are heterogeneous exploratory observations. Their ledger
contains 3,696 applied decisions, 3,790 attempts, 20,474,750 recorded tokens, and
$113.84 recorded historical cost. These are not thousands of independent samples.
Seat order, opponent roster, endpoint/version, and exposure differ. They support
mechanisms and codebook development, not stable model rankings or collusion rates.

I would narrow the initial substantive questions to:

1. How do liquidity and development decisions relate to survival and productive
   asset use under a fixed opponent roster?
2. When coordination is proposed, is it accepted, implemented, maintained, or
   abandoned, and what legal opportunities existed to act on it?
3. Which commitments or factual claims are contradicted by later/available evidence,
   and which apparent violations have benign explanations?

Capability and trustworthy communication remain separate dimensions. Coalition
play in a competitive board game is not automatically a violation of instructions.
Assess instruction compliance against the actual frozen prompts. Model-reported
private rationales provide evidence to examine, not privileged access to intent.

The existing codebook already provides much of this structure. Reconcile its old
judge-first and three-coder calibration requirements with the September local
review plan; write one current review contract. A documented reviewer workflow is
still needed even if no new automated judge service is built. Do not fabricate
human validation through additional agent passes.

Full historical traces exceed the bounded memory available to an acting model:
the prompt memory defaults include 20 public timeline entries and 10 private
rationales. When evaluating long-term consistency or breach, record whether the
relevant promise was still in the decision's actual input. The historical
exact-history proof illustrates why a fresh-memory micro fixture cannot stand in
for its original full-game decision.

## Campaign design assessment

The proposed 48 games are a useful planning option, not a power result. Two rosters
times six shared seeds times four cyclic rotations produce six seed blocks per
roster. The rosters share seeds, so cross-roster inference must preserve that
matching. Provider sampling is still stochastic; equal initial seeds do not ensure
equal future dice exposure after divergent actions.

Cyclic rotations balance absolute seat position but preserve the circular opponent
order. If conclusions require averaging over who acts immediately before/after a
model, counterbalance relative order too or explicitly condition on it. There is
no need to launch all 24 permutations automatically; define the estimand first.

The default campaign bootstrap is unsuitable as-is for this design. Predeclare the
unit of analysis and paired comparisons, preserve all rotations in a resampled
seed block, and retain shared seeds in cross-roster comparisons. Six blocks can
still yield wide/unstable uncertainty. Choose a precision target using suitable
variance evidence rather than treating game count as a publication threshold.

Freeze a small primary outcome set. Placement/survival requires explicit tie and
turn-cap handling. An economic trajectory endpoint needs a horizon and a policy for
bankruptcy and unfinished games; avoid averaging only surviving players. Cash,
development, rent, and the face-value asset proxy can then explain outcomes.

Do not interpret different-size rosters as a causal model-size experiment. Changing
the full opponent ecosystem changes the treatment. One roster with deeper seed
coverage is an option if the budget cannot support both with useful precision.

Define review capacity alongside provider spend. A linear extrapolation from the
eight historical games to 48 gives roughly 22,000 decisions and 2,800 three-turn
windows. That is workload planning only; it is not a prediction of campaign length
or behavior prevalence. Reserve time for negative windows and independent checks,
not just interesting candidates. The historical $100 E1 ceiling and BYOK projection
are not a budget for the new campaign and are not current prices/credit availability.

## Current literature and positioning

The June feedback's claim that there is no dedicated Monopoly LLM benchmark should
not be reused. [Ethan Pan's project page](https://about.ethanpan.me/bare/Ethan/research/monopoly-benchmark.html)
describes a Monopoly-based LLM benchmark with negotiation, coalitions, replay, and
rule-changing phases. This is a public project description; this review did not
establish a completed peer-reviewed evaluation or feature parity.

[Cattle Trade](https://arxiv.org/abs/2605.14537) reports 242 games with seven language
models and three deterministic agents, including behavioral trace analysis.
[Vending-Bench Arena](https://andonlabs.com/evals/vending-bench-arena) already studies
competitive economic interaction and coordination.
[CoffeeBench](https://arxiv.org/abs/2606.16613) studies long-horizon heterogeneous
firms using fixed reference agents around the evaluated agent.

My inference: the defensible distinction is validated analysis of liquidity,
development, finite inventory, and insolvency within an explicitly versioned,
replayable legal-action environment. Neither Monopoly familiarity nor observing
collusion by itself establishes novelty. An uncertainty-aware comparison table
should state exactly which measurement each neighboring environment enables and
which additional measurement this benchmark validates. This was a targeted
literature refresh, not an exhaustive novelty search or venue assessment.

## Recommended work sequence and completion criteria

1. **Settle and test the rules.** Produce a rule-to-code-to-test/deviation matrix.
   Resolve bankruptcy transfer behavior first, then interacting liquidation,
   inventory, auction, trade, and jail cases. Preserve legacy replay versions.
2. **Harden campaign identity, recovery, and accounting.** Treatment changes must
   invalidate reuse; malformed/incomplete evidence must not count as completed;
   spending semantics must match the approved limit; every failed/planned cell
   remains in the ledger. Add corruption and interrupted-run checks.
3. **Validate outcomes and reference policies.** Separate text features from
   action metrics, correct cash calculations, specify ranks/ties/censoring, and
   demonstrate known contrasts on targeted cases and unpaid policy runs. Add the
   micro suite to verification and repair Mac type checking.
4. **Freeze one behavioral and statistical contract.** Adapt existing codebooks,
   choose the small primary question set, plan review sampling and human checks,
   and implement seed-aware analysis with known synthetic contrasts.
5. **Prepare concrete campaign options.** Compare one deeper roster against two
   shallower rosters for precision, current route availability, review workload,
   and cost. Obtain a scoped spending decision only after a reviewable manifest
   and operational plan exist. Keep checks separate from campaign cells unless
   declared otherwise before execution.
6. **Execute, analyze, and make the two-paper decision from evidence.** Paper A's
   milestone is demonstrated instrument validity plus reproducible examples.
   Paper B's milestone is independently supported substantive findings beyond
   those examples. A sparse or ambiguous behavioral result must be reported
   honestly; it may justify a narrower Paper B or deferral.

The next implementation task should cover the first three packages with explicit
boundaries, rather than another roadmap rewrite or an immediate paid batch.
No prompts, rules, scoring contracts, or existing research files were changed by
this review. Subsequent behavioral changes require the repository's versioning,
prompt-preservation, replay, and artifact checks.
