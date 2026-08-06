# Exact-History Fixture Format Migration

Status: v2 is canonical; v1 is retained as a failed implementation record  
Date: 2026-07-29  
Provider calls used to detect or repair the issue: 0

## Finding

The v1 extractor proved byte equality while the replayed decision and memory objects
were still in memory, then wrote those objects as sorted JSON for inspection. Sorting
did not change their JSON meaning, but it changed object insertion order. The current
prompt builder serializes objects in insertion order, so a write/read/reconstruct test
against the persisted v1 inputs failed for all 12 fixtures.

This is a derived-fixture serialization defect. It does not affect the original saved
game artifacts, the original prompts, the source game actions, or the earlier in-memory
engine/event reconstruction result.

## Evidence

- v1 extraction-time comparison: 12/12 reported exact.
- v1 independent persisted-input execution precheck: 0/12 exact.
- v1 precheck failure class: prompt/tool byte mismatch after sorted-JSON reload.
- v2 independent persisted-input execution precheck: 12/12 exact.
- v2 errors: 0.
- Paid execution remains blocked solely by the independent credit preflight.

The failed v1 collection and its failed precheck remain preserved at:

- `analysis/research_protocol/architecture_proof/fixtures/`
- `analysis/research_protocol/pilot/fixture_repetition_execution_e0/`

They must not be used for repeated-query execution.

## Correction

`trajectory_fixture_v2` adds compact, insertion-order-preserving prompt inputs:

- `source/decision_ordered.json`
- `reconstructed/engine_decision_ordered.json`
- `reconstructed/prompt_memory_ordered.json`

Sorted, indented companions remain available for human inspection. The execution
runner now refuses v1 fixtures and independently rebuilds the first-attempt system,
user, and tool bytes from v2 persisted inputs before it can authorize a provider call.

Canonical zero-call outputs:

- v2 fixtures: `analysis/research_protocol/architecture_proof/fixtures_v2/`
- v2 repetition plan:
  `analysis/research_protocol/architecture_proof/repetition_plan_v2/`
- v2 execution precheck:
  `analysis/research_protocol/pilot/fixture_repetition_execution_e0_v2/`

## Frozen identifiers

- v1 collection tree SHA-256:
  `311c38dc6c18f4c19c70747bb0d609f1c3dc96ea85dcb3bc4c5ba8555a0fb525`
- v2 collection tree SHA-256:
  `f8157cc306ca46f25283b9930eb895b6009142b5bb40bb6e04caf072dd65337f`
- v2 collection manifest SHA-256:
  `483d6434c7245de3f1cc9788878f5ae01363e510c276c39ace24c6718a4143a7`

