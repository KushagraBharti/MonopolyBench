# Standardized Analysis: frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview

## Run

- Run ID: `mock-44910-42ec35c5`
- Winner: `Gemini 3 Flash Preview`
- Turns: `273`
- End reason: `BANKRUPTCY`
- Usage rows: `549`
- Decision rows: `1080`
- Action rows: `540`
- Event rows: `4102`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| OpenAI GPT 5.4 Mini | openai/gpt-5.4-mini | medium | 0 | 0 | True |
| Claude Haiku 4.5 | anthropic/claude-haiku-4.5 | medium | 0 | 0 | True |
| Gemini 3 Flash Preview | google/gemini-3-flash-preview | medium | 3921 | 10071 | False |
| Grok 4.3 | x-ai/grok-4.3 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Haiku 4.5 | 88 | $1.383437 | 405302 | 195627 | 86468 | 600929 | 48569.35 |
| Gemini 3 Flash Preview | 192 | $1.177550 | 902291 | 244565 | 210782 | 1146856 | 15705.3 |
| Grok 4.3 | 180 | $1.033793 | 701770 | 107952 | 91539 | 809722 | 10980.1 |
| OpenAI GPT 5.4 Mini | 89 | $0.649973 | 290348 | 97391 | 89321 | 387739 | 27366.8 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`

The original run analysis is preserved at `run/analysis/`. This folder is the standardized cross-run analysis layer.
