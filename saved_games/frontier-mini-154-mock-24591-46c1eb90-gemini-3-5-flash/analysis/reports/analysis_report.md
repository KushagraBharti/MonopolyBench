# Standardized Analysis: frontier-mini-154-mock-24591-46c1eb90-gemini-3-5-flash

## Run

- Run ID: `mock-24591-46c1eb90`
- Winner: `Gemini 3.5 Flash`
- Turns: `154`
- End reason: `BANKRUPTCY`
- Usage rows: `401`
- Decision rows: `792`
- Action rows: `396`
- Event rows: `2916`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| OpenAI GPT 5.4 mini | openai/gpt-5.4-mini | medium | 0 | 0 | True |
| Claude Haiku 4.5 | anthropic/claude-haiku-4.5 | medium | 0 | 0 | True |
| Gemini 3.5 Flash | google/gemini-3.5-flash | medium | 589 | 9449 | False |
| Grok 4.3 | x-ai/grok-4.3 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Haiku 4.5 | 71 | $0.905397 | 330912 | 114897 | 54069 | 445809 | 30964.0 |
| Gemini 3.5 Flash | 122 | $2.357675 | 522831 | 175238 | 154966 | 698069 | 15596.6 |
| Grok 4.3 | 45 | $0.241145 | 161909 | 23191 | 19359 | 185100 | 12727.8 |
| OpenAI GPT 5.4 mini | 163 | $1.148539 | 547877 | 166606 | 153185 | 714483 | 35910.8 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
