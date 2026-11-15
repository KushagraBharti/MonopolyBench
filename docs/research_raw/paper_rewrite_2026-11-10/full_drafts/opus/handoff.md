# Handoff: Opus independent full draft

Author stream: Claude Opus 5.5 (`claude-opus-5-5`), xhigh, working alone with no subagents. Written 2026-11-10 before reading any other full draft. I did not open `../fable_5_2/`, `../sol/` or `../../coauthors/`.

## Deliverables

| Path | Content |
|---|---|
| `manuscript.tex`, `manuscript.pdf` | Complete paper, 43 pages: main text pp. 1-28 with references through p. 30, appendices A to H on pp. 31-43. |
| `sections/` | Main sections, appendices, generated tables (`gen_*.tex`) and new quote macros (`opus_quotes.tex`). |
| `preamble.tex`, `references.bib` | Local copies of the shared preamble and bibliography, plus additions (incident macros; 17 new bib entries). |
| `tools/retabulate.py` | Re-tabulates the shared ledgers into `data/opus_retabulation.json`. |
| `tools/build_tables.py` | Writes the appendix tables from that output. |
| `tools/build_opus_quotes.py` | Extracts 10 new exact spans from canonical `decisions.jsonl`; writes macros and `data/opus_quote_manifest.json`. |
| `tools/check_delivery.py` | Confirms the new quoted messages appear in recipients' next prompts; writes `data/opus_delivery_checks.json`. |
| `tools/count_words.py` | Rough prose word count. |
| `initial_position.md`, `evidence_map.md`, `figure_table_decisions.md`, `literature_updates.md` | Required supporting documents. |

Build: from this folder run the four Python tools, then `latexmk -lualatex -outdir=build manuscript.tex` and copy `build/manuscript.pdf`. The figures (`../../assets/`) and shared quote macros (`../../sections/transcript_quotes.tex`) are read by relative path. The final build has no errors, no undefined references or citations and no overfull boxes; one font-shape substitution warning (bold Latin Modern Mono) remains and is harmless. I rendered every page with Ghostscript at 70 dpi and inspected the opening, bargaining tables, an incident page, the liquidity table, the coverage table and an appendix page. I did not run a PDF text-extraction or link checker.

Word count: about 9,500 words of main prose by the rough counter, about 9,280 excluding incident source notes (abstract, tables, figures, quotes and references excluded). This is slightly above the 7,000 to 9,000 target.

## Thesis and structure

The paper is an observational study of a connected economic chain: recipients refuse or price a rival's color-group completion; completion becomes construction only when a build can be executed; nominal wealth misstates accessible liquidity in both directions; and creditor inheritance concentrates estates in eventual winners, with the most consequential selected bargaining conduct appearing at solvency and inheritance points. Order: introduction (opening with the G2 Marvin Gardens arc), environment and run conditions, measurement, bargaining, construction, liquidity and inheritance, distress and conduct, plans and repeated errors, related work, discussion with a question-coverage table, limitations, conclusion.

## New evidence in this draft (existing-data analysis only)

1. **Counter content.** Of 111 counters to author-only offers, 92 keep the author's completion; 85 of the 88 that give the counterer nothing raise its cash (median +$125); 13 swap to the counterer's own completion; 6 remove completion. Counters in every cell ask for more, so the premium is ordinary bargaining. The specific finding is that the completing deed stays on the table.
2. **Thread outcomes.** 26 of 187 threads opening with an initiator-only completion settle; in 24 the initiator still completes after raising its offer by a median $97.50.
3. **Consistency check of the rival-completion pattern.** The acceptance gradient holds for Sol, Gemini and Grok and not for Opus (7/52 vs 5/42). Opus still prices completion in counters (34/36, median +$77.50). Reject share direction holds in 5/5 seed blocks and 17/19 games; acceptance reverses in block 3. **The contract's request to check "Fable's prior consistency claims" is answered: a universal consistency claim across configurations is not supported.**
4. **Displayed menus understate finance** in all three payable eliminations (menu-only $183, $43, $30 against $500, $250, $550).
5. **Estate re-tabulation** reproduces 54/60, 35/40 and 202/227.
6. **Two new incidents with verified quotes and delivery**: G2 d124–128 and d197–198 (Sol prices Opus's completion, Opus bluffs "final" $450 with a private $475 ceiling, the trade later reverses, Sol builds without rent and is eliminated to Gemini, which inherits the yellows and wins); G11 d255–258 (Grok refuses its own pink completion because it completes Sol's greens; the blocker was itself inherited).
7. **Chronology additions**: G18 Pacific came to Sol from Grok's estate and reached Opus only in the terminal estate; G18 d442 is an Opus rejection of its own completion at its advertised price.

## Substantive choices

- **Behavioral identity, not method.** Legal-sequence checks are a supporting method with a support table (App. D) that states what is not established.
- **Counter content leads the bargaining result**, because reject/counter shares are dominated by configuration style.
- **The Opus exception is in the main result**, with its action-only confound stated once.
- **Incidents sit inside the results they illuminate** (G2 and G11 in bargaining, G12 in liquidity), with five in a distress-and-conduct section. Eight main incidents, two appendix.
- **The eight questions and A to C organize one discussion table**, not the paper.
- **The cohort/winner figure moved to the appendix**; the first figure is the offer-response chart.
- **Prospective experiment designs were removed.** No new evaluations are in scope; the critique treated future-work protocols as padding.
- **Reference-policy pilot reduced to one short appendix** supporting Q8 and C.

## Objections to the contract and points of dissent

1. **"Rival-sensitive bargaining" should not be stated as uniform.** The pattern is configuration-dependent; the robust form is "refused or priced", which holds for all four configurations only through counter content.
2. **"Distress bargaining" is not a measured construct.** I give one labeled descriptive cut (cash-seeking offers by author cash on hand) and otherwise treat distress through incidents. Another draft that presents distress bargaining as a population finding would overreach.
3. **The G13 and G18 incidents show distress-related conduct, but the strongest economic reading of G18 is benign**: Opus's stated reason (paying $250 prolongs a near-bankrupt rival) is economically intelligible. Presenting G18 primarily as "broken commitment" would misframe it.
4. **"Conduct concentrates near solvency and inheritance" is a property of the selection**, which was purposive and partly chosen for stakes. I state it as such. I would object to any draft that turns it into a population claim.
5. **Target length.** I land slightly above 9,000. Cutting further would remove either the G3 incident or the Opus heterogeneity discussion; I would cut G3 first.
6. **Opus-family authorship.** This draft is by an Opus-family run and reports results that are less favorable to the Opus configuration in construction and more nuanced in bargaining. Cross-reviewers should check that the Opus exception is neither excused nor overstated.

## Checks not performed

No engine replay, certificate re-execution, new witness or search; no model calls, games, reference-policy runs or synthetic tests; no human annotation; no re-reading of all provider reasoning; delivery checks only for the ten new spans (shared-manifest incidents inherit their checks); literature checked mainly at abstract-page level (full texts of CICERO and the deception survey not read). The G11 provider-explanation echo-then-correction is inherited from the baseline, not re-read.

## Questions for cross-review

- Is the counter-content result stated at the right strength given that counters in every cell ask for more?
- Should G3 or G19 move to the appendix to meet length?
- Is the coverage table's Q3 entry ("low acceptance does not establish absence of agreement bias") clear enough?
- Does the introduction's G2 vignette risk overreading a single thread as the paper's thesis?
