# Standardized Analysis: frontier-115-mock-321229807-87ca99d7-gemini-3-1-pro-preview

## Run

- Run ID: `mock-321229807-87ca99d7`
- Winner: `Gemini 3.1 Pro Preview`
- Turns: `115`
- End reason: `BANKRUPTCY`
- Usage rows: `377`
- Decision rows: `732`
- Action rows: `366`
- Event rows: `2488`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| Claude Opus 4.8 | anthropic/claude-opus-4.8 | medium | 0 | 0 | True |
| Gemini 3.1 Pro Preview | google/gemini-3.1-pro-preview | medium | 1451 | 8141 | False |
| Grok 4.3 | x-ai/grok-4.3 | medium | 0 | 0 | True |
| OpenAI GPT 5.5 | openai/gpt-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | 62 | $3.287270 | 442489 | 42993 | 8845 | 485482 | 25270.05 |
| Gemini 3.1 Pro Preview | 71 | $1.010306 | 280015 | 37523 | 30599 | 317538 | 10420.0 |
| Grok 4.3 | 87 | $0.475871 | 335582 | 47018 | 38811 | 382600 | 12282.7 |
| OpenAI GPT 5.5 | 157 | $9.840936 | 568554 | 234693 | 212905 | 803247 | 70211.8 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
