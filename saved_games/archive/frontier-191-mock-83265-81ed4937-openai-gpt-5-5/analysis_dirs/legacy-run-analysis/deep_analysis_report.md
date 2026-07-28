# Deep Run Analysis: mock-83265-81ed4937

## Integrity
- Raw winner: `OpenAI GPT 5.5`
- End reason: `BANKRUPTCY`
- Turn count: `191`
- Replay status: `failed`
- Replay first mismatch: `669`
- Derived summary winner bankrupt flag: `False`
- Corrected final snapshot winner bankrupt flag: `False`

## Cost And Tokens
- Total cost: `$27.711730`
- Tokens: `2,884,068` input, `640,477` output, `452,058` reasoning, `3,524,545` total
- Calls/retries/fallbacks/invalid attempts: `583` / `21` / `2` / `23`
- Median latency: `12,115 ms`; max latency: `197,305 ms`

## Final Players
- OpenAI GPT 5.5: cash `$718`, net `$9,708`, property value `$5,690`, building value `$5,150`, mortgage liability `$1,850`, bankrupt `False`
- Claude Opus 4.8: cash `$0`, net `$0`, property value `$0`, building value `$0`, mortgage liability `$0`, bankrupt `True`
- Gemini 3.1 Pro Preview: cash `$0`, net `$0`, property value `$0`, building value `$0`, mortgage liability `$0`, bankrupt `True`
- Grok 4.3: cash `$0`, net `$0`, property value `$0`, building value `$0`, mortgage liability `$0`, bankrupt `True`

## Model Usage
- OpenAI GPT 5.5: `260` calls, `$15.906450`, `1,018,164` in, `364,553` out, `333,728` reasoning
- Claude Opus 4.8: `134` calls, `$9.491715`, `1,092,918` in, `161,085` out, `23,008` reasoning
- Gemini 3.1 Pro Preview: `121` calls, `$1.901478`, `507,591` in, `73,858` out, `60,431` reasoning
- Grok 4.3: `68` calls, `$0.412087`, `265,395` in, `40,981` out, `34,891` reasoning

## Rent Flow
- OpenAI GPT 5.5: collected `$7,358`, paid `$2,526`, net `$4,832`
- Claude Opus 4.8: collected `$2,783`, paid `$3,642`, net `$-859`
- Gemini 3.1 Pro Preview: collected `$84`, paid `$1,930`, net `$-1,846`
- Grok 4.3: collected `$205`, paid `$2,332`, net `$-2,127`

## Bankruptcies
- Turn `113`: `Grok 4.3`
- Turn `126`: `Gemini 3.1 Pro Preview`
- Turn `190`: `Claude Opus 4.8`

## Top Costliest Calls
- call `393`, turn `100`, `Claude Opus 4.8`, `POST_TURN_ACTION_DECISION` -> `end_turn`: `$0.207870`, `15,354` tokens, `90.8s`
- call `527`, turn `160`, `OpenAI GPT 5.5`, `POST_TURN_ACTION_DECISION` -> `propose_trade`: `$0.194290`, `9,653` tokens, `197.3s`
- call `451`, turn `119`, `OpenAI GPT 5.5`, `POST_TURN_ACTION_DECISION` -> `propose_trade`: `$0.188471`, `9,922` tokens, `147.7s`
- call `433`, turn `114`, `OpenAI GPT 5.5`, `LIQUIDATION_DECISION` -> `sell_houses_or_hotel`: `$0.182574`, `12,560` tokens, `132.0s`
- call `449`, turn `119`, `OpenAI GPT 5.5`, `POST_TURN_ACTION_DECISION` -> `propose_trade`: `$0.180315`, `9,288` tokens, `168.8s`
- call `388`, turn `99`, `OpenAI GPT 5.5`, `POST_TURN_ACTION_DECISION` -> `unmortgage_property`: `$0.177464`, `12,783` tokens, `141.0s`
- call `490`, turn `137`, `Claude Opus 4.8`, `POST_TURN_ACTION_DECISION` -> `build_houses_or_hotel`: `$0.173420`, `14,096` tokens, `74.7s`
- call `101`, turn `35`, `Claude Opus 4.8`, `TRADE_RESPONSE_DECISION` -> `counter_trade`: `$0.166515`, `18,927` tokens, `50.9s`
- call `387`, turn `99`, `OpenAI GPT 5.5`, `POST_TURN_ACTION_DECISION` -> `unmortgage_property`: `$0.164214`, `12,353` tokens, `131.4s`
- call `306`, turn `79`, `Claude Opus 4.8`, `TRADE_RESPONSE_DECISION` -> `counter_trade`: `$0.161310`, `13,702` tokens, `65.5s`

## External Framing Notes
- AgentBench motivates multi-turn interactive evaluation and highlights long-term reasoning, decision-making, and instruction following as common agent failure modes: https://arxiv.org/abs/2308.03688
- DSGBench argues for fine-grained decision tracking and strategy turning-point analysis in strategic-game benchmarks: https://arxiv.org/abs/2503.06047
- ReliabilityBench argues that single-run success rates miss reliability properties; retries, fallbacks, perturbations, and fault tolerance should be tracked separately: https://arxiv.org/abs/2601.06112
- Hasbro Monopoly rules ground the housing-shortage and bankruptcy interpretation: 32 houses, 12 hotels, buildings sold back at half price, and last remaining player wins: https://www.hasbro.com/common/instruct/40753.pdf

## Generated Artifacts
- `analysis/tables/*.csv`
- `analysis/plots/*.png`
- `analysis/deep_analysis_summary.json`
- `analysis/deep_analysis_report.md`