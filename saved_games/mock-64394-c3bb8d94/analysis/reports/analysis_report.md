# Standardized Analysis: mock-64394-c3bb8d94

## Run

- Run ID: `mock-64394-c3bb8d94`
- Winner: `Grok 4.3`
- Turns: `157`
- End reason: `BANKRUPTCY`
- Usage rows: `355`
- Decision rows: `692`
- Action rows: `346`
- Event rows: `2606`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| OpenAI GPT 5.4 mini | openai/gpt-5.4-mini | medium | 0 | 0 | True |
| Claude Haiku 4.5 | anthropic/claude-haiku-4.5 | medium | 0 | 0 | True |
| Gemini 3.5 Flash | google/gemini-3.5-flash | medium | 0 | 0 | True |
| Grok 4.3 | x-ai/grok-4.3 | medium | 1664 | 9374 | False |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Haiku 4.5 | 67 | $1.018500 | 301890 | 143322 | 65510 | 445212 | 43276.4 |
| Gemini 3.5 Flash | 116 | $1.820204 | 481780 | 124380 | 105587 | 606160 | 13030.75 |
| Grok 4.3 | 80 | $0.450320 | 295225 | 51009 | 43931 | 346234 | 21346.0 |
| OpenAI GPT 5.4 mini | 92 | $0.747534 | 306348 | 116059 | 107315 | 422407 | 28301.6 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
