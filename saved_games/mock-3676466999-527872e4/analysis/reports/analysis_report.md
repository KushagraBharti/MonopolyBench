# Standardized Analysis: mock-3676466999-527872e4

## Run

- Run ID: `mock-3676466999-527872e4`
- Winner: `Claude Opus 4.8`
- Turns: `166`
- End reason: `BANKRUPTCY`
- Usage rows: `502`
- Decision rows: `977`
- Action rows: `488`
- Event rows: `3341`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| Claude Opus 4.8 | anthropic/claude-opus-4.8 | medium | 1624 | 9454 | False |
| Gemini 3.1 Pro Preview | google/gemini-3.1-pro-preview | medium | 0 | 0 | True |
| Grok 4.3 | x-ai/grok-4.3 | medium | 0 | 0 | True |
| OpenAI GPT 5.5 | openai/gpt-5.5 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | 88 | $4.305005 | 634681 | 45264 | 8879 | 679945 | 18786.85 |
| Gemini 3.1 Pro Preview | 119 | $1.811970 | 487059 | 69821 | 57774 | 556880 | 12879.6 |
| Grok 4.3 | 81 | $0.479975 | 325641 | 44948 | 37467 | 370589 | 12594.0 |
| OpenAI GPT 5.5 | 214 | $15.317136 | 804354 | 379085 | 349972 | 1183439 | 83989.7 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
