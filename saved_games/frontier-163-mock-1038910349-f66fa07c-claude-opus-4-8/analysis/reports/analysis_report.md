# Standardized Analysis: frontier-163-mock-1038910349-f66fa07c-claude-opus-4-8

## Run

- Run ID: `mock-1038910349-f66fa07c`
- Winner: `Claude Opus 4.8`
- Turns: `163`
- End reason: `BANKRUPTCY`
- Usage rows: `371`
- Decision rows: `728`
- Action rows: `364`
- Event rows: `2694`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| Claude Opus 4.8 | anthropic/claude-opus-4.8 | medium | 652 | 9532 | False |
| Gemini 3.1 Pro Preview | google/gemini-3.1-pro-preview | medium | 0 | 0 | True |
| Grok 4.3 | x-ai/grok-4.3 | medium | 0 | 0 | True |
| OpenAI GPT 5.5 | openai/gpt-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | 86 | $4.298305 | 592591 | 53414 | 10252 | 646005 | 20704.0 |
| Gemini 3.1 Pro Preview | 88 | $1.278006 | 343485 | 49253 | 40133 | 392738 | 9535.5 |
| Grok 4.3 | 71 | $0.365715 | 245709 | 39452 | 33093 | 285161 | 13488.0 |
| OpenAI GPT 5.5 | 126 | $6.120730 | 427238 | 133010 | 118805 | 560248 | 69751.0 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
