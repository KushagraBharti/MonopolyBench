# Handoff

Fable 5.2 complete independent draft. Frozen at handoff. `MANIFEST.sha256` lists every delivered file with its hash.

## Delivered

- `manuscript.pdf`, 29 pages. The main text ends on page 9, where the references begin. The appendix is pages 11 to 29.
- Full LaTeX source, eight read-only analysis scripts, generated data, a machine-readable supplement and one figure.
- `README.md` with the build command, `evidence_map.md`, `changes_and_dissent.md`, `verification.md` and this file.

The build exits 0 and all 36 checks in `tools/08_verify.py` pass.

## The paper in brief

**Title.** What Can Be Raised? Financial Assessment and Economic Conduct of LLM Agents in Twenty Monopoly Games.

**Question.** What do these agents count as raisable money, their own when a debt arrives and a rival's when a trade is proposed, how accurate is the count, and how does the applied action relate to it?

**Findings, in the order the paper gives them.**

1. In all 131 payable entry states, any uninterrupted sequence of valid cash-raising actions pays. This is an argument from source and recorded holdings. Nothing was run. Payment therefore records that an agent did not stop.
2. On unpayable debts, 43 of 48 first responses state the full asset bound, its proceeds or the gap to the dollar. The menu shows no prices and the prompt states no rules.
3. In the sixteen payable debts that need released collateral, the first responses divide into 5 explicit dependency statements, 3 ordered routes, 5 inclusive budgets, 1 tentative question and 2 omissions. Every stated asset value but one is correct. Three stated remainders are met exactly.
4. Five first responses, from all four systems, stop at the listed-only total. Three are on debts that were unpayable either way. Two are the false budgets, and both agents declared.
5. Financing is selective. With enough listed mortgages, agents kept every building in 28 of 30 payments. Gemini's G13 route names the deeds to keep and keeps them.
6. Nine first actions depart from the asset bound: the two false budgets, six Grok responses whose text and call disagree, and one Gemini mortgage justified by a rulebook charge that this engine does not levy.
7. The engine matches the published rules on what can be raised and departs from them, without disclosure, on what stopping costs.
8. Bargaining is exploratory: the 920-response census, a swap contrast that follows the mix of proposers, and four incidents in which an agent writes a budget for another player.

## What is new in this draft

These came from existing records in this round and were not in the 12 November manuscript or the 14 November reviews.

- The 43 of 48 number match on unpayable debts.
- The denominator for the listed-only total: 5 of 37 first responses, and the three harmless cases.
- The selective-financing counts: 28 of 30, 46 of 52, 122 of 128 and 119 of 128.
- Incident 1 (G13 d195) as a main-text case of a selected route.
- A statement of the fourth coverage condition as a general sufficient condition, with the bundled-plan case written out.
- One system prompt confirmed across all 6,989 decisions and one recovery prompt across 1,604 attempts.

## Where the brief's required content is

| Requirement | Location |
|---|---|
| 188-episode census | Section 3.1; `supplement/episodes_188.csv` |
| Justified 62/53/16 partition | Table 2, section 3.1, Appendix C |
| Both failed budget calculations | Section 4.3, both channels in Appendix E |
| Successful dependency statements | Section 4.2, Table 3, Appendix D |
| Selective financing | Section 4.4 |
| Continued financing suffices; source argument, not a baseline | Section 3.2, Appendix B |
| All sixteen first texts, both channels | Appendix E; `supplement/sixteen_first_texts.json` |
| Channel definitions; joint generation; no timing from field order | Section 2.4 |
| Five-tier rubric, limits stated once, arithmetic, errors, incomplete fields | Sections 2.5 and 4.2, Appendix D |
| Six above-bound starts and the payable Grok declaration, with calls and prose | Section 5, Appendix G; `supplement/nine_departures.json` |
| Unequal observability of the named-action scan | Sections 2.4 and 5 |
| No accuracy headline | Section 5, second paragraph |
| Published against implemented rules, with consequences | Table 1, sections 2.3 and 5 |
| False budget kept apart from motive | Section 4.3, last paragraph |
| 920-response census, exploratory; no causal or null claim; separate 61 of 74 | Section 6.1, Appendix I |
| Eight incidents | Incidents 2 to 6 in the main text and 7 to 9 in Appendix J. Incident 1 is new |
| Eight questions plus A to C | Appendix A |
| Related work with the named distinctions | Section 7; access depth in `evidence_map.md` |
| Artifact entry point, seeds, commits, rules version, provenance, build | Appendix M, Table 18, `README.md` |
| Retained witnesses and replays, not rerun | Sections 2.5 and 8, Appendix M |
| Named author, no affiliation or email, AI assistance in an appendix | Title block, Appendix N |
| Length | 9 main pages before references; 5,500 authored words; 10 pt; one-inch margins |

## Exact cuts if the integration needs room

The draft is inside the page and word targets, with about 0.4 of a column free on page 9. If a merged paper needs space, cut in this order. Word counts are authored words.

1. Section 6.1, fourth paragraph (the 61 of 74 reading). 70 words. Appendix I can carry one sentence.
2. Incident 5, last two sentences (Grok's $600 bluff). 14 words and two quotations.
3. Section 7, "Negotiation" paragraph. 88 words.
4. Section 7, "Rules agents know" paragraph. 49 words.
5. Table 3. Figure 1 already groups the sixteen by tier, so the table can go to Appendix D. About 0.15 of a column.
6. Section 4.2, the sentence on the G5 revision and its quotation block. 13 words and a 30-word quotation.
7. Section 3.1, the four G7 sentences. 79 words. Sections 3.2 and 5 refer to G7 and would each need a clause.

Appendix cuts, if the appendix must shrink: Appendix H (carried notes), the full provider field of G18 d313 in Appendix E (one page; it is in the supplement), and the long assistant-content fields in Appendix G.

## Weak points I know of

- **The tier coding is a model reading.** The spans are printed and checked for presence. No person has read them.
- **The number match depends on a stated figure.** Two responses itemize without a total and had to be read directly.
- **Four of five inclusive budgets are Opus provider fields.** Tier and channel are confounded for Opus, and the paper says so.
- **Incident continuations are thin.** I cut outcomes that the 12 November text carried (later rents in G7, the G2 reversal, the G13 probability miscount). They are true and were verified, and the integration can restore them from `evidence_map.md`.
- **The human-contribution sentence in Appendix N** states only what the project records support. The owner should confirm it.
- **Related work on negotiation** rests on other authors' reading for four sources. The evidence map marks them.
- **The 5,500-word count is at the limit.** Any added sentence in the main text needs a matching cut for the verifier to pass.

## For the owner

1. Confirm or rewrite the human-contribution sentence and the assistant names in Appendix N.
2. Decide whether a person will read the sixteen first responses against Table 3. Appendices D and E are laid out for that.
3. Decide on the title.
4. The repository's own rule against undocumented house rules now has a concrete list in Table 1.

## Inherited and checked

`evidence_map.md` marks every claim. In short: every count over the 188 episodes and the 920 responses, every quotation, every sum and every route was recomputed from raw records in this round. The three payment witnesses, the G7 menu search, the replay comparisons, the 61 of 74 reading, the price pairs, the settlement histories, the tool-choice setting and the cost figure are inherited.

## Not done

- No game, engine execution, replay, policy, search or model call.
- No commit and no push.
- No file written outside this folder.
- The other authors' new drafts were not opened.
- Persistent memory was not updated.
