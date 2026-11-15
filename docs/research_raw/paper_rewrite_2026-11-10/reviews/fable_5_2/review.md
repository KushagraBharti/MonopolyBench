# Whole-paper cross-review (Fable 5.2)

Written 2026-11-11. I read all four complete drafts in full, wrote `initial_position.md`, and only then opened `reviews/astra/`. I read Astra's `all_four_review.md`, `comparison_in_progress.md`, `check_counteroffers.py`, the three JSON outputs, `literature_followup.md` and `render_review.md`. I did not open the `reviews/sol` or `reviews/opus` folders. I used no subagents and ran no game, engine, model call, synthetic test or reference policy. Every number below marked "checked" comes from a script in `tools/` that reads retained ledgers or canonical saved-game records. Every engine result (payment witnesses, reordered build plans, the G7 search, replay) is inherited from the 29 October audit and I did not re-execute it.

Finding identifiers (FX-…) point into `findings.json`. Replacement blocks (R0 to R13) point into `replacement_prose.tex`.

## 1. Central thesis

The paper should say this. In twenty complete games, four configured LLM systems completed similar numbers of color groups by trade and realized very different amounts from them, and the difference was made after the deal, in the cash the deal left behind and at the execution layer. Bargaining over completion was contested but less distinctive than a pooled table suggests. Nearly every bankruptcy was unpayable when it came, and estates went to the player already collecting rent.

That is a behavioral paper that follows one sequence: bargain, build, pay, inherit. All four drafts reached that sequence independently, which is the best argument that it is right.

## 2. What survives the observational design

Ranked by how little each depends on a counterfactual.

1. **Conversion of traded groups (checked).** 17, 18, 15 and 13 groups completed by trade. 16, 17, 7 and 3 built in the first management window. Groups built in the first window collect \$53,810 of \$57,378. The twenty unbuilt windows partition cleanly once the menus are read (FX-D01). For the 66 defaults the path inside each decision is recorded, which makes this the only result in the corpus with a documented mechanism. That 63 of 70 targets were reachable is inherited.
2. **Eliminations (checked for the bound, inherited for the witnesses).** 56 of 60 fall below a bound that needs no engine. Two of the three payable declarations omit the same step, collateral that appears after buildings are sold (\$340 and \$375, read from the notes and menus, FX-L01).
3. **Bargaining (checked).** An offer completing only its author's group is accepted 19 times in 289. As an opening offer it is accepted 3 times in 187, and only once by a response whose text and call agree. Three of four systems reject such offers more often than offers completing their own group. This is real and narrower than the drafts say (section 4).
4. **Estates follow rent (checked).** The winner is creditor in 35 of 40 eliminations before the last. In-play estates complete 52 groups, 45 for the winner, and those groups collect \$11,472 of \$95,278.
5. **Seat and system (checked).** Seven games follow the seat that bought an early monopoly from the bank under different systems. Four follow one system across seats. This is the closest thing the cohort has to a designed contrast, and it answers question C more directly than anything else in the record (FX-S01).

The finding that changes what a reader learns is the first, read together with the fifth. A deal count and a win count would both misdescribe these systems, and the paper can show exactly why, decision by decision.

## 3. Objections to each draft

### Fable 5.2 (my own)

My draft found the most and overread the most. These are errors, not matters of emphasis.

| Finding | Passage | What is wrong |
|---|---|---|
| FX-B03 | "The systems price the completion itself" | Cash direction is the buyer paying. The baseline without completion is 309 of 313. |
| FX-I01 | "Estates complete 121 groups against 63 by trade"; heading "Estates move more property than trades" | 69 of the 121 arrive when play is over. |
| FX-D01 | "Nine could not legally be built on"; "17 of 20 trace to the acquisition or the response path" | Four of the nine are Grok holds with redemption on the menu and a stated reason. |
| FX-I02 | "The protection bought lasted 43 turns" | A later bankruptcy is not a purchased duration. |
| FX-B06 | "Mainly when their holder is short of cash" | 21 of 48, and Opus is 13 of the 21. |
| FX-D02 | "Lost most of their early value" to the refusal path | Three of Opus's eight unbuilt windows are defaults. Lost rent is not observed. |
| FX-R02 | "Coherent spending predicts rank"; "concede without compensation" | Neither matches the abstract it cites. |
| FX-D05, FX-C05, FX-C06 | Table row G20; G1 note; eight card labels | Incomplete reason; a figure off by a dollar for this engine; whole fields labelled excerpts. |
| Astra F3, F6, F7, F9, F10 | Private-note honesty; G2 d129; "sound as plans"; "three independent places"; comparator generalizations | I accept all five. |

