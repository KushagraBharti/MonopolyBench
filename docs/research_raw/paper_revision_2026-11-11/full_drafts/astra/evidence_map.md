# Evidence map

## New read-only tabulations

`tools/analyze_records.py` imports no engine or model code. Inputs are pinned in `data/source_hashes.json`.

| Result | Source and output | Verification and limit |
|---|---|---|
| 188 liquidation episodes, 128 paid, 60 bankrupt | Original twenty `decisions.jsonl` and `events.jsonl`; `data/liquidation_episodes.json` | Episodes close on original cash-payment/bankruptcy events. Every liquidation decision is consumed; no unclosed episode. All 269 paid-episode actions have `fallback_used=false`. The boundary excludes cash-sufficient automatic payment. |
| 61 multi-action payments; 180 mortgages, 89 sale actions; total debt paid 51,997 | Same | Actions are calls, not numbers of individual buildings. Actual payment proves the local endpoint, not strategic optimality. |
| Seller/mortgage asking ratios | Retained offer ledger plus board prices; `data/single_deed_prices.json` and `analysis.json` | Exact one-deed-for-cash filter, no jail cards. Six multi-observation seller/mortgage pairs show higher medians for completion; Gemini has one completing ask. Seven same-game/seller/deed comparisons are mixed. Not a matched premium. |
| Rejection split and leave-one-block sensitivity | 918 legal rows from 920; `analysis.json` | Counts reproduce the existing table; leave-one-out ranges are concentration diagnostics, not CIs. |
| Trade-group exposure | Retained 63 episodes joined to original events; `data/trade_group_exposure.json` | All rent sums reconcile to inherited episode totals. Opponent movement is a crude exposure descriptor, not a landing-risk adjustment. |
| Pre-first-estate positions | Original delivered state before final liquidation action; `data/first_estates.json` | Timing is before residual cash and estate transfer. Cash/deeds/building levels are separate proxies, not a net-worth rank or causal model. |

## Inherited, not re-executed

- All 60 historical elimination classifications and 66 default checks: previous executable audit, summarized in the old integrated methods and Appendix B/C. No engine imported or invoked here.
- 61/74 agreed rival-reason labels and per-configuration counts: the preserved two Astra codings. Retrospective, partly unblinded and not human-validated.
- 63 trade groups and first-window categories: prior event/decision reconstruction. New script reads group-specific windows and does not substitute whole-menu availability.
- 209 completion episodes; 227 nonterminal estate deeds; 35/40 nonterminal estates to winners; 57/60 developed-rent elimination debts: prior complete event accounts and final cross-review.
- 240-record planning sample, prospective statements and targets: prior temporal protocol. No new semantic labels were generated for this draft.
- Reconstruction and replay counts: preserved historical reports. This revision does not reproduce them by running the engine.

## Prompt, usage and response evidence

The two system prompts are extracted directly from a G1 standard/refusal recovery chain by `tools/build_assets.py`, with raw text and line-wrapped display copies. Word-preservation is asserted. The metadata census in `paper_rewrite_2026-11-10/feedback/2026-11-11_additional_referee/check_new_claims.py` supplies refusal, timing, reasoning-token and cost-field counts. Its original source hashes are archived; these are usage-field observations, not billing invoices or cognitive measurements. Historical prompt equality/recovery claims in the prior manuscript are corrected here.

## Quotations and case context

Exact definition files and the three quotation manifests are copied from the prior integrated package. Seventeen displayed cards cover eight incidents. `tools/verify_document.py` verifies each original source hash, JSON field hash, character span and rendered text. Case context is inherited from the original-event checks documented in the old final-review folders; the handoff makes clear it is not a fresh engine audit. G2 undeveloped versus developed rent, G13 temporal ordering and G18 bid direction retain prior corrections.

## Protected sources and build

The new directory-level baseline preserves the prior integrated package and feedback. The previous 272 protected source files and 81 frozen-draft files are also checked. New files are owned only by this draft. PDF verification includes missing glyphs, overflows, unresolved references, launch links, page bounds and quoted text. Contact sheets cover all pages; source/raster inspection is distinct from data recomputation.
