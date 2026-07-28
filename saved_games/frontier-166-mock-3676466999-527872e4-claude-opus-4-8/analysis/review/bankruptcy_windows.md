# Bankruptcy Windows

Each section includes the terminal decision, the five prior and five subsequent global decisions where available, the legal liquidation menu, and the state facts. “Unavoidable” is used only when the prompt's legal menu and reported liquidity arithmetic are consistent with the snapshot; otherwise the status remains unproven.

## Grok 4.3 — turn 134, `mock-3676466999-527872e4-dec-000428`

Trigger facts: start cash $274; position 7; 2 deeds, 2 mortgaged. Prompt scenario `{"note":"Choose exactly one liquidation action now. The engine will apply it, update your cash/assets, and ask you again if you still cannot pay. Declare bankruptcy only when you cannot or should not raise enough cash.","options":{"mortgageable_space_keys":[],"sellable_building_space_keys":[]},"owed_amount":625,"owed_to_player_id":"Claude Opus 4.8","reason":"RENT","shortfall":351}`; legal menu `["declare_bankruptcy"]`.

Selected action/public record: `declare_bankruptcy` — “Can't cover the $625 rent with only mortgaged dark blues left. Out of options—gg.”

Reported reasoning: “No liquidation options remain; cash $274 vs $625 owed. Bankruptcy inevitable. Claude wins.”

Decision window:

| Offset | Turn | Decision | Player | Legal menu | Action |
|---:|---:|---|---|---|---|
| -5 | 130 | `mock-3676466999-527872e4-dec-000423` | Gemini 3.1 Pro Preview | `["accept_trade","reject_trade","counter_trade"]` | `reject_trade` |
| -4 | 130 | `mock-3676466999-527872e4-dec-000424` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property"]` | `end_turn` |
| -3 | 131 | `mock-3676466999-527872e4-dec-000425` | Claude Opus 4.8 | `["pay_jail_fine","roll_for_doubles"]` | `roll_for_doubles` |
| -2 | 132 | `mock-3676466999-527872e4-dec-000426` | Gemini 3.1 Pro Preview | `["end_turn","propose_trade","mortgage_property","sell_houses_or_hotel"]` | `end_turn` |
| -1 | 133 | `mock-3676466999-527872e4-dec-000427` | Grok 4.3 | `["end_turn","propose_trade","unmortgage_property"]` | `end_turn` |
| +0 | 134 | `mock-3676466999-527872e4-dec-000428` | Grok 4.3 | `["declare_bankruptcy"]` | `declare_bankruptcy` |
| +1 | 136 | `mock-3676466999-527872e4-dec-000429` | Claude Opus 4.8 | `["pay_jail_fine","roll_for_doubles"]` | `roll_for_doubles` |
| +2 | 137 | `mock-3676466999-527872e4-dec-000430` | Gemini 3.1 Pro Preview | `["end_turn","propose_trade","mortgage_property","sell_houses_or_hotel"]` | `end_turn` |
| +3 | 138 | `mock-3676466999-527872e4-dec-000431` | OpenAI GPT 5.5 | `["roll_for_doubles","use_get_out_of_jail_card"]` | `roll_for_doubles` |
| +4 | 139 | `mock-3676466999-527872e4-dec-000432` | Claude Opus 4.8 | `["pay_jail_fine","roll_for_doubles"]` | `roll_for_doubles` |
| +5 | 139 | `mock-3676466999-527872e4-dec-000433` | Claude Opus 4.8 | `["pay_jail_fine"]` | `pay_jail_fine` |

Legal-proof assessment: owed amount=$625; prompt liquidation options=`{"mortgageable_space_keys":[],"sellable_building_space_keys":[]}`. Snapshot/menu maximum terminal liquidity is $274 cash + $0 building sellback + $0 mortgages = $274, which is below the $625 obligation. The terminal prompt offered `declare_bankruptcy`; 0 owned spaces were mechanically liquidatable at the turn-start snapshot, but only the prompt-listed actions were legally selectable at this decision.

Interpretation: terminal bankruptcy is engine-valid and asset transfers are canonical. It is mechanically unavoidable at this terminal decision because every prompt-listed liquidation source leaves total cash below the obligation. Avoidability over earlier turns is not asserted: proving a superior prior policy would require a declared counterfactual continuation oracle, which was not run.

Evidence: `run/state/turn_0134.json`, `run/decisions.jsonl` (`mock-3676466999-527872e4-dec-000428`), `run/actions.jsonl`, and events `mock-3676466999-527872e4-evt-002870`, `mock-3676466999-527872e4-evt-002871`, `mock-3676466999-527872e4-evt-002872`, `mock-3676466999-527872e4-evt-002873`, `mock-3676466999-527872e4-evt-002874`, `mock-3676466999-527872e4-evt-002875`.

