# Preregistration Freeze Readiness

- Status: **not_ready**
- Freeze ready: **False**
- Required inputs: 23
- Worktree clean: False
- Provider calls: 0

## Blocking gates

- Missing required input: analysis/research_protocol/preregistration/inputs/ecological_campaign/campaign_config.json
- Missing required input: analysis/research_protocol/preregistration/inputs/endpoint_preflight.json
- Missing required input: analysis/research_protocol/preregistration/inputs/endpoint_window.json
- Missing required input: analysis/research_protocol/preregistration/inputs/ecological_campaign/execution_manifest.json
- Missing required input: analysis/research_protocol/preregistration/inputs/primary_seed_draw.json
- Missing required input: analysis/research_protocol/preregistration/inputs/ecological_campaign/run_matrix.json
- Missing required input: analysis/research_protocol/pilot/design_lock.json
- Missing required input: analysis/research_protocol/pilot/trajectory_fixture_repetitions_e1/manifest.json
- E1 empirical validation has not passed.
- The blinded E1 analysis matrix is incomplete.
- Power simulation has not selected a budget-approved design.
- The pilot design lock is absent or not final.
- E1-derived 20–30 fixture repetition coverage is incomplete.
- Confirmatory seed draw does not match the selected block count.
- Confirmatory execution manifest is absent or structurally incomplete.
- Endpoint execution window is absent, invalid, or not frozen.
- Comparison families remain draft.
- Analysis plan remains draft.

The freeze operation additionally requires every source input to be tracked
and the worktree to be clean. Existing frozen packages are never overwritten.
