# Integration proposal: one complete paper from four drafts

This is a complete-paper architecture with keep/cut/rewrite decisions for every part. Finished text for the material changes is in `replacement_prose.tex`. Finding IDs (OPR-nn) refer to `findings.json`. Nothing here edits the original outline or any draft.

## Governing decisions

1. **Identity.** An observational behavioral study of bargaining, development, debt and inheritance in one recorded economy. The audit and replay machinery is evidence discipline, stated once in Measurement and the appendix. It is not a contribution claim (all four drafts agree).
2. **Headline evidence is stratified.** The completion contrast appears by thread position, with the responder exception (OPR-06). Cash terms are read against list price, not as signed medians (OPR-03).
3. **Execution partition with access arithmetic.** "No construction option in the window" replaces "never legal" and "could not be built". The financing arithmetic is stated (OPR-02). No "lost value" claim (OPR-01).
4. **Inheritance headline uses nonterminal populations and concentration** (OPR-04, OPR-28).
5. **No causal verbs for associations, no purchased-survival durations, no selection-as-finding** (OPR-07, OPR-10).
6. **Seven main incidents with distinct mechanisms.** Each has setup, exact channel-labelled excerpt, outcome, and a reading that names arithmetic errors in quotes.
7. **Length target:** about 8,500 words of main prose, results starting by page 4 or 5, and an evidence appendix for everything exhaustive.

## Title and abstract

- **Title (proposal):** *Bargaining, Building and Inheritance: Four LLM Systems in Twenty Games of Monopoly*. Alternatives: Astra's *Bargaining, Development, and Inheritance in MonopolyBench*, or my draft's *Bargaining, Building and Bankruptcy*. Avoid "Who completes, who builds, who inherits", which implies a ranking of systems by outcome.
- **Abstract:** rewrite (replacement provided). Keep: the cohort and conditions in one sentence; the stratified bargaining contrast with the Opus exception; counter content conditional on countering; 63/43 and the window partition stated as observed access; 61/61 reachable; 56/3/1 with the G7 numbers; nonterminal concentration; seven incidents; scope. Cut: 373/429; per-configuration rent; 121 v 63; 54/60; "mainly"; any "lost value", "price the completion" or "premium"; selection-as-finding.

## 1. Introduction (≈850 words)

- **Keep:** Astra's and Sol's opening idea that a trade changes a rival's construction budget and a future creditor's estate. Fable's "one question, three results" structure.
- **Cut:** the G2 vignette at the head of my draft. It reads as the thesis. Also cut my unsupported deployment sentence (OPR-18), Fable's "bargained hard" and "lost most" claims, and Astra's "do not respond to incoming cash alone".
- **Rewrite:** three numbered results matching the corrected abstract, then a scope paragraph naming the conditions and the non-claims once. One sentence positions against AgentMonopoly, FinBoardBench, the Arena study and DECE without novelty claims.

## 2. Environment, cohort and conditions (≈1,200 words, 2 tables)

- **Keep:** Sol's rules paragraph (§2.1–2.2); my five-rule list for the rules that matter (mortgaged-deed trades, per-entry even-build check, liquidation menu with declaration while payable, intact inheritance, redemption overcharge); Fable's prompt-norm quotations (exact prompt text, already source-read by Fable).
- **Table 1:** Fable's configuration table with a "departure from the standard path" column, corrected to read "refused first attempt and action-only recovery in 1,604 decisions; one further refusal on a second attempt (G2 d129); 61 engine defaults" (OPR-15).
- **Conditions paragraphs:**
  - Opus refusal: 215 of 306 decisions in G1–4 and 1,390 of 1,390 in G5–20 (Fable recount). Cause unresolved.
  - Memory: 1,394 decisions without a model-authored note in the window, and 1,544 applied actions without a note. State that these are different measures.
  - Grok conflicts: 139. Give Fable's breakdown plus my addition: 60 end→propose, 22 build→end, 11 buy→auction, 7 accept against reject/counter content, and 7 where content named bankruptcy and the call financed, with one reverse case (OPR-27). Localization to non-streamed bodies.
  - Formatter: 44/26/232, present in 2,054 prompts.
  - Delivery: 149 messages not delivered.
  - Channel availability.
