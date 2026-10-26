# Standardized Analysis: package-9geaulll

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-0-b80938d4d5`
- Winner: `p1`
- Turns: `185`
- End reason: `BANKRUPTCY`
- Usage rows: `469`
- Decision rows: `712`
- Action rows: `356`
- Event rows: `2675`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | anthropic/claude-opus-5.5 | medium | 4228 | 8713 | False |
| p2 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p3 | google/gemini-4-argon | medium | 0 | 0 | True |
| p4 | x-ai/grok-4.7 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 224 | unknown ($3.470536 known, 112 calls missing) | 595159 | 54495 | 35105 | 649654 | 9503.25 |
| p2 | 102 | $0.925030 | 326325 | 10937 | 2380 | 337262 | 10442.1 |
| p3 | 50 | $0.559618 | 176269 | 20708 | 14705 | 196977 | 20879.7 |
| p4 | 93 | $4.006048 | 534413 | 526081 | 493368 | 1060494 | 244555.6 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
