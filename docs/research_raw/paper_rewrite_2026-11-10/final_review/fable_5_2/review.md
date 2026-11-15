# Whole-paper review of the integrated manuscript

Fable 5.2 xhigh, 11 November 2026. Target: `integrated/manuscript.pdf`, 33 pages, SHA-256
`8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5`. I read every section and
all 33 rendered pages, recorded `initial_position.md`, and only then opened the root review,
the decision log and the evidence map. I ran no game, engine code, replay, branch, synthetic
test, reference policy or model evaluation query.

## Verdict

The paper is sound. Every count I re-derived matches the page, and I re-derived most of them.
No result is overturned.

Three statements are wrong as worded and need a wording fix. None changes a number. Twelve
more passages are accurate but leave out something that changes what a reader concludes. In
most of those the missing material makes the paper's case stronger, not weaker.

My main criticism is the opposite of the usual one. The manuscript under-reports its own
evidence. It tells the reader what a number does not show more often than what the record
does show, and in several places the retained files hold a sharper fact than the one printed.

## What reproduces

I re-tabulated from `data/agenda_offers.json`, read canonical `decisions.jsonl` and
`events.jsonl` for all twenty games, and joined retained ledgers. These reproduce exactly:

- Table 1, the 50,918 events, and the Opus counts 1,604, 1,605, 215 of 306 and 1,390.
- Tables 2, 3 and 8 in every cell, the six quoted percentages, and the seed-block and game
  counts (five blocks, 17 of 19 games, four blocks, 13 games).
- Table 4 (111/92/79 and 110/87/81), and the 88, 85, $125, 169 and 59.
- The nineteen accepted author-only offers and their four overlapping subsets.
- Every cash-at-settlement figure, the four threshold cuts, and all sixteen Table 9 medians.
- Grok's 139 conflicts, re-derived from every Grok decision record and identical to the
  retained ledger, then the 64 conflicting openings, 17 settled, and the 7/1/3 response split.
- First-window causes (43/9/4/4/3 and 34/3/3/2) and every Table 11 row and remainder.
- All sixty elimination rows, the 56/3/1 split and the four automatic terminations.
- Estate and trade flows counted directly from events: 207, 397, 227, 202, $7,843, $7,148,
  54 = 35 + 19, the first estate in 18 games and all three in 16.
- Rent and routes: $121,154 over 905 payments, $57,378, $53,810, $3,568, 51 of 63, 14 of 52.
- All 49 declared quote cards, 35 of them displayed, match their original field verbatim.
- The five redemption principals with a one-dollar overcharge, by arithmetic.

`verification.md` lists the scripts, sources and limits.

## Strongest findings

1. **Unequal conversion.** Four similar trade-completion totals become 16, 17, 7 and 3
   first-window builds, and the record says why for each configuration. The original prompts
   support the decomposition.
2. **Current-debt classification.** Fifty-six bound negatives, three witnesses and one hotel
   lock are narrow, checkable and correctly scoped.
3. **Creditor concentration before the final elimination.** 202 of 227 deeds and 35 of 40
   estates, read directly from events.
4. **The G2, G13 and G12 chains.** Each ties quoted bargaining to a ledger consequence. G2
   and G13 are stronger than the paper presents them (FF-C02, FF-C04).

## Remaining weaknesses

- The paper pools where it has just shown that pooling misleads (FF-B01).
- It discloses who dominates the rejection-reason population but not who dominates the
  counter population, the 240-decision sample or the price cuts (FF-B02, FF-T01, FF-B04).
- It states caveats about received-call conflicts and leaves out the count that describes
  them: in 22 of 24, the content names a build (FF-D02).
- The abstract's headline numbers carry no labels (FF-W01).
- About one main-text sentence in five limits scope, and several caveats appear three or
  more times (FF-W02).
- Six of eight incidents involve Grok. The paper says so. It remains a real limit.

## Blocking corrections

Each is a wording fix. `replacement_prose.tex` has the text.

