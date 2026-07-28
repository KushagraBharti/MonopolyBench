# Verification Log

All commands were run from the repository root. No command made an LLM/provider call.

| Command | Exit code | Result |
|---|---:|---|
| `uv run --project python --all-packages --with matplotlib --with pandas python scripts/standardize_saved_games.py mock-64394-c3bb8d94` | 0 | Standard analysis, plots, reports, manifest, and zip generated. |
| `uv run --project python --all-packages python scripts/analyze_saved_game.py saved_games/mock-64394-c3bb8d94 --output-dir saved_games/mock-64394-c3bb8d94/analysis/expanded_metrics` | 0 | Expanded deterministic metrics generated. |
| `uv run --project python --all-packages --with matplotlib --with pandas python saved_games/mock-64394-c3bb8d94/analysis/tools/regenerate_cost_plots.py` | 0 | Four affected cost plots regenerated from canonical CSV tables with unique cent-level ticks. |
| `uv run --project python --all-packages python saved_games/mock-64394-c3bb8d94/analysis/tools/verify_integrity.py` | 0 | State/artifact replay passed; source hashes and usage cost reconciled. |
| `uv run --project python --all-packages pytest -q python/packages/telemetry/tests/test_expanded_metrics.py python/apps/api/tests/test_replay_runner.py` | 0 | 3 tests passed. |

The raw source also contained `run/replay_report.json` version `replay_report_v1`, which passed with 2,606 original/replayed events. The current verifier produced split downstream state and artifact reports under `analysis/quality/`; both passed with zero mismatches.
