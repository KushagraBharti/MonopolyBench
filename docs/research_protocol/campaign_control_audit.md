# Campaign Control Audit

Audit date: 2026-07-29  
Audited commit: `7ce810ebb71bbe102335304f43b17eaa45f43512`  
Scope: campaign planning/execution, OpenRouter routing, endpoint identity, sampling,
and execution-time drift. Engine and prompt behavior are out of scope for change.

## 1. Gate summary

| Control | Current state | Pre-pilot disposition | E2 requirement |
|---|---|---|---|
| Seed × cyclic-seat expansion | Implemented and tested | Accept | Freeze manifest |
| Repetitions per seed | Implemented and tested | Accept | Pilot selects count |
| Execution order | SHA-256-keyed randomized manifest implemented and tested | Resolved | Freeze manifest |
| Configured concurrency | Requested and effective values distinguished; effective value is 1 | Resolved by disclosure | Sequential randomized execution |
| Provider routing in ordinary saved games | Pinned in `run_config.json` | Accept for historical artifacts | Preserve exact provider constraint |
| Provider routing in `long_campaign` adapter | Validated constraint reaches `PlayerConfig` | Resolved | Verify returned route post hoc |
| Endpoint ID | Live catalog and exact endpoint-route preflight captured and execution-gated | Resolved for E1 planning | Refresh immediately before execution |
| Immutable model revision | Not guaranteed by mutable provider aliases | Unavailable | Time-bounded claim and sentinel repeats |
| Temperature / `top_p` | Not sent by production resolver | Disclose | Register provider-default sampling |
| Roster `top_p` metadata | Present as `null`; ignored by adapter | Disclose | Keep null; make no control claim |
| Execution timestamps | Campaign-row UTC start/end plus call timing | Accept | UTC window and sentinel schedule |
| Usage/cost metadata | Recorded when provider returns it | Partial | Missingness thresholds and reconciliation |
| Prompt preservation | Persisted-input v2 reconstruction plus exact saved prompt artifacts | Accept | Hash gate before each campaign |
| Available-credit gate | Enforced before the first generation call; complete planned ledger retained | Resolved | Freeze threshold and fresh snapshot |

The two implementation blockers are resolved. The E1 dry run contains eight cells,
an outcome-blind seed draw, a deterministic randomized execution manifest, explicit
provider constraints, and complete seat balance. Paid execution is currently blocked
by the independent credit gate, not by engine or campaign-control readiness.

The first independent repetition-runner precheck also caught a derived-fixture defect:
the v1 writer sorted JSON keys after an in-memory equality check, which preserved JSON
meaning but broke byte-exact prompt reconstruction after reload. The original run
artifacts were unaffected. The preserved failure and v2 correction are documented in
`analysis/research_protocol/architecture_proof/fixture_format_migration.md`. The v2
collection now passes 12/12 persisted-input system/user/tool reconstruction checks,
and the runner refuses the v1 format.

## 2. Sequential execution

### Finding

The original runner iterated natural matrix order and merely recorded `concurrency`.
The revised runner still executes one game at a time, but it executes fixed cells by
`execution_rank` from a separately persisted SHA-256-keyed randomization manifest.
Natural `run_index`, run ID, seed, and seat assignment remain unchanged.

### Resolution contract

Implemented for E1:

- `execution_manifest.json` and `execution_manifest.jsonl`;
- `execution_rank`, `execution_order_key`, `execution_order_seed`, and original
  `run_index`;
- execution in manifest order without changing cell identity;
- observed UTC campaign-row start/end fields;
- complete ledgers after max-run, budget, and failure stops;
- tests for deterministic ordering, permutation completeness, failure-stop
  accounting, max-run accounting, and budget-stop accounting.

Pilot execution is sequential in randomized order unless a separate concurrency
implementation passes rate-limit, ordering, and artifact-isolation tests. Sequential
randomized execution is preferable to unvalidated concurrency.

## 3. Provider routing

### Finding

Historical canonical runs contain explicit provider constraints such as:

```json
{"only": ["openai"], "allow_fallbacks": false}
```

The regular resolver forwards `PlayerConfig.provider` to first attempts and retries.
The original long-campaign adapter omitted it. The revised research registry validates
`provider`, carries it into every run-matrix actor, and passes it into
`PlayerConfig`. The primary roster specifies one exact OpenRouter provider tag per
model and `allow_fallbacks: false`.

### Resolution contract

Completed before E1:

- research-registry provider metadata for every primary actor;
- JSON Schema and TypeScript contract coverage;
- roster-manifest, matrix, `PlayerConfig`, request, run-config, and result-ledger
  propagation;
- fallback routing disabled;
- endpoint preflight confirms one currently available exact-tag endpoint supporting
  `tools`, `tool_choice`, and `reasoning_effort` for every primary model;
- a forced tool call confirms the returned model and provider on every exact route;
- OpenAI is the sole BYOK-required actor. Anthropic, Google, and xAI are budgeted as
  OpenRouter-credit routes;
- every OpenAI campaign response must report provider `OpenAI` and
  `usage.is_byok=true`. The campaign writes a billing-policy violation artifact and
  fails the cell before applying an action if either condition is not confirmed.

Post-run route reconciliation remains mandatory. A mismatch is a technical protocol
violation and is retained; it is not reassigned to the intended provider.

This changes experimental routing configuration, not model-facing message or tool
content.

## 4. Endpoint pinning

### Finding

The campaign records an OpenRouter model ID, but a public model ID may resolve to a
mutable provider implementation. The repository has no immutable vendor-weight
revision identifier.

### Resolution contract

