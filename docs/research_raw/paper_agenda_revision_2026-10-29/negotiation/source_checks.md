# Original-source and outlier checks

The canonical event reducer, delivered-state checks and independent list-based completion check cover the full population. The following additional records were inspected directly during this extension.

## Every longest-thread outlier

| Thread | Decision span | Counters | Terminal result | Checked final terms |
|---|---|---:|---|---|
| G09-T023 | 147–159 | 11 | accepted | Sol gives Virginia for Opus's Vermont, Connecticut and 325 |
| G10-T013 | 93–104 | 10 | accepted | Sol gives 250, B&O and States for Gemini's Vermont |
| G15-T003 | 46–56 | 9 | accepted | Sol gives Park Place for Opus's 750 and Electric |
| G18-T011 | 162–172 | 9 | accepted | Sol gives Oriental for Opus's 300 |
| G01-T057 | 414–422 | 7 | accepted | Sol gives Kentucky, Indiana, both utilities and two cards for Grok's 325 |
| G04-T021 | 157–165 | 7 | accepted | Grok gives Kentucky for Opus's 600 and a card |
| G07-T021 | 156–163 | 6 | accepted | Opus gives 900 for Grok's B&O |
| G17-T022 | 132–139 | 6 | accepted | Opus gives 200, St James and New York for Sol's Illinois |
| G01-T059 | 435–441 | 5 | rejected | Grok's 150 for Sol's three pinks is rejected |
| G07-T018 | 132–138 | 5 | accepted | Opus gives Park Place for Sol's 800 and States |

Original canonical trade-event indexes alternate their actors and increment the exchange index for every counter. Terminal actors match the current recipient. All ten exchanges stay within the same global turn. The longest thread therefore represents an extended negotiation, not a long-horizon board trajectory.

## Unavailable acceptance

G4 d219 and G12 d228 are the only response opportunities without accept_trade in the delivered menu. Including mandatory incoming-mortgage interest leaves the recipient at -5 and -6 respectively. Their outcomes are rejection and counteroffer. They are retained in the 920-offer census but excluded from the 918-offer acceptance-choice table.

## Attribution and semantic exceptions

G1 d112 is a counterparty-authored settlement. The current author is Opus; Grok receives Connecticut and gives St James plus 100. The canonical transfer direction matches the delivered structured bundle, despite the separately documented prose/tool discrepancy. This check prevents initiator-oriented reversal in the new reducer.

G15 d106 and G17 d186 are coded role errors after comparing the full public/private text with the same-row current-offer actor, cash and holdings. The former claims seller Baltic and 8 cash while Grok actually receives Baltic and has 903. The latter speaks as Oriental's seller while the actor is its prospective buyer. Price/portfolio words in those texts remain recorded expressions, not reliable intentions.

G13 d303 is the sole direct own-completing rejection that also relinquishes an existing recipient color group. Its result is not an exception to the 74-record count, but the paper should disclose that completion alone is not a monotone gain. The other 73 rejections do not break an existing recipient color group.

All 74 applied public/private record pairs were read for the manual coding. Exact quote validation initially caught two transcription mismatches, uppercase versus lowercase at G1 d255 and an absent short phrase at G4 d333. Both were corrected against the complete field before the annotation export passed. No factual or causal correctness was inferred from the coded phrases.

## Scope not checked

This extension does not re-read every provider reasoning trace, independently evaluate 74 labels through a second annotator, replay hypothetical acceptances through the engine, or estimate utility. Acceptance legality comes from the canonical delivered menu and a matching mechanical calculation; actual settlements additionally check their realized output state. The semantic population is exactly the 74 direct rejections defined by the protocol, not all public messages or all rejected trades.
