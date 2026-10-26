# Standardized Analysis: package-l4zzcx_2

## Run

- Run ID: `campaign-81cf4868c2db4b77a0f0319b59fd6dee-2-10fa91a1eb`
- Winner: `p1`
- Turns: `283`
- End reason: `BANKRUPTCY`
- Usage rows: `644`
- Decision rows: `1204`
- Action rows: `602`
- Event rows: `4427`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | google/gemini-4-argon | medium | 251 | 11291 | False |
| p2 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p3 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p4 | openai/gpt-6.1-sol | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 212 | $2.479770 | 825070 | 82963 | 60108 | 908033 | 17853.55 |
| p2 | 211 | unknown ($7.449394 known, 1 calls missing) | 1323812 | 886855 | 821013 | 2210667 | 178331.5 |
| p3 | 83 | unknown ($1.693636 known, 28 calls missing) | 310909 | 22500 | 13622 | 333409 | 9094.5 |
| p4 | 138 | $1.345998 | 485038 | 13361 | 2864 | 498399 | 8780.05 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