**FF-D01. "No construction option on any recorded menu" is false for two of nine windows.**
In Grok's G1 orange window (d298) and G1 dark-blue window (d314) the menu lists
`build_houses_or_hotel` with Atlantic Avenue buildable. The category is true per completed
group, which is how the retained ledger defines it. As worded, the section also contradicts
itself, because those two decisions are counted among the 663 ends "on menus offering
construction". The phrase recurs in `development.tex` lines 6 and 10, the Figure 1 label,
`methods.tex` line 8 and Appendix B.1. Both G1 notes decline the Atlantic house, which
supports the paper's reading that these windows are choices about finance.

**FF-L01. No liquidation was executed at G16 d602.** `finance_inheritance.tex` line 18 says
"extensive liquidation instead reaches $1,393" under the topic sentence "Actual staged
liquidation can succeed". Gemini declares at the first debt menu with $288. Its note adds
$375 and $730 to reach $1,393, which equals the bound. The sentence should present a correct
insolvency calculation.

**FF-Q01. Fifteen displayed cards say "excerpt" and quote the whole field.** The integration
fixed this for eight Fable cards and left the same condition in `transcript_quotes.tex`. The
quoted text is right in every case. `findings.json` lists the seventeen affected lines.

## Should-fix items

| ID | Passage | What is missing or ambiguous |
|---|---|---|
| FF-C01 | G18, "Subsequent $150 and $225 offers also fail" | Both are Opus's bids below the withdrawn $250. Sol asks $450, $350 and $300. Opus also redeems two greens within four turns, against its quoted reason. |
| FF-R01 | "Its prompt encourages bluffing" | The archived repository file has no prompt text. The claim is in the paper, Section 4 and Appendix A.2. The three repository facts check out. |
| FF-B01 | "Sol, Gemini and Grok reject … Opus reverses" | Pooled over position. Within position the rejection ordering holds in five of six cells and the acceptance ordering in three of six. The "neither" row gives a better reference. |
| FF-B02 | "Eighty-five improve the counterer's net cash" | Out of 88. Sol and Opus write 92 of the 111 counters. The form is still the majority for each counterer. |
| FF-B03 | "the agreed sixty-one are not itemized" | They can be: Gemini 29 of 31, Grok 27 of 31, Sol 4 of 4, Opus 1 of 8; 34 of 36 both-completing. |
| FF-D02 | "content may request a mortgage or an invalid build" | True for G20 and G12. In G8 and G13 the content names a one-house-per-deed plan on listed buildable deeds with enough cash, after mortgages in the same window. |
| FF-L02 | "The note also contains arithmetic errors" | The same note derives the five-sale route and $43 remainder. |
| FF-S01 | Refusal recovery | The policy lists a fallback model as a third stage. It never ran. The public records show the fallback name. |
| FF-S02 | "contain 139 disagreements" | No denominator. By a simple pattern, 1,068 of Grok's 1,663 selected responses name an action in content. |
| FF-T01 | "fixed 240-decision sample … passages" | Three hash-ranked decisions per player-game, sixty per configuration. The unit is decisions. Grok supplies 39 of 59 and 22 of 36. |
| FF-T02 | "configurations differ" | All 59 successors without delivered feedback are Opus's. |
| FF-W01 | Abstract | Unlabeled four-tuples, an unnamed participant, and plurals for single incidents. |

## Optional edits

- **FF-C02.** One turn before the G2 card begins, Sol asks Grok, who holds no yellow, $450 for
  Marvin Gardens. Sol then asks Opus $650 and refuses $450. This is the most direct evidence
  in the corpus for the section's subject. The G2 ledger is also fuller than printed.
- **FF-C03.** G7's deed returns to Sol inside a complete green group 85 turns later, through
  Grok's estate, and Sol builds on it. Three sentences make the card fit the paper's sequence.
- **FF-C04.** The mortgaged Pennsylvania sold in G13 was mortgaged in the first-window
  conflict the development section counts. Grok never builds in that game.
- **FF-C05, FF-C06.** Small precision points in G19, G20 and the G3 control.
- **FF-I01.** State the one-in-four reference beside 18 of 63, and move 57 of 60 to the text.
- **FF-B04.** Composition of two exploratory cuts.
- **FF-W03.** "This rewrite" appears six times in a paper whose reader has no referent for it.
- **FF-W04.** Figure 2 splits Transcript 5, and Table 4 lands before its subsection.
- **FF-P01.** Six exhibit inputs sit outside the 38-file pin.
- **FF-R02.** One Arena detail confirmed only by an earlier reviewer's section read.

