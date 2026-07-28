# Verification Log

All commands were run from the repository root. No command made an LLM/provider call.

| Command | Exit code | Result |
|---|---:|---|
| `uv run --project python --all-packages --with matplotlib --with pandas python scripts/standardize_saved_games.py mock-64394-c3bb8d94` | 0 | Standard analysis, plots, reports, manifest, and zip generated. |
| `uv run --project python --all-packages python scripts/analyze_saved_game.py saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3 --output-dir saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/analysis/expanded_metrics` | 0 | Expanded deterministic metrics generated. |
| `uv run --project python --all-packages --with matplotlib --with pandas python saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/analysis/tools/regenerate_cost_plots.py` | 0 | Four affected cost plots regenerated from canonical CSV tables with unique cent-level ticks. |
| `uv run --project python --all-packages python saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/analysis/tools/verify_integrity.py` | 0 | Prior quantitative worktree materialization: state/artifact replay, source-manifest bytes, and usage cost reconciled. The later canonical-blob check below supersedes the source-byte interpretation after the branch rematerialized LF blobs. |
| `uv run --project python --all-packages pytest -q python/packages/telemetry/tests/test_expanded_metrics.py python/apps/api/tests/test_replay_runner.py` | 0 | 3 tests passed. |
| `uv run --project python --all-packages python saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/analysis/tools/verify_integrity.py` | 1 | Qualitative recheck: state replay passed (2,606 events), artifact replay passed, 346 actions/355 attempts reconciled, and usage cost matched. Source-manifest comparison reported 373 run and 355 quality-check line-ending mismatches; direct source-commit blob comparison below adjudicates provenance. |
| `git diff --name-status 2d7abea16a20ab2a4174784c8009c4f4b80c6274 -- saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/run saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/quality_check` | 0 | Empty output: no canonical raw artifact differs from the source commit. |
| `uv run --project python --all-packages pytest -q python/packages/telemetry/tests/test_expanded_metrics.py python/apps/api/tests/test_replay_runner.py` | 0 | Qualitative final gate: 3 tests passed. |
| `python -` qualitative structure validator (command recorded in task transcript) | 0 | 53 blocks exactly cover turns 0–157; maximum width 3; 346 actions, 346 decision starts/resolutions, and 355 attempts reconcile; 28 evidence rows, 14 lifecycle rows, 28 communication rows, and 12 review packets parse; eight case studies contain every required section. |
| Manual inspection of `cost_by_model.png`, `cost_by_turn.png`, `cost_per_call.png`, and `cumulative_cost_by_call.png` | N/A | All four plots remain visually legible with cent-level axes; no regeneration was required in the qualitative phase. The shared formatter defect and prior package-local regeneration remain documented in `analysis/quality/plot_quality.json`. |
| `python -` deterministic package refresh (command recorded in task transcript) | 0 | Rebuilt `generated_artifact_hashes.json` for 94 non-self-referential analysis files, created a sorted fixed-metadata analysis ZIP, refreshed its SHA-256 sidecar, and updated `saved_game_manifest.json`. |
| `python -` generated-manifest/ZIP validator (command recorded in task transcript) | 0 | Every generated hash, byte count, ZIP member, fixed timestamp/mode, extracted byte, checksum sidecar, and saved-manifest ZIP field reconciled; in-memory rebuild was byte-identical. |

The raw source also contained `run/replay_report.json` version `replay_report_v1`, which passed with 2,606 original/replayed events. The current verifier produced split downstream state and artifact reports under `analysis/quality/`; both passed with zero mismatches.

## Source-hash provenance

The immutable `source_artifact_hashes.json` describes original CRLF source bytes. Canonical commit `2d7abea16a20ab2a4174784c8009c4f4b80c6274` contains LF-normalized blobs. The worktree matches those canonical blobs exactly.

- Run: 2,319 expected and actual files, no missing or extra files; 373 manifest-byte mismatches attributable to CRLF→LF normalization.
- Quality check: 710 expected and actual files, no missing or extra files; 355 manifest-byte mismatches attributable to CRLF→LF normalization.
- First run mismatch, `run/actions.jsonl`: manifest 244,046 bytes / `55cd74c8a59d0c3d14e22b2083309e72cb6903d0a59a172e5be6015cb3011165`; worktree and source-commit blob 243,700 bytes / `fda13c641cae47863679a1b06c48141a349ae0e8556f929c21c3e8663ca88ac8`. Converting the canonical LF blob to CRLF reproduces the manifest bytes and hash exactly.
- First quality-check mismatch, `quality_check/decision_mock-64394-c3bb8d94-dec-000000_response.txt`: manifest 3,531 bytes / `106b76547a54a80a6fc6401a861250f6a905e2cfa33fdda9a759fdc15011d753`; worktree and source-commit blob 3,523 bytes / `84e9188d61d278f1f4277562db0ce032e9afbd845cac7b8bb4839b369f71540c`. Converting the canonical LF blob to CRLF reproduces the manifest bytes and hash exactly.

No raw evidence or source manifest was changed. This is a provenance distinction, not a semantic or replay defect.
