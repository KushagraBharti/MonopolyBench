# Verification record (Opus final review)

Everything below is source reading, arithmetic over saved records, quote checks, primary-literature retrieval, or a document build inside this folder. No game, engine import or execution, replay, policy or baseline run, state search, synthetic scenario, provider call or judge call was made. Historical engine witnesses, the G7 menu search and replay reports are **inherited**: I read their stored results and did not rerun them.

## Pins

| Check | Before (`checks/pin_check_before.json`) | After (`checks/pin_check_after.json`) |
|---|---|---|
| Finalization manifest SHA-256 | `a362c4c6d020adb115a50b919d85d3db6777d223189493d7c4edd1517885e269` | same |
| Finalization entries matching | 2396/2396 | 2396/2396 |
| Integrated PDF SHA-256 | `e5c44bebfb1d6b0b7c434d875261be63b11e4c6457396ee97596457a0c840dae` | same |
| November 12 manifest SHA-256 | `04d0a0d3ac02a337ebfc4c7426c184f85862e53d60984e8beaba724ab29e5460` | same |
| November 12 entries matching | 84/84 | 84/84 |

The repository's dirty or untracked state outside `paper_finalization_2026-11-14/` matches the session-start snapshot. I wrote only under `final_review/opus/`.

I did not use the PyMuPDF in the pinned Sol `.venv`, because importing from it could write bytecode into 2054 pinned files. Rendering used a scratch venv at `/private/tmp/monopoly-finalization-venv` with `python -B`.

## Checked directly in this review

| Item | Script or output | Result |
|---|---|---|
| Entry sums for all 188 episodes, recomputed from each first liquidation prompt plus `board.json` (not reused from the packaged ledger) | `checks/recount_finance.py` → `recount_finance.json` | C, D, S, M0 and M* match `episodes_188.json` in every row. 128 paid; 131 payable; 62/53/16; paid 62/52/14 |
| 28/30 | same | 30 owners, all paid, 28 without sale. Sellers G12 d282 and G18 d372 (Opus), one States Avenue house each. G7 d318's first and only menu has no sellable building |
| First actions | same | Bound covers: 129 finance, 3 declare. Short: 6 finance, 50 declare, 8 forced |
| Entries with M* > M0 | same | 121 (30 initial, 53 middle, 16 necessity, 21 short, 1 G7). Confirms root's rejection of the 5/37 denominator |
| 920/918 census; 74 and 61/74 cells; concentration; disagreement keys | `checks/recount_other.py` → `recount_other.json` | 113/394/413; 918 legal; 38 + 36 = 74; 27 + 34 = 61; G1 22, G15 12; Grok 31, Gemini 31 |
| Opening-swap proposer cells | same | Sol 44/50 vs 9/11; Gemini 4/8 vs 0/2; Opus 42/50 vs 15/23; Grok 5/8 vs 13/36; pooled 95/116 vs 37/72 |
| G7 d139–d152 | same, `g7_trace` | All figures in the integrated text and casebook check; the three new quotations are exact substrings |
| Liquidation content observability | same | Sol 93/0/0, Gemini 89/0/0, Opus 100/19/0, Grok 56/56/27 (decisions / with content / naming an action) |
| Per-game run commit; rules hashes | same | G1–G4 at `42f85183…`, G5–G20 at `d6808534…`. `engine.py` `122edf5f…` and `board.json` `fc30829e…` at both commits and in the working tree |
| 43/48 numeric presence | `checks/numeric_presence.py` → `numeric_presence.txt` | 43/48 reproduced (34 contain U* itself). 27/27 without locked collateral, 16/21 with it. The five non-matches read in full |
| All channels of the sixteen | Read `integrated/sections/all_channels.tex` in full | No non-selected channel moves a case to a stronger category |
| G20 d327 components | Read the returned explanation | 49 + (325 + 280 + 60) + (450 + 250) = 1,414; salvage \$700, mortgage \$665 |
| Continuation proof | Read `_resolve_pending_payment`, `_mortgageable_space_indices`, `_sellable_building_space_indices` and `_validate_sell_plan` in `engine.py` | Argument correct for the stated conditions, including bundles (final-state validation; per-unit effect on B + H is never negative) |
| Static rebuild | `build_check/` (copied static sources only), `bash build.sh` | Exit 0; 29 pages; extracted text identical to the pinned PDF on every page. Byte hash differs (`823aba2f…`), as expected from PDF identifiers |
| Quote and field verification | Copied `tools/verify_document.py` run inside `build_check/` | 23 displayed quotes and 29 focal fields match canonical sources and appear in the PDF; 84 protected files unchanged; no diagnostics, out-of-page text or blank pages |
| Rendered pages | `render/p01–p29.png` from the pinned PDF | Main text ends on page 7; references on pages 7–8; supplement on pages 9–29. Pages 1, 4, 7, 12, 20, 28 and 29 inspected at full size; the rest via text extraction and the section/table map |
| Proposed replacements | `checks/replacements.py --apply` → `amended_build/` | All 15 old strings occur exactly once and apply. The amended copy compiles with no warnings; 29 pages; main text still ends on page 7; PDF metadata populated. Pages 3, 5, 6, 7 and 8 rendered and inspected |
| Primary literature | WebFetch of arXiv/ACL/ICML pages, 15 Nov 2026 | Oota et al. 2609.38108; Xiong et al. ACL 2026 long 27, pp. 623–645; Co and Konuganti, ICML 2026 workshop poster 67788; Cattle Trade 2605.14537; DECE 2610.35773. All match how they are characterized |

## Inherited, not rechecked here

- The three payable-declaration payment witnesses and the G7 restricted-menu search (historical engine executions).
- The twenty replay-report pairs.
- The episode boundary detector.
- The completion classification of the 920 offers.
- The bootstrap and leave-one-out ranges.
- The two model-assisted semantic readings behind 61/74.
- Refusal, tool-choice, token, cost and delivery censuses.
- Incident continuations beyond G7 d139–d152 and the quoted fields.
- Rulebook clause readings from earlier primary-source checks.

## Limits of this verification

- The sixteen-text and 61/74 categories remain model-assisted, and my reading is a further model reading, not human annotation.
- Literature pages were read through a summarizing fetch tool. The quoted figures (for example, 22–45% in Oota et al.) were returned by that tool.
- A matching extracted text with a different byte hash shows a portable static build, not byte-identical reproducibility.
