# Standardized Analysis: package-jco8t7p1

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-6-f542507ff9`
- Winner: `p1`
- Turns: `175`
- End reason: `BANKRUPTCY`
- Usage rows: `405`
- Decision rows: `646`
- Action rows: `323`
- Event rows: `2500`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | google/gemini-4-argon | medium | 451 | 10191 | False |
| p2 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p3 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p4 | openai/gpt-6.1-sol | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 99 | $1.077534 | 366342 | 34485 | 23675 | 400827 | 14559.2 |
| p2 | 54 | $1.808520 | 293658 | 226638 | 209684 | 520296 | 172568.4 |
| p3 | 154 | unknown ($2.065372 known, 77 calls missing) | 373468 | 28575 | 18648 | 402043 | 9030.7 |
| p4 | 98 | $0.932001 | 324387 | 12118 | 3629 | 336505 | 10297.5 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
