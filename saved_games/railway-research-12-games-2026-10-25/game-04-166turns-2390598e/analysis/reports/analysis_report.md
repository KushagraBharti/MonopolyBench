# Standardized Analysis: package-mtoqhrwn

## Run

- Run ID: `campaign-81cf4868c2db4b77a0f0319b59fd6dee-3-66bf24232c`
- Winner: `p1`
- Turns: `166`
- End reason: `BANKRUPTCY`
- Usage rows: `436`
- Decision rows: `698`
- Action rows: `349`
- Event rows: `2567`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | x-ai/grok-4.7 | medium | 2524 | 9019 | False |
| p2 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p3 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p4 | google/gemini-4-argon | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 110 | $3.582170 | 680767 | 415706 | 377364 | 1096473 | 143322.3 |
| p2 | 189 | unknown ($3.594508 known, 79 calls missing) | 670397 | 45646 | 26252 | 716043 | 8883.6 |
| p3 | 58 | $0.540370 | 184443 | 7935 | 2209 | 192378 | 8260.8 |
| p4 | 79 | $0.914488 | 293024 | 32844 | 23437 | 325868 | 22903.3 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
