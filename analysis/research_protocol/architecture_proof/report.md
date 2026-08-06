# Zero-Cost Prompt Reconstruction Proof

This report was generated without any provider calls and without modifying source
saved-game artifacts. It compares the original attempt-0 prompt bytes with prompts
rebuilt from (a) a current engine replay plus reconstructed `PromptMemory`,
(b) the original recorded event stream plus the replayed decision object, and
(c) the current micro-fixture behavior using fresh empty memory.

## Result

- Source code commit: `7ce810ebb71bbe102335304f43b17eaa45f43512`
- Selection manifest SHA-256: `77f02b474334dc00cb0a8bc8df416a9ce37f0d75b07fafddf22a9a65386c4603`
- Decisions tested: **12**
- Exact engine-replay system/user/tools triples: **12/12**
- Exact recorded-event system/user/tools triples: **12/12**
- Empty-memory fixture user prompts identical to source: **0/12**
- Public timeline entries removed by empty fixtures: **240**
- Private-thought entries removed by empty fixtures: **120**
- All saved system prompts match the current default after newline normalization: **True**

## Persisted-Input Gate

The 12/12 results above concern reconstructed objects before serialization. A separate
execution precheck then tested whether the persisted fixture inputs could regenerate
the same bytes after a write/read cycle. It exposed a v1 key-order defect: sorted JSON
retained the same values but changed compact prompt serialization. The v1 precheck
failed 12/12 and remains preserved.

The v2 fixture format stores explicit insertion-order-preserving decision and memory
objects. Its independent execution precheck passes **12/12**, with all fixture tree
hashes, generated-file inventories, source prompt hashes, and reconstructed
system/user/tool hashes verified. See `fixture_format_migration.md`. Only v2 is
eligible for repeated-query execution.

## Decision-Level Evidence

| ID | Category | Run | Turn | Decision/action | Engine replay | Recorded events | Empty fixture | Lost memory (public/private) |
|---|---|---|---:|---|---|---|---|---:|
| P01 | trade_proposal | `mock-83265-81ed4937` | 79 | POST_TURN_ACTION_DECISION / propose_trade | exact | exact | different | 20/10 |
| P02 | trade_counter | `mock-321229807-87ca99d7` | 73 | TRADE_RESPONSE_DECISION / counter_trade | exact | exact | different | 20/10 |
| P03 | trade_acceptance | `mock-44910-42ec35c5` | 167 | TRADE_RESPONSE_DECISION / accept_trade | exact | exact | different | 20/10 |
| P04 | auction_bid | `mock-1038910349-f66fa07c` | 113 | AUCTION_BID_DECISION / bid_auction | exact | exact | different | 20/10 |
| P05 | auction_dropout | `mock-24591-46c1eb90` | 141 | AUCTION_BID_DECISION / drop_out | exact | exact | different | 20/10 |
| P06 | building | `mock-3676466999-527872e4` | 139 | POST_TURN_ACTION_DECISION / build_houses_or_hotel | exact | exact | different | 20/10 |
| P07 | building | `mock-44910-42ec35c5` | 265 | POST_TURN_ACTION_DECISION / build_houses_or_hotel | exact | exact | different | 20/10 |
| P08 | liquidation_mortgage | `mock-64394-c3bb8d94` | 153 | LIQUIDATION_DECISION / mortgage_property | exact | exact | different | 20/10 |
| P09 | liquidation_sale | `mock-2413970733-53b199c1` | 171 | LIQUIDATION_DECISION / sell_houses_or_hotel | exact | exact | different | 20/10 |
| P10 | bankruptcy_declaration | `mock-83265-81ed4937` | 190 | LIQUIDATION_DECISION / declare_bankruptcy | exact | exact | different | 20/10 |
| P11 | bankruptcy_fallback | `mock-321229807-87ca99d7` | 95 | LIQUIDATION_DECISION / declare_bankruptcy | exact | exact | different | 20/10 |
| P12 | liquidation_sale | `mock-1038910349-f66fa07c` | 147 | LIQUIDATION_DECISION / sell_houses_or_hotel | exact | exact | different | 20/10 |

## Interpretation Contract

- `exact` means byte-identical UTF-8 system, compact user JSON, and compact tools JSON.
- A recorded-event exact match proves that the saved event stream contains enough
  information to restore the bounded prompt memory when paired with the reconstructed
  engine decision.
- An engine-replay mismatch is reported separately because a state-valid replay can
  still differ in observation-event representation.
- `different` for the empty fixture is expected when the source decision had history.
  The exact removed entries are preserved in `memory_loss.jsonl`.
- This proof does not evaluate model behavior, decision quality, or branch value.