What my draft contributes that should survive: the thread-position split, the conflict join carried into the bargaining counts, the conversion table with rent, the route census with terminal estates separated, the seed-block mechanism, the G15 incident, and the three-way provenance table.

### Opus

- **FX-B02.** The lead bargaining result claims specificity it does not have. Counters keep the requested deed 83 percent of the time when it completes the asker's group and 79 percent when it does not. Opus's counts are right. The inference is not.
- **FX-C01, FX-C02.** G2 is the best incident in any draft and its write-up has three faults: the note's house count is three times too high and is presented as a computation (Astra found this), the reversal happens when the seller has \$17 and the text does not say so, and "collects no rent" is \$44.
- **FX-D03.** G2 d243 is Gemini's decision. The text gives it to Sol, who had been eliminated four decisions earlier.
- **FX-L01.** "Displayed options understated finance" is wrong as written. The sale action was displayed and two notes count it.
- **FX-I01, FX-I02.** "54 of 60 estates" in the abstract and discussion includes 19 game-ending estates. "The insurance bought time."
- **FX-D02, FX-D04, FX-C04, FX-D07, FX-L03, FX-S03.** Lost development; "sound"; conduct "concentrates"; 1,605 recovery decisions; "every text channel"; deployment claim in the first sentence. Astra raised each and I agree.
- Forty-three pages. The appendix tables are useful and the main text has to lose about a quarter.

What should survive: counter content with a baseline, per-recipient heterogeneity with the Opus exception in the main result, thread outcomes, the conditions table, the claim-class support table, G2 and G11, and the single coverage table.

### Astra

- **FX-B01.** The headline contrast is printed without position or the Opus exception. Astra's own A1 concedes the second.
- **FX-D01.** "Never buildable" is used as lack of access and as a reason the build fractions "cannot simply be named willingness to invest". For Grok's four windows the notes are about willingness.
- **FX-W02.** The discussion is careful and mostly negative. A reader finishes it knowing what the evidence does not show.
- No new incident, so the first research question's own example never appears. One figure.
- **FX-R01.** The AgentMonopoly creditor sentence rests on a repository inspection the paper text does not support by itself.

What should survive: the shortest architecture, the finance paragraphs, the channel distinctions in G12 and G19, the corrections table in the appendix, and "bought immediate liquidity without preventing the later event", which is the only supported G13 wording in any draft.

### Sol

- **FX-B01, FX-D01** as for Astra.
- **FX-I02.** "Purchases time."
- The eight questions are covered twice, in prose and in an appendix table.
- The conduct section runs seven cases in a row (FX-W01).

What should survive: the continuous economic argument, the methods subsection that separates checked from inherited work, the versioned related-work section, the abstract's use of the nonterminal 202 of 227, and the finance figure.

## 4. Challenge to Astra's review

Astra's review is the strongest document in the package and I agree with most of it. I list agreement briefly and dissent at length.

**Agreement.** O1 to O9, F1, F3 to F10, A1, S1 and P1. The behavioral identity, conditions first, the 56/3/1 partition kept exact, incidents beside results, the same seven incidents (I reached the same list before reading Astra), no audit-method claim, no "mostly", "sound", "lost value", "premium", "protection lasted" or "only delays". Astra's O1 caught an error I missed (FX-X01).

**Dissent D1. The pooled rejection contrast needs the position split, and Astra's review never mentions position.** 187 of 289 author-only offers open a thread and 89 of 140 recipient-only offers follow a counter. Within position the gap is about 13 points against 28 pooled. Astra's thesis item 1 asks for heterogeneity by configuration only. An integrated table that prints 159 of 289 against 38 of 140 without this is printing a composition effect (FX-B01, R4 Table "cells"). Astra's later integrated text does give the split (section 10).

