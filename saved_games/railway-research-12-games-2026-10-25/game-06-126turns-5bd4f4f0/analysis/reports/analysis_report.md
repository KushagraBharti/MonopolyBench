# Standardized Analysis: package-twj5vlrb

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-1-f79cf92b21`
- Winner: `p1`
- Turns: `126`
- End reason: `BANKRUPTCY`
- Usage rows: `304`
- Decision rows: `466`
- Action rows: `233`
- Event rows: `1806`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | openai/gpt-6.1-sol | medium | 1913 | 8863 | False |
| p2 | google/gemini-4-argon | medium | 0 | 0 | True |
| p3 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p4 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 74 | $0.653329 | 229320 | 8014 | 1270 | 237334 | 7154.4 |
| p2 | 61 | $0.580288 | 205244 | 16980 | 10901 | 222224 | 13640.0 |
| p3 | 35 | $0.725764 | 174236 | 77666 | 68762 | 251902 | 83676.8 |
| p4 | 134 | unknown ($1.776756 known, 67 calls missing) | 312054 | 26427 | 17169 | 338481 | 8615.65 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
