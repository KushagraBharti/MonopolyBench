# Verification record: Opus cross-review

11 November 2026. All work is under `docs/research_raw/paper_revision_2026-11-11/reviews/opus/`. Scripts run from the repository root with `python3 -I` unless noted.

## Scope and compliance

- No game, engine import or run, replay, branch, synthetic test, baseline, model evaluation call, prompt edit, commit or push. No subagents and no contact with peers.
- The canonical records (`saved_games/railway-research-*/game-*/run/decisions.jsonl`) were opened read-only for the paid-debt channel check, the unlocked-collateral check, the quotation spot-check and the two payable-bankruptcy notes. Folding recorded events or fields is existing-record arithmetic, not an executed replay.
- Writes went only to this folder. `git status` at the end shows the same two untracked directories as at the start and no modified tracked file.
- **Reading order.** I read all four frozen drafts, then wrote `initial_position.md` (mtime 05:59:47). Only after that did I open root's `reviews/astra/` material. I never opened `reviews/fable_5_2/`. Root's file timestamps predate my position because root wrote them earlier; the order of reading is a statement about this session, not something those timestamps prove.
- **Literature reading.** I read primary literature only to check central relevance (see below). Web access was limited to two pages.

## Frozen-draft integrity

| Check | Result |
|---|---|
| `four_draft_hashes.json` (sha256 `b8741a1a…8a1ce3`), before reading | 235/235 match (`data/hash_check_before.json`) |
| Same file set, after all work | 235/235 match (`data/hash_check_after.json`); the hash file itself is unchanged |

## Inputs to new arithmetic

| Input | sha256 (prefix) | Status |
|---|---|---|
| `full_drafts/opus/data/offers_rebuilt.json` | `4b1616d83a381a7b` | 920 offers rebuilt from recipients' delivered requests (Opus draft) |
| `full_drafts/fable_5_2/data/a2_offer_ledger.json` | `701e587dee3765e5` | Independent 920-row rebuild (Fable). Agrees with the row above on response, stage, completion cell, and author and recipient cash: 0 mismatches in `data/cross_checks.json` |
| `contracts/data/board.json` | `fc30829e23b8dc9d` | Board, house costs and group sizes |
| `full_drafts/opus/data/completion_episodes.json` | `c94de665fd11a6b4` | 209 completion episodes (Opus draft; Fable reproduces the route counts) |
| `full_drafts/fable_5_2/data/a6_dyads.json` | `8f8295f9ebeaf263` | 148 holder–buyer pairs (Fable) |
| `full_drafts/fable_5_2/data/a7_conversion.json` | `d47daaeb5556f409` | 43 one-sided sale rows (Fable) |
| Fable, Astra and Opus debt ledgers | `016f0f52…`, `e0fac77a…`, `40033658…` | 188 episodes each |
| Canonical `decisions.jsonl` for the games used | per-file sha256 in `data/cross_checks.json`, `data/unlock_check.json` and `data/quote_spotcheck.json` | Read-only |

## Scripts and outputs

