# MonopolyBench Run Analysis: mock-83265-81ed4937

## Integrity
- Artifact status: `incomplete_no_game_ended`
- Last saved event: seq `3628`, turn `167`, type `LLM_DECISION_REQUESTED`
- GAME_ENDED events: `0`
- Unresolved decision ids in event log: `mock-83265-81ed4937-dec-000539`
- Events/actions/resolved calls: `3629` / `539` / `539`

## Cost And Tokens
- Total cost: `$24.751285`
- Tokens: `2,645,235` input, `580,015` output, `403,183` reasoning, `3,225,250` total
- Missing usage calls: `1`
- Retries/fallbacks/invalid attempts: `21` / `2` / `23`

## Final Saved State
- OpenAI GPT 5.5: cash `$1`, net worth `$7,006`, properties `21`, houses `32`, hotels `0`, bankrupt `False`
- Claude Opus 4.8: cash `$1,451`, net worth `$2,941`, properties `7`, houses `0`, hotels `3`, bankrupt `False`
- Gemini 3.1 Pro Preview: cash `$0`, net worth `$0`, properties `0`, houses `0`, hotels `0`, bankrupt `True`
- Grok 4.3: cash `$0`, net worth `$0`, properties `0`, houses `0`, hotels `0`, bankrupt `True`

## Top Costliest Calls
- call 393 turn 100 Claude Opus 4.8 POST_TURN_ACTION_DECISION `end_turn`: $0.207870, 15,354 tokens, 90.8s
- call 527 turn 160 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `propose_trade`: $0.194290, 9,653 tokens, 197.3s
- call 451 turn 119 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `propose_trade`: $0.188471, 9,922 tokens, 147.7s
- call 433 turn 114 OpenAI GPT 5.5 LIQUIDATION_DECISION `sell_houses_or_hotel`: $0.182574, 12,560 tokens, 132.0s
- call 449 turn 119 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `propose_trade`: $0.180315, 9,288 tokens, 168.8s

## Top Slowest Calls
- call 527 turn 160 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `propose_trade`: 197.3s, $0.194290
- call 449 turn 119 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `propose_trade`: 168.8s, $0.180315
- call 451 turn 119 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `propose_trade`: 147.7s, $0.188471
- call 388 turn 99 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `unmortgage_property`: 141.0s, $0.177464
- call 364 turn 88 OpenAI GPT 5.5 POST_TURN_ACTION_DECISION `propose_trade`: 139.8s, $0.143665

## Generated Files
- `analysis/plots/*.png`
- `analysis/tables/*.csv`
- `analysis/analysis_summary.json`