# Handoff: Fable 5.2 complete independent draft

Written 10 November 2026. I wrote this draft alone, without subagents, and did not open any other author's `full_drafts/` folder. I read the rewrite contract, the full critique, every section and appendix of the 29 October manuscript, its evidence map and review dispositions, the question transcription and coverage assessment, and Sol's superseded section-level position note in `coauthors/sol/`.

## What is here

Everything is under `docs/research_raw/paper_rewrite_2026-11-10/full_drafts/fable_5_2/`.

| Path | Content |
|---|---|
| `manuscript.pdf` | 39 pages. Main text to page 26, references to page 28, appendices A to F |
| `manuscript.tex`, `sections/*.tex`, `preamble.tex`, `references.bib` | Native LaTeX. `preamble.tex` is a local copy of the shared preamble with incident and inline-quote macros added. `references.bib` is a local copy of the shared file plus 13 entries |
| `initial_position.md` | Written first, before any re-tabulation |
| `evidence_map.md`, `figure_table_decisions.md`, `literature_updates.md` | Supporting documents |
| `tools/` | Nine scripts: decision census, four re-tabulations, quote builder and verifier, table generator, figure generator, manuscript checker |
| `data/` | Outputs of those scripts and the supplementary quote manifest |
| `figures/` | Four figures as PDF and PNG with a manifest |
| `qa/` | Logs, `quote_verification.json`, `manuscript_checks.json`, page renders |

Shared inputs are read through relative paths and never written: `../../data/*.json`, `../../sections/transcript_quotes.tex`, `../../../paper_phase1_2026-10-28/sol/group_episodes.jsonl`, the repository's `contracts/data/board.json`, and the canonical `saved_games/railway-research-*/game-NN-*/run/decisions.jsonl`. No shared asset figure is used.

Build: `./build.sh` from this folder. It reruns the census and re-tabulations, regenerates quotes, tables and figures, runs `latexmk -lualatex`, copies the PDF and runs the checker. It needs TeX Live with LuaLaTeX and the repository virtualenv at `python/.venv` for matplotlib and PyMuPDF. A clean build from an empty `build/` succeeded with no overfull box and no undefined reference, and the checker reports 77 of 77 assertions and all 41 used excerpts found in the PDF text. Figure PDFs are not byte-stable across runs.

## Thesis

Title: *Who completes, who builds, who inherits: bargaining and economic execution by four LLM systems in twenty games of Monopoly*.

One question: where along the path from trade to rent to bankruptcy were these games decided, and what did the systems do and say at each step. Three findings:

1. **Bargaining is priced and rival-sensitive.** The completing side pays in 373 of 429 one-sided offers. Writer-only offers are rejected 159 of 289 and accepted 19. Recipient-only offers are mostly countered. Acceptance is 26 to 30 offers per system and the declining styles differ. Completing deeds are released mostly by cash-poor holders (21 of 48 completing sales from a seller under $100).
2. **A completed group is not yet a developed one.** 17, 18, 15 and 13 trade completions become 16, 17, 7 and 3 first-window builds and $20,818, $26,070, $5,930 and $4,560 in rent. Seventeen of twenty unbuilt windows trace to the acquisition terms or the response path.
3. **Bankruptcy moves more property than trade.** 56 of 60 eliminations are unpayable on a generous bound. Estates complete 121 groups against 63 by trade. One creditor takes all three estates in 16 games.

## Substantive choices

