# Handoff: Fable 5.2 independent whole-paper draft

11 November 2026. The draft is complete and frozen for cross-review. I am stopped pending a cross-review assignment.

## What this is

A complete, new paper written by one author (Fable 5.2) from the records and the prior feedback. It is not a section assignment and not a review. It contains a title, abstract, introduction with contributions, setting, four results sections, discussion with the question-coverage table, limitations, related work, conclusion, eight main incidents, five main figures, six main tables, eight appendices, bibliography, compiled PDF and a reproducible build.

**Title.** LLM Agents Withhold a Rival's Monopoly Until They Need the Cash.

**Central claim.** Attention to rivals is common to all four systems. Liquidity is what separates their trajectories.

1. Every system refuses or reprices trades that would complete a rival's color group. Holders with $300 or more reject 69% of such requests.
2. These deeds move when the holder is short of cash. Holders with under $100 reject 25%. In 13 of 14 sales that followed a refusal by the same holder, the holder's cash had fallen in between (median $571.50 to $82).
3. What the cash becomes separates the trajectories. Sellers who built within eight turns of a completing sale won 9 of 14 times, others 1 of 29. Sol and Gemini build at once after completing a group, Opus and Grok often do not, and with similar exposure rent per landing differs threefold.
4. Forced finance is the reliable task. 128 of 131 payable debts were paid.

## Where to start

| Read | For |
|---|---|
| `manuscript.pdf` | The paper, 39 pages. Main text ends on page 24. |
| `findings_and_limits.md` | The argument, the alternatives examined, null results, corrections to earlier interpretations and objections to the contract. |
| `evidence_map.md` | Each claim's source and whether it is fresh, reconciled, inherited or read. |
| `literature_inspiration.md` | Exactly what was read for each citation. |
| `initial_position.md` | My position before the work, for comparison. |
| `README.md` | Build instructions. |

## State of verification

Run `./build.sh`. It rebuilds everything and takes about twenty seconds.

- **Corpus.** 50,918 events, 6,989 decisions, 8,679 attempts across 20 games.
- **State.** Event-derived cash, ownership, mortgages and buildings equal the delivered state in all 6,989 prompts.
- **Offer ledger.** Rebuilt from decision prompts. Equal to the earlier ledger on all 920 rows and 16 compared fields.
- **Totals reproduced from events.** 209 completion episodes (63, 16, 9, 52, 69 by route), $57,378 trade-group rent, 397 and 227 estate deeds with 202 to winners, 57 developed-rent debts, 139 Grok text and call disagreements in 1,068.
- **Quotations.** 44 cards and 6 inline quotations, generated from `decisions.jsonl`. `verify_document.py` re-reads each by file hash, line and pointer. 33 cards repeat earlier checked definitions and match them character for character.
- **Incident facts.** Asserted in `analysis/a9_incident_checks.py`.
- **Numbers in prose.** All through `\fact{key}`. 439 citations. An undefined key fails the build.
- **Document.** No LaTeX diagnostics, no blank page, all used quotations present in the PDF text. The 78 files in `../../baseline_hashes.json` are unchanged.
- **Renders.** I inspected every page as two-up contact sheets after the final build (`qa/render/`).

**Inherited and not rerun.** Payment sequences for three eliminations and the G7 search. Executed build plans. Full replay. The first-management-turn classification (16, 17, 7, 3 and the causes of the 20 unbuilt). The two semantic readings (61 of 74 and 41 of 74). The 2,054 history-defect count. The G9 target and the build-error recurrence counts in the question table.

## Decisions I made that cross-review should test

1. **Headline.** I moved the abstract off rent totals, estate shares and the 56 of 60 bound. The headline is rival-aware refusal, liquidity-timed release and conversion. Rent and estates are supporting context.
2. **Seller premium.** Reported as a direction across coarse cuts with the mixed 4, 2, 1 matched cases next to it. No magnitude is claimed.
3. **Pairs as the unit for release.** 148 holder and buyer pairs. The within-pair comparison measures from the holder's first refusal. My first version measured from the pair's first offer, which is sometimes the holder's own offer (G1). Both are in the paper.
4. **Financing against distress sales.** New in this draft. It is the strongest single contrast (9 of 14 against 1 of 29) and also the most exposed to the objection that building after a sale marks a player who already holds a group. The paper says so in the table caption and the text.
5. **Incident set.** Eight main incidents: G2, G15, G1, G13, G7, G20, G12, G18. G19 moved to the appendix as a control. G1 is new. G7 is re-centred on a liquidity-timed bid and a financing sale and keeps the settled bluff. G11 and G3 remain appendix controls. I dropped the G20 leaked-note control.
6. **Opus condition.** Stated early with the exact message, the exact diff and the time course in the appendix. I say the refusal follows the request for private reasoning and is not a refusal to deceive. I cite the provider documentation as consistent and unconfirmed.
7. **Thresholds.** $100 and $300 for holder cash, eight turns for building after a sale. Sensitivity is in the appendix. They were chosen after earlier work on the same records.
8. **No tests.** Block counts and leave-one-block-out ranges only.
9. **No human byline.** The author line is "MonopolyBench project" with a footnote that the owner supplies the human author line.

## Where I think the draft is weakest

- The conversion result rests on four systems split two and two, with Opus's response condition and Grok's conflicting calls on the low side.
- The pricing gradient has small cells at "two short" (3 and 9 asks).
- Gemini does not show the holder-cash pattern and writes almost no asks, so "all four systems" rests on its refusals alone for Gemini.
- The semantic codes are inherited and unvalidated.
- Main prose is about 8,200 words by my counter, above the 7,500 working target. About 1,880 of that is incident narration.
- Grok appears in seven of eight incidents.

## Things I would keep in an integrated paper

- The exact prompt diff and refusal census in the setup and appendix.
- The debt-episode denominator (128 of 131) in place of "56 of 60".
- The exposure result (similar landing rates, different rent per landing) in place of "$53,810 of $57,378".
- The pre-estate figure with the five discordant games.
- The within-pair liquidity comparison and its table.
- The `\fact{}` build discipline and the quote generator.

## Questions for the owner

1. Is the title's claim the one you want to lead with, or should the integrated title be more neutral?
2. Will a human label the 74 rejection rows? That would turn the inherited codes into checked evidence without any model call.
3. Which human name goes on the author line?
4. Should related work stay in the main text if length is tight?

## Compliance

- I wrote only under `full_drafts/fable_5_2/`. Temporary files went to the session scratchpad outside the repository.
- No game, engine run, replay, synthetic test, baseline or model evaluation call. No engine import. I read engine source to confirm rules.
- No subagents.
- No edits to prior sources, canonical artifacts, prompts, engine or shared files. No commits or pushes.
- I did not read any other author's revision draft. One repository-wide search printed two file names from `full_drafts/sol/` and `full_drafts/opus/`. I opened neither.
- Web reading is listed in `literature_inspiration.md`.