**Dissent D2. Counter content is weaker than Astra allows.** Astra verified that 79 of the 88 are pure cash repricings and wrote that this is "negotiation over terms, not proof of a uniquely rival-sensitive price premium". That is right and stops short. I ran the same join where no completion is involved. Pure repricings are 81 of 110 there. Requested deeds are kept in 87 of 110. The markup over the cash offered is 1.54 times against 1.56. The counter table should stay, with the neither row beside it, and the paper should say that counters reprice every kind of deed alike. What does differ is the asking level by system: Sol and Grok ask about 3 times list for a completing deed and 2 times otherwise, and Opus asks less for completing deeds than for others (FX-B02, R4 section 4.3).

**Dissent D3. "373 of 429" is correct and not useful.** Astra calls it "correct and useful" and proposes "the completing side usually pays net cash". In offers that complete nothing, the side receiving more deeds pays in 309 of 313. The sentence tells the reader that buyers pay. I would cut it or print it with the baseline (FX-B03).

**Dissent D4. Estate volume is the wrong main result.** Astra's item 4 makes "52 complete groups and 227 deeds … against 63 trade completions and 207 traded deeds" the meaningful result. The nonterminal population is the right one. The comparison of volumes still invites my draft's bad heading. The informative facts are concentration (35 of 40; one creditor for both pre-final estates in 16 games) and order (estate-completed groups collect 12 percent of complete-group rent, and the creditor usually owned the group that caused the debt). I would lead with those and give volumes in one sentence (FX-I03, R7).

**Dissent D5. The seed-block mechanism is missing from Astra's review.** The review credits my draft with several things and not this one. I think it is the most direct evidence in the corpus on skill and luck and it costs one paragraph (FX-S01, R2). The later integrated text has one of the two blocks (section 10).

**Extension E1. Never-legal windows.** Astra's F5 says the nine are not demonstrated impossibilities and that Grok's notes "in several" express an intention to wait. Reading the menus makes this exact: four Grok windows with redemption offered and a stated reserve reason, two of them with cash covering redemption plus a house, and five Opus windows with \$7 to \$268 and no note. Astra's "seven mortgaged, two cash-short" repeats an error in my table. Eight had a mortgaged group deed at the first management decision (FX-D01, FX-D05).

**Extension E2. G13.** Astra's F8 corrects my 43 turns. The same fault is in Sol ("purchases time") and Opus ("bought time"). The cash path shows Grok did not land on Short Line on the roll it described and paid a different railroad 39 turns later. One fact no draft has: Opus completed the green group at auction seven turns after buying Pennsylvania, so Opus was also buying a deed it used (FX-I02).

**Extension E3. Scope of the stated reasons.** Sixty-two of the 74 coded rejections are Grok's or Gemini's, and 35 of the first reader's 63 rival-consequence codes sit in the both-completing cell (FX-B05). Astra's F9 separates attention from preference and quality. This adds that the attention is documented for two systems.

**Extension E4. Things neither Astra nor any draft has.** The nineteen accepted author-only offers described one by one (FX-B08). Three of Opus's fifteen trade completions accepted by conflicted Grok calls, all unbuilt (FX-D06). Seven reverse-direction bankruptcy disagreements, all in unpayable eliminations (FX-L02). G2 d243 misattributed (FX-D03). AgentMonopoly's creditor rule and trade interface absent from the paper text; FinBoardBench's counteroffers and five-failure budget (FX-R01, FX-R03).

**A challenge to my own earlier claims.** My handoff defended the cash-poor tabulation as robust to threshold. It is robust in direction and it is carried by one system under a nonstandard condition. My handoff asked for inheritance to have "structural weight" on the strength of 121 completions. The weight belongs to the 35 of 40 and to the rent comparison, which cuts against my own heading. My handoff said the Grok conflicts should be carried into the bargaining counts, and that still stands and matters more than I said: two of the three accepted opening author-only offers are conflicted calls.

## 5. The contract's eight questions

**Which positive finding survives and changes what a reader learns?** Conversion. Two systems realized their bargains and two did not, for reasons the record separates into stated holds, low cash, engine defaults after an invalid encoding with no retry left, and calls that contradict their own text. It teaches that an economic agent's outcome is set at the execution layer and in its cash position as much as in its bargaining, and that the retry budget is part of the agent.