- **Cut from main text:** token/latency detail beyond one sentence; the commit hashes (move to appendix).
- **Cohort paragraph:** wins in one sentence with the not-a-ranking caveat, five seeds by four cyclic rotations, and dependence.

## 3. Measurement (≈800 words)

- **Keep:** my units paragraph with the current-author definition; Fable's ledger list; the bound, witness and guarded-search paragraph (Sol and mine); Astra's statement paragraph on proposition, channel, delivery, response and consequence.
- **Add:** the access arithmetic for no-construction windows (replacement provided) and the list-price comparison definition.
- **Coding:** the 74-rejection codes and 240-sample codes are by GPT-6 Astra instances, with the second reader partly unblinded. Name every research-assistant model and its family overlap once. The research-roles statement goes in the appendix (OPR-29).
- **Checked versus inherited:** one sentence here, the full table in Appendix H.

## 4. Bargaining over completion (≈1,700 words + 2 incidents)

1. **Population** (Sol and mine): 526 threads, 920 responses (113/394/413), 918 acceptance-legal, short threads, 414 repeat-pair threads, 44 settlements whose final author is not the initiator.
2. **Table 2 (new combination):** completion cell × thread position (first offer / later offer) × A/C/R. The four pooled rows stay as a column. Data: `checks/settlement_checks.json`; matches Fable's appendix table.
3. **Responder paragraph and Table 3:** styles table (all four drafts agree; use Fable's with a condition column). One sentence on rejection contrast by responder, with the Opus exception and the small-count acceptance comparisons kept out of headline language (OPR-08).
4. **Counter content:** my Table counters (all 394), with Astra's 79-of-88 pure-cash refinement in the caption and the explicit statement that cash rises in every cell. Fix the caption omissions (Astra O7).
5. **Cash and list price:** one paragraph replacing every "despite \$200" and "price the completion" sentence (OPR-03). Put the 373/429 orientation fact and the list-price table in Appendix C.
6. **Stated reasons:** 61/74 two-reader agreement, with 38 recipient-only and 36 both. Disagreements, wrong-role notes and the G1/G15 concentration go in one paragraph.
7. **Initiation:** proposals per eligible own turn, plus Fable's join: 64 of Grok's 136 openings came from a call whose content named another action, 17 settled, and 7 of 28 acceptances came from conflicting calls, three of which completed Opus groups.
8. **Exploratory cash-poor sentence:** \$194 v \$571 median seller cash and 21/48, with the Opus composition. Fable's Table 3 goes to the appendix.
9. **Incidents:** G15 (Fable card; add a sentence that Gemini's three-house oranges were checked in the d168 prompt) and G2 (my card; flag the "nine houses" error; delete "shows the whole chain"; one sentence contrasting G7's settled bluff).

## 5. From completion to construction (≈1,100 words)

- **Table 4:** the first-window partition by configuration (Sol's table) plus an "ever built" column (Fable). Rename the "never legal" column to "no build option in window".
- **Never-legal explanation (replacement provided):** 7 arrived with a mortgaged group deed and 2 left less than a house. Two owners could redeem and build from cash (G14 Grok, G16 Grok). Five more could have done so by mortgaging their other deeds. Two (G15 Opus, G20 Opus) had no own-asset route. Grok's notes defer redemption in its four. G16 Opus redeemed and stopped. All of this is arithmetic under the engine's buildable and redemption rules, not an executed witness.
- **Entry-buildable subset:** 34/42 with 3/3/2.
- **END census table:** keep mine or Fable's (identical).
- **Reachable multisets:** 63/70 targets and 63/66 decisions; 61/61 Opus. G2 d129 ordering. 55/66 in G5 and G13. Recovery table. G2 d243 same-target versus changed-target. G14 attainment.
- **Valid holds:** G3 d176 and G1 d426.
- **Cut:** "earns nothing", "sound", "lost most", "properties of the purchase", "17 of 20 trace to". Move per-configuration rent to Appendix D, with one sentence on first-window-built versus unbuilt rent and unequal exposure.

## 6. Debt, liquidation and inheritance (≈1,300 words + G12)

- **Figure:** debt versus bound for all 60 (any of the three existing renderings). Use Fable's validated palette if its colors are kept.
- **Table:** the four nontrivial cases with my "menu mortgages" column relabelled "cash + menu mortgages" (OPR-12).
- **Mechanisms:** keep them distinct (Sol): G12 d190 and G17 d234 omit unlocked collateral; G12 d249 is a channel conflict; G7 d339 is the hotel lock. Successful liquidations G20 d327–336 and G16 d602.
- **G12 incident:** Astra's or Sol's reading. Name the conflicting channels precisely (OPR-13). Add the 7-reverse-direction sentence (OPR-27).
- **Spending units:** one paragraph (103 units, \$103,450, \$93,000, 40 zero, 26 no elimination, the G19 dark-blue succession).
- **Inheritance:**
  - Fable's route figure with the terminal bar separate.
  - Text (replacement provided): 52 during play against 63; 45/52 against 18/63 winner-owned; 14/52 collect rent; 35/40 nonterminal estates and 202/227 deeds; first estate to the eventual winner in 18 games; a single creditor in 16 games. Winner conditioning stated once.
  - Trajectories, without survival durations: G15 blockers to Gemini, G13 yellows to Sol at d311, G18 Illinois to Sol, the G11 blocker inherited from Gemini, G2 yellows to Gemini, and the G1 Boardwalk purchase justified by estate destination.

## 7. Conduct at distress, coordination and correction (≈1,600 words, 4 incidents)

- **G13 insurance:** Astra's text, plus Fable's \$1,926 Opus cash and Sol's events and \$235. The OPR-10 fix. Keep the 4/36 correction, the d244 prior correction, the formatter condition and the refusal-posture reading.
- **G18 withdrawal:** Astra's or Sol's reading. Fable's "Sol had refused that price as too low" and "Opus holds \$2,125". OPR-22 fix.
- **G20 appeal:** Sol's text with the d97 fact corrected (OPR-11). Keep Sol's d95 prior statement and Opus's later cash offers.
- **G19 correction with acceptance:** Astra's or Fable's text. Add Fable's note that it is one of the 60 end→propose conflicts.
- **Synthesis paragraph:** Astra's last paragraph ("Calling all of them deception … Calling none strategically meaningful …"). It is the best closing in any draft.
- **Appendix E:** G3, G7, G11, G4, G6, G12 d195, the G1 Boardwalk note (with the \$221 flag, OPR-24) and the G20 d1 disclosure.

## 8. Plans, forecasts and repeated errors (≈500 words)

Use Fable's version, which is compact: the G16 plan lost at the call, the G9 target, accounting-type forecasts and the recurrence table. Fix OPR-17 ("no probability forecasts"). Opus notes are absent in 53 of 60 sampled decisions. Drop auction-ceiling detail to the appendix.

## 9. Related work (≈600 words)

Merge Sol's and my paragraphs, narrowing every comparator to the inspected version and scope:

- Arena v3: 2,583 emails, 20 runs, cross-judge replication, the 1.58× low-inventory odds, and the finding that rank does not predict misalignment.
- AgentMonopoly v2: four families at two sizes; persona effects on words and some actions; larger models not consistently winning; the inherited rule differences, labelled inherited.
- FinBoardBench v1: three games; buildings sold to the bank (inherited).
- DECE v1: harness matters.
- Hardy et al. v1: system versus model ranking reliability.
- Yang et al. v1: a contamination audit with matched controls and scorer validation, whose scorer failed its validation gate.
- Cosentino et al.: accuracy conditional on given preference information, plus anchoring.
- Shah et al.: rigid extreme anchoring.
- Cattle Trade: strategic coherence associated with rank (OPR-19).
- CEO-Bench: all models below the rule-based baseline.
- Supply-chain bargaining: provider identity predicts surplus capture better than capability rank (abstract only).

State that most recent sources were checked at abstract level and that the closest comparisons rely on the 29 October section-level reading.

## 10. Discussion (≈900 words) and question map

- **Rewrite the implications** (replacement provided):
  - Report offers by whose position they change, by thread position and against list price.
  - Separate menu access, financing choice, encoding and execution.
  - Measure liquidity as legally reachable money.
  - Follow estates.
- **Cut** "pressure points" (OPR-07) and "agreement rate reflects pricing" (OPR-08).
- **Question map:** one table that merges Astra's two-column honesty with Fable's level column. Use Q1–Q8 rows and A–C rows, with no process language (OPR-29). The replacement provides the rows.
- **A–C paragraphs:**
  - A: Fable's four-way separation (statement, plan, submission, applied action) without "sound" (OPR-16).
  - B: not evaluated.
  - C: Fable's seed-block observations without "the dice decided" or "follow". Block 3: seat 2 buys both dark blues by turn 29 and wins in all four rotations. Block 4: seat 1 completes oranges by purchase at turn 47 and wins in three. Block 2: Sol wins from every seat. The shares are not estimable.

## 11. Limitations (≈500 words)

Use Sol's section with three additions: the access arithmetic and list-price comparisons are descriptive checks, not executed witnesses or valuations; the incidents are purposive and six of seven involve Grok's observable channels; and research-assistant model overlap.

## 12. Conclusion (≈200 words)

Use the replacement. It avoids "bargained hard", "lost most", "mainly", "priced completion" and selection claims.

## Appendices

- **A. Cohort, rules and outcomes.** The cohort table with Fable's first-complete-group columns (moved from main, OPR-30), the redemption overcharge, the bundled-sale rule, the version boundary, and the cohort figure if wanted.
- **B. Conditions detail.** Refusal chains, action-only prompt text, Grok conflict breakdown, delivery, channel availability, and the norms comparison table (mine).
- **C. Bargaining tables.** Cell × responder, × block, × game, × position. Cash direction and the list-price table (new). Counter transitions in full. Initiation. Cash-poor sensitivity (Fable).
- **D. Development and finance tables.** The nine no-option windows with redemption arithmetic (new; from `checks/never_legal_access.json`), END provenance, all 60 eliminations (Fable), the certificate support table (mine), the per-game table, and rent by configuration.
- **E. Further incidents and controls.** Listed in section 7 above.
- **F. Temporal exhibits** (mine or Fable's).
- **G. Reference-policy readiness** (one paragraph, Sol's).
- **H. Provenance and research roles.** A per-quantity checked, inherited or new table that merges Fable's three-way status scheme with my author-attributed table. Public repository, checkpoint and baseline hashes.

## What not to integrate

- Any 10/10, acceptance or superiority language.
- Future experiment protocols.
- Audit-method novelty.
- The winner grid in the main text.
- The spending scatter in the main text.
- Network diagrams.
- Model-level conclusions about Opus or Grok from conditions-affected rows.

## Open decisions for the parent

1. G2 or G7 as the main bluff case. My recommendation is G2 with the arithmetic flag. The fallback is G7 if length forces a cut.
2. Whether my access arithmetic for the nine windows enters the main text (my recommendation) or only Appendix D. It has had no second reviewer.
3. Whether the list-price comparison appears as a main-text paragraph (my recommendation) or only in Appendix C.
4. Human authorship line. All four drafts use "MonopolyBench project". The parent and user should set it, with LLM roles disclosed.
