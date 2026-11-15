# Verification: Opus cross-review

12 November 2026. Everything here was run from the repository root unless noted. No game, engine execution, replay, baseline, synthetic state, rollout, provider probe or model query. No subagents, commits, pushes or messages to peers.

## Frozen inputs

| Check | Before review | After review |
|---|---|---|
| `four_draft_manifest.json`, 234 files | 0 mismatches | 0 mismatches |
| `baseline_manifest.json`, 72 files | 0 mismatches | 0 mismatches |
| `four_draft_manifest.json` SHA-256 | `17ef65a4d24f43d595f7e1587dea79632bd79edc414feff98908f5ce1166bae6` | same |
| `baseline_manifest.json` SHA-256 | `4aa83b668b530ec033b7aa210f0348492df17eae58f66092eec3fc23152faa2b` | same |
| `CHARTER.md` SHA-256 | `3f388517175c8f73b28346ff82dd630e35a95d3c7cd6eaec5361cd4a82e41f97` | same |
| `CROSS_REVIEW.md` SHA-256 | `db4fb25a8af0ab8a60fd4f00ed895d74807d088f444a3434390372d378964a39` | same |

`git status` shows no tracked change; the only untracked paths are the three research folders that were untracked when the session began. All files I wrote are under `reviews/opus/`.

## Independence

- `initial_position.md` was written after reading the charter, the brief, both external reports and all four drafts with their handoffs and evidence maps, and before any fresh check.
- I did not open any other November 12 review. At the start `reviews/astra/` existed and I did not open it. During the review, `reviews/sol/` and `reviews/fable_5_2/` appeared; my closing scope check (`find -newer`) printed some of their file names, and I opened none of them. I opened no integration file.

## Fresh checks

`python3 -I docs/research_raw/paper_revision_2026-11-12/reviews/opus/checks/run_checks.py docs/research_raw/paper_revision_2026-11-12/reviews/opus/checks/fresh_checks.json` (about 12 s). Inputs and their SHA-256 are recorded under `sources` in the output. It reads stored events, prompts, players files and request records, the board file, the frozen 11 November offer and debt ledgers, my frozen draft's finance rows and necessary-collateral table, and the conflict flags in Fable's frozen offer ledger. It produces:

- quit or continue by tier and visible-sum shortfall (`quit_or_continue`);
- what the sixteen first-decision prompts and carried notes contain (`first_decision_prompts`), plus the scenario note in all 439 liquidation prompts and the field inventory of trade and liquidation prompts;
- tool choice in 8,687 request records;
- the opening table, acceptance by author, thread settlement, proposer and recipient strata, recipient standardization, counters, capacity bins, refusal wording with baselines and the 74-row population;
- two-stage and games-only resampling (20,000 draws, generator seed 7) with per-block and leave-one-block-out values for three composition versions;
- nonterminal estates.

Exact whole-block enumeration (3,125 ordered draws, 126 multisets) was run inline and reproduces Astra's and Sol's bands (24.2 to 35.5; -3.8 to 31.9; 8.1 to 34.9 without conflicting openings; cash bids -18.0 to 3.2), and gives -21.3 to -0.1 for cash bids without Grok-authored offers.

Incident continuations (G2, G7, G13, G15, G20) and Sol's G9, G14 and G15 examples were read from `events.jsonl` and stored prompts with short inline scripts; results are reported in `review.md` section 3.12.

The carried-note classification in `review.md` section 3.3 is a text search followed by my reading of every matching sentence. It is one model's reading.

## Quotations and receipt

`python3 -I docs/research_raw/paper_revision_2026-11-12/reviews/opus/checks/verify_quotes.py docs/research_raw/paper_revision_2026-11-12/reviews/opus/checks/quote_checks.json`

- 13 strings checked against raw `events.jsonl` fields or the stored prompt: the liquidation note, eleven full fields and one exact span (G15 d169 note). All exact. The G1 d476 excerpt in the prose is a contiguous substring of a verified full field.
- Every quotation used in `replacement_prose.tex` was found verbatim in the PDF text after normalizing typographic quotes and line breaks (the G1 d170 quotation crosses the page 6/7 break, so the extracted text carries the page number inside it; the words match); the G17 note is paraphrased, not quoted, and the G2 "final" and G20 "$325 idle mortgage capacity" inline fragments come from the frozen Opus quote manifest and the G20 d327 prompt.
- Receipt (`checks/receipt_checks.txt`): G2 d119, d122 and d124 and G15 d166 and d169 public messages each appear in the addressee's next stored prompt.
- `findings.json`: all 35 quoted draft passages occur verbatim at the stated file and line (validator run inline).

## Build

```sh
cd docs/research_raw/paper_revision_2026-11-12/reviews/opus
latexmk -lualatex -bibtex -outdir=build -interaction=nonstopmode -halt-on-error replacement_prose.tex
```

- Exit 0; zero LaTeX or package warnings, overfull or underfull boxes, missing characters or undefined references in `build/replacement_prose.log`.
- `build/replacement_prose.pdf`: 9 pages, about 4,600 words of PDF text including references.
- `bib/` holds byte copies of the four bibliography files from my frozen draft (hashes equal).
- All nine pages rendered at 70 dpi (`build/render/page_*.png`, `contact_*.png`) and inspected. Two layout issues were fixed and rebuilt: the liquidation note split across a page, and awkward punctuation after the G15 public refusal. No other problem seen.

## Inherited, not rerun

The offer ledger's post-trade reconstruction; the debt ledger's episode boundaries; the 61/74 semantic codes; three engine-executed payment sequences; the G7 menu search; both stored replay comparisons; cost and token accounting; first-window builds, construction receipts, first-estate counts, asking-price pairs and the fourteen paired histories. The sixteen first-decision readings (13 count, 1 raises, 2 omit) and the 12-of-13 accuracy count come from my frozen draft and were not re-read here, though Fable's independent reading agrees.

## Deliverables

- `initial_position.md`
- `review.md`
- `findings.json` (16 findings, 35 located passages, plus confirmations)
- `integration_proposal.md`
- `replacement_prose.tex` and `build/replacement_prose.pdf`
- `verification.md` (this file)
- `checks/run_checks.py`, `checks/fresh_checks.json`, `checks/verify_quotes.py`, `checks/quote_checks.json`, `checks/receipt_checks.txt`
