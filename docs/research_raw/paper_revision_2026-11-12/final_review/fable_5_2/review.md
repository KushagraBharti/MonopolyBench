# Final whole-paper review of the integrated manuscript

Fable 5.2 xhigh, 12 November 2026. Target: `integrated/manuscript.pdf`, SHA-256 `f0312183aa8794ec08614966570395e55abd769410ff99f06992f25f314ed8a1`, 21 pages.

I read both referee reports, the charter, every active LaTeX source and all 21 rendered pages. I wrote `initial_position.md` before opening the integration decisions. I then rebuilt the two populations from the raw decision files, checked each of the eight incidents against its source decisions and events, and read `INTEGRATION_DECISIONS.md` and `adjudication.json`. I ran no engine, replay, game, baseline or model query. I did not open any other final reviewer's folder.

Findings are in `findings.json` (FR-F52-01 to 17). Replacement text is in `replacement_prose.tex` (R01 to R15). `verification.md` separates what I checked from what I inherited.

## Judgment

The paper states a coherent result and supports it. I would not restructure it again.

The result is this. When paying a debt requires a mortgage that the first menu does not offer, the agent's first text names that resource in thirteen of fourteen successes and raises it as a question in the fourteenth. Both failures add up only what the menu lists and quit. The paper prints all sixteen texts, the three numbers behind each row, and the 188-episode population around them. I read the sixteen texts and agree with the 13, 1 and 2 reading. I rebuilt all sixteen rows from the raw requests and they match.

The positive accomplishments are real and the paper should say them plainly:

- A complete debt population. I rebuilt all 188 episodes from `decisions.jsonl`. Debt, cash, bound and action sequence match the integrated ledger in every episode. The 62, 53 and 16 partition, the 128 payments and every count in section 3.1 reproduce.
- A complete negotiation population. I rebuilt all 920 responses with form, stage and completion from the raw requests. There are zero row differences from the integrated data, and every cell of Tables 3 to 7 reproduces.
- A bargaining contrast that the paper demotes correctly. The population, the proposer and recipient strata and the three resampling schemes answer the referees' composition criticism. No sentence treats the 61 of 74 reasons as an explanation of the contrast.
- Eight incidents whose quotations, channels, delivery claims and continuations hold up. I traced each one. All twenty cards match their source fields, and I found no false continuation.
- Response conditions that are stated and correct: the liquidation instruction (identical in all 338 liquidation requests), tool choice in all 8,687 saved requests, the refusal counts, both printed prompts and both replay comparisons in all twenty stored reports.

The limits the paper states are the right ones. My findings concern four places where the paper says less than its own records support, or frames an incident in a way the records qualify.

## Major findings

**1. G18 (FR-F52-01).** The paper says "The records establish neither original insincerity nor a cost incurred by relying on the offer." The response that carries the quoted renewal, "My Pacific offer still stands," also returns this reasoning: "Buying Pacific might just prolong p1's survival, so maybe it's smarter to hold onto cash." Two turns earlier the returned text says that trading for Pacific at $300 "isn't appealing" while the public message repeats that the offer stands. The first $250 counter does read as a live offer. So the survival motive is right, and it is recorded one turn before the withdrawal, beside the public renewal. This is the paper's own subject, a public statement against the text returned with it, and the incident currently reports only half of it. R13 gives the corrected passage. It also fixes "over the next four turns" (eight turn indices by the paper's own convention) and "repeatedly offers $250" (one $250 counter and four public restatements).

**2. G15 and G2 (FR-F52-02).** The integration added a rival's public warning before each focal statement. Both warnings are real and delivered. In both games the agent's own notes hold the blocking rule earlier. Grok's note says "Don't sell Ventnor back to p4" at turn 33, thirty turns before Sol's offers, and Gemini and Opus had been urging Grok publicly since turn 55. Sol's note says "Keep Marvin blocking p4's yellows" four turns before Opus's bid, and Sol's own public counter names the yellow monopoly before Grok's warning. As printed, a reader takes each statement as prompted by the warning. One or two sentences per incident restore the order (R10, R11). The fuller G15 sequence also gives the paper its only shown case of a rule kept in notes across many turns and then acted on.

**3. The fourth text channel is undefined (FR-F52-03).** "Provider-returned explanation" carries five of the sixteen financing texts and the key sentences of G5, G13 and G18. It is the gateway's reasoning field. The prompt does not ask for it, no player sees it and no later prompt carries it. The gateway labels it a summary of encrypted reasoning for Grok and Sol. It is present in 1,662 of 1,663 final Grok responses and in 287 of 1,961 for Sol. A reader needs this to weigh the G13 sentence "This is slightly deceptive," which sits in a provider summary of a long trace. R01 is a four-sentence definition.

**4. The central result is not placed on the distinction the paper cites (FR-F52-04).** Related work cites PlanBench for the difference between planning and retrieving familiar knowledge, and then does not say where the paper's own evidence falls. I checked the sixteen first requests. No system prompt mentions mortgages. No menu lists a dollar value. The timeline shows a value for a released deed once. The rule appears only in the agents' own carried notes, stated in G1 d476 and implied for a rival's group in G18 d309. So the environment supplies neither the rule nor the values, the agents bring both, and the rule is a standard rule of a widely published game. The finding is that agents apply a familiar rule to a live state before the menu shows the resource. It is not evidence about unfamiliar dependencies. Saying so costs the paper nothing and tells a planning researcher what was measured (R03, R04). The same check shows that both failed sums reuse figures from the agents' own carried notes, and that carried partial figures also precede two successes, so I draw no causal reading from it.

