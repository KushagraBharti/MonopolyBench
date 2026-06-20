# Standardized Analysis: frontier-191-mock-83265-81ed4937-openai-gpt-5-5

## Run

- Run ID: `mock-83265-81ed4937`
- Winner: `OpenAI GPT 5.5`
- Turns: `191`
- End reason: `BANKRUPTCY`
- Usage rows: `604`
- Decision rows: `1166`
- Action rows: `583`
- Event rows: `3972`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| OpenAI GPT 5.5 | openai/gpt-5.5 | medium | 718 | 9708 | False |
| Claude Opus 4.8 | anthropic/claude-opus-4.8 | medium | 0 | 0 | True |
| Gemini 3.1 Pro Preview | google/gemini-3.1-pro-preview | medium | 0 | 0 | True |
| Grok 4.3 | x-ai/grok-4.3 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | 139 | $9.491715 | 1092918 | 161085 | 23008 | 1254003 | 45324.6 |
| Gemini 3.1 Pro Preview | 126 | $1.901478 | 507591 | 73858 | 60431 | 581449 | 11831.5 |
| Grok 4.3 | 72 | $0.412087 | 265395 | 40981 | 34891 | 306376 | 7355.25 |
| OpenAI GPT 5.5 | 267 | $15.906450 | 1018164 | 364553 | 333728 | 1382717 | 97442.2 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`

The original run analysis is preserved at `run/analysis/`. This folder is the standardized cross-run analysis layer.
