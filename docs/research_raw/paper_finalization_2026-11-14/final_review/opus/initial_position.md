# Initial position (Opus final reviewer), formed before reading INTEGRATION_DECISIONS.md

Written 15 November 2026, after reading `BRIEF.md`, `FINAL_REVIEW_BRIEF.md`, `INTEGRATION_CRITERIA.md`, all four frozen drafts and handoffs (Astra, Sol, Opus, Fable 5.2), and the complete integrated candidate. I compared identical source files by hash and read every distinct authored file. I had not opened `INTEGRATION_DECISIONS.md` or any peer's final review when I wrote this.

Pins before review: 2396/2396 finalization entries match manifest `a362c4c6…885e269`. The integrated PDF is `e5c44beb…0dae`. The November 12 historical pin holds 84/84 under manifest `04d0a0d3…5e2`. Details are in `checks/pin_check_before.json`.

## What the integrated candidate is

The candidate is Astra's draft carried over almost verbatim, with targeted additions from the other three:

- Sol: the 188-entry refresh, the row-level rubric table and the full offer table.
- Opus: the 28/30 development cut, the G7 development-budget exchange and the corrected Catan sentence.
- Fable: the 43/48 numeric presence (supplement only) and the bundled-plan clause of the proof.

The main text ends on page 7 and references run to page 8, so it sits comfortably inside the nine-page ceiling at normal 10 pt. The supplement is complete and legible. Every rendered page I opened is clean.

## Overall judgment

The candidate is a coherent observational paper, and its core numbers are right. Its central move is sound: payment follows from continuing valid financing, so the evidence lies in what agents count, which assets they keep, whether they stop, and how text and call relate. The paper states that move once, with its conditions, and then spends its words on the positive content. I found **no factual blocker** in the main argument.

## Independently rechecked (raw decision logs and board data only; no engine import)

| Claim | My result |
|---|---|
| 188 episodes, 128 paid | Reproduced |
| 131 payable, split 62/53/16 (paid 62/52/14) | Reproduced; entry C, D, S, M0 and M* agree with `episodes_188.json` in every row |
| First actions: 132 covered (129 finance, 3 declare); 56 short (6 finance, 50 declare, 8 forced) | Reproduced |
| 28/30 | Reproduced. The two sellers are both Opus (G12 d282, G18 d372) and sell one house each |
| 74 recipient-completing legal rejections (38 recipient-only, 36 both); 61 common positives (27 + 34) | Reproduced. The disagreement keys are G15 d106, d108, G3 d506 and G13 d303 |
| Proposer table cells; neither-completing accepts 17, of which Grok 15 | Reproduced |
| G7 d141–d152 sequence | Every figure checks. Sol \$84 + \$700 − \$600 = \$184; \$84 + \$520 = \$604; Gemini \$745 − \$700 = \$45; mortgages 75 + 75 + 50 + 110 + 140 = \$450; four orange houses \$400, leaving \$95 |
| G20 d327 returned-explanation components | Sum to \$700 salvage and \$665 mortgage principal, as the integrated text now says. Astra's original "note gives \$700 … \$665" was wrong and has been fixed |
| 43/48 numeric presence | Reproduced. 34 of the 43 contain U* itself. All 27 entries without locked collateral match; 16 of the 21 with locked collateral do |
| 131-entry continuation argument (classes 108/12/9/2), including bundles | Correct as a conditional source argument. Engine and board hashes are identical at both run commits |

Checking every channel of the sixteen texts shows that no non-selected channel would move a case into a stronger category. The 5/3/5/1/2 split therefore also holds under an all-channel reading, which matches Fable's independent all-channel coding. G6 d185 and G17 d254 are genuine inclusive/ordered boundary cases.

## Initial findings, by tier

**Factual blockers.** None found.

**Material (each needs a sentence or a clause, not a restructuring):**

1. **28/30 and choice.** In G7 d318, one of the 28, the first and only menu offered no building sale: one hotel, two bank houses, and the other lots not the highest built. So "choices preserve development" overstates by one case. The exact choice population is 27 of the 29 debtors who were offered a sale. "Preference" is also more motive-laden than the descriptive scope the paper promises.
2. **Stopping is called informative but never shown.** The main text says stopping decisions are more discriminating than payment, yet it reports only the exceptions. The complete first-action pattern (129/132 versus 6/56, with 8 forced) appears only in supplement Table 13. One main-text sentence pointing to Table 13, with its non-score caveat, would make the stated thesis visible at population level without an accuracy headline.
3. **Related work omits memory and statement/action literature.** The brief requires both. The integrated draft cites only explanation-faithfulness work (in §2) and makes a memory remark with no citation. Opus, Sol and Fable all carried verified entries: Xiong et al. (ACL 2026) on memory, and Oota et al. and the atomic-chess workshop paper on statement versus action. One short paragraph fixes this.
4. **Named-action observability wording.** "Explicit action naming is much more observable in Grok's content" is imprecise. No other system's assistant content names a liquidation action at all: 0 of 93 Sol, 0 of 89 Gemini, 0 of 100 Opus (19 have content), against 27 of 56 Grok.
5. **61/74 caveats.** The two Astra readings are not independent: the packaged comparison records first-row exposure. The 74 are also concentrated (G1 has 22 and G15 has 12; Grok and Gemini recipients 31 each). The main text says only that the "readings agree".
6. **Versioned rules in the artifact appendix.** The appendix gives both commits but not which games ran at each (G1–G4 at 42f8…, G5–G20 at d680…). It omits the frozen engine/board SHA-256s that identify the implemented rules, and it gives no repository commit or archive hash for the package itself. Sol's draft has the hashes; they are verified above.

**Optional (worth doing; not required for release):**

- **G7, strongest omitted positive insight.** Gemini's public counter claims that \$700 would leave it "unable to build". Its own note in the same response counts \$450 of mortgageable non-orange deeds. Sol's note calls the claimed constraint overstated, and Gemini then mortgages exactly \$450 and builds. This is a counterparty correctly discounting a strategic understatement of financing capacity, and it is confirmed by the speaker's private note and its later actions. It is the cleanest opponent-modeling evidence in the corpus.
- **Numeric presence.** State the locked/unlocked split (27/27 versus 16/21). Note that three of the five non-matching unpayable responses (G3 d426, G5 d309, G8 d280) state exactly U0 as a maximum, the same listed-only form as the two payable failures, where it does not change the verdict. Give no exhaustive denominator.
- **Proof, third class.** Add one sentence on why stock cannot obstruct (bank houses minus four per hotel never falls).
- **Release hygiene.** Eleven unused `sections/*.tex` files ship in the release manifest. The README heading still says "finalization in progress". PDF metadata has an empty author and title.

## Positions on the known contested points (before reading the decision log)

- **Fable's 5/37 denominator.** Should be declined as an exhaustive denominator: 121 of 188 entries have collateral the first menu does not list. The listed-only form itself can still be mentioned without a denominator.
- **43/48 numeric presence.** Supplement only, with its limited semantics, is right. It must not become whole-response accuracy.
- **Selected-field rubric.** Fine as defined. One clause noting that an all-channel reading gives the same split would pre-empt the obvious objection.
- **Main-text incidents.** Five compact incidents plus a three-incident paragraph is a good balance. All eight are in the supplement with their economic meaning intact.
