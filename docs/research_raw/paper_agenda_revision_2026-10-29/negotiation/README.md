# Negotiation and collective-flow extension

This directory adds finite-cohort evidence for Q1, Q3 and Q7. It changes no saved game, engine, prompt or manuscript. The protocol was written before the new census. The stated-reason subset was fixed before reading its text.

## Results ready for integration

- 526 complete negotiation threads; 920 received offers; 918 with acceptance legal; 113 settlements, 394 counters and 413 rejections.
- Among 221 acceptance-legal offers newly completing the recipient's color set: 34 accept, 113 counter, 74 reject. Only one of those 74 rejections also breaks an existing recipient set.
- Both-party completion is also insufficient: 10 accept, 35 counter, 36 reject among 81 legal offers.
- 81 of 113 settlements follow counters. In 44, the final author differs from the initiator. All threads resolve within one global game turn. There are 414 subsequent threads between a pair already observed in that game.
- The complete flow ledger separates trade cash, traded deeds, paid rent, estate cash and inherited deeds. Winners receive 202 of 227 nonterminal inherited deeds and 7,148 of 7,843 nonterminal estate cash. These are realized pathways, not effects on winning.

`methods_results.tex` is finished manuscript prose with a native LaTeX table and explicit answer boundaries. The strongest new contribution is a complete opportunity denominator for the proposition that obtaining a set should induce acceptance.

## Semantic results requiring independent challenge

`rejection_reason_coding.json` contains all 74 complete applied public/private fields, exact span evidence, source records and manual nonexclusive tags. One model-assisted pass found 63 rival completion/development/funding/survival/estate-denial mentions, 42 price/liquidity mentions, 21 portfolio-retention mentions and 13 timing/reconsideration mentions. Two records have explicit buyer/seller role errors; two contain no applicable consideration in the two coded fields. All have public text; 66 have applied private text. Provider summaries are excluded from this coding, not claimed unavailable.

These are stated considerations, not proven motives, truthful arithmetic, rationality, persuasion or gold-standard human labels. G1 supplies 22 and G15 twelve of the 74 records. The output deliberately does not infer a coalition or deception label from keywords or graph edges. Independent adjudication of the 74 records is the next review step, not silently claimed complete here.

## Reproduce

From the repository root, using Python 3.11 or newer and only the standard library:

```sh
python3 docs/research_raw/paper_agenda_revision_2026-10-29/negotiation/analyze_negotiation.py
python3 docs/research_raw/paper_agenda_revision_2026-10-29/negotiation/code_rejection_reasons.py
python3 docs/research_raw/paper_agenda_revision_2026-10-29/negotiation/validate_extension.py
```

The raw inputs are the two original saved-game collections, plus the board specification. `results.json` records every input SHA-256 and the producing script/protocol hashes. The script writes only here. JSON records retain nested fields; CSVs retain the same nested values as JSON cells. `threads`, `offers`, `flows`, `concentration`, and `games` are separate ledgers. `results.json` includes all eighty game/configuration and 120 game/pair strata.

## Checks performed

- All 6,989 delivered initial cash/ownership/mortgage/development states equal an event reconstruction.
- Every received offer's author and bundles match its delivered structured current-offer fields; all 920 acceptance-feasibility calculations match the engine menu.
- All 113 settlement predictions match the next cash and property state, including transfer interest.
- A separately implemented delivered-bundle completion count agrees for every offer.
- All typed flow sums reconcile to canonical cash, rent and deed events.
- Source checks and eight deliberately corrupted copies pass in `validation.json`.
- All 74 semantic records were read in full and each retained quote is checked as an exact substring of its field.
- All ten longest threads were inspected against their original event sequence, actors, exchange indexes, final bundle and selected terminal action. They include the eleven-counter G9 thread, ten-counter G10 thread, and the sole rejection among the ten, G1 d441.

No engine branch, paid model call, new game, policy experiment, commit or push was run. This is one implementation plus source checks, not independent scientific replication. Existing shared response conditions and repeated-game dependencies remain. Do not convert these finite counts into IID confidence intervals or claim negotiation effectiveness from counteroffer association.
