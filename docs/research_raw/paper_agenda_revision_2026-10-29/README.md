# Research-agenda extension, 29 October 2026

This package supports the manuscript revision organized around eight research questions and three broader questions. It is a completed account of the analyses performed here, not a claim that the full experimental agenda has been answered.

## Contents and reproduction

- **negotiation/**: complete 526-thread/920-response reconstruction, typed transfers, 74 source-linked rejection-reason records, independent consistency checks. Start with README.md. Run analyze_negotiation.py and validate_extension.py using the repository's Python environment.
- **temporal/**: all 240 previously fixed public-unflagged sampled records, their public/private fields, manual codebook and ledger, full opportunity searches for eight landing policies, selected chronological witnesses and 26 source assertions. Start with handoff.md. Manual labels are retained inputs, not produced by an LLM call in the reproduction scripts.
- **integration/**: full-corpus construction recurrence; run recurrence_audit.py and test_recurrence.py from the repository root. Also contains the adjudicated negotiation prose and methodological source notes.
- **evaluation/**: 20 new baseline-only games, two exact repeats, 130 supplied static scenarios, six policies, run protocol and replay results. Start with README.md. Use python/.venv/bin/python; no provider client or model query is used by these scripts.
- **reviews/**: fresh negotiation, temporal, evaluation/recurrence and integrated-argument checks, with independent ledgers, source references and limitations.
- **baseline/**: preserved pre-revision manuscript and package, intentionally excluded from the source-audit ZIP to avoid recursive historical archives.

The archive preserves these directories at docs/research_raw/paper_agenda_revision_2026-10-29/. Source-dependent scripts expect this location in the MonopolyBench checkout and the saved-game paths recorded in their manifests. They are not standalone engine implementations. Canonical source games, prompts, the rules engine, earlier outline and literature review were not changed.

## Interpretation

The historical cohort is 20 LLM games. The new pilot is 20 baseline-policy games, of which 19 are censored; two exact repeats are repeatability checks, not independent games. These populations must not be pooled into 40 LLM observations or a new model ranking.

The negotiation mechanics and financial transfers were independently reconstructed. Semantic reason codes disagree in 43 of 74 rows across broad categories; the ledgers retain both readings. The 61 common rival-consequence positives do not prove motives or causation. The second reader had accidental initial label exposure, disclosed in its review.

Temporal P/O/R counts are exploratory textual screens. Most candidate opponent forecasts are public-capacity or conditional-financing propositions rather than private-belief predictions. No-opportunity plans are not failures. Recurrence after a corrective request differs from recurrence after an applied construction repair, and same-turn continuations differ from later turns.

The future evaluation arms are **designs only**, not an implemented paid evaluation pipeline. They still require adjudicated tasks, meaningful opponents, randomized conditions, precision targets, current cost bounds and explicit execution scope. No new LLM call or training run occurred.
