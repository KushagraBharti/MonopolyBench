# Integrity Report: mock-321229807-87ca99d7

## Outcome

Status: **valid with provenance warnings**. There are no blocking completeness, replay, linkage, usage, cost, or package-integrity failures.

- Endpoint: bankruptcy at turn 115.
- Winner: Gemini 3.1 Pro Preview.
- Events/actions/resolved decisions: 2,488 / 366 / 366.
- State replay: passed, 1,024 compared events, zero mismatches.
- Artifact replay: passed, 2,488 compared events, zero mismatches.
- Model call attempts: 377, including 11 retry attempts.
- Actual OpenRouter cost: $14.6143825.
- Reported tokens: 1,626,640 input; 362,227 output; 291,160 reasoning; 1,988,867 total.

## Freeze And Packaging

The source run and quality-check folders were moved with `git mv` into the canonical saved-game layout. Tree hashes were computed before and after the move and matched:

| Tree | Files | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `run/` | 2,409 | 40,801,519 | `75f647ae4c86656e1f21fa008015883fe5e2c71caa320071214fea1ab94a4842` |
| `quality_check/` | 754 | 9,185,413 | `ad9dbfbdb2a02cfa52e26ed4022952916569ed9859f602c3dc760ce8fa5c7913` |

All 41 file hashes in the original `run/artifact_manifest.json` match. The intake commit is `e2623b39ebc054283197a1021a60910172f0279d`; the source artifacts do not record the commit used at run time.

## Completeness

All 44 top-level artifacts prescribed by `scripts/standardize_saved_games.py` are present, with no missing or extra top-level entries. Event sequence numbers are contiguous from 0 through 2,487.

Each of 377 call attempts has:

- one unique `usage_attempts.jsonl` row;
- five prompt artifacts under `run/prompts/` (1,885 files total);
- one request and one response text file under `quality_check/` (754 files total).

There are 116 canonical turn snapshots (`turn_0000.json` through `turn_0115.json`) and 482 total snapshot/checkpoint files. The final snapshot is `GAME_OVER`; its cash/bankruptcy state agrees with `summary.json` and the scorecard, which agree on winner, endpoint, and turn.

Warnings:

- Run-time source commit, explicit prompt hash, and explicit ruleset hash are not recorded.
- The manifest records medium reasoning effort and omitted max-token controls, but does not explicitly record whether temperature was sent.
- There is no separate `responses/` directory; complete response JSON is under `run/prompts/` and response text is under `quality_check/`.
- Manual review label/summary artifacts are absent. No qualitative review was authorized or performed.

## Replay

A fresh read-only replay was performed with the current `build_replay_verification_reports` implementation. It reproduced both source reports exactly:

| Gate | Status | Compared events | Original hash | Replayed hash | Mismatches |
| --- | --- | ---: | --- | --- | ---: |
| State | Passed | 1,024 | `bfaff3cb…c3dd` | `bfaff3cb…c3dd` | 0 |
| Full artifact | Passed | 2,488 | `bde49339…2596` | `bde49339…2596` | 0 |

Missing/extra actions and events are all zero. No canonical replay artifact was rewritten.

## Calls, Retries, Fallbacks, Usage, And Cost

The 366 resolved decisions reconcile one-to-one with 366 applied actions. The 377 attempt records reconcile one-to-one with 377 usage rows.

- Valid attempts: 364.
- Invalid attempts: 13 (11 malformed, 2 illogical).
- Corrective retry attempts: 11.
- Deterministic action fallbacks: 2.
- Provider-route fallbacks: 0.
- Missing actual usage rows: 0.

The two deterministic fallbacks are recorded in `quality/call_reconciliation.json`. Attempt sums equal `usage.json` for every token, cache, latency, and cost field. `cost_report.json` equals the usage cost exactly. `summary.json` rounds cost to six decimal places; its total-token count is exact.

Reasoning tokens remain a separate raw field and are not added to output or reported total tokens.

## Deterministic Outputs

Standardization generated 26 tables, 23 plots, three standard reports, coverage/inventory CSVs, the saved-game manifest, and the share zip. Expanded analysis generated:

- 85 trade episodes and 170 player-episode rows;
- 0 auction episodes (the canonical auction stream is present and empty);
- 18 mortgage episodes;
- 52 cash-reason rows;
- decision, cash-ledger, player, semantic-status, definitions, and report outputs.

The share zip is validated against the current `analysis/` tree after finalization.

## Commands

Commands were run from the repository root:

```powershell
python scripts/standardize_saved_games.py mock-321229807-87ca99d7
python scripts/analyze_saved_game.py saved_games/mock-321229807-87ca99d7
```

Both exited 0. Replay verification used a read-only inline Python invocation of `monopoly_arena.replay_verification.build_replay_verification_reports` with the packaged `run/`; it exited 0.

The `uv run` environment did not expose analysis-only `matplotlib`, so standardization used system Python 3.13.9 with pandas 2.3.3 and matplotlib 3.10.6. No provider or LLM call was made.
