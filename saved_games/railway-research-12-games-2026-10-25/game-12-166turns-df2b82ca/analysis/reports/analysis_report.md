# Standardized Analysis: package-ysbi3x27

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-7-eb71418166`
- Winner: `p2`
- Turns: `166`
- End reason: `BANKRUPTCY`
- Usage rows: `479`
- Decision rows: `688`
- Action rows: `344`
- Event rows: `2464`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p2 | anthropic/claude-opus-5.5 | medium | 1235 | 10315 | False |
| p3 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p4 | google/gemini-4-argon | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 69 | $2.189112 | 394356 | 261464 | 239328 | 655820 | 162134.2 |
| p2 | 266 | unknown ($3.911808 known, 133 calls missing) | 700087 | 55573 | 36912 | 755660 | 9305.5 |
| p3 | 58 | $0.543285 | 181897 | 8863 | 3549 | 190760 | 12866.25 |
| p4 | 86 | $0.891174 | 315617 | 25994 | 16365 | 341611 | 14152.5 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
