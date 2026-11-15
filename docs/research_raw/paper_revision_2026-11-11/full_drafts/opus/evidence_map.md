# Evidence map (Opus draft, 11 November 2026 revision)

Status vocabulary:

- **Fresh**: computed in this draft from canonical saved records by a script in `tools/` (no engine import, no model call). Output file named.
- **Rebuilt-and-matched**: fresh, and also compared with a retained ledger from earlier work.
- **Inherited (engine)**: from earlier engine-executed audits (witnesses, bounds, replays); not rerun.
- **Inherited (record audit)**: from earlier record-reading audits; not rerun unless stated.
- **Inherited (semantic)**: earlier LLM-assisted labels, joined without recoding.
- **Quote-checked**: displayed text reloaded from the original field and compared exactly (`qa/quote_checks.json`).

Source hashes for every canonical file read are in `data/source_hashes.json`. Cache building: `tools/corpus.py` (reads 120 files across 20 games; decision/attempt/event totals 6,989 / 8,679 / 50,918 reproduce).

## Setup and conditions

| Manuscript claim | Status | Source / output |
|---|---|---|
| 20 games, 5 seeds x 4 cyclic rotations, winners 8/7/3/2, seats 7/7/3/3, turns 75–386 | Rebuilt-and-matched | `tools/sensitivity.py` → `data/sensitivity.json` (`cohort_matches_retained: true` vs `t01_cohort.json`) |
| Decisions and attempts per system (1,961/1,991; 1,669/1,689; 1,696/3,301; 1,663/1,698) | Fresh | `corpus.py` cache; `conditions.py` |
| No token cap, no sampling parameter; Grok `tool_choice: required`, others `auto` (8,679 requests) | Fresh | `tools/requests_census.py` → `data/requests_census.json` |
| Standard system prompt verbatim; action-only diff (removes private-thought lines, keeps "Deception in public chat is allowed" and "bluff, deceive"; adds "Return only a legal tool call...") | Fresh | `tools/conditions.py` → `data/conditions.json` (`standard_system_prompt`, `system_prompt_diff`); standard text from `recovery_prompts.json`, action-only text from stored attempt-1 prompts |
| 1,605 identical refusal strings, `content_filter`/`refusal`; 1,604 first-attempt refusals; 0 of 1,604 action-only refused; chains 91 / 1,544 / 60 / 1 | Fresh | `data/conditions.json` |
| G1–G4 refusal 64/84, 40/60, 30/53, 80/109; last accepted 16:14:55–16:38:11 UTC; all refused from 16:40; G5–G20 1,390/1,390 | Fresh | `data/conditions.json` (`per_game`, `g1_4_ten_minute_bins_utc`) |
| Anthropic doc: reasoning-extraction requests "might be declined with the `reasoning_extraction` category" | External, read 11 Nov 2026 | `literature_inspiration.md` |
| Opus memory window 1,108 empty / 286 fallback / 302 with note | Fresh (reproduces inherited) | `data/conditions.json` |
| 60 of 61 Opus construction defaults follow invalid action-only build | Fresh chain count + inherited construction classification | chains in `data/conditions.json`; 61 executable targets inherited (engine) |
| Reasoning tokens 38/254/259/3,589; Sol zeros 1,296/1,991; Grok max completion 69,595, max reasoning 28,018 | Fresh | `data/conditions.json` |
| Cost: usage.cost $76.04; upstream $141.71; BYOK-aware rule $141.39; 1,600 Opus + 3 Grok attempts without usage | Fresh | `data/conditions.json` |
| Grok 139 conflicts of 1,663; 1,068 named content | Inherited (record audit) | `paper_rewrite_2026-11-10/data/resolution_conditions.json` |
| 64 Grok conflict-opened threads, 17 settled | Fresh join of inherited conflict list | `data/sensitivity.json` |
| 2,054 misattributed-history prompts; 149 undelivered messages | Inherited (record audit) | earlier audits cited in integrated evidence map |
| House conventions (estate keeps buildings and mortgages, no interest; bank estate unowned, no auction; developed-group deeds untradeable; redemption ceil(1.1M)) | Source read | `engine.py` lines ~1770–1776, 2484–2490, 2955–3020 |

## Bargaining (Section 4)

