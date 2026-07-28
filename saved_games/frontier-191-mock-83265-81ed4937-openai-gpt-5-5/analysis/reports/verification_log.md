# Deterministic verification log

All commands ran from repository commit
`fa773791718e3b5d8ff18448e2ad3fa42b375259`. No provider, model, or network
service was called.

## Generation

- `python scripts/standardize_saved_games.py frontier-191-mock-83265-81ed4937-openai-gpt-5-5`
  — passed; standardized analysis and expanded metrics regenerated.
- `python analysis/tools/build_deterministic_integrity.py` with the frozen
  source inventory supplied in `MONOPOLY_SOURCE_FREEZE` — passed.
- Prior analysis and ZIP confirmed under
  `saved_games/archive/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/`.

## Focused tests

- `uv run pytest -q` from `python/packages/telemetry` — 19 passed.
- `uv run --project . --with-editable ../../packages/engine --with-editable
  ../../packages/arena --with-editable ../../packages/telemetry pytest
  tests/test_replay_runner.py -q` from `python/apps/api` — 2 passed.

## Package validation

- `python analysis/tools/validate_deterministic.py` — passed.
- Complete pre/post source inventories match exactly: 5,043 files and
  81,969,149 bytes, with no missing, extra, or mismatched file.
- Every JSON/JSONL and CSV parses.
- Every PNG has a valid signature, IHDR, and plausible dimensions.
- Generated-output hashes match the declared manifest.
- ZIP CRC, exact entry-set parity, and byte-identical content parity pass.
- `saved_game_manifest.json` agrees with the final ZIP hash and entry count.

The replay validator intentionally accepts only the documented aggregate result
`state_passed_artifact_failed`; it does not accept a softened pass.
