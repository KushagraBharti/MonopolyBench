# Standardized Analysis: package-l9l6nn2g

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-7-a8adf27ba7`
- Winner: `p4`
- Turns: `115`
- End reason: `BANKRUPTCY`
- Usage rows: `442`
- Decision rows: `710`
- Action rows: `355`
- Event rows: `2406`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p2 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p3 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p4 | google/gemini-4-argon | medium | 864 | 8069 | False |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 71 | $1.648954 | 366200 | 180055 | 163918 | 546255 | 131104.0 |
| p2 | 164 | unknown ($2.262864 known, 82 calls missing) | 409221 | 31299 | 19993 | 440520 | 9751.95 |
| p3 | 115 | $1.067740 | 369013 | 14538 | 4266 | 383551 | 10613.7 |
| p4 | 92 | $1.096826 | 350853 | 39512 | 28918 | 390365 | 21564.85 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
