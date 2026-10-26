# Standardized Analysis: package-vep4wc0a

## Run

- Run ID: `campaign-c0761df29478459ab4cea725626ea259-0-f5a29652ac`
- Winner: `p2`
- Turns: `170`
- End reason: `BANKRUPTCY`
- Usage rows: `402`
- Decision rows: `620`
- Action rows: `310`
- Event rows: `2383`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p2 | openai/gpt-6.1-sol | medium | 677 | 9257 | False |
| p3 | google/gemini-4-argon | medium | 0 | 0 | True |
| p4 | x-ai/grok-4.7 | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 174 | unknown ($2.424812 known, 87 calls missing) | 416138 | 38013 | 25804 | 454151 | 9782.05 |
| p2 | 92 | $0.848839 | 295911 | 10920 | 2618 | 306831 | 9650.75 |
| p3 | 75 | $0.778226 | 263943 | 25034 | 17170 | 288977 | 13949.1 |
| p4 | 61 | $1.664678 | 322213 | 195994 | 181335 | 518207 | 133771.0 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
