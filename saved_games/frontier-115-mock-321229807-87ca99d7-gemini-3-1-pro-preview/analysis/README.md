# Analysis Package: mock-321229807-87ca99d7

This folder contains deterministic, downstream analysis for the immutable run in `../run/` and its human-readable request/response mirrors in `../quality_check/`.

Start with:

- `reports/manual_review_report.md` for the exhaustive qualitative synthesis, methods, conclusions, and limitations.
- `review/chronological_turn_review.md` for every turn in blocks of no more than three turns.
- `review/review_packet.jsonl` and `review/evidence_index.csv` for machine-readable decision/evidence joins.
- `review/player_dossiers.md`, `review/bankruptcy_windows.md`, and `review/negotiation_review.md` for focused manual review.
- `reports/case_studies.md` for five deep mechanism studies.
- `reports/integrity_report.md` for freeze, completeness, replay, and usage reconciliation.
- `reports/coverage_report.md` for prescribed artifact presence.
- `reports/analysis_report.md` for the standard descriptive summary.
- `expanded_metrics/expanded_metrics_report.md` for deterministic episode metrics.
- `manifests/source_artifact_hashes.json` for source-tree checksums and tool provenance.

The raw run and quality-check trees remain immutable. Qualitative labels are downstream, single-analyst judgments: facts, reported reasoning, interpretation, uncertainty, and speculation are kept separate; private/public differences are not deception by themselves; and immediate avoidability is claimed only when an explicit unilateral legal line is demonstrated.

The historical source-freeze manifest preserves the original ingested byte hashes. `manifests/qualitative_review_manifest.json` separately records LF-normalized baseline commit-blob provenance, current raw parity, structured coverage checks, and the hashes of qualitative outputs.