## Hedging

A pattern count finds about 111 scope-limiting sentences among 537 in the abstract and main
sections, and 52 of 97 prose paragraphs end in one. The count is a regular-expression
estimate from `tools/count_hedges.py`, so treat it as approximate.

Each caveat is correct. The repetition hides the findings. I would delete or compress these:

| File and line | Sentence or clause | Why it can go |
|---|---|---|
| `bargaining.tex` 30 | "These checks do not remove price, portfolio or response-condition differences." | Table 2 caption and line 28 already say it. |
| `bargaining.tex` 52 | The four-sentence paragraph on agreement bias | One sentence carries it. |
| `bargaining.tex` 74 | "Board price is not a valuation standard." | Appendix A.1 says it twice. |
| `bargaining.tex` 110 | "The latter denominator conditions on low cash rather than on completion." | Appendix A explains both denominators. |
| `bargaining.tex` 112 | "but neither cash scarcity nor price is assigned" | The paragraph's last sentence says it. |
| `development.tex` 10 | "A received conflict does not imply … an executable plan." | Replaced by the specific description in FF-D02. |
| `development.tex` 34 | "without treating them as a performance ranking" | Appendix B says it. |
| `finance_inheritance.tex` 36 | "The contrast describes concentration conditional on the same games' outcomes." | Table 5 caption and line 55 say it. |
| `temporal_discussion.tex` 31 | "This local precision supports … a general auditor." | Introduction and related work say it. |
| `appendix.tex` 65 | "These exploratory cuts are not used to score pricing skill." | The preceding sentence covers it. |
| `appendix.tex` 97 | "No hypothetical engine state or new continuation was executed." | Methods line 25 says it. |
| `appendix.tex` 146 | "This rewrite adds no games, engine alternatives or evaluation calls." | Limitations line 23 says it. |

## Dissent and agreement

**I dissent from the root review's statement that no unresolved factual defect remains.**
FF-D01, FF-L01 and FF-Q01 are factual as worded. All three are small.

**I dissent from the decision to disclose the agreed sixty-one as not itemized.** Both
row-level codings are in the archive, and a join itemizes them. The itemization also shows
that only one of Opus's eight rejections carries an agreed reason.

**The label correction is incomplete.** The decision log reports eight Fable labels corrected
and verified. Fifteen displayed cards in the Astra quote file have the same defect.

**On G7 I change my position.** I began where Opus and my earlier review stood, preferring
seven main incidents. The events show a follow-through I did not expect. With FF-C03 applied
I support eight. Without it, G7 is the one card with no later consequence, and my preference
for the appendix stands as an editorial dissent.

**I agree with the root on four contested points.** Shared early purchase paths do not show
that dice decided seven games. Similar counter proportions do not show equivalent bargaining
across deeds. The 1.56 and 1.54 markup cut from my earlier review should stay out. The nine
static budgets are not executed witnesses, and my read of the original prompts confirms the
root's corrected collateral for all nine.

## What changed from my initial position

- **Resolved in the paper's favor.** The two Table 4 predicates select the identical 92
  counters. G15 has three offers and three refusals. The default denominators in
  Section 5.2 are all uneven-build rejections. The G20 chronology is right. The G12 note
  does contain errors.
- **Confirmed.** The G16 sentence, the unstated denominator for 85, the "Its prompt"
  antecedent, the G18 agent, the unpinned data inputs and every exposition point.
- **New after source reads.** The two G1 menus, the fallback stage, the 22 of 24, the
  itemized 61, the label defect, and the G2, G7 and G13 follow-throughs.

## Not verified

I did not re-run the witnesses, replays, memory reconstruction or snapshot checks. I did not
recode any semantic label. I did not re-derive the 15 and 5 argument-equality counts, the
history-formatter counts, the delivery counts, the spending-unit figures or the 1,394 memory
count. Literature passages came through a fetch tool that returns extracted text. These
remain inherited, as the paper says.
