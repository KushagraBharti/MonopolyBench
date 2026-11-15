# Opus xhigh final review: verification record

## Pins (checked before any other work)

- `integrated/manuscript.pdf`: SHA-256 `8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5` (matches the pin).
- `integrated/qa/integrated_file_hashes.json`: 38 entries, 0 mismatches, rechecked at the end by `checks/opus_final_checks.py`.
- Repository HEAD `a10419d239ff75f9e75a77d1634261a6ca24148c`. The only untracked path is the rewrite package.
- Order of work: I read the full source and recorded `initial_position.md`, then read `final_review/astra/root_review.md`, `integrated/integration_decisions.md` and `integrated/evidence_map.md`.

## What I ran

Every check is read-only. No game, engine call, replay, branch, synthetic test, reference policy or model query was run. Commands ran with `python3 -I` from the repository root. My exploratory scripts were first written to the session scratchpad and then deleted. Everything they computed is consolidated in:

- `checks/opus_final_checks.py` (SHA-256 `7b9e2b57c3b34d58e5b4029986be1bf4487f3f96bd089ce1dc5105b0077ac761`)
- `checks/opus_final_checks.json` (SHA-256 `c43983ee76f6e22bf841c978b6c38f0db23c8960abfb6db9018f52b39665afbe`)

| Check | Source | Result |
|---|---|---|
| Counter predicates (Table 4, bargaining.tex:56, appendix.tex:39) | `integrated/data/agenda_offers.json`, joining each counter to the next offer in its thread | Author-only: 111 counters; requested-deed retention 92 and completion preservation 92 (identical sets, 0 records differ); only-author 88; of those, 85 with higher counterer cash (median $125); same noncash bundle with more cash 79. Neither: 169 counters, 110 requesting a deed, 87 retain, 81 same-bundle with more cash. |
| Opening/later cells, Table 2 arithmetic | same | All 20 cells and the margins sum correctly; 113/393/412 legal plus 1 counter and 1 reject ineligible = 920. |
| Seed-block/game consistency | same + `t01_cohort.json` | Rejection contrast 5/5 blocks, 17/19 games; acceptance 4/5 blocks, 13/19 games. |
| Initiation, earlier same-pair threads | same | Opus 240, Grok 136, Sol 132, Gemini 18; 414 threads. |
| Settlement cash cuts | same | 48 payer-completing (23 recipient-only, 18 author-only, 7 both), median $194, 21 below $100 (Opus 13; 6 eventual winners); neither 57, median $571; thresholds 14/20, 21/30, 22/36, 24/40; Opus receiver in 16 of 30; cash offers to recipients below $100: 12/85 accepted vs 47/407. |
| Nineteen author-only acceptances; 74 reason population | same | 16 later, 8 recipients below $100, 7 Opus (all action-only); all three opening acceptances are Grok standard responses (G3 d194, G16 d247, G18 d083); 74 = Grok 31, Gemini 31, Opus 8, Sol 4; G1 22 + G15 12 = 34. |
| Appendix cash direction | same | 429 one-sided offers, all with a deed to the completing side, 373 paying; medians $200/−$350/−$100/$100. |
| Price table (Table 9) | same + `contracts/data/board.json` (names normalized to keys; B&O = $200) | All 16 cells reproduce exactly, including counts 131/176/87/113. |
| First-window decomposition (Figure 1, development.tex) | `integrated/data/first_management_windows.json`, `t03_trade_groups.json`, `t09_entry_nonbuild_records.json` | Per configuration: Sol 16 built + 1 default; Gemini 17 + 1 valid end; Opus 7 + 5 no-option + 3 defaults after refusal; Grok 3 + 4 no-option + 4 conflicts + 2 valid ends. Entry-buildable 42 → 34 built + 3 defaults + 3 conflicts + 2 stated holds. |
| Static access budgets (Table 11) | Table rows, plus original G1 d298 request | All nine remainders recompute. G1 d298 outside mortgages are Mediterranean + Park Place = $205 (Atlantic not on menu), confirming root's correction to my earlier script. |
| Routes and receipts (Table 5) | `docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl` | 209 episodes: trade 63/18 winner/51 with rent/$57,378 (built-first $53,810 + others $3,568; 11 built later); purchase 16/12/$23,070; auction 9/2; inheritance 121 with 114 winner-owned, 52 observed nonterminal (45 winner), 69 terminal; estate rent $11,472, 14 episodes with rent. G15 Gemini orange: purchase turn 47, first build turn 47, $3,250; green completes turn 114. |
| Estates and creditors | Original `events.jsonl` for all 20 games (`BANKRUPTCY` markers, `BANKRUPTCY_CASH`, zero-price `PROPERTY_PURCHASED`) | Nonterminal 40 eliminations / 227 deeds; winner creditor 35 / 202 deeds; first estate to winner in 18 games, all three in 16; terminal 20 = 19 winner + G13 bank; 170 terminal deeds (397 total). |
| Elimination triggers (OPF-05) | Same events; debtor's last move before each bankruptcy, with building state tracked from build/sell events | 57/60 on a developed colour deed (38/40 nonterminal, 19/20 terminal). Exceptions: G1 Sol (railroad), G13 Grok (Short Line), G13 Sol (luxury tax). |
| Prompt economic-field census (OPF-01, OPF-02) | All 6,989 `decision_started` payloads (game_state minus memory, plus action_state) | Buy-or-auction 547/547 contain price, house cost, rent, group and group progress; auction 854/854 contain group; post-turn 0/4,081, trade response 0/920, jail 0/249, liquidation 0/338 contain any such field. G1 d298 system prompt and tool descriptions read in full: no costs. |
| Opus private-memory field (OPF-08) | Opus `decision_started` payloads | Empty 1,108, only "fallback" 286, real notes 302 (1,394 of 1,696 without a real note). |
| G7 d339 (OPF-03) | Original request; `python/packages/engine/src/monopoly_engine/engine.py` (`_sellable_building_space_indices`, `_build_liquidation_decision`, `_validate_sell_plan`, `_apply_sell_plan`) | Menu: mortgage Oriental or bankruptcy; no sellable keys; bank houses 0; pinks 4/4/hotel; cash $390. Source shows that the sale menu requires highest-built deeds and ≥4 bank houses for a hotel, while the validator checks only final evenness and net stock. The $650 bundle total is arithmetic from the engine's halving of a $100 pink house cost; the bundle was **not** executed. |
| Redemption charge (OPF-01) | `_unmortgage_cost` = `int(math.ceil(value*1.1))` | Principals 50, 90, 100, 110 and 200 are overcharged by $1, matching Appendix C. |
| G12 d249 full note (OPF-11) | Original resolved decision | Opens "Full even liquidation cannot cover the $250"; later recomputes; "survive with $43 and 5 houses" (two would remain). |
| G3 d176 (OPF-06), G1 d426 | Original resolved decisions | G3: action-only attempt 1, public "Holding steady. Done.", no note; the reserve reasoning is in assistant content. G1 d426: content carries public/private fields only; the note says "Do not build". |
| G20 d88–103, 129–160 (OPF-07) | Original resolved decisions | Sol d95 private note declines to fund red development before Gemini's d96 appeal; Grok d97 note "cash boycott", call `end_turn`; d100 Vermont $150, d101 refusal, d102 mortgage. Opus d129 ($140 NY, "money you can put into more red houses") is rejected; d156/158 Vermont $100/$140 is countered at $300/$250, and Opus declines. |
| G13 chronology (OPF-10) | Original events and resolved decisions | Turn 107 Grok 23→26 (Atlantic); trade seq 1808, interest $16; turn 111 roll 26→29 (Marvin); turn 114 auction, event 1911 `PROPERTY_PURCHASED` NC $650 by Opus; turn 146 B&O $200; turn 150 Short Line bankruptcy, yellows to p2 (Sol). The d250 note counts Short Line as an 8 (5/36); the d252 provider text uses 4/36 and calls $130 "the clear survival choice" before the $200 counter. |
| G18 d415–452 | Original resolved decisions and events | $200 offer → $250 "final" (d421); "offer stands" d423/425/427/431; $750 rents at turns 186 and 188; $450 and $350 packages rejected; d441 invocation, d442 withdrawal. |
| G2 d196–198 | Original resolved decisions | Sol offers two railroads for Atlantic + Ventnor; Opus (attempt 1) asks +$100; Sol accepts. |
| G16 d159; G9 target | Original decision and events | Grok $371, Virginia $160 with group shown on the buy prompt; content buy, call auction; Gemini wins at $380 (turn 87). G9 dark blues reach 3/3 houses at turn 60. |
| AgentMonopoly facts | `integrated/qa/literature/agentmonopoly_engine_2434f427.py.txt` (SHA-256 `f509b017…c6`, matching sources.json) | Rent bankruptcy at negative balance; a player-creditor receives spaces with buildings intact; the trade response menu is accept/reject. |
| Replacement prose compiles | Copies of `integrated/preamble.tex` and `sections/opus_quotes.tex` in `build_test/` | LuaLaTeX exit 0. The only warnings are undefined cross-document label/citation references, which are expected. G2 quote cards render (test page 3 inspected). |

