# Handoff: Opus complete independent draft (frozen)

**Manuscript.** `manuscript.pdf`: *Financial Assessment and Strategic Conduct of LLM Agents in Twenty Monopoly Games*, by Kushagra Bharti. It has 22 pages. The main text runs from page 1 to page 8, where the references begin. Main prose is about 5,330 words plus a 290-word abstract. Type is 10 pt, in two columns with 0.75 in side margins. The final PDF SHA-256 (`a7d61c0d1614419c9e5ea80d998c0e93f7560a281d5e9a445de3d23a2db18be1`) and the hashes of every source, data, tool, document and QA text file are in `FREEZE_SHA256.txt`; rendered page PNGs and `build/` intermediates are excluded. Two consecutive rebuilds give the same PDF hash. Rebuild with `PAPER_PYTHON=python3 bash build.sh`.

## Central question and answer

When an obligation arrives, what do these configured agents count, how accurately do they value it, and does the applied action follow? The answer has five parts.

1. **Stopping tracks asset coverage.** Agents declare at the first menu in 3 of 132 bound-covered episodes and in 50 of 56 short ones.
2. **Payment shows continuing, not routing.** Proposition 1 shows that continuing valid financing pays every one of the 131 payable debts. It is a source argument, explicitly not an executed baseline.
3. **The sixteen texts value what the menu does not price.** They contain one aggregate value error. The rubric gives 5 explicit dependency statements, 3 ordered routes, 5 inclusive budgets, 1 tentative case and 2 omissions. Three remainders are realized to the dollar, and G13 shows a selective plan.
4. **Financing preserves development.** 28 of 30 building owners pay with mortgages alone when listed mortgages suffice.
5. **Failures and conflicts.** The two false budgets equal U0. Every observed conflict between a named action and the applied call is Grok's, under unequal observability. Gemini's fee motive matches the published rule that the engine does not implement.

Bargaining is exploratory. It shows rival-budget calculations, buyer pricing, a bluff and survival bargaining; the completion contrast is sensitive to who wrote the offers, with an interval spanning zero.

## Structure

1. Introduction
2. Setting: information, four channels, published versus implemented rules, bounds, Proposition 1, rubric and its limits
3. Financial assessment: census and stopping, financing order, the sixteen texts, Incident 1, two false budgets, divergences
4. Strategic conduct: census, composition, rival finances, Incidents 2 to 5
5. Related work, organized by construct
6. Discussion and scope
7. Conclusion

Appendices:

- A: artifacts, commits, source hashes, cohort, build, inherited-versus-recomputed table
- B: rules, with quotations and engine functions
- C: full proof
- D: census details, the five derived routes and the scan table
- E: every channel for all sixteen texts
- F: channels for the departures
- G: bargaining tables
- H: Incidents 6 to 8
- I: research-question map, covering the eight questions plus A to C
- J: verbatim prompts
- K: authorship and AI assistance

## For the integrator

- **Positive findings to carry forward.** The mortgage-first regularity (§3.1), the G7 New York development-budget negotiation (Incident 4) and Grok's rival-liquidity note (§4.2) appear in no earlier draft. Check them against `data/finance_census.json` and `data/quote_manifest.json`.
- **Proposition 1.** The 131-state coverage combines Fable's 129-entry conditions with Astra's two-entry extension. I re-derived it from the original entry prompts and checked it against the source (`changes_and_dissent.md` J1). It has not been run.
- **Wording to keep exact.** "Every observed conflict … comes from Grok, the only configuration whose free text names actions." Do not turn this into a claim that the other systems are consistent.
- **What not to reintroduce.** No 179/188 figure, Fisher p-value, binomial interval, "reproducible result", "before choosing", "dependent execution", or "planted number".

## Exact cuts, if a venue needs fewer than eight pages

The draft is already within the 9-page target. These cuts are in priority order:

1. Move Incident 5 (G13 survival bargaining) to Appendix H. This saves about 0.2 column and leaves four main-text incidents, below the brief's minimum of five; do it only if a venue forces it.
2. Shorten Related work's "Economic games and agents" paragraph to its AgentMonopoly and FinBoardBench sentences. This saves about 0.15 column.
3. Fold the "second channel" paragraph of §3.2 into one sentence that points to Appendix E. This saves about 0.1 column.
4. Drop the bottom half of Table 6 and keep the numbers in the prose. This saves about 0.2 column.

## Open items for the owner

- Choose a venue template and anonymity mode. This draft is a named preprint.
- Commit and release this folder. It is uncommitted, and Appendix A says so.
- Decide whether to commission human annotation of the sixteen texts and the 74 rejections. None exists.
- Make any new evaluation a separate, explicitly authorized project. This draft does not propose one.

I am frozen at this handoff. Any later change belongs to a fresh task.
