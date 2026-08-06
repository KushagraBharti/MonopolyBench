# Preregistration Freeze Contract

## 1. Purpose

The preregistration package is the immutable boundary between calibration and the
confirmatory ecological campaign. It is not a planning folder and it is not created
merely because campaign code is ready. The freeze records exactly what was known,
chosen, and executable before the first E2 provider call.

The builder is downstream-only. It does not change the engine, prompts, tool schemas,
retry policy, or provider requests.

## 2. Required completed evidence

The package may be frozen only when all of the following pass:

1. E1 contains every planned ledger row, at least six integrity-eligible games, and
   complete four-rotation coverage for every seed block used for nuisance estimation.
2. Every integrity-eligible E1 game passes decision/action bijection and state replay.
   Artifact replay defects must either pass or be registered with a bounded,
   outcome-independent eligibility rule.
3. The blinded E1 analysis matrix is complete and contains no model-identity mapping.
4. Power, precision, interval coverage, attrition, and cost simulations are complete.
5. A design lock names the final primary block count, games, diagnostic fixture
   repetitions, robustness rings, sentinels, and approved cost ceiling.
6. The E1-derived exact-history set contains 20–30 fixtures with complete planned-call
   coverage and preserved failures.
7. The exhaustive social-judge protocol, masking policy, output schema, human
   verification strata, and judge-negative audit rule are fixed. Human verification
   results are a later publication-facing social-claim gate, not an E2 execution
   prerequisite.
8. The confirmatory seed draw, cyclic rotations, and randomized sequential execution
   manifest are complete.
9. Roster, exact OpenRouter model IDs, exact provider constraints, endpoint policy,
   provider-default sampling disclosure, retry/fallback policy, and execution window
   are fixed.
10. Primary estimands, smallest meaningful effects, comparison families,
    multiplicity, inclusion/exclusion, stopping, rerun, missingness, and analysis code
    are fixed.

## 3. Endpoint and time window

The endpoint window is chosen from E1 wall-clock duration without inspecting model
outcomes:

\[
W_{\max}
=
\min(21\text{ days},
\max(72\text{ hours},1.5\,\widehat W_{\mathrm{sequential}})).
\]

The frozen file records:

- earliest permitted UTC start;
- latest permitted UTC finish;
- exact model and provider constraints;
- endpoint/model metadata snapshot hashes;
- maximum metadata-snapshot age at campaign start;
- sentinel placement rule;
- pause rule when a route disappears or returned provider/model metadata changes.

Randomized execution and temporal sentinels measure service variation. They do not
turn a mutable hosted model into a deterministic object.

## 4. Canonical frozen tree

```text
analysis/research_protocol/preregistration/frozen/
  protocol/
    scientific_protocol_v2.md
    downstream_bridge_contracts.md
    campaign_control_audit.md
    social_evidence_codebook.md
    llm_judge_social_evidence_protocol.md
    preregistration_freeze_contract.md
  pilot/
    e1_validation.json
    e1_analysis_matrix_manifest.json
    power_simulation.json
    design_lock.json
    budget_projection.json
    communication_packet_manifest.json
    trajectory_fixture_repetition_manifest.json
  campaign/
    primary_seed_draw.json
    campaign_config.json
    run_matrix.json
    execution_manifest.json
    model_roster.json
    endpoint_window.json
    endpoint_preflight.json
  analysis/
    comparison_families.json
    analysis_plan.json
    social_judge_rubric.json
  provenance/
    source_hashes.json
    tree_hash.json
  preregistration_manifest.json
  preregistration_manifest.sha256
```

The copied files are the preregistration record. Their original working locations
remain canonical operational inputs but must hash-identically at execution.

## 5. Git and hash boundary

The builder requires every source input to be tracked, a clean worktree, and a single
source commit. It never overwrites an existing frozen package.

The freeze is two-phase:

1. commit all source inputs and analysis code;
2. build the frozen tree from that clean commit, then commit the frozen tree.

`preregistration_manifest.sha256` is a detached SHA-256 seal over the canonical
manifest bytes. Git history authenticates the committed provenance boundary. A
separate cryptographic researcher signature may be added, but a checksum is never
described as a personal digital signature.

## 6. Execution gate

Before E2, the campaign runner or a separate verifier must prove:

- current `HEAD` descends from the preregistration source commit;
- each operational input hash equals the frozen copy;
- current UTC time lies inside the endpoint window;
- the preflight snapshot is fresh and all exact routes are available;
- credits satisfy the frozen budget gate;
- no planned cell is missing or duplicated.

If any check fails, E2 does not start. A protocol amendment creates a new version; it
never mutates the frozen package.
