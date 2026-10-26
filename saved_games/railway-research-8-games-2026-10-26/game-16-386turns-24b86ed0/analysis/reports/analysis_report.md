# Standardized Analysis: package-22ofylas

## Run

- Run ID: `campaign-8d77f7b822c6458fa9a5be0e884f74ef-3-6f1cbd6799`
- Winner: `p3`
- Turns: `386`
- End reason: `BANKRUPTCY`
- Usage rows: `751`
- Decision rows: `1206`
- Action rows: `603`
- Event rows: `4849`

## Players

| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |
| --- | --- | --- | ---: | ---: | --- |
| p1 | x-ai/grok-4.7 | medium | 0 | 0 | True |
| p2 | anthropic/claude-opus-5.5 | medium | 0 | 0 | True |
| p3 | openai/gpt-6.1-sol | medium | 5136 | 14176 | False |
| p4 | google/gemini-4-argon | medium | 0 | 0 | True |

## Model Usage

| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| p1 | 110 | $3.663272 | 614797 | 449709 | 356559 | 1064506 | 166819.0 |
| p2 | 284 | unknown ($3.921584 known, 142 calls missing) | 689276 | 58224 | 37103 | 747500 | 9041.0 |
| p3 | 193 | $1.767998 | 624703 | 20653 | 5101 | 645356 | 10653.8 |
| p4 | 164 | $1.604684 | 588812 | 42706 | 27850 | 631518 | 14114.0 |

## Standardized Outputs

- Tables: `26`
- Plots: `23`
- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`
- Expanded metrics: `expanded_metrics/`

Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.