## Gemini 3.1 Pro Preview — turn 150, `mock-3676466999-527872e4-dec-000465`

Trigger facts: start cash $441; position 28; 13 deeds, 10 mortgaged. Prompt scenario `{"note":"Choose exactly one liquidation action now. The engine will apply it, update your cash/assets, and ask you again if you still cannot pay. Declare bankruptcy only when you cannot or should not raise enough cash.","options":{"mortgageable_space_keys":[],"sellable_building_space_keys":["ORIENTAL_AVENUE","VERMONT_AVENUE","CONNECTICUT_AVENUE"]},"owed_amount":1300,"owed_to_player_id":"Claude Opus 4.8","reason":"RENT","shortfall":859}`; legal menu `["sell_houses_or_hotel","declare_bankruptcy"]`.

Selected action/public record: `declare_bankruptcy` — “Well played, Claude! Your board was just too deadly. I don't have enough to cover $1300 even after liquidating everything. I yield!”

Reported reasoning: “I owe $1300 to Claude, but if I liquidate everything (all 12 houses on light blue for $300, and mortgage the three properties for $160), my max cash would be $901. Since my total liquidity is less than the $1300 owed, I have no choice but to declare bankruptcy.”

Decision window:

| Offset | Turn | Decision | Player | Legal menu | Action |
|---:|---:|---|---|---|---|
| -5 | 147 | `mock-3676466999-527872e4-dec-000460` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `unmortgage_property` |
| -4 | 147 | `mock-3676466999-527872e4-dec-000461` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `end_turn` |
| -3 | 148 | `mock-3676466999-527872e4-dec-000462` | Claude Opus 4.8 | `["pay_jail_fine","roll_for_doubles"]` | `roll_for_doubles` |
| -2 | 148 | `mock-3676466999-527872e4-dec-000463` | Claude Opus 4.8 | `["end_turn","propose_trade","mortgage_property","build_houses_or_hotel","sell_houses_or_hotel"]` | `end_turn` |
| -1 | 149 | `mock-3676466999-527872e4-dec-000464` | Gemini 3.1 Pro Preview | `["end_turn","propose_trade","unmortgage_property","build_houses_or_hotel","sell_houses_or_hotel"]` | `end_turn` |
| +0 | 150 | `mock-3676466999-527872e4-dec-000465` | Gemini 3.1 Pro Preview | `["sell_houses_or_hotel","declare_bankruptcy"]` | `declare_bankruptcy` |
| +1 | 151 | `mock-3676466999-527872e4-dec-000466` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `end_turn` |
| +2 | 152 | `mock-3676466999-527872e4-dec-000467` | Claude Opus 4.8 | `["end_turn","propose_trade","mortgage_property","unmortgage_property","build_houses_or_hotel","sell_houses_or_hotel"]` | `end_turn` |
| +3 | 153 | `mock-3676466999-527872e4-dec-000468` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `end_turn` |
| +4 | 154 | `mock-3676466999-527872e4-dec-000469` | Claude Opus 4.8 | `["end_turn","propose_trade","mortgage_property","unmortgage_property","build_houses_or_hotel","sell_houses_or_hotel"]` | `end_turn` |
| +5 | 155 | `mock-3676466999-527872e4-dec-000470` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `propose_trade` |

Legal-proof assessment: owed amount=$1300; prompt liquidation options=`{"mortgageable_space_keys":[],"sellable_building_space_keys":["ORIENTAL_AVENUE","VERMONT_AVENUE","CONNECTICUT_AVENUE"]}`. Snapshot/menu maximum terminal liquidity is $441 cash + $300 building sellback + $160 mortgages = $901, which is below the $1300 obligation. The terminal prompt offered `declare_bankruptcy`; 3 owned spaces were mechanically liquidatable at the turn-start snapshot, but only the prompt-listed actions were legally selectable at this decision.

Interpretation: terminal bankruptcy is engine-valid and asset transfers are canonical. It is mechanically unavoidable at this terminal decision because every prompt-listed liquidation source leaves total cash below the obligation. Avoidability over earlier turns is not asserted: proving a superior prior policy would require a declared counterfactual continuation oracle, which was not run.

