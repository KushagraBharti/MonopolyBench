# Standardized Analysis: package-o5m9jipg

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-2-eb52464883`
- Winner: `p4`
- Turns: `150`
- End reason: `BANKRUPTCY`
- Usage rows: `446`
- Decision rows: `680`
- Action rows: `340`
- Event rows: `2390`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | google/gemini-4-argon | medium | 0 | 0 | True |
| p2 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p3 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p4 | openai/gpt-6.1-sol | medium | 585 | 9805 | False |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 72 | $0.754076 | 254508 | 24506 | 16465 | 279014 | 16033.9 |
| p2 | 74 | unknown ($2.019668 known, 1 calls missing) | 400264 | 236150 | 212016 | 636414 | 127633.3 |
| p3 | 208 | unknown ($2.972368 known, 104 calls missing) | 516557 | 45307 | 31465 | 561864 | 9024.75 |
| p4 | 92 | $0.857204 | 295937 | 11750 | 3901 | 307687 | 10253.65 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
