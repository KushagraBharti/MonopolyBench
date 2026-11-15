# Opus initial position, 12 November 2026

Written before drafting, and before opening any other author's 12 November draft. The folder `full_drafts/opus/` did not exist when I started, so there was no collision with an active duplicate task.

## What I read first

- `paper_revision_2026-11-12/CHARTER.md` and `baseline_manifest.json`.
- Both referee reports in full: `attached_review.txt` (649 lines) and `inline_review.md` (129 lines).
- All four completed assessments (`astra.md`, `sol.md`, `opus.md`, `fable_5_2.md`), `team_synthesis.md` and the superseded `synthesis_in_progress.md`.
- The frozen integrated manuscript of 11 November: `manuscript.tex`, every section and table it inputs, all four quotation files, `evidence_map.md`, `integration_decisions.md`, `README.md`, `data/integration_checks.json`.
- The 10 November integrated appendix and setup for the seeds, game map, repository URL and configuration table that the 11 November version dropped.

## Thesis I intend to defend

The paper should be an observational account of how LLM agents' prospective statements about changing economic options, their own and their rivals', line up with what they then do. Two results carry it, in this order.

1. **Own changing options (finance).** In 16 of 188 liquidation episodes, cash plus every building's salvage plus the mortgages listed on the first menu fall short of the debt, while the full own-asset bound covers it. Payment then requires mortgages that only appear after buildings are sold. Agents pay 14 and declare bankruptcy in 2. At the first decision, the recorded text states those later mortgages, or a budget that includes them, in 13 of the 14 payments and raises them as an open check in one. Both failures add up only listed items and declare at once. This is the clearest link in the corpus between a prospective statement and a dependent action sequence. It is evidence of expressed anticipation, accurate assessment and consistent action. It is not evidence of internal computation, lookahead depth, optimal liquidation or superiority to a policy nobody ran.
2. **Rival changing options (bargaining).** Recipients often refuse or reprice offers that would complete another player's group, and they say why, usually in terms of the rival's next construction. The opening-swap contrast (95/116 versus 37/72 rejected) is real in direction in every proposer stratum with data, but its size depends heavily on proposer composition (16.7 points without Grok-authored offers, with a game-resampled interval that includes zero). Cash bids show no corresponding increase (42/70 versus 67/103). The stated-reason evidence (61/74) comes from a disjoint population and cannot explain the swap/cash difference. In the headline cells, rejections cite completion and building under both offer forms. So the bargaining evidence reaches "expressed concern, sometimes accurate, consistent with the action" and stops short of "demonstrated sensitivity to the rival's opportunity".

The connecting idea is the attached review's evidence ladder: expressed concern, accurate assessment, action consistency, demonstrated sensitivity, effectiveness. Every result in the paper gets tagged with the highest level it reaches. Finance reaches the third level in a set fixed by rule arithmetic. Bargaining reaches the third level in individual cases and has an exploratory population pattern whose cause is not identified. Nothing reaches the fourth or fifth level.

## What I will not do

- Make the swap/cash split the title or the sole discovery.
- Promote the 14/16 contrast to a planning-capability claim, a "planning boundary", or a ten-step lookahead claim.
- Treat twenty games as twenty independent draws, or present resampling intervals as confirmation of a selected contrast.
- Print any hypothetical baseline score (the inline review's "131 of 131" stays an unexecuted prediction).
- Treat LLM readings as human validation.
- Run any engine, replay, game, model call, provider probe or synthetic state.

## Required corrections I will carry

- G18: the stated motive is withholding survival cash from the last remaining opponent. No Opus text mentions inheritance. Opus redeems its greens before bidding again. The estate is terminal.
- Replay: name both stored modes (artifact mode compares the complete decoded event stream; state mode drops four LLM event types and renumbers identifiers and timing).
- Grok `tool_choice: "required"`, checked at both run-source commits.
- Repository URL, checkpoint, both run-source commits, five seeds, G1–G20 map and an analysis entry point.
- Eight distinct incidents with exact quotations, named channels, receipt claimed only where the recipient's stored prompt was checked, and supported outcomes.

## Where I expect to dissent

- From the 11 November title and abstract, which I think overstate the bargaining interpretation.
- From my own earlier recommendation to cut the main text to three incidents. The charter asks for eight in the package; I will keep the main narrative readable by giving each incident one job and moving the full cards to an appendix where needed.
- From any framing that reads the corpus as a catalogue of failures. The positive findings (payments using unlocked collateral, factual correction without rejecting good terms, a ten-action plan reaching its stated remainder, refusals with checkable cash figures) deserve to lead.

## What I will check myself versus inherit

I will recompute from existing records: the full form × completion × stage table, proposer and recipient strata, five seed-block sensitivity and resampling, the 188/131/128/56/16/14/19 partition and difficulty descriptors, the first-decision text and channel in all sixteen necessary episodes, the 61/74 population membership, Grok tool choice at both commits, G18 text, both replay report modes, and every displayed quotation against its original field plus receipt in the recipient's stored prompt.

I will inherit and label as inherited: the 61/74 semantic codes themselves, the three historical payment witnesses and the G7 menu search, the 66 construction defaults, the Opus refusal and Grok conflict totals unless rechecked, cost and token accounting, and the correctness of the historical replay executions.
