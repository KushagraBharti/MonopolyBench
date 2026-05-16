# Handoff

Repo: `C:\Users\kushagra\OneDrive\Documents\CS Projects\MonopolyBench`
Branch: `main`

## Current State

- `/micro` has been rebuilt around the category-card workflow.
- Micro runs are model-only. Baseline runner paths and deterministic micro baselines were removed.
- Micro prompt mode is fixed to `live_game`.
- The `/micro` config now exposes only:
  - suite
  - reasoning effort
  - model id
  - display name
- Prompt condition selection and system prompt override were removed.
- Multi-scenario model runs stream in waves of 20.
- Each selected scenario has an inline `Show Response` dropdown with stacked reasoning and output.
- Scenario results appear as each scenario finishes, without waiting for the full batch.
- If the micro resolver falls back to a deterministic action, the micro run now errors instead of returning/scoring that fallback result.
- OpenRouter streaming emits reasoning, content, tool name/arguments, and raw provider deltas when needed.

## Backend Notes

- Backend dev command should bind explicitly on Windows:

```powershell
cd python/apps/api
uv run python -m uvicorn monopoly_api.main:app --host 127.0.0.1 --port 8000 --reload
```

- Frontend:

```powershell
cd frontend
yarn dev
```

- Micro TUI:

```powershell
cd python/packages/microbench
uv run monopoly-micro tui
```

## Verification

Completed successfully:

```powershell
pwsh -File scripts/verify.ps1
```

Result: all checks passed.

Known benign note: Windows still prints pytest temp cleanup permission warnings after successful pytest runs.