## Rendered pages checked

I rendered the pinned PDF with Ghostscript at 70 dpi (all 33 pages, `render/p01–p33.png`) and extracted per-page text. I visually inspected page 1 (title and abstract), page 8 (G2 card), page 12 (Figure 1), page 14 (Figure 2, re-rendered at 160 dpi), page 20 (Table 6) and page 26 (Tables 8–9). Figure annotations match the text (43/9/4/4/3; 34/3/3/2; 56/3/1). The build log's final pass has no rerun warning.

## Inherited (not re-verified by me)

These remain inherited: the engine-executed witnesses for 60 eliminations and 66 defaults (including all 61 Opus reachable targets and the five-sale G12 witness); full replays and their 50,918-event equality; memory reconstruction against 6,989 prompts and 10,235 snapshots; the 139/15/5 Grok conflict census and the 64 conflicting openings; history-formatter counts (44/26/232/2,054); delivery counts (6,882/149/13); the 61/74 semantic agreement; the 240-decision prospective coding; the 114-error recurrence ledger; spending-unit totals ($103,450/$93,000/$92,550; 40/26; 58/34/30); paid-rent and flow totals in Appendix B; the G2 $44 event; G15 balances and the G7 note; FinBoardBench section content (not re-fetched); and the AgentMonopoly prompt-policy sentence (its prompt file is not archived in qa/literature).

## Limits

- The trigger count for OPF-05 identifies the debt by the debtor's last move. It agrees with the retained 57, but it is a reconstruction, not the reducer that produced the retained figure.
- The OPF-03 conclusion that the validator would accept a group-clearing bundle is a reading of source code. I did not submit a plan to the engine, and the scope rules prohibit doing so.
- The prompt census covers initial prompts. Corrective and action-only retry prompts were not separately censused.
- My review shares a model identifier with an evaluated participant (disclosed in review.md).