**How to combine rejection, counter changes, cash direction and stated reasons?** One table of responses by cell and position. One sentence on the within-position gap. The per-recipient row with Opus as the exception. Counters as repricing in every cell, with asks relative to list by system. The nineteen acceptances described. Stated reasons scoped to Grok and Gemini. No uniform rival effect, no premium, no verdict on agreement bias. R4 is the finished text.

**How to present never-legal, default, conflict and valid-end?** As five groups, not four: 4 with redemption offered and a stated reserve reason, 5 low-cash without notes, 4 defaults, 4 received-call disagreements, 3 end-of-turn choices with construction listed. Say that none is shown impossible and that the defaults measure failed execution at 61 decisions and not rent. R5 and the appendix table.

**Which inheritance population in the headline?** The forty eliminations before the last. 35 of 40, 202 of 227 deeds, 52 groups of which 45 to the winner. Name the 69 terminal completions once as not usable. Connect to bargaining through four sequences (G13, G18 Illinois, G15, G2) and the G1 note, each stated as a sequence. R7.

**Which seven or eight incidents?** G2, G15, G19, G20, G12, G13, G18 in the main text. G7, G11, G3, the G1 note and the G20 d1 disclosure in the appendix. G15 over G11 because four players are alive, the offer completes both sides, the proposer's note counts on the asymmetry the refuser names, and the refuser goes bankrupt first. G2 over G7 because it is the same bluff with consequences along the whole path, and G7 is then the contrast in which the bluff settles. Quotes stay verbatim. The text says where they are wrong: G2's nine houses, G13's 5 in 36, G1's \$220. `integration_proposal.md` section 5 gives channel, exposure, correction and outcome for each.

**Main text or appendix?** Main: one conditions table, three bargaining tables, the conversion table and figure, the finance figure and four-case table, the coverage table, seven incidents. Appendix: cohort table with first completions, per-recipient-by-cell, block and game tables, price ratios, the unbuilt-window table, all sixty eliminations, END provenance, recovery and recurrence tables, further incidents, claim-class support table, provenance table, research roles. Caveats are stated once per section in one sentence and consolidated in six limitation paragraphs (R10).

**Does every claim about another paper match the inspected version?** Not yet. See FX-R01 to FX-R04. Sol's related-work text is the only one that states version and depth of inspection per source and should be the base.

**Are authorship, assistance, conditions, hashes and provenance candid?** Conditions and provenance are, in all four. The assistance statements differ in how plainly they say that two assistants carry the same model identifiers as two players and that the incidents were selected by those assistants. R12 gives one paragraph. The byline is the human author's decision and depends on venue policy.

## 6. Section-by-section recommendation

| Section | Base | Change |
|---|---|---|
| Title, abstract | R0 | New. Leads with conversion. |
| Introduction | Fable opening, Opus vignette | R1. Four results, G2 corrected, seat sentence. |
| Environment and conditions | Opus rules list and conditions table | R2 paragraphs for refusal, norms, cohort. |
| Measurement | Sol units and checked-versus-inherited, Opus legal tests | R3 for offer descriptors and coding scope. |
| Bargaining | R4 | Full replacement, with G2, G15 and G19. |
| Development | Fable conversion table and figure, Opus END table | R5 for the unbuilt windows and the default path. G20 kept. |
| Liquidity | Sol text and figure, four-case table | R6 for the payable cases and reverse disagreements. G12 kept with two sentences changed. |
| Estates | R7 | Full replacement. G13 and G18 cards kept, outcomes and readings replaced. |
| Plans and recurrence | Opus three paragraphs | Scope "no probability forecasts" to the coded targets (Astra O9). |
| Related work | Sol | R9 paragraph. Add Cosentino and LLM-Stakeholders from Opus and Fable at abstract scope. |
| Discussion | R8 | Four paragraphs and one coverage table. |
| Limitations | R10 | Six paragraphs. |
| Conclusion | R11 | New. |
| Appendix | Opus and Fable tables, Astra corrections table | R12 additions. |

## 7. Three likely rejection reasons for the best integrated paper

