# Standardized Analysis: package-soft4yhg

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-2-291c6c4036`
- Winner: `p1`
- Turns: `114`
- End reason: `BANKRUPTCY`
- Usage rows: `329`
- Decision rows: `554`
- Action rows: `277`
- Event rows: `1998`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | google/gemini-4-argon | medium | 1299 | 9164 | False |
| p2 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p3 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p4 | openai/gpt-6.1-sol | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 85 | $0.889480 | 312690 | 26410 | 17141 | 339100 | 15605.2 |
| p2 | 52 | $1.858176 | 290502 | 235646 | 218393 | 526148 | 167764.55 |
| p3 | 98 | unknown ($1.266388 known, 49 calls missing) | 239237 | 15472 | 8877 | 254709 | 7304.8 |
| p4 | 94 | $0.894732 | 298869 | 14770 | 5802 | 313639 | 14125.3 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
