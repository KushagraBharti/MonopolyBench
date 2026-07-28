# Deterministic integrity report

## Scope

This pass is integrity-only. Qualitative and semantic review is deferred, and
no LLM/provider/network call was made.

## Source freeze

- Source commit: `fa773791718e3b5d8ff18448e2ad3fa42b375259`
- `run/`: 3835 files,
  66557598.0 bytes,
  tree SHA-256 `d14d8c74621416ba87bfeca9e66527f27976de4a7847ba8fcb36b360fd15a79e`
- `quality_check/`: 1208 files,
  15411551.0 bytes,
  tree SHA-256 `2d0572f2f20f65d3f5790fca212791a000bfddcb0b87a56db18bbe63c0cd9de0`
- Combined tree SHA-256: `5b5a35d4d9497a1c23d2d1fb56d230993d545be3d18d4641b727ac789f3fcc64`
- Tree format: For each regular file recursively under the artifact-set root: relative POSIX path + NUL (0x00) + lowercase hexadecimal file SHA-256 + LF (0x0A), sorted by relative path using ordinal case-sensitive order; SHA-256 the UTF-8 byte stream.

The post-generation inventory exactly matches the pre-generation inventory:
no missing, extra, byte-count-changed, or hash-changed source file.

## Completeness and calls

- 3,972 events, 583 actions, 583 started decisions, and 583 resolved decisions
  form an exact decision-ID bijection with decision request/response events.
- 604 attempts reconcile to 21 retry decisions, 23 invalid attempts, two
  deterministic fallbacks, and exactly one applied action per decision.
- Every attempt has five JSON/text prompt artifacts and one quality-check
  request/response pair: 3,020 prompt files and 1,208 quality-check files.
- One initial attempt for `mock-83265-81ed4937-dec-000389` received provider
  HTTP 503 and has no usage or cost. Its retry succeeded. Missing usage remains
  null and is not estimated.
- Recorded OpenRouter actual cost reconciles exactly at
  `27.71173045`.
- The final `turn_0191.json` snapshot agrees with `summary.json`: winner
  OpenAI GPT 5.5, bankruptcy terminal reason, winner cash 718, and the other
  three players bankrupt with zero cash.

## Replay

Aggregate replay status is **`state_passed_artifact_failed`**. State replay
passes across 1,640 state-relevant compared events with canonical hash
`8c07e7d3c6b5d88b6ac9735315eb58182eb977de2d2c13d670842018ef32fc3c` and zero mismatch.
Full artifact replay compares all 3,972 events and fails first at index/sequence
669, event `mock-83265-81ed4937-evt-000669`, decision
`mock-83265-81ed4937-dec-000096`.

The original `LLM_DECISION_RESPONSE` records `valid=false` and
`error="fallback:illogical_after_retry"` for `reject_trade`; deterministic
replay records the already-applied fallback action as `valid=true` and
`error=null`. Original artifact hash:
`ca1c3493b525189d6025fb741cc206396efc2bc64c1b2a543eb517044b6eabf6`. Replay artifact
hash: `7d51584d2acdd326b97b4105251293bd17d8399c34b7d231b17eb488cd71adf1`.
`missing_actions=0`, `extra_actions=0`, and `decision_id_mismatch=false`.
Exact payloads are preserved in `quality/replay_verification.json`. This known
strict artifact mismatch is not softened to a pass and no raw record is altered.

## Legacy artifact-manifest audit

The checked-in raw bytes are canonical. The older `run/artifact_manifest.json`
has 35 exact matches,
4 mismatches, and
2 entries correctly declaring
absent optional review outputs. It remains untouched.

- `summary.json`: declared 5399 bytes / `b3146dd199e6a3610c076f80bc35974ddd792c7a800867eea58680a31149afb2`, current 5272 bytes / `178325e5d92e4c138274b0060b3d553b70c6001a679832e9699348d979e151c0`.
- `scorecard.json`: declared 1006399 bytes / `91861c0c1ea3e89f5285873cd223e5ede80b1e1c363e5b403e707799ef34df5e`, current 1006400 bytes / `8fe4fef8c85f1b820288f2f63f20af86fc5445ea68011cd50e98aca86ff5173e`.
- `scorecard_players.json`: declared 9677 bytes / `585a4f2df7b196e19e42338deaf8e2723e7a7fdce653ac21613fedcbc8a19658`, current 9678 bytes / `d44895259c40be64f045b35f068e7c8a77f2ccc3978682381662e57634dc17b1`.
- `replay_report.json`: declared 1621 bytes / `8c5293b825711ccf0e39d92eb627c0657f919292f6a096a5ac1276230486e2d2`, current 1621 bytes / `bd7a1500272277f0860456ee22f2a71a5a2071ee168a91d1dddc62afc2e32008`.

## Packaging

The final share ZIP is generated only after all analysis files are complete.
The package validator checks CRC, exact entry-set parity, byte-identical
contents, PNG signatures/dimensions, JSON/CSV parseability, generated hashes,
source preservation, and saved-game manifest consistency.
