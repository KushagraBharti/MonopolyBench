# Integrity Report: mock-64394-c3bb8d94

- Overall completeness: `warning` (no blocking failures; 4 warnings).
- State replay: `passed`; 2,606 events, zero mismatches.
- Artifact replay: `passed`; 2,606 events, zero mismatches.
- Call reconciliation: `pass`; 346 decisions, 355 attempts, 9 corrective attempts, 0 fallbacks.
- Usage/cost: 1,385,243 input tokens; 434,770 output tokens; 322,343 reported reasoning tokens; 1,820,013 total tokens; $4.03655795 actual cost.

## Warnings

- `raw_split_replay_reports`: evidence `run/`.
- `separate_responses_directory`: evidence `run/prompts/`.
- `run_manifest_metadata`: evidence `run/experiment_manifest.json`.
- `provider_route_summary`: evidence `run/run_config.json`.

## Scope

This report is deterministic integrity, replay, completeness, and accounting work only. It contains no qualitative game review or behavioral labels.

## Plot Tooling Defect

The standardizer generated four cost plots with whole-dollar tick formatting, which collapsed distinct ticks. Only those four derived PNGs were regenerated from the canonical CSV tables with cent-level dollar axes; shared code and raw evidence were not changed. See `analysis/quality/plot_quality.json`.
