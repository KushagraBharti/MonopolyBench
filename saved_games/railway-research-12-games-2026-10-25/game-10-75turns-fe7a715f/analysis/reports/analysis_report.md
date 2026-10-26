# Standardized Analysis: package-4kbafzll

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-5-d2c12a6f23`
- Winner: `p2`
- Turns: `75`
- End reason: `BANKRUPTCY`
- Usage rows: `240`
- Decision rows: `398`
- Action rows: `199`
- Event rows: `1402`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p2 | google/gemini-4-argon | medium | 525 | 7425 | False |
| p3 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p4 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 53 | $0.491256 | 167534 | 7250 | 2048 | 174784 | 8588.6 |
| p2 | 61 | $0.752276 | 225333 | 30161 | 22461 | 255494 | 21071.0 |
| p3 | 46 | $1.257940 | 242945 | 147459 | 134592 | 390404 | 146438.5 |
| p4 | 80 | unknown ($1.037928 known, 40 calls missing) | 186487 | 14599 | 9046 | 201086 | 8037.0 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
