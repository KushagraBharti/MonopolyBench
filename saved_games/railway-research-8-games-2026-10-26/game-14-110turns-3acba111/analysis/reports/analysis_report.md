# Standardized Analysis: package-y2q0nr5u

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-1-a12c9b8580`
- Winner: `p1`
- Turns: `110`
- End reason: `BANKRUPTCY`
- Usage rows: `300`
- Decision rows: `470`
- Action rows: `235`
- Event rows: `1744`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | openai/gpt-6.1-sol | medium | 999 | 9319 | False |
| p2 | google/gemini-4-argon | medium | 0 | 0 | True |
| p3 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p4 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 69 | $0.604683 | 213205 | 7458 | 1806 | 220663 | 8941.8 |
| p2 | 56 | $0.610968 | 199239 | 21249 | 14811 | 220488 | 17190.0 |
| p3 | 53 | $1.814648 | 285844 | 227960 | 214046 | 513804 | 177026.0 |
| p4 | 122 | unknown ($1.616388 known, 61 calls missing) | 287907 | 23238 | 14450 | 311145 | 8153.9 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
