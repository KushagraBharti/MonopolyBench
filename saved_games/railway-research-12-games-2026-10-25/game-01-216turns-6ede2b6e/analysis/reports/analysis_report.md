# Standardized Analysis: package-cvjes96b

## Run

- Run ID: `campaign-81cf4868c2db4b77a0f0319b59fd6dee-0-d9d0ba7cca`
- Winner: `p3`
- Turns: `216`
- End reason: `BANKRUPTCY`
- Usage rows: `556`
- Decision rows: `972`
- Action rows: `486`
- Event rows: `3529`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p2 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p3 | google/gemini-4-argon | medium | 1867 | 11492 | False |
| p4 | x-ai/grok-4.7 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 148 | unknown ($2.682956 known, 63 calls missing) | 493884 | 35371 | 19739 | 529255 | 8112.45 |
| p2 | 139 | $1.426362 | 465832 | 26199 | 11752 | 492031 | 16590.1 |
| p3 | 125 | $1.419394 | 487497 | 44440 | 30218 | 531937 | 17517.8 |
| p4 | 144 | $6.086834 | 876520 | 775675 | 660239 | 1652195 | 211646.65 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
