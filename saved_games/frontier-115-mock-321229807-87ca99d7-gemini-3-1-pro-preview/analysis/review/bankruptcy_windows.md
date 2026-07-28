# Bankruptcy windows

The three windows use the required applied-decision ±5 convention. “Avoidable” is asserted only when an immediate unilateral legal action is explicitly exposed and sufficient. All decision IDs below expand to `mock-321229807-87ca99d7-dec-NNNNNN`.

## Claude Opus 4.8 — turn 95

| Relative position | Decision | Turn | Actor | Applied action | Role |
|---:|---|---:|---|---|---|
| -5 | `000325` | 94 | Grok | reject trade | prior negotiation |
| -4 | `000326` | 94 | OpenAI | end turn | prior turn closure |
| -3 | `000327` | 95 | Claude | mortgage Illinois | raises $120 |
| -2 | `000328` | 95 | Claude | mortgage Reading | raises $100 |
| -1 | `000329` | 95 | Claude | mortgage Tennessee | raises $90 |
| 0 | `000330` | 95 | Claude | declare bankruptcy (fallback) | elimination |
| +1 | `000331` | 96 | Gemini | end turn (fallback) | post-transfer build delayed |
| +2 | `000332` | 97 | Grok | end turn | post-elimination |
| +3 | `000333` | 98 | OpenAI | propose Pacific/Ventnor sale | post-elimination market |
| +4 | `000334` | 98 | Grok | reject | post-elimination market |
| +5 | `000335` | 98 | OpenAI | propose blocker swap | post-elimination market |

**Immediate state and legal proof.** Boardwalk rent was $1,400. Claude began with $893, then the three mortgages raised $310, yielding $1,203 and a $197 shortfall. The `dec-000330` scenario exposed `sell_houses_or_hotel` and `declare_bankruptcy`; Mediterranean and Baltic each had four sellable houses. Sale proceeds were $25 per house. Eight houses therefore yielded $200, enough to pay and leave $3.

**Model attempts and fallback.** Both attempts selected a build-sale plan of four houses from each brown and explicitly computed the $200 proceeds. Both failed validation because the public message was embedded in malformed tool arguments rather than supplied in the required schema position. Deterministic fallback selected bankruptcy. This decision is one fallback decision out of 366 applied decisions; its two attempt rows are two of four `fallback_used=true` attempt rows out of 377 calls.

**Causal buildup.** Gemini’s targeted third Boardwalk house at `dec-000321` raised rent to $1,400. Claude’s earlier 4/4 brown development created the exact emergency liquidity that could have survived. The terminal cause was therefore the serialization/fallback path, not absence of assets or a strategic choice to prefer bankruptcy.

**Assessment.** Avoidable immediate bankruptcy, high confidence. The claim is limited to surviving this payment; no claim is made about later victory.

Evidence: `run/decisions.jsonl`; `run/actions.jsonl`; seq 2150–2206 in `run/events.jsonl`; `run/state/turn_0095_decision_0004.json`; all `quality_check/decision_mock-321229807-87ca99d7-dec-000330_*`.

## OpenAI GPT 5.5 — turn 106

| Relative position | Decision | Turn | Actor | Applied action | Role |
|---:|---|---:|---|---|---|
| -5 | `000350` | 103 | Gemini | reject trade | final blocker-sale rejection |
| -4 | `000351` | 103 | OpenAI | end turn | retained mortgaged blockers |
| -3 | `000352` | 104 | Gemini | build two dark-blue hotels | raises Park rent to $1,500 |
| -2 | `000353` | 104 | Gemini | end turn | closes build turn |
| -1 | `000354` | 105 | Grok | end turn | preceding decision |
| 0 | `000355` | 106 | OpenAI | declare bankruptcy | elimination |
| +1 | `000356` | 107 | Gemini | build two brown hotels | converts inherited group |
| +2 | `000357` | 107 | Gemini | end turn | post-elimination |
| +3 | `000358` | 108 | Grok | end turn | post-elimination |
| +4 | `000359` | 110 | Grok | end turn | post-elimination |
| +5 | `000360` | 111 | Gemini | roll for doubles | post-elimination |

**Immediate state and legal proof.** Hotel Park Place rent was $1,500 and OpenAI held $569. Pacific and Ventnor were already mortgaged and OpenAI had no buildings. The authoritative `dec-000355` menu exposed only `declare_bankruptcy`; it did not expose a mortgage, building sale, or trade.

**Causal buildup.** OpenAI had repeatedly tried to sell Pacific/Ventnor at varying prices, including immediately before Gemini’s hotel conversion, and retained them after rejection. Those prior choices affected the path to $569, but an opponent-accepted trade is not a unilateral bankruptcy escape. Gemini’s turn-104 hotel build was the immediate rent escalation.

**Assessment.** Forced within the immediate legal menu, high confidence. Earlier strategy is reviewable but does not justify an “avoidable bankruptcy” label.

Evidence: `run/decisions.jsonl`; `run/actions.jsonl`; seq 2368–2394 in `run/events.jsonl`; `run/state/turn_0106_decision_0001.json`; `quality_check/decision_mock-321229807-87ca99d7-dec-000355_*`.

## Grok 4.3 — turn 114

| Relative position | Decision | Turn | Actor | Applied action | Role |
|---:|---|---:|---|---|---|
| -5 | `000360` | 111 | Gemini | roll for doubles | late jail strategy |
| -4 | `000361` | 112 | Grok | end turn | conserved $755 |
| -3 | `000362` | 113 | Gemini | roll for doubles | jail exit sequence |
| -2 | `000363` | 113 | Gemini | unmortgage Reading | secondary rent activation |
| -1 | `000364` | 113 | Gemini | end turn | preceding decision |
| 0 | `000365` | 114 | Grok | declare bankruptcy | terminal elimination |
| +1 through +5 | — | — | — | censored | game ended |

**Immediate state and legal proof.** Chance advanced Grok to hotel Boardwalk for $2,000. Grok held $755 and was short $1,245. The menu exposed mortgages on Oriental ($50), Pennsylvania Railroad ($100), Kentucky ($110), and North Carolina ($125), totaling about $385. Even exhausting them would yield about $1,140, still roughly $860 short. No buildings were saleable.

**Causal buildup.** Grok had completed light blue at turn 103 but left its deeds mortgaged and prioritized liquidity. Unmortgaging them would have consumed cash and could not by itself bridge the terminal shortfall. Gemini’s dark-blue completion and hotel build were the direct rent mechanism.

**Assessment.** Forced within the immediate unilateral legal set, high confidence. The +5 side is right-censored by game termination and is not treated as missing evidence.

Evidence: `run/decisions.jsonl`; `run/actions.jsonl`; seq 2471–2487 in `run/events.jsonl`; `run/state/turn_0114_decision_0001.json`; `quality_check/decision_mock-321229807-87ca99d7-dec-000365_*`.

## Reconciliation

- Bankruptcy decisions: 3 (`dec-000330`, `dec-000355`, `dec-000365`).
- Bankruptcy windows: 3, with 11 applied decisions each where available; Grok’s post-window is terminally censored.
- Avoidable immediate bankruptcies: Claude only, supported by an exact legal action and arithmetic.
- Forced immediate bankruptcies: OpenAI and Grok, supported by legal menus and asset/liquidity states.
- Deterministic fallbacks: 2/366 decisions. Attempt rows marked fallback: 4/377. Only Claude’s fallback directly caused elimination; Gemini’s fallback delayed a build.
