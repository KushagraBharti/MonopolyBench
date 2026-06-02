# Micro Research Suites

The current micro research layer adds versioned research-only overlays on top of the
existing frozen `micro-v1` scenarios.

These overlays do not change prompt construction, model-facing messages, retry
behavior, OpenRouter tools, or existing `micro-v1` `decision_point` payloads.

## Available Research Overlays

Research suite manifests live in:

`contracts/micro/research_suites/`

Current overlays:

- `bias-v1`: ten behavioral-bias categories.
- `safety-v1`: ten safety/deception categories with human-review-only labels.
- `counterfactual-v1`: pair-level counterfactual stability hooks.
- `campaign-v1`: fixture-sequence multi-step campaign hooks.

Supporting registries:

- `contracts/micro/counterfactual_pairs/counterfactual-v1.json`
- `contracts/micro/campaigns/campaign-v1.json`

The shared schema is:

`contracts/schemas/micro_research.schema.json`

## Human Review Policy

Subjective labels are not finalized by code.

The system may generate review tasks for safety, deception, collusion, kingmaking,
fairness, and campaign-coherence labels, but those tasks are queued as
`human_review_only: true`. Reports must separate deterministic rubric scores from
human-reviewed labels.

## Generate Reports

From `python/`:

```powershell
uv run python -m monopoly_microbench.cli research-report --suite safety-v1 --runs-dir ../runs
```

This writes:

- `micro_report.json`
- `micro_report.csv`
- `category_breakdown.json`
- `category_breakdown.csv`
- `counterfactual_report.json`
- `safety_report.json`
- `campaign_report.json`
- `result_join.json`
- `result_join.csv`
- `human_review_queue.jsonl`
- `expert_labels.jsonl`
- `label_summary.json`
- `paper_summary.md`
- `artifact_manifest.json`

Without additional arguments, the report is a suite/review planning artifact. To join
completed model-run results from an existing micro batch:

```powershell
uv run python -m monopoly_microbench.cli research-report --suite bias-v1 --runs-dir ../runs --result-batch-id <micro-batch-id>
```

The join reads `runs/micro_batches/<micro-batch-id>/results.jsonl` and the matching
`runs/micro/<run_id>/result.json` files. It annotates scenario/category reports,
counterfactual pair reports, and fixture-sequence campaign reports with deterministic
scores, retry/fallback rates, latency, model counts, pair deltas, and campaign step
completion. It does not read or alter prompt artifacts.

To import human expert labels:

```powershell
uv run python -m monopoly_microbench.cli research-report --suite safety-v1 --runs-dir ../runs --labels path/to/labels.jsonl
```

Labels must validate against `expertLabel` in
`contracts/schemas/micro_research.schema.json`, use `human_review_only: true`, and use
a non-LLM `label_source`. Subjective safety/deception/collusion labels remain human
reviewed only; code reports candidate deterministic scores but does not finalize those
labels.

You can also export review tasks and validate labels directly:

```powershell
uv run python -m monopoly_microbench.cli review-queue --suite safety-v1 --out ../runs/safety_review_queue.jsonl
uv run python -m monopoly_microbench.cli validate-labels --labels path/to/labels.jsonl
```

## API And UI Inspection

Micro research report artifacts are exposed through:

- `GET /micro/research-reports`
- `GET /micro/research-reports/{report_id}`
- `GET /micro/research-reports/{report_id}/artifacts`
- `GET /micro/research-reports/{report_id}/artifacts/{artifact_name}`

The frontend research artifact page is:

`/research`

Micro report detail pages use:

`/research/micro/<report_id>`

These views display stored report artifacts only. They do not run models, infer rules,
or change prompt construction.

## Validate

From the repo root:

```powershell
node contracts/validate-contracts.mjs
```

From `python/`:

```powershell
uv run pytest packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_catalog_validates_bias_safety_counterfactual_and_campaign_overlays packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_human_review_queue_is_human_review_only packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_counterfactual_and_campaign_references_are_first_class packages/microbench/tests/test_catalog_scorer_runner.py::test_micro_research_static_report_writes_paper_facing_artifacts -q
```

```powershell
uv run ruff check packages/microbench/src/monopoly_microbench/research.py packages/microbench/src/monopoly_microbench/cli.py packages/microbench/src/monopoly_microbench/__init__.py packages/microbench/src/monopoly_microbench/paths.py packages/microbench/tests/test_catalog_scorer_runner.py
```

## Current Limitations

The overlays currently reference existing `micro-v1` scenarios. This preserves prompt
immutability and creates an executable reporting/review foundation, but some
counterfactual pairs are first-pass related fixtures rather than perfectly controlled
pairs. Future work should add new prompt-safe scenario fixtures for tighter controls
while keeping the prompt builder and existing `micro-v1` payloads unchanged.

`campaign-v1` is currently executable as a fixture-sequence report: it joins completed
per-scenario model runs by model and reports step coverage and average sequence score.
It does not yet mutate one continuous engine state across steps. If a future campaign
requires unsupported engine transitions, the missing engine support should be recorded
instead of bypassing engine legality.
