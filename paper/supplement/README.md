# MonopolyBench anonymous review supplement

This package accompanies the paper **“MonopolyBench: Auditing Long-Horizon
Economic Agency in Multi-Agent Language Models.”** It is a compact review
surface for the eight frozen games used in the paper. It does not replace the
full canonical saved-game packages.

## Contents

- `monopolybench_eight_run_ledger_2026-07-28.csv`: exact corpus accounting,
  endpoint rosters, seeds, outcomes, replay status, usage, and cost.
- `claim_source_audit.md`: claim-by-claim provenance, metric definitions,
  exact mechanism windows, and bibliography audit.
- `run115_source_file_inventory.csv`: 3,163 per-file SHA-256 records for the
  legacy Run 115 package. Its canonical source-freeze manifest stores the two
  aggregate tree hashes; this addendum supplies the full file inventory and
  recomputes exactly to those frozen hashes.
- `figures/`: the two publication figures in PDF and PNG form.
- `runs/<saved-game>/saved_game_manifest.json`: package layout, source commit,
  tree hashes, replay status, and analysis ZIP integrity.
- `runs/<saved-game>/analysis/manifests/`: the available analysis manifest plus
  source-freeze records for the frozen `run/` and `quality_check/` trees.
  Seven package-local records contain per-file hashes; the Run 115 addendum
  above completes the eighth.
- `runs/<saved-game>/run/replay_report.json`: the canonical package replay
  report.
- `runs/<saved-game>/analysis/quality/`: available standardized
  artifact-completeness, call-reconciliation, replay-verification, and
  quality-flag records.
- `runs/<saved-game>/analysis/review/`: the evidence index and any
  package-specific decision-coverage CSV.
- `runs/<saved-game>/analysis/reports/`: integrity, manual review, and
  mechanism case reports.
- `supplement_manifest.csv`: SHA-256 and byte count for every payload file
  (the manifest does not hash itself).

## Evidence boundary

The rules engine is authoritative. Events record what happened; actions record
what was applied; decisions and provider attempts record the legal surface and
validation chain; snapshots checkpoint state. Qualitative reports are
downstream interpretations and must resolve to those canonical artifacts.

Replay re-executes the recorded action sequence. State replay compares
canonicalized state-relevant events. Strict artifact replay compares the
complete event stream after versioned canonicalization; it is distinct from
byte identity of stored files.

Run `mock-83265-81ed4937` remains
`state_passed_artifact_failed`: all 1,640 state-relevant comparisons pass, while
strict artifact replay has two fallback-validity provenance mismatches, at
sequences 669 and 1202. The applied `reject_trade` and `drop_out` actions,
decision mappings, and state trajectory remain unchanged; the standard replay
report exposes the first mismatch.

## Full packages

The complete immutable packages remain under the corresponding
`saved_games/<saved-game>/run/` and `quality_check/` roots in the research
artifact. This compact ZIP carries their complete source-hash inventories and
the downstream reports needed to navigate and review the paper’s claims without
duplicating roughly 672 MB of canonical source data.
