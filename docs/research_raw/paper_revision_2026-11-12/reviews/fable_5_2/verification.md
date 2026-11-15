# Fable 5.2 cross-review: verification record

12 November 2026. This file says what I checked myself in this review, what I read, what I inherited, and how to rerun it.

## Scope kept

- No game, engine execution, replay execution, baseline, synthetic state, branch, rollout, provider probe or model query. No engine or arena import.
- Stored records only: `decisions.jsonl`, `events.jsonl`, `players.json`, `contracts/data/board.json`, and the frozen ledgers in the drafts for reconciliation.
- No subagent, commit, push or message to another reviewer.
- I wrote only under `reviews/fable_5_2/`. Two exceptions sit outside the repository: build logs in the session scratchpad, and a short note with its index line in the assistant's memory folder. The note says where this review is and gives none of its conclusions, so that it cannot reach another reviewer before their own position is written.
- I did not open any file under `reviews/astra/`, `reviews/opus/` or `reviews/sol/`, and no integration file. One `find` for files newer than the manifest printed those folder names with file counts. I read no content from them.
- One exposure to a peer's conclusions, after my work was done. When I opened the memory index to add my pointer, it held a one-line summary of the Opus cross-review that another session had added. By then every deliverable in this folder was written and built. I changed nothing in response, and I did not open the linked note or the Opus folder. The memory index loaded at the start of my session did not contain that line.
- All Python ran with `-B`, so no bytecode was written into any folder.

## Frozen hashes

`tools/check_frozen_hashes.py` hashes every file named in `four_draft_manifest.json` and `baseline_manifest.json`.

| When | Four-draft manifest | Baseline manifest | Output |
|---|---|---|---|
| Before any reading | 234 of 234 match | 72 of 72 match | `data/frozen_hashes_before.json` |
| After the last build | 234 of 234 match | 72 of 72 match | `data/frozen_hashes_after.json` |

The two reports are identical apart from their label. `CHARTER.md` and `CROSS_REVIEW.md` have the same hashes before and after. `git status` shows no change under `saved_games`, `contracts`, `python`, `frontend` or `scripts`. No file under `full_drafts/` is newer than the manifest.

## What I read

Both referee reports in full. For each of the four drafts: `manuscript.tex`, every authored section file, every generated table, the quotation files, `README.md`, `initial_position.md`, `handoff.md`, `findings_and_limits.md`, `evidence_map.md`, the literature notes where present, and the figures. For Sol, the sixteen full first-decision texts. I viewed the figure images of Astra, Opus and my own draft. I read Sol's figures only through their captions and the tables that hold the same numbers.

## Checks I ran on stored records

Each script is in `tools/` and writes to `data/`. None imports another draft's code.

| Check | Script | Result |
|---|---|---|
| 188 debt episodes rebuilt from raw liquidation decisions | `check_debts.py` | Equal to the frozen debt ledger on identity, debt, cash, bound, outcome and actions, 188 of 188 |
| Paid, eliminated, above every asset | same | 128, 60, 56. The four eliminations within the bound are G7 d338, G12 d190, G12 d249, G17 d234 |
| Partition of payable debts | same | 62/62, 53/52, 16/14 paid. One-action payments 37, 30, 0 |
| Payment descriptors | same | 67 one-action payments, 180 mortgages, 89 sales, $51,997, no fallback action, median debt 36% of the bound |
| First applied action | same | Bankruptcy first in 3 of 131 payable and 50 of 56 above-bound debts |
| Menus of the above-bound debts | same | 8 list bankruptcy alone. Of the other 48, 42 declared first. Assets over debt: quartiles 0.45, 0.61, 0.79. Within a tenth of the debt: 6, of which 3 declared first |
| The sixteen | same | By system 2/3, 5/6, 5/5, 2/2. Twelve games, five blocks. Gap $12 to $326. Nine notes and five provider texts among the payments. Thirteen sales first, one listed mortgage first. All fourteen use a released mortgage |
| Released collateral used | same | 19 payments, 33 mortgages, 14 necessary and 5 optional (G3 d228, d356, d461, d482, G18 d428) |
| Content of liquidation requests | `check_request_values.py` | 338 requests. No value-like field in the menu or the player's state. No release rule in the menu note or system prompt. Timeline rows for mortgages carry dollar amounts |
| Request memory for the sixteen | same, and `verify_replacement.py` | No timeline mortgage of an unlisted deed. One redemption price (G13, Park Place, $193) |
| 920 responses rebuilt from raw trade-response decisions | `check_offers.py` | Equal to the frozen offer ledger on response, completion cell, exchange index, legality, both models, offer decision and form, 920 of 920 |
| Full opening and later tables | same | Every cell equals the four drafts |
| Proposer and recipient strata, nine pairs | same | Equal to Opus and Fable. Seven of nine pairs positive |
| Composition versions | same | 95/116 and 37/72, 93/112 and 26/43, 90/108 and 24/36. Cash bids −5.0, −4.1, −8.6 |
| Proposer-standardized gap | same | 16.0, 21.5, 18.1 |
| Seed blocks and leave-one-out | same | Equal to all four drafts |
| Resampling under three units | same | Whole blocks, exact over 3,125: 24.2 to 35.5. Games, 20,000 draws: 14.0 to 47.9. Blocks then games: 12.5 to 48.8. Without Grok-authored offers: −3.8 to 31.9, −1.9 to 37.9, −10.1 to 40.5. Simulated ends differ from the drafts by at most 0.4 points |
| Counters | same, and `check_response_conflicts.py` | 26/70 and 20/116. 15 of 26 keep the deeds. All stages 79/111 and 81/110 |
| Conflicts between assistant content and the received call | `check_response_conflicts.py` | 139 of 1,068 Grok responses. 64 of 136 Grok openings. 11 of 920 responses, 7 of them among Grok's 28 acceptances |
| Accepted completing openings | same | 3 of 186: G3 d194, G16 d247, G18 d83. The last two name `reject_trade` in content |
| Holder cash | same | 17/69 and 120/175. By recipient as printed in Sol and Opus. 13/20 and 105/125, 4/9 and 92/138 for opening requests to three recipients |
| Proposer house capacity | same | Swaps 4/8, 26/33, 42/48, 23/27. Cash bids 2/3, 13/19, 7/20, 20/28 |
| List value | `check_offers.py` | Medians $170 and $80. 86/103 and 24/48. 81/95 and 18/25 without Grok |
| Ownership transfers | `check_economy.py` | 113 accepted trades, 207 deeds, 63 groups. Non-final estates 227 deeds, 52 groups. Final eliminations 69 groups. 38 of 40 non-final eliminations after developed color rent. First estate to the eventual winner in 18 of 20 games |
| Incident facts | `verify_replacement.py` and direct reads | G5 d258 note present in the d263 request. G13 cash, distance, next roll, auction, final menu, estate and winner. G16 and G18 applied acceptances. G12 d249. G20 sales, mortgages, cash before and after. G7 builds at turns 67, 68 and 71 and the sale at turn 72. G2 bankruptcies at turns 72 and 85. G15 offers, the earlier public appeal and its receipt. G11 correction exchange |

