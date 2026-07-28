# Standardized Analysis: frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview

## Run

- Run ID: `mock-2413970733-53b199c1`
- Winner: `Gemini 3.1 Pro Preview`
- Turns: `172`
- End reason: `BANKRUPTCY`
- Usage rows: `631`
- Decision rows: `1227`
- Action rows: `613`
- Event rows: `4073`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| Claude Opus 4.8 | anthropic/claude-opus-4.8 | medium | 0 | 0 | True |
| Gemini 3.1 Pro Preview | google/gemini-3.1-pro-preview | medium | 634 | 9974 | False |
| Grok 4.3 | x-ai/grok-4.3 | medium | 0 | 0 | True |
| OpenAI GPT 5.5 | openai/gpt-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | 139 | $7.519705 | 1002326 | 100323 | 19440 | 1102649 | 27222.1 |
| Gemini 3.1 Pro Preview | 147 | $2.274480 | 613560 | 87280 | 71638 | 700840 | 12526.4 |
| Grok 4.3 | 103 | $0.580630 | 395758 | 50259 | 41817 | 446017 | 12223.2 |
| OpenAI GPT 5.5 | 242 | $14.229761 | 901681 | 326426 | 293536 | 1228107 | 95232.6 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
