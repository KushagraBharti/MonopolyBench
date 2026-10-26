# Standardized Analysis: package-oi64rfxq

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-4-858401cbbe`
- Winner: `p2`
- Turns: `118`
- End reason: `BANKRUPTCY`
- Usage rows: `478`
- Decision rows: `798`
- Action rows: `399`
- Event rows: `2584`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p2 | openai/gpt-6.1-sol | medium | 507 | 8037 | False |
| p3 | google/gemini-4-argon | medium | 0 | 0 | True |
| p4 | x-ai/grok-4.7 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 148 | unknown ($2.012912 known, 74 calls missing) | 359293 | 28787 | 17019 | 388080 | 7588.95 |
| p2 | 140 | $1.366820 | 488380 | 14608 | 3574 | 502988 | 9441.0 |
| p3 | 50 | $0.565378 | 180839 | 20370 | 14582 | 201209 | 17912.9 |
| p4 | 140 | $4.450668 | 833874 | 523404 | 484020 | 1357278 | 180573.55 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
