# Verification notes

Fable 5.2, final whole-paper review, 15 November 2026.

## Scope I kept to

- No game, engine import or execution, replay, policy or baseline run, search over game states, synthetic scenario, or model, provider or judge call.
- No subagents. No commit, push or external message. HEAD is `863f8ef7` before and after.
- I wrote only under `final_review/fable_5_2/`. I wrote no memory file.
- I did not open the `final_review` folders of Astra, Sol or Opus, or `final_review/ADJUDICATION.md`. I saw their names in one directory listing.
- I wrote `initial_position.md` before opening `INTEGRATION_DECISIONS.md` or `adversarial/`. Its hash and time are in `checks/initial_position_sha256.txt`. The task brief had already told me three root decisions, and the note says so.
- Network use was three arXiv abstract pages (2605.14537, 2610.35773, 2608.14825). The requests carried no project or user detail.

## Pins

| Pin | Before | After |
|---|---|---|
| `integration_review_manifest.json`, SHA-256 `a362c4c6…e269` | 2,396 of 2,396 | 2,396 of 2,396 |
| `integrated/manuscript.pdf` | `e5c44beb…0dae` | `e5c44beb…0dae` |
| November 12 `final_manuscript_manifest.json`, SHA-256 `04d0a0d3…e5460` | 84 of 84 | 84 of 84 |

Records are in `checks/pin_check_*.json`. Another process rewrote four unpinned files in `integrated/` during my review (`release.zip`, `release.sha256`, `release_manifest.json`, `qa/portability_candidate.json`). I did not write them.

## What I read

- The two briefs and the criteria file.
- The integrated candidate: all text the build reads, the compiled bibliography, README, evidence map, all seven tools, QA records, and rendered pages 1 to 12 and 19 to 24.
- All four frozen drafts: main text, appendices, handoff, dissent, evidence map, verification and README. Astra's draft is the candidate's base, so I read its main text, supplement and casebook as diffs against the candidate.
- After the initial position: `INTEGRATION_DECISIONS.md` and the fresh adversarial review with its replacement prose.

Not read as manuscript text: eleven section files the build does not use (ten are byte-identical to the 12 November package, one to Sol's `sixteen_full.tex`), the long source-field printouts in the Sol, Opus and Fable drafts that repeat the sixteen responses I read in the candidate, pages 13 to 18 and 25 to 29 as rendered images, and Sol's `.venv`.

## Checked directly in this review

All from saved records, with scripts in `tools/` that import no engine code. Outputs are in `checks/`.

| Item | Method | Result |
|---|---|---|
| 188 episodes, 128 paid, $51,997, 180 mortgages, 89 sale actions, 67 and 61, no fallback in a payment | Rebuilt episodes from `decisions.jsonl`; paid means not declared and cash plus proceeds covers the debt | Match |
| 62/53/16 and 62/52/14 | Entry cash, salvage and listed mortgages from the first prompt | Match |
| First actions 3 of 132 and 50 of 56; eight forced menus; the six above-bound starts; per-system cells | Same rebuild | Match |
| 28 of 30 | Class A entries with buildings; any sale action in the route | Match. Membership equals the shipped file. A sale was offered in 29 first menus |
| Menu order | `available_actions` in all 188 first prompts | Mortgage precedes sale in all 61 menus that offer both |
| 108/12/9/2; ownership and evenness in all 131; the two G3 entries | Holdings and bank stock at the first prompt | Match. One hotel per hotel-bearing group in both G3 entries |
| Engine premises | Read `engine.py` lines 2386 to 2459, 2492 to 2504, 2552 to 2573, 2667 to 2707 and 2814 to 2868. File SHA-256 `122edf5f…3e0d` | Appendix C describes them correctly |
| Rubric table remainders | Cash plus route proceeds minus debt | All fourteen match |
| 5/3/5/1/2 | My own reading of the sixteen selected fields | Same assignment |
| Listed-only total in selected fields | Numeral match against U0 | Five successes and both failures |
| 920, 918, 113/394/413, per-recipient counts, 110 of 173 cash bids | Stored offer ledger | Match |
| 61 of 74; 27/38 and 34/36; 63, 63, 4, 9 | The two shipped coding files joined to the ledger | Match. Keys equal the ledger's 74 |
| G7 d138 to d151 and continuation | Decisions and events | Every figure and quotation in Incident 4 confirmed |
| G13 d250 to d253 | Decisions | Chronology differs from one main-text sentence (F-01) |
| G12 d249, all channels | Decisions | Two channels first count only the listed sale target (M-01) |
| Six above-bound starts, all channels | Decisions | Appendix D is accurate |
| 43 of 48 and its split | Shipped match table plus my reading of all 21 locked contexts | 27 of 27 and 16 of 21; two itemize; three listed-only |
| Static build | Copied sources, `latexmk -lualatex` in my folder | 29 pages, main text ends on page 7, no warnings, text identical to the pinned PDF, 60 bytes differ near the trailer |
| Five recheck scripts | Read first, then run on a copy in my folder | All exit 0. 85 of 86 files byte-identical. `continuation_premises.json` differs in key order only |
| Cattle Trade, DECE and Arena abstracts | Fetched | The first two match their citing sentence. The Arena abstract mentions no human annotation |

My offer-form classifier is a simple one and gives 114 and 71 for the two opening-swap cells where the paper has 116 and 72. I did not chase the three offers. The paper's classification is the preserved 12 November one, which I rebuilt in full on that date.

I removed the two working copies (`build_check/`, `recheck_copy/`) after recording their results in `checks/release_checks.json`.

## Inherited, not rechecked here

- The three engine-executed payment witnesses, the G7 restricted-menu search, the construction audit and both replay comparisons.
- Episode boundaries agree with my rebuild. The offer completion classification, the conflicting-openings list, all bootstrap and leave-one-out ranges, the price pairs and the fourteen settlement histories are taken from the stored package.
- 38 of 40 eliminations, 227 deeds and 52 groups.
- Refusal counts, tool-choice settings, the 8,687 request records, delivery counts, token means and cost figures.
- Continuations of incidents other than G7, G13 and the financing cases.
- The Arena study's 50-message check: from my 14 November reading and the adversarial review. FinBoardBench, PlanBench, ACPBench, the menu paper, AgentMonopoly and Vending-Bench: from my 14 November literature matrix. The Catan compliance point: from Opus's direct read. Jehiel et al.: from prior knowledge of the paper.

## Limits

- Every reading of model text here is mine, an LLM's. That includes the rubric check and the 21 locked contexts. No person has checked them.
- I did not run `verify_document.py`, which needs PyMuPDF. I compared text with Ghostscript instead.
- I did not test a clean external checkout or an anonymous download.

## Files

- `initial_position.md`, `review.md`, `findings.json`, `replacement_prose.tex` and its PDF, `verification.md`, `handoff.md`.
- `tools/`: `lib.py`, `episodes.py`, `checks_finance.py`, `checks_offers.py`, `checks_totals.py`, `pin_check.py`, `pin_check_nov12.py`. Standard library only. Run each from `tools/` with `python3 -I`.
- `checks/`: the rebuilt episodes, the outputs of each script, pin records and release notes.