The authenticated preflight at
`analysis/research_protocol/control_audit/openrouter_preflight.json` combines catalog
metadata with one separate forced tool call through each of the four exact routes. It
verifies the returned model/provider identities, tool-call structure, and registered
billing policy—including OpenAI BYOK—and contains no API key. These calls use a
preflight-only prompt and do not construct or modify a MonopolyBench game prompt.

Before E1 execution and again immediately before E2:

- query the official OpenRouter model catalog;
- store the raw response and SHA-256 hash;
- record availability, canonical ID/slug, creation metadata, architecture,
  supported parameters, context length, pricing, and provider routing;
- issue no paid call to an unavailable or mismatched endpoint;
- issue one forced tool call per exact route and require the registered billing-policy
  verdict before campaign authorization;
- preserve returned model/provider identifiers and OpenRouter request IDs per call;
- execute within a preregistered UTC window;
- state claims as applying to the endpoint as served in that window.

E1 additionally names the secret-free preflight artifact in its campaign config,
requires an authorized verdict, requires the roster-registry hash to match, and
rejects a snapshot older than six hours. The preflight payload and its source-byte
SHA-256 are copied into `execution_preflight_snapshot.json`. A failed gate preserves every cell as
`not_started_preflight_gate` and makes no generation call.

If an endpoint changes or disappears mid-campaign, stop under the registered endpoint
drift rule. Do not substitute a newer model into the same campaign ID.

## 5. Sampling parameters

### Finding

The production decision request forwards:

- model;
- system/user messages;
- tools;
- automatic tool choice;
- `parallel_tool_calls=false`;
- supported reasoning policy;
- optional provider constraint.

It does not send temperature, `top_p`, or a model seed. The registry's `top_p` fields
are currently `null`, and the long-campaign adapter would ignore non-null values.

### Disposition

For E1/E2:

- use the current production request unchanged;
- register sampling as `provider_default_unseeded`;
- keep all roster `top_p` values null;
- do not claim fixed temperature, `top_p`, or deterministic model generations;
- quantify stochasticity using fixture repetitions, full-game repetitions selected by
  the pilot, and time-sentinel cells;
- preserve raw request bodies so the absence of sampling fields is auditable.

Adding sampling parameters would change benchmark behavior and is not authorized in
this protocol.

## 6. Temporal drift

### Risks

- provider endpoint updates during a multi-day campaign;
- service load or routing changes;
- price updates;
- rate-limit or outage clusters;
- sequential order correlated with model/seat/seed.

### Controls

- randomized execution manifest;
- narrow preregistered execution window;
- provider pinning with fallback disabled;
- UTC timestamps and request IDs for every attempt;
- catalog/pricing snapshots before, during, and after;
- sentinel cells near beginning, middle, and end;
- mixed models that include execution rank/time as a sensitivity covariate;
- no replacement of failed cells based on observed game outcome.

Temporal sensitivity is reportable only from the sentinel design. Time covariates alone
do not identify endpoint drift.

## 7. Budget and failure controls

Before paid execution, freeze:

- available-credit snapshot;
- approved pilot and confirmatory maximum spend;
- preflight projected cost;
- actual-cost stop policy;
- maximum consecutive provider failures;
- maximum route mismatches;
- maximum missing-usage rate;
- maximum systemic replay-failure rate;
- resume and general technical-rerun rules.

The stop decision must use operational metadata only, not model ranking or interesting
behavior. E1 uses a $100 full-game campaign ceiling and a $110 end-to-end
available-credit gate. The calculation prices OpenAI at zero only when both the
preflight and runtime response confirm BYOK; Anthropic, Google, and xAI retain their
current OpenRouter prices. The gate covers the BYOK-adjusted maximum historical
eight-game envelope, 24 × 4 × 3 repeated fixture calls, and a 10% contingency.
The campaign now enforces that threshold before its first generation call. A missing
or unreadable credit response fails closed; an insufficient balance records all eight
cells as `not_started_credit_gate`. The current preflight fails that balance gate, so
no pilot game has started.

## 8. Required control artifacts

```text
analysis/research_protocol/control_audit/
  openrouter_preflight.json
analysis/research_protocol/pilot/
  seed_draw.json
  planning_runs/campaigns/<campaign-id>/
    execution_manifest.jsonl
    execution_manifest.json
    run_matrix.jsonl
    run_matrix.json
    endpoint_snapshot_before.json
    endpoint_snapshot_after.json
    execution_preflight_snapshot.json
    credits_before.json
    credits_after.json
    budget_report.json
analysis/research_protocol/pilot/controls/
  openrouter_catalog_mid.json
  endpoint_availability.csv
  provider_constraints.json
  sampling_policy.json
  observed_execution_order.jsonl
  temporal_sentinels.json
  budget_preflight.json
  control_verification_report.json
  source_hashes.json
  generated_hashes.json
```

## 9. Pre-pilot acceptance checklist

- [x] Randomized execution order is deterministic from its committed seed and tested.
- [x] Every primary LLM row carries a validated provider constraint.
- [x] Fallback routing is disabled.
- [x] Current endpoint availability and pricing are archived.
- [x] Request construction proves provider-default sampling with no hidden local overrides.
- [ ] UTC execution window and sentinel rules are frozen.
- [x] Budget and failure stops are frozen for E1.
- [x] Prompt hashes remain unchanged.
- [x] Focused campaign, contract, lint, type, and prompt-reconstruction checks pass.
- [ ] Available credits meet the $110 end-to-end E1 gate.

Until every item is checked, E1 remains blocked. At this checkpoint the only external
execution blocker is the credit balance; the UTC window is frozen only when funds are
available so its duration remains meaningful.
