# Standardized Analysis: package-zo399hou

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-4-6b9a4be27d`
- Winner: `p2`
- Turns: `88`
- End reason: `BANKRUPTCY`
- Usage rows: `288`
- Decision rows: `442`
- Action rows: `221`
- Event rows: `1550`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p2 | openai/gpt-6.1-sol | medium | 227 | 7637 | False |
| p3 | google/gemini-4-argon | medium | 0 | 0 | True |
| p4 | x-ai/grok-4.7 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 130 | unknown ($1.943484 known, 65 calls missing) | 332066 | 30761 | 20403 | 362827 | 9835.85 |
| p2 | 78 | $0.747605 | 254853 | 11059 | 3397 | 265912 | 9705.35 |
| p3 | 40 | $0.391360 | 138245 | 11487 | 7249 | 149732 | 13337.25 |
| p4 | 40 | $1.009916 | 216352 | 113162 | 101800 | 329514 | 98664.8 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