| Claim | Status | Output |
|---|---|---|
| 920 offers / 526 threads / 113-394-413 responses / 918 acceptance-legal; zero field mismatches with retained ledger | Rebuilt-and-matched | `tools/offers.py` → `data/offers_rebuilt.json`, `data/offers_rebuilt_check.json` |
| Census by cell × stage (Table 3) | Fresh | `data/bargaining.json` (`census`) |
| Opening rejection 138/187 vs 152/238 (+9.9); blocks +15.0/+18.9/+5.8/+7.6/+10.8; leave-one-out 8.7–11.3; recipients Sol +17.1, Gemini +5.1, Grok +9.6, Opus −7.1 | Fresh | `data/bargaining.json` (`open_reject`) |
| Without Grok conflict threads +9.7; without Opus either side +19.0; G1–4 +15.0; G5–20 +9.2 | Fresh | `data/sensitivity.json` |
| Opponent standing null (67/70/67% opening rejection) | Fresh | `tools/extras.py` → `data/extras.json` (`standing`) |
| Concessions 199; author-only 9/58, neither 24/86; without Opus recipient 4/42 vs 16/62; 4 of 5 blocks | Fresh | `data/bargaining.json` (`concessions`), `data/sensitivity.json` |
| Counters repricing same bundle 79/111 vs 81/110 | Rebuilt-and-matched (reproduces retained) | `data/bargaining.json` (`counter_repricing`) |
| Asks 1.625 (87) vs 1.083 (113); standard 2.286 vs 1.389; Sol 2.32/1.80; Grok 2.00/1.05; Opus 0.93/0.88; mortgage cells; blocks 3 of 5 | Fresh (pooled reproduces retained Table 9) | `tools/pricing.py` → `data/pricing.json`; `data/bargaining.json` (`prices`) |
| Bids 1.31 vs 1.39; standard 1.13 vs 1.50; Sol 1.88/1.25; Grok 0.50/1.54; Opus 1.50/1.36 | Fresh | same |
| Same-seller single-deed pairs: 7; first ask higher 5, lower 1, equal 1; all-above in 3 (G2, G16, G20); up to 106 turns apart | Fresh | `data/extras.json` (`same_deed_pairs`, `same_deed_summary`) |
| Rival-consequence codes 61/74 (κ 0.786), 34/36 both, 27/38 recipient-only; own-cost 41/74 (κ 0.775); by recipient 29/27/4/1 of 31/31/4/8; 31 of 61 from G1+G15 | Inherited (semantic), joined and κ computed fresh | `data/bargaining.json` (`reason_codes`); ledgers hashed in `reason_sources` |
| Capacity gradient flat: 100/134, 32/42, 6/11 opening; 13/65, 7/34, 1/3 later | Fresh | `data/extras.json` (`capacity_author_only`) |
| Settled sales: completing 22 (14 seller < $100, median $61) vs other 31 (7, $276); without Opus 6/11 vs 4/22; low-cash standard median 2.25×, Opus 0.66× | Fresh | `data/bargaining.json` (`settled_sales`), `data/pricing.json` |
| Opus authored 381 offers, opened 240 threads; 162/189 trade responses action-only; 11 of 22 completing sales, 8 of 14 low-cash | Fresh | `data/sensitivity.json`, `data/offers_rebuilt.json` |

## Development, debts and estates (Section 5)

| Claim | Status | Output |
|---|---|---|
| Event tracker matches 3,246 turn-start snapshots (cash, owner, mortgage, buildings) | Fresh | `tools/track.py` (prints; zero mismatches) |
| 63 trade groups (17/18/15/13); purchase 16 ($23,070); auction 9 ($3,358); nonterminal estates 52 ($11,472; 45 winner-owned); terminal 69; trade rent $57,378 | Rebuilt-and-matched (all equal retained counts) | `tools/groups.py` → `data/completion_episodes.json` |
| 54 built; 44 by owner's next turn; 213 landings, 150 developed; $56,126 developed rent; $374 vs $20 per landing; per-system landing splits; 9 never built with 33 landings and $538 | Fresh | `data/completion_episodes.json` |
| 8 of 9 never-built vs 10 of 54 built had a mortgaged deed at completion | Fresh | same |
| Grok notes defer redemption on four groups; three Opus first-window defaults | Inherited (record audit) | integrated `first_management_windows.json` |
| 188 debt episodes; 128 paid; 61 multi-decision; 68 with building sales; mortgage-first 40/51; medians $250 vs $925; 108 rent; 102/128 later eliminated | Fresh | `tools/debts.py` → `data/debt_episodes.json` |
| 56 bound-negative / 3 payable / 1 menu lock (G7) | Inherited (engine) | `t06_eliminations.json` joined in `data/debt_episodes.json` |
| First creditor wins 18/20; is asset leader 15/20; rent leader 15/20; developed group 20/20; leader wins 15; divergent games G4, G7, G15, G17, G20; median first-estate turn 88.5 | Fresh | `tools/estates.py` → `data/first_estates.json` |

## Incidents

All eight incidents (G2, G15, G20, G12, G13, G18, G7, G19) use quote definitions verified by `tools/verify_quotes.py` (31 cards; exact span, label, TeX decoding and rendered presence all true). Four G2 definitions are new (`sections/new_quotes.tex`, `data/new_quote_manifest.json`) and their public messages were confirmed in the counterparty's next request. The economic narratives (later turns, estates, auction purchases, witnesses) are inherited from the 10 November integrated record checks, except the G15 balances ($830/$233; $480/$583) and G2 d118–d128 sequence, which were read fresh from `data/offers_rebuilt.json` and the raw decision stream.

## Figures and tables

- Figure 1 (`assets/bargaining.pdf`), Figure 2 (`assets/distress.pdf`), Figure 3 (`assets/lifecycle.pdf`): `tools/build_figures.py` from `data/bargaining.json`, `data/pricing.json`, `data/completion_episodes.json`. Palette checked with the dataviz validator (blue/orange/aqua all-pairs CVD ΔE ≥ 9.2).
- Appendix tables: `tools/build_tables.py` → `sections/gen_tables.tex`, `sections/gen_prompt.tex`.
- Main-text Tables 1–5 are hand-set from the same JSON values (checked against the outputs above).