| Script | Output | What it establishes |
|---|---|---|
| `tools/check_hashes.py` | `data/hash_check_{before,after}.json` | Frozen package unchanged |
| `tools/cross_checks.py` | `data/cross_checks.json` | (A) the matched opening comparator by block and recipient, plus the later-offer null; (B) holder-cash × request type × recipient × stage, and targeting; (C) holder cash × rival post-trade building capacity; (D) the 14 refusal-then-sale pairs; (E) seller build/win split by held-group stratum; (F) the seven same-deed rows with both estimands; (G) three-ledger debt reconciliation, fallbacks and paid-decision channels |
| `tools/liquidity_openings.py` | `data/liquidity_openings.json` | Opening and later cells by cash band and request type, by recipient; opening targeting; net cash offered |
| `tools/concessions_matched.py` | `data/concessions_matched.json` | Reproduces the 199 concessions (9/58 vs 24/86; 38 and 43 threads) and gives the matched comparison 9/58 vs 17/56 (4/42 vs 11/45 without Opus) |
| `tools/unlock_check.py` | `data/unlock_check.json` | 19 paid episodes and 33 actions use collateral that becomes available only after a building sale; reproduces 180 paid mortgages; no unlocked mortgage occurs without a sale |
| `tools/verify_quotes.py` | `data/quote_spotcheck.json` | 44 argument-bearing Fable quotations match the canonical file hash, field hash and exact span offsets |
| `tools/build_findings.py` | `findings.json` | 27 findings; every quoted passage is asserted verbatim in its frozen file, with line numbers recorded |
| `tools/build_quotes.py` | `replacement_quotes.tex` | 27 cards re-read from the canonical lines with hash checks (26 from Fable's manifest, plus G2 d119 from the Opus manifest) |
| `tools/make_figure.py` (Astra's temporary venv, read-only use) | `assets/fig_guard_liquidity.{pdf,png}` | Central-result figure |
| `tools/check_render.py` (same venv) | `data/replacement_quote_render_check.json` | All 24 cards used appear in the rendered PDF text after typographic normalisation |

**Direct record reads, not scripted.**

- *G12 Sol d190 and G17 Gemini d234.* Holdings, menu options, applied action, and the public and private fields. Both notes sum cash, salvage and only the deeds then listed as mortgageable ($408 vs $500; $530 vs $550). They omit the $340 and $375 that the house sales would release.
- *Paying-decision conditions.* All 82 Opus paying decisions carry `same_model_without_private_thought`. The other 187 paying decisions are standard.
- *Opus timing.* The last non-refused first attempts fall between 16:14:55 and 16:38:11 UTC (`full_drafts/opus/data/conditions.json`, which agrees with Fable's `a1_conditions.json`).
- *Prompt difference.* Read from Fable's stored unified diff and Sol's `prompt_difference.diff`. The two quoted "added sentence" forms are the system-prompt sentence and the separate user-payload `response_instruction`.

## Evidence status of numbers used in the review and replacement prose

- **Fresh in this review.**
  - Matched opening and later contrasts, and the block and recipient splits.
  - Matched concessions.
  - All holder-cash cells by stage and recipient, targeting at openings, and net cash offered.
  - The rival-capacity gradient within holder-cash bands.
  - Pair-level under-$100-at-sale counts.
  - The held-group seller stratum.
  - The turn gaps and first-ask directions of the same-deed rows.
  - Three-ledger debt reconciliation, the paid-decision channel and condition census, unlocked collateral, and the static-menu reading of the two payable bankruptcies.
- **Reproduced and matching drafts.** The 920/918 census; the 199 concessions; the 79/111 and 81/110 counter counts; 188/128/60; 269 paying actions and 61 multi-decision payments; the 14 pairs with 13 lower; 9/14 vs 1/29; the seven same-deed medians.
- **Inherited and not recomputed.**
  - The semantic codes (61/74, κ 0.79, 27/38) and their G1/G15 concentration (31 of 61, from root's join and Fable).
  - The three payment witnesses and the G7 menu lock.
  - The construction-window classification (16/17/7/3, and the causes of the 20 unbuilt groups).
  - From Fable: rent per landing, landing rates, mortgaged-at-completion counts and post-trade cash; asks and bids by buyer position; the 2-of-68 building-sale statistic and the 25-of-128 margin statistic; one-sided settlement prices by seller cash and condition; unsettled-pair drift; pre-estate asset and rent ranks (with Sol's rank figure for buildings and cash).
  - Usage and cost totals.
  - Root's thread counts for Sol's low-cash requests (`reviews/astra/fable_comparison.json`).

## Literature checked

- **FinBoardBench**, arXiv:2605.27896v1. I read the abstract and §3.1–3.2 in the team's archived text copy (`docs/research_raw/paper_phase3_2026-10-29/sol/sources/finboard.txt`, lines 57 and 1195–1225). I checked the Monopoly negotiation statistics (82 of 86 deals in one round; 33.3% counters), the purchase-side liquidity statement and the non-thinking model setting.
- **Cosentino et al.**, arXiv:2605.16575v1. I read the abstract page, fetched 11 November 2026. I checked the title, authors, date and the abstract's claims about counterparty modelling versus outcomes, opening anchors and sellers being more accommodating. I did not read the full paper; root's notes record a reading of the v1 HTML through §4.
- **Jehiel and Moldovanu (1995).** I read the IDEAS bibliographic record for Econometrica 63(6):1321–1335, with its abstract paraphrase. The full paper was not read.
- **Not re-read:** AgentMonopoly, the Vending-Bench Arena study, NegotiationArena, Jehiel–Moldovanu–Stacchetti (1996), Shleifer–Vishny, and Turpin et al. Bibliographic details in `replacement_prose.tex` are copied from the drafts' verified `.bib` entries.

## Build of the replacement prose

- **Build.** `lualatex` twice into `build/`. The final log has no warnings, no overfull boxes, no undefined references and no missing characters. The output is 16 pages (`replacement_prose.pdf`, sha256 `5984ee58…ffe32c9`).
- **Inspection.** All pages were rendered at 70 dpi (`build/render/p01–p16.png`, `sheet1.png`, `sheet2.png`) and checked as contact sheets. The figure was checked at full resolution, and its label collisions were fixed before the final build.
- **Size.** The main prose is about 6,000 words (sections 1–9, excluding cards, tables and bibliography). The abstract is 338 words; the integrated paper should cut it to about 250.

## Remaining risks

- The matched comparator, cash bands and windows were chosen after inspecting these records. They are descriptive, and I report all cells, but a reader could still see them as specification search. The direction of the main contrast is unchanged under the unmatched comparator (+9.9 points), and the matched one is larger.
- Several inputs are peer ledgers, not my own rebuild from raw events. The 920-offer ledger rests on two independent rebuilds that agree, but Fable's pair and seller tables have not been independently rebuilt from events by me.
- The held-group stratum depends on my draft's completion-episode boundaries, which are matched to turn-start snapshots, at turn granularity.
- The static-menu reading of the two payable bankruptcies rests on two notes. It is a precise description, not a rate.
- The quotation spot-check covers the cards I propose. It does not cover every card in all four drafts.
- None of this establishes effectiveness, causal effects of liquidity, validated semantic labels, novelty, or acceptance.