Evidence: `run/state/turn_0150.json`, `run/decisions.jsonl` (`mock-3676466999-527872e4-dec-000465`), `run/actions.jsonl`, and events `mock-3676466999-527872e4-evt-003135`, `mock-3676466999-527872e4-evt-003136`, `mock-3676466999-527872e4-evt-003137`, `mock-3676466999-527872e4-evt-003138`, `mock-3676466999-527872e4-evt-003139`, `mock-3676466999-527872e4-evt-003140`, `mock-3676466999-527872e4-evt-003141`, `mock-3676466999-527872e4-evt-003142`, `mock-3676466999-527872e4-evt-003143`, `mock-3676466999-527872e4-evt-003144`, `mock-3676466999-527872e4-evt-003145`, `mock-3676466999-527872e4-evt-003146`, `mock-3676466999-527872e4-evt-003147`, `mock-3676466999-527872e4-evt-003148`, `mock-3676466999-527872e4-evt-003149`, `mock-3676466999-527872e4-evt-003150`, `mock-3676466999-527872e4-evt-003151`.

## OpenAI GPT 5.5 — turn 165, `mock-3676466999-527872e4-dec-000487`

Trigger facts: start cash $335; position 32; 7 deeds, 3 mortgaged. Prompt scenario `{"note":"Choose exactly one liquidation action now. The engine will apply it, update your cash/assets, and ask you again if you still cannot pay. Declare bankruptcy only when you cannot or should not raise enough cash.","options":{"mortgageable_space_keys":["READING_RAILROAD","PENNSYLVANIA_RAILROAD","B_O_RAILROAD","SHORT_LINE"],"sellable_building_space_keys":[]},"owed_amount":1300,"owed_to_player_id":"Claude Opus 4.8","reason":"RENT","shortfall":965}`; legal menu `["mortgage_property","declare_bankruptcy"]`.

Selected action/public record: `declare_bankruptcy` — “That $1,300 Park Place hit is fatal. No amount of rail mortgaging covers it — GG, Claude.”

Reported reasoning: “Shortfall is $965; even mortgaging all four railroads raises only $400, so survival is impossible. Declare now rather than hand over extra cash through pointless liquidation.”

Decision window:

| Offset | Turn | Decision | Player | Legal menu | Action |
|---:|---:|---|---|---|---|
| -5 | 161 | `mock-3676466999-527872e4-dec-000482` | Claude Opus 4.8 | `["accept_trade","reject_trade","counter_trade"]` | `reject_trade` |
| -4 | 161 | `mock-3676466999-527872e4-dec-000483` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `end_turn` |
| -3 | 162 | `mock-3676466999-527872e4-dec-000484` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `end_turn` |
| -2 | 163 | `mock-3676466999-527872e4-dec-000485` | OpenAI GPT 5.5 | `["end_turn","propose_trade","mortgage_property","unmortgage_property"]` | `end_turn` |
| -1 | 164 | `mock-3676466999-527872e4-dec-000486` | Claude Opus 4.8 | `["pay_jail_fine","roll_for_doubles"]` | `roll_for_doubles` |
| +0 | 165 | `mock-3676466999-527872e4-dec-000487` | OpenAI GPT 5.5 | `["mortgage_property","declare_bankruptcy"]` | `declare_bankruptcy` |

Legal-proof assessment: owed amount=$1300; prompt liquidation options=`{"mortgageable_space_keys":["READING_RAILROAD","PENNSYLVANIA_RAILROAD","B_O_RAILROAD","SHORT_LINE"],"sellable_building_space_keys":[]}`. Snapshot/menu maximum terminal liquidity is $335 cash + $0 building sellback + $400 mortgages = $735, which is below the $1300 obligation. The terminal prompt offered `declare_bankruptcy`; 4 owned spaces were mechanically liquidatable at the turn-start snapshot, but only the prompt-listed actions were legally selectable at this decision.

Interpretation: terminal bankruptcy is engine-valid and asset transfers are canonical. It is mechanically unavoidable at this terminal decision because every prompt-listed liquidation source leaves total cash below the obligation. Avoidability over earlier turns is not asserted: proving a superior prior policy would require a declared counterfactual continuation oracle, which was not run.

Evidence: `run/state/turn_0165.json`, `run/decisions.jsonl` (`mock-3676466999-527872e4-dec-000487`), `run/actions.jsonl`, and events `mock-3676466999-527872e4-evt-003329`, `mock-3676466999-527872e4-evt-003330`, `mock-3676466999-527872e4-evt-003331`, `mock-3676466999-527872e4-evt-003332`, `mock-3676466999-527872e4-evt-003333`, `mock-3676466999-527872e4-evt-003334`, `mock-3676466999-527872e4-evt-003335`, `mock-3676466999-527872e4-evt-003336`, `mock-3676466999-527872e4-evt-003337`, `mock-3676466999-527872e4-evt-003338`, `mock-3676466999-527872e4-evt-003339`, `mock-3676466999-527872e4-evt-003340`.