1. **Nothing is identified.** The paper's most quotable bargaining number halves under one stratification that the paper itself reports, holds for three of four systems, and has no valuation behind it. A reviewer who wanted a behavioral finding can fairly say the paper documents and does not explain.
2. **The execution result reads as a harness defect.** One system played 95 percent of its decisions through a recovery path, 29 percent of all prompts carried a garbled history line, and the 61 defaults follow from one validator rule meeting one retry budget. The obvious request is to fix the interface and rerun, which is outside what this paper can do.
3. **The paper's own evidence says early dice decided a third of the games, and its semantic layer was coded and selected by models that overlap with the players.** Seven of twenty games follow a seat. No human read the 74 rejections or chose the incidents. A reviewer can accept every count and still conclude that twenty games from five seeds, analyzed by the participants' siblings, do not support a paper at a selective venue.

None of these can be written away, and the limitations section should say all three plainly.

## 8. Strongest dissent

The integrated bargaining section must not lead with 159 of 289 against 38 of 140 unqualified, and must not present 92 of 111 as a fact about rival completion. Three drafts do the first and one does the second. Both are true counts and both mislead. If the parent keeps either as written I ask that this dissent be recorded with the integrated paper.

Second, I dissent from my own draft's two headings, "the completing side pays" and "estates move more property than trades". Neither should survive in any form.

## 9. What I did not check

I re-executed no certificate, replay or witness. I did not re-read the 74 rejection texts or the 240 sampled decisions, and the 61 agreed codes are not itemized in the retained file, so my split uses the first reader's codes. My window check is arithmetic on cash and collateral and is not a feasibility result. I checked delivery for the fifteen new public quotes and not again for the 28 baseline quotes. Literature checks used a fetch tool that summarizes pages, so I report section pointers and no quotations. I did not read the AgentMonopoly repository. I did not open the Sol or Opus review folders.

## 10. Snapshot of `integrated/` (outside the assigned scope)

While I was writing, an `integrated/` folder appeared with a first integration by Astra. Its `integration_decisions.md` lists this review as pending input. I read it only after sections 1 to 9 above, the findings and the replacement prose were complete, so it did not shape them. I read it once, at about 05:49 UTC on 11 November (PDF hash prefix `0feea7e4c8014626`), and did not edit it. It may have moved since.

It already resolves 14 of my 40 findings, among them the G2 arithmetic, the 43 turns, lost value, the nonterminal estate population, the position counts and the G12 channels. Twelve still apply and eight apply in part. `findings.json` carries a status and a line pointer for each. The ones that matter:

| Finding | Where in `integrated/` | Fix |
|---|---|---|
| FX-B02 | Abstract; `bargaining.tex` lines 54 to 56; conclusion. 92 of 111 and 79 are presented with no non-completion baseline, and the abstract leads its bargaining result with them | R13a, R13d |
| FX-B03 | `bargaining.tex` line 26, "The completing side usually pays … 373/429" | R13b |
| FX-B04 | The one-in-187 fact is absent | R13c |
| FX-B05 | Line 56 gives 61 of 74 without the two-system scope | R13e |
| FX-D01, FX-D05 | `development.tex` line 14, "Seven of the nine … The other two settlements leave \$158 and \$125 … In several of these purchases Grok also states" | R13h. Eight have a mortgaged group deed. Four Grok windows have redemption on the menu and a stated reason. Five Opus windows have no note |
| FX-I02 | G13 finding has the right reading and lacks the cash path and Opus's auction completion | R13j |
| FX-C02 | G2 lacks Opus's \$17 at the sale and its elimination three turns later | R13g |
| FX-S01 | `temporal_discussion.tex` line 60 has seat 2 and the dark blues, not the orange block | R13k |
| FX-R01 | `related_limits.tex` line 7 states three AgentMonopoly implementation facts and cites only the paper | R13l |
| FX-B06 | Seller-cash subsection lacks the Opus share | R13f, or move to the appendix |
| FX-L02 | Reverse-direction disagreements absent | R13i |
| FX-C06 | `sections/fable_quotes.tex` still labels eight whole fields "excerpt" | Relabel in the merged quote generator |

Two matters of judgment where I would go further than the integrated text. It opens its results with bargaining and its discussion does not say what a reader should do differently. I would lead with conversion and use the first paragraph of R8. And it keeps G7 as an eighth main incident. That is defensible. I would still move it to the appendix, because G2 already shows the same bluff and the main text is long.

If the parent prefers to keep the integrated sections, R13 is a set of twelve insertions that closes every finding marked "applies" without taking R4, R5 or R7 whole.
