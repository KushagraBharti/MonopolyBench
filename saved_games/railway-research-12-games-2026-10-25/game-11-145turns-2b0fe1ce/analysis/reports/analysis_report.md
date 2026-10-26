# Standardized Analysis: package-bd5l7sa6

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-6-f3049e5157`
- Winner: `p2`
- Turns: `145`
- End reason: `BANKRUPTCY`
- Usage rows: `404`
- Decision rows: `652`
- Action rows: `326`
- Event rows: `2310`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | google/gemini-4-argon | medium | 0 | 0 | True |
| p2 | x-ai/grok-4.7 | medium | 1368 | 9758 | False |
| p3 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p4 | openai/gpt-6.1-sol | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 51 | $0.552482 | 179401 | 19368 | 14043 | 198769 | 22001.5 |
| p2 | 109 | $4.229402 | 617902 | 540565 | 510623 | 1158467 | 224857.0 |
| p3 | 144 | unknown ($1.916548 known, 72 calls missing) | 349987 | 25830 | 15126 | 375817 | 7353.85 |
| p4 | 100 | $0.940348 | 324183 | 13004 | 4312 | 337187 | 11598.9 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