`check_economy.py` counts 61 elimination records because the last elimination in G13 emits two bankruptcy events. The debt ledger has 60, and I use 60.

## Readings, which are judgments

- I read the sixteen first texts in full and agree with thirteen that include the unlisted mortgages or a budget containing them, one question and two omissions. I am a language model. Four language-model readers now agree, all after reading the same referee reports. No human annotated the texts.
- I checked every financing amount in the sixteen texts against the state and board by hand. All match except Sol's $430 in G2. Nine successful texts value the unlisted mortgages. I did not check non-financing figures such as a rent quoted for another square.
- "Named a rejection" for the two conflicted acceptances rests on a pattern match of the tool name in assistant content, confirmed by reading both texts.

## Inherited and not rerun

- The three engine-executed payment sequences for G12 d190, G12 d249 and G17 d234, and the G7 menu search.
- Both stored replay comparisons.
- The 74 reason codes and their agreement. Gemini and Grok's share and the two-game share are as computed in the Opus and Fable drafts.
- First-window construction counts, rent receipts, the fourteen paired histories, asking-price comparisons, the 66 construction defaults, Opus refusal counts and timing, the 2,054 prompts with misattributed summaries, cost and token accounting.
- The keyword screens in the Opus and Fable drafts. I did not rerun them.
- Tool-choice settings at the two run commits. Three drafts report reading the source. I did not re-read it.

## Findings file

`tools/write_findings.py` writes `findings.json` and confirms that each quoted passage occurs on the stated line of the stated frozen file. Twenty findings, all passages found.

## Replacement prose build

- Command: `./build.sh` in `reviews/fable_5_2/`. It reruns every check, regenerates the quotation macros, compiles with `latexmk -lualatex` into `build/`, copies the PDF to `replacement_prose.pdf` and runs `tools/verify_replacement.py`. `./build.sh --tex-only` skips the checks.
- Environment: `/tmp/monopoly-astra-rewrite-venv/bin/python` (Python 3.14.7, NumPy, PyMuPDF, Pillow) and LuaHBTeX 1.24.0, TeX Live 2026. Set `PAPER_PYTHON` for another interpreter.
- Result: 14 pages, SHA-256 `8782ab1fdef77fa8430dde5cd3c9798c5955aa08be2fce122b249182347cd71a`. No overfull box, no undefined reference, no missing character.
- `data/replacement_checks.json`: 39 quotations re-read from the stored field by offset and hash and found in the PDF text. 3 public-message receipts found in the recipient's stored request. 110 number phrases tied to the check outputs. 23 incident facts. All pass.
- Quotations are extracted by anchors from stored fields in `tools/build_quotes.py`. I retyped none. Whitespace inside a span prints as one space, and `data/quote_manifest.json` keeps the stored text, offsets and hashes.
- I looked at all 14 rendered pages as contact sheets and at pages 1, 3, 4, 5, 7, 8, 9, 10 and 12 at reading size. Page 11 has white space above a floated table.

## Limits of this verification

- A rebuild from the same raw records by the same kind of reader is a check of arithmetic and sources. It is not replication, and it says nothing about new games.
- Resampling describes how one cohort's contrast moves with the games counted. Five seed blocks and one roster cannot give a sampling law.
- Where I say a draft's sentence overreaches, that is my judgment about wording, and the integrator may weigh it differently. The counts under it are in `data/`.
- I state no review score and no acceptance forecast, and I name no human author.
