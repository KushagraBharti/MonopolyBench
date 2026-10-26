# Standardized Analysis: package-i1w4cbwg

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-3-c0ff63802e`
- Winner: `p3`
- Turns: `139`
- End reason: `BANKRUPTCY`
- Usage rows: `370`
- Decision rows: `576`
- Action rows: `288`
- Event rows: `2106`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p2 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p3 | openai/gpt-6.1-sol | medium | 1171 | 9291 | False |
| p4 | google/gemini-4-argon | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 68 | $1.875206 | 366010 | 219299 | 198920 | 585309 | 133536.75 |
| p2 | 156 | unknown ($2.076852 known, 78 calls missing) | 370543 | 29734 | 18477 | 400277 | 8555.25 |
| p3 | 73 | $0.668721 | 234436 | 8274 | 1772 | 242710 | 7710.6 |
| p4 | 73 | $0.859418 | 266389 | 32664 | 23768 | 299053 | 21162.0 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
