# Integrity Report: mock-2413970733-53b199c1

## Result

- Package status: **pass with documented warnings**.
- Canonical artifact presence: **44/44 present**; no unexpected canonical top-level artifacts.
- Byte preservation: **passed** for the canonical run, quality checks, and pre-resume recovery evidence.
- State replay: **passed** (1621 compared events; zero mismatches).
- Artifact replay: **passed** (4073 compared events; zero mismatches).
- Call/cost reconciliation: **passed** (613 decisions, 631 attempts, 613 applied actions, zero missing usage rows).

## Frozen Sources

| Evidence tree | Files | Bytes | Intake/package inventory SHA-256 |
| --- | ---: | ---: | --- |
| Canonical `run/` | 3,984 | 68,046,355 | `0ed2893cfd553410e006d146f84b6c2e0536f5f17875c0f30a4e31bbab9d5870` |
| `quality_check/` | 1,262 | 15,208,599 | `58d6ed9c2a992a9d32e63924ee1f654de24e4f8aefd9e141dc5463c138d17a3b` |
| Pre-resume recovery evidence | 2,068 | 25,405,334 | `0857c2c9770f9cbcfbf72c69db4b9c91c9252d683ee00ffbcee837ac71b826fa` |

Per-file hashes are in `analysis/manifests/source_artifact_hashes.json`.

## Replay

The saved reports and an independent read-only recomputation agree. The action sequence contains 613 actions and reproduces all 4073 events. State canonical hash: `772ab9601f35d31c82df76c65eef2710ed4905e041718902de8a155b51c3015e`. Full artifact canonical hash: `94c7d8301a3d77b97e54e2211fb70c8b7c7e0685ccc030068960bf9cab884f48`.

## Calls, Retries, Fallbacks, And Cost

- Decisions: 613.
- Initial attempts: 613; corrective retry attempts: 18; all attempts: 631.
- Attempt outcomes: 611 valid, 16 malformed, 4 illogical.
- Deterministic fallback decisions: 2. Provider-route fallbacks: 0.
- Actual OpenRouter usage coverage: 631/631 attempts.
- Input tokens: 2,913,325; output tokens: 564,288; reported total: 3,477,613; reasoning tokens: 426,431; cached tokens: 53,696.
- Actual cost: $24.6045758. Attempt rows, `usage.json`, and `cost_report.json` reconcile; the only delta is binary floating-point noise below 1e-14 USD.

Reasoning tokens are preserved as a separate raw field and are not added to reported total tokens a second time.

## Warnings

1. `decisions.jsonl` contains two non-identical `decision_started` rows for `...dec-000242` around the resume boundary (lines 485-486). There is still exactly one resolved decision, one applied action, and complete attempt accounting for that ID.
2. The ideal guide names a standalone `responses/` directory, but this run stores complete response artifacts in `run/prompts/*_response.json` and `quality_check/*_response.txt`.
3. The run-time repository commit is not recorded in raw metadata. The intake/source commit is `e2623b39ebc054283197a1021a60910172f0279d`.
4. `run_manifest.json`, `provider_route_summary.csv`, and raw `metric_definitions.json` are not present under those exact names; equivalent evidence is distributed across `experiment_manifest.json`, per-response provider fields, `pricing_snapshot.json`, and derived expanded metric definitions.
5. Manual review label files are absent. This task explicitly excluded qualitative review, so no labels were fabricated.
6. The standardizer uses whole-dollar labels for every money plot, which made sub-dollar cost ticks ambiguous. The four cost plots in this package were deterministically regenerated from their standardized CSV tables with two-decimal USD axes; shared source code was not changed.

## Focused Verification

- `uv run --project . --package monopoly-telemetry pytest packages/telemetry/tests/test_expanded_metrics.py` from `python/`: exit 0, 1 passed.
- `uv run --project . --package monopoly-api pytest apps/api/tests/test_replay_runner.py` from `python/`: exit 0, 2 passed.
- `uv run --project python python <temporary package/hash/archive validator>`: exit 0; validated 7,314 source hashes, 7,393 package checksums, 75 zip members, 3,344 JSON files, 18 JSONL files/20,120 rows, and 38 CSV files.

## Scope

This package supports integrity, replay, deterministic metric, usage, and cost claims. It makes no qualitative claims about negotiation, bankruptcy windows, deception, collusion, promises, or case studies.