- **Incidents sit inside the sections they illustrate.** There is no separate social section. Seven main incidents: swap refusal (G15, new), corrected false premise (G19), bluffed final price (G7), boycott appeal (G20), bankruptcy against the response's own text (G12), insurance sale (G13), withdrawn standing offer (G18). Three more and four short notes are in Appendix E.
- **A new lead incident.** G15 d168–175 is a refusal of one's own monopoly on stated grounds about the counterparty's ability to build, in a four-player state, with the proposer's private note counting on the same asymmetry. It answers the first question's own example more directly than G11, which is a two-player endgame and is now in the appendix. Its quotes were extracted from the canonical log by script. It has not had a bounded source review like the 29 October incidents.
- **Conditions are stated once, early and with counts,** then attached to the specific rows they qualify (Table 2's condition column, the Grok thread count, the first-window causes).
- **The eight questions are one discussion table** with a supported level per row. The introduction states one question.
- **The audit machinery is two paragraphs of method.** The 126-case suite is cited as the source of four classifications and of the rebuilt build plans. No method claim.
- **The readiness pilot and scenario audit are one appendix paragraph** marked as historical and not used.
- **All figures were redrawn.** The shared palette fails a color-vision check (details in `figure_table_decisions.md`).

## New existing-data results in this draft (none has had a second reviewer)

1. Cash direction by completion category, and the 48 / 9 split of who paid for trade-completed groups.
2. Robustness of the writer-only versus recipient-only contrast by recipient, seed block, game and thread position. This is the check the contract asked for. Result: rejection contrast holds in 5 of 5 blocks, 17 of 19 games and 3 of 4 recipients and fails for Opus; the acceptance contrast is weaker (4 of 5 blocks, 13 of 19 games); thread position accounts for part of the raw contrast.
3. Join of Grok's 139 text and tool-call disagreements to the negotiation ledgers: 64 of its 136 threads were opened by a disagreeing call, and 7 of its 28 acceptances, three of which completed Opus groups.
4. Cash-poor sellers and the response tables by cash position, with threshold sensitivity.
5. Rent by owner on trade-completed groups, cross-checked between two independently built ledgers (209 of 209 episodes agree).
6. Reasons for the nine never-legal completions (seven arrived mortgaged, two left under one house of cash).
7. Estate recipients by elimination order, the 16-game single-creditor count, completions and rent by route and winner.
8. First complete group per game against first-window building and outcome, and the block 3 and block 4 seat patterns.
9. Refusal counts by game recounted from the decision logs (215 of 306, then 1,390 of 1,390).

## Dissent from the contract

1. **"Provisional order … contextual conduct" as its own section.** I integrated the incidents. A separate conduct section recreates the old paper's split between counts and anecdotes, and the critique's complaint that the cases withhold their interpretation follows from that split.
2. **"Distress bargaining" as a link in the argument.** The label overstates what the ledger supports. Being under $100 in cash is not distress (winners sold completing deeds in that state six times), and the tabulation shows no rise in agreement. I use "cash-poor", define it mechanically and label the tables exploratory.
3. **Opus consistency.** The contract's cell counts are right, but any sentence saying the contrast is consistent across configurations is wrong for Opus. I state the exception in the main text.
4. **"Do not call default END a chosen hold" is necessary and not sufficient.** The larger risk is on the other side of the table: 64 Grok proposals and 7 acceptances come from calls its own text contradicted, and those sit inside the bargaining counts. Any integrated draft should carry this condition into the bargaining section.
5. **Inheritance deserves structural weight.** The contract lists it last and warns only about winner conditioning. The route census (121 estate completions, 52 during play, one creditor in 16 games) is among the most consequential descriptive facts in the corpus and depends on the intact-inheritance rule. I give it a full section and keep the causal disclaimer.
6. **Length.** My counter gives about 9,900 words of main prose including incident setup, outcome and reading, against the 7,000 to 9,000 target. I chose completeness. The first cuts I would make are Incident 3, the position-in-thread paragraph and the last subsection of Section 6.

## Objections I expect and my answers

- *The cash-poor result is a threshold artifact.* The count of completing sales among cash-poor sellers is 14 of 20, 21 of 30, 22 of 36 and 24 of 40 at $50, $100, $150 and $200. The medians ($194 against $571) do not use a threshold. Opus is the seller in 16 of 30, which the text states.
- *Rent by owner is a ranking in disguise.* The text says the order matches the order of wins and gives three reasons the table cannot carry a causal reading. The table's purpose is to locate the loss in the acquisition terms and the response path.
- *The first-completion table is winner-conditioned storytelling.* It is presented as twenty dependent games with a selected endpoint, with four of the fifteen wins attributed to the dark-blue seed block. I would accept moving it wholly to the appendix.
- *Six of seven incidents feature Grok.* Stated in the appendix with the reason (observable channels).
- *"Bargained hard" in the conclusion is a judgment.* It rests on the 88 percent decline-or-counter share and the pricing structure. I would accept "rarely accepted an offer as written".

## Checked versus inherited

Full table in `evidence_map.md` and in Appendix B of the manuscript. In short: counts from the decision logs and all quotes are recounted from canonical files; all offer, completion, window, elimination and estate tabulations are recomputed from retained ledgers; engine executions, prompt-defect counts, memory-window counts, semantic codes, token figures and most event-level incident facts are inherited.

## Checks I did not perform

- No engine execution of any kind, so no independent confirmation of the three payment sequences, the game-7 lock, the 61 rebuilt build plans or the replay.
- No re-derivation of the retained ledgers from raw events, apart from the decision census and the incident chronologies.
- No re-check of recipient-prompt delivery for the new G15, G1 and G11 quotes beyond the engine's delivery of the offers.
- No re-read of the 74 rejection texts or the 240 sampled decisions. Their coded counts are inherited.
- No verification of the refusal message text across all 1,605 refusals, of token or latency figures, or of the formatter-defect counts.
- No full-text reading of any cited paper in this pass (abstract pages only), and no re-inspection of the AgentMonopoly repository.
- No human reading of the PDF. I inspected page renders at 100 dpi for layout, figure collisions and quote rendering.
- `pdftotext` is not installed. Text extraction used PyMuPDF.

## Unresolved, and stated as such in the manuscript

The upstream cause of the Opus refusals and of the change at game 5. The origin of Grok's text and tool-call disagreements. Whether any refusal, purchase or bankruptcy was good play. Any effect of a rival's completion, of a message, of feedback or of inheritance. Whether low acceptance reflects absence of agreement bias. Transfer to other opponents, rules or runs.
