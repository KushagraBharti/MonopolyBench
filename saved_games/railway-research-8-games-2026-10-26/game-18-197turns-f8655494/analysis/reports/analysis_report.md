# Standardized Analysis: package-bsmkmmmr

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-5-7284733ce7`
- Winner: `p4`
- Turns: `197`
- End reason: `BANKRUPTCY`
- Usage rows: `613`
- Decision rows: `928`
- Action rows: `464`
- Event rows: `3252`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | openai/gpt-6.1-sol | medium | 0 | 0 | True |
| p2 | google/gemini-4-argon | medium | 0 | 0 | True |
| p3 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p4 | anthropic/claude-opus-5.5 | medium | 2057 | 9687 | False |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 152 | $1.430459 | 500583 | 17923 | 5281 | 518506 | 10050.95 |
| p2 | 69 | $0.806978 | 258584 | 28981 | 20044 | 287565 | 17200.0 |
| p3 | 98 | $2.639606 | 559885 | 297146 | 270359 | 857031 | 126105.45 |
| p4 | 294 | unknown ($4.316076 known, 147 calls missing) | 779539 | 59896 | 40251 | 839435 | 9144.3 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
