# Deterministic Integrity Report

## Scope

This report covers deterministic preparation, source preservation, artifact completeness,
call/usage reconciliation, endpoint consistency, and read-only replay. Chronological
qualitative review, bankruptcy interpretation, negotiation review, deception/collusion
labeling, player dossiers, promise analysis, and case-study construction are deferred.

## Source freeze

- Source commit: `fa773791718e3b5d8ff18448e2ad3fa42b375259`
- `run/`: 3,599 files, 64,390,347 bytes, tree SHA-256 `25524577aa9ec7754151d9997627cec1280bf0255293085d59670bb617477f50`
- `quality_check/`: 1,098 files, 14,843,083 bytes, tree SHA-256 `ff2e7c006d723b85936e530b13b779b55922a3082fd32ac97ccf32457e6663d1`
- Tree format: `sha256(UTF-8 lines: relative_path<TAB>file_sha256<TAB>bytes<LF>, sorted by relative_path using POSIX separators and ordinal Unicode code-point order)`
- Final source verification: exact byte-for-byte match to the pre-regeneration freeze.

## Legacy manifest audit

`run/artifact_manifest.json` was audited but not rewritten: 36
entries match exactly, 3 differ, and 2 name
files absent from the frozen source. The mismatches are `summary.json`,
`scorecard.json`, and `scorecard_players.json`; the absent entries are
`reviews/review_labels.jsonl` and `reviews/review_summary.json`.

## Artifact completeness and decisions

- Events: 4,102; contiguous zero-based sequence: pass.
- Decision starts/resolutions/actions: 540 /
  540 /
  540; all three decision-ID sets are bijective.
- Attempts: 549; retries:
  9; invalid attempts:
  9; fallbacks:
  0.
- Exactly-once applied actions: pass.
- Prompt attempt sets: 549 complete sets × 5 files = 2,745 files.
- Quality-check pairs: 549 complete request/response pairs = 1,098 files.
- Package-local correction: `decision_type_counts.csv` and its plot count the 540
  `decision_resolved` rows, not both start/resolution protocol rows.

## Usage and cost

All 549 attempts have OpenRouter actual usage. Token sums
match `usage.json` and `cost_report.json` exactly. Attempt-row cost sums exactly to
`$4.24475240`; the aggregate files render
the binary-float total as `4.244752400000001` (a 1E-15 presentation delta). Reasoning tokens are
preserved as raw OpenRouter completion-detail values and are not double-counted on top
of output/total tokens. Missing native/provider-normalized fields are not imputed.

## Endpoint

- Winner: `Gemini 3 Flash Preview`; exactly one canonical snapshot survivor: pass.
- Terminal reason: `BANKRUPTCY` and snapshot phase
  `GAME_OVER`: consistent.
- Final turn: 273; cash and bankrupt status match for all players.
- Summary net-worth estimates are retained as derived valuation fields rather than
  silently recomputed with a different convention.

## Read-only replay

- Full artifact replay: `passed`; 4,102 compared events;
  zero missing/extra events and zero mismatch.
- State replay: `passed`; 1,942 state-relevant compared
  events; zero missing/extra events and zero mismatch.
- `missing_actions=0`, `extra_actions=0`, `decision_id_mismatch=false`.
- Replay reports were built in memory and no report was written into `run/`.

## Result

Deterministic integrity passes. The package is ready for a later, separately scoped
qualitative review. The legacy manifest drift and missing normalized provider field are
documented warnings, not mutations or replay blockers.
