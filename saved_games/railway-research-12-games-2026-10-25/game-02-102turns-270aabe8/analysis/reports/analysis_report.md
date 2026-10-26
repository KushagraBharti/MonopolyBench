# Standardized Analysis: package-ua25kj35

## Run

- Run ID: `campaign-81cf4868c2db4b77a0f0319b59fd6dee-1-403baf7dc7`
- Winner: `p2`
- Turns: `102`
- End reason: `BANKRUPTCY`
- Usage rows: `323`
- Decision rows: `558`
- Action rows: `279`
- Event rows: `1976`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p2 | google/gemini-4-argon | medium | 214 | 9074 | False |
| p3 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p4 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 73 | $0.662281 | 223292 | 10416 | 4037 | 233708 | 15775.4 |
| p2 | 89 | $1.005822 | 332821 | 34018 | 24845 | 366839 | 14794.8 |
| p3 | 60 | unknown ($1.619398 known, 1 calls missing) | 323891 | 184112 | 166338 | 508003 | 116303.95 |
| p4 | 101 | unknown ($1.839388 known, 40 calls missing) | 332057 | 25558 | 14598 | 357615 | 9357.0 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
