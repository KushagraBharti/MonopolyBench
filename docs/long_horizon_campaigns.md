# Long-Horizon Campaigns

`monopoly-long-v1` is the full-game research track for Long-Horizon Economic Agency
in Monopoly. The campaign tooling creates deterministic research plans, can execute
the expanded run matrix, and writes campaign-level research artifacts without changing
prompt construction.

## Prompt Invariant

Campaign planning and reporting must not change model-facing prompts.

The seed registry, model roster registry, campaign config, run matrix, manifests, and
reports are research/config artifacts only. They do not change prompt text, message
structure, OpenRouter tool schemas, retry wording, private thought requirements, or
anything else the LLM sees.

## Research Registries

Fixed seed cohorts live at:

`contracts/research/monopoly_long_v1_seed_registry.json`

Model and baseline rosters live at:

`contracts/research/monopoly_long_v1_model_rosters.json`

The research contract is:

`contracts/schemas/research_registry.schema.json`

The first campaign config is:

`campaigns/monopoly-long-v1-smoke.json`

It uses the `smoke` seed cohort, the `smoke` roster, one repetition per seed, and
`latin_square` seat assignment.

## Dry-Run A Campaign Matrix

From the repo root:

```powershell
cd python/packages/arena
uv run python -m monopoly_arena.long_campaign --config campaigns/monopoly-long-v1-smoke.json --runs-dir runs
```

This writes:

- `runs/campaigns/<campaign_id>/campaign_config.json`
- `runs/campaigns/<campaign_id>/campaign_manifest.json`
- `runs/campaigns/<campaign_id>/seed_manifest.json`
- `runs/campaigns/<campaign_id>/model_roster.json`
- `runs/campaigns/<campaign_id>/baseline_roster.json`
- `runs/campaigns/<campaign_id>/run_matrix.json`
- `runs/campaigns/<campaign_id>/run_matrix.jsonl`
- `runs/campaigns/<campaign_id>/batch_runner_compatibility.json`
- `runs/campaigns/<campaign_id>/artifact_manifest.json`

For the smoke config, the matrix has 8 planned rows:

- 2 fixed seeds,
- 1 repetition per seed,
- 4 Latin-square seat rotations.

The matrix distinguishes roster slots as well as actor ids, so a repeated model still
gets measurable seat coverage.

Rows that include deterministic baselines also include `baseline_strategies`, a
`player_id -> baseline_id` map that can be passed to `LlmRunner(...,
baseline_strategies=...)`. Baseline actors choose from engine-provided legal actions
only, do not construct prompts, and do not call OpenRouter.

## Execute A Campaign Matrix

Campaign execution is explicit. If the config has `dry_run: true`, execution also
requires `--force-execute`:

```powershell
cd python/packages/arena
uv run python -m monopoly_arena.long_campaign --config campaigns/monopoly-long-v1-smoke.json --runs-dir runs --execute --force-execute
```

For a cheap local smoke execution, select the `baseline_field` roster in a temporary
campaign config and optionally cap execution with `--max-runs 1`. All-baseline rows
run without OpenRouter calls and should produce zero prompt artifact files.

Execution writes the planning artifacts above plus:

- `runs/campaigns/<campaign_id>/results.jsonl`
- `runs/campaigns/<campaign_id>/results.csv`
- `runs/campaigns/<campaign_id>/run_results.json`
- `runs/campaigns/<campaign_id>/leaderboard.json`
- `runs/campaigns/<campaign_id>/leaderboard.csv`
- `runs/campaigns/<campaign_id>/statistics.json`
- `runs/campaigns/<campaign_id>/baseline_comparison.json`
- `runs/campaigns/<campaign_id>/paper_report.md`
- `runs/campaigns/<campaign_id>/execution_result.json`

Each completed run still writes the normal run-level artifacts under
`runs/<run_id>/`, including events, actions, decisions, snapshots, scorecards, usage,
cost reports, replay verification, trace findings, failure taxonomy, and review queue.

The campaign runner resumes cells only when the completed artifact set already exists.
If a run directory exists but is incomplete, the cell is recorded as failed rather than
appending to partial logs.

## Reports

The campaign report stack keeps final net worth as the primary score and reports other
dimensions separately:

- leaderboard rank, win rate, average final net worth, average final rank,
- deterministic bootstrap confidence intervals for numeric metrics,
- seat-effect summaries,
- seed-level summaries,
- fallback/retry/reliability summaries,
- OpenRouter actual cost/token summaries from existing run artifacts,
- baseline-normalized net worth when baseline actors are present,
- replay verification aggregate,
- failure taxonomy aggregate,
- and a Markdown `paper_report.md` for quick paper-style inspection.

The report is descriptive. Human analysis is still required for qualitative claims
about negotiation, deception, safety, or strategic intent.

## API And UI Inspection

Campaign artifacts are exposed through:

- `GET /campaigns`
- `GET /campaigns/{campaign_id}`
- `GET /campaigns/{campaign_id}/artifacts`
- `GET /campaigns/{campaign_id}/artifacts/{artifact_name}`

The frontend research artifact page is:

`/research`

Campaign detail pages use:

`/research/campaigns/<campaign_id>`

These pages display stored campaign artifacts only. They do not infer Monopoly rules or
modify prompts.

## Validation

Run contract validation from the repo root:

```powershell
node contracts/validate-contracts.mjs
```

Run focused campaign tests:

```powershell
cd python
uv run pytest packages/arena/tests/test_research_campaign.py -q
```

Run focused lint:

```powershell
cd python
uv run ruff check packages/arena/src/monopoly_arena/research_registry.py packages/arena/src/monopoly_arena/long_campaign.py packages/arena/tests/test_research_campaign.py
```