## Bounded fixes

- **First actions (FR-F52-05, R02).** "Agents begin financing in 128 of 131 payable episodes" is true by construction. Classes defined at entry are 132 and 56, with first-menu declarations in 3 and 50. The paragraph should also say what the context is for: agents usually stop when resources fall short, so they are not running a loop over listed actions. Five of the six exceptions are Grok.
- **Cash-bid proposers (FR-F52-06, R08).** Opus writes 110 of the 173 opening cash bids, 105 of them in action-only recovery. The swap and cash-bid rows differ in who proposes as well as in form. The paper gives proposer composition for swaps only.
- **Block cells (FR-F52-07, R09).** The widest ticks in the main figure come from cells of four and eleven offers. A small table of block counts fixes this.
- **G5 (FR-F52-08, R05).** The carried note predates the episode by four turns and the returned text revises its own first sum without citing the note. "Correction within an episode" and "revises that assessment" overstate.
- **The engine audit (FR-F52-09, R14).** The paper describes it as "historical" and "earlier" and does not print the three witnesses. They are short, and I read them from the stored report.
- **Abstract (FR-F52-10, R06).** "Completing and non-completing swaps" names a different population. The body supports a more informative sentence: every recipient rejects proposer-only swaps more often, and the pooled size depends on who proposes.
- **Repetition (FR-F52-13).** About 70 of 445 main-text sentences bound or disclaim an inference. That is the share the second referee measured in the previous version. The five recurring limits each appear five to seven times. I list ten passages that can go because sections 2.1, 2.3 or 8 already say the same thing.

Minor items are FR-F52-11, 12, 14, 15, 16 and 17: four statements without printed numbers, the G20 cash path, an unpinned analysis input, two missing cross-links in G2, a question-map row without a shown example, and two layout defects.

## The review priorities, one by one

1. Coherent and worthwhile result: yes, as above.
2. Populations and inference boundaries: sixteen texts, 13 plus 1 plus 2, bounds against witnesses, and requirements against difficulty are all stated correctly. The first-action census is context in the paper. FR-F52-05 asks only for an entry-defined wording.
3. Negotiation: all four forms, both stages and all sixteen cells per stage are printed and reproduce. Proposer and recipient strata reproduce. The three resampling definitions are stated and distinguished, and the text says none corrects selection. The figure shows block points and leave-one-block-out ranges as described. Additions: FR-F52-06 and 07.
4. Incidents: all eight are present and distinct. G13 reports both buyer motives and the quoted span is exact. G19 is kept as a positive correction. G18's motive is survival funding. New spans: the G5 and G13 cards are exact, and the G2 and G15 warnings are delivered as claimed. Corrections: FR-F52-01, 02, 08 and 12.
5. Response conditions: confirmed in full. See `verification.md`.
6. Clarity and repetition: FR-F52-03, 09, 10, 11 and 13.
7. Rendering: I rendered the pinned PDF with Ghostscript and inspected all 21 pages. Two layout defects, FR-F52-17.

## Review of the integration decisions

I agree with decisions 2, 4, 5, 6, 8, 9 and 10 as written.

- **Decision 1, first actions.** I agree with keeping them as context and with refusing a matched-shortfall headline. I dissent on wording only. The printed paragraph uses an outcome-defined class and gives the reader no purpose for the numbers.
- **Decision 3, information and memory.** I agree that the paper must not assert recall as a mechanism. I dissent from stopping at "the records do not identify the source of every value." The request contents were checked and can be reported. They carry a scope statement the paper needs.
- **Decision 7, incidents.** The G2 and G15 additions are accurate and incomplete (FR-F52-02). The G5 wording is loose (FR-F52-08). The G18 motive is right and the sincerity sentence is incomplete (FR-F52-01).
- **The adjudication record.** `adjudication.json` assigns one decision string per topic, so several findings with different recommendations carry the same text. My XR-F52-03 asked for a specific sentence about the sixteen requests. It is marked "Accepted with a narrower presentation," and the sentence is absent. A reader of the record cannot tell which recommendations were dropped.
- **An unpinned input.** The decisions file says no reviewer folder is a build dependency. That holds. `tools/analyze.py` does read `qa/fable_cross_review_reproduction.json`, which the manifest does not pin (FR-F52-14).

## Errors in my own earlier contributions

- XR-F52-19 recommended adding Opus's G15 appeal. I had checked only the turn before the offers. Grok's notes from turn 33 and the appeals from turn 55 change the reading.
- XR-F52-18 introduced the G5 sequence under a title that said the omission was "revised at the debt." The returned text revises its own first sum. It does not cite the note.
- XR-F52-03 asked the paper to say the values "are not in the request for those deeds." That is too strong for G1 d476, where Grok's own carried note has the rule and the yellow total.
- My draft called the first-action counts discrimination. My cross-review withdrew that, and I do not ask to restore it.
- The conflict-opening list that `analyze.py` reads came from my 11 November cross-review and reached the build unpinned.

## What I would leave alone

The title, the order of sections, the eight incidents, the full question map, the sixteen printed texts, the three resampling schemes and the limitations section. Authorship and venue remain with the project owner.
