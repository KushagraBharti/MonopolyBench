# Opus xhigh: initial independent position (before reading root_review.md or integration_decisions.md)

Recorded on 2026-11-11 after:
- pinning `integrated/manuscript.pdf` (SHA-256 `8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5`, matches)
- checking all 38 entries of `integrated/qa/integrated_file_hashes.json` (0 mismatches)
- reading `manuscript.tex`, every `sections/*.tex` file (including the row and quote macro files), and the rendered PDF pages for both figures, Table 1, Table 6 and the appendix tables (rendered with Ghostscript into `final_review/opus/render/`).

Nothing below has yet been checked against retained ledgers or original records. Every item is a reading-level judgment I intend to verify or withdraw.

## Overall judgment

The integrated manuscript is a coherent observational paper. The economic sequence holds together: offer census, then counters, then first-window development, then current-debt finance, then estates. Response and information conditions now come before the results and are carried into the populations rather than being parked in a limitations paragraph. The table arithmetic I checked by hand is internally consistent. Table 1 and its opening/later split sum correctly, Table 2 sums to 920, the appendix response cells sum to the Table 1 margins, the access budget remainders recompute, the cohort winner totals (8/7/3/2) match the cohort rows, and the eight Grok-involved incident count is right (six of eight). The abstract now leads with unequal conversion, which is the strongest finding.

I do not see a framing-level blocker. My concerns are a small number of internal inconsistencies, one possibly misattributed error, two places where an appendix caveat creates a doubt that the main text does not close, and some unsupported or unsourced sentences.

## Candidate blocking issues (to verify)

1. **Counter predicate mismatch.** Table 3's header says "All requested deeds retained" (92/111), and its caption says that the same deed-retention predicate is used in both rows. The main text (bargaining.tex l.56) says that ninety-two "preserve the same original author's newly complete group", and the appendix (l.39) calls 92/111 the "retained-completion result" concerning the author's group. These are different predicates: retaining every requested deed implies the completion is preserved, but the converse does not hold. Either the two counts coincide and the text needs to say so, or one label is wrong. In addition, "Eighty-five improve the counterer's net cash" has an ambiguous denominator (111 or 88).
2. **Grok's redemption arithmetic may be misattributed (appendix l.112).** "Their arithmetic is not uniformly correct: G1 notes quote $198 … rather than the implemented $200 … $220 … rather than $221 … $110 … rather than $111." These quoted figures are the mathematically correct 10% redemption charges. The discrepancy comes from the engine's floating-point ceiling, which the paper discloses elsewhere. Unless the prompt displayed the exact implemented charge, this is an implementation overcharge and not a model arithmetic error. It is an unsupported negative statement about a participant.
3. **The G12 "note also contains arithmetic errors" claim (finance l.29) is unsupported in the quoted text.** The quoted note's figures ($350 from seven houses at $50; $207 = $250 − $43) are correct. If the error is in unquoted text, the paper must say where. Otherwise the sentence should be removed.
4. **The G7 hotel lock against the bundled-sale caveat.** Appendix C says that sale validation can accept a bundled operation using final evenness and net stock. A whole-group bundle (hotel plus eight houses down to 0/0/0) would increase bank stock and end even, and it would appear to pay $750 (bound $1,310). The main text explains why per-building selling is blocked but never says whether the d339 menu offered any building-sale action. If the engine menu offered none, the paper should say so directly. That is the reason the restricted search is valid there. If it did offer one, the lock claim is at risk. This must be verified from the original decision menu and the engine source.

## Material but probably non-blocking

5. The abstract reports "17, 18, 15 and 13 … 16, 17, 7 and 3" without naming the systems. A reader of the abstract alone cannot map these numbers to configurations.
6. "Construction gaps mix deferred financing, engine defaults and received actions conflicting …" (abstract). Only four of the twenty residual windows carry a stated deferral. The five Opus no-option windows have no note, and three valid ends and the no-option category itself are omitted. Consider "missing construction options, engine defaults, received-call conflicts and a few stated holds".
7. In G20, "Sol had already stated its own reason not to fund Grok" has no source decision and no quote.
8. At G3 d176, "Opus … states a preference for reserves" is made under action-only recovery, which removes the private note. The channel (provider explanation? public message?) is not named, which matters given the paper's channel discipline.
9. Appendix l.92, "Fifty-seven developed-color rent elimination triggers concern events.", is an orphan statistic that the main text never uses.
10. Setup l.38, "the later private-memory window contains either no note or only synthetic fallback notes", is unclear. It needs a definition (the ten-note memory shown in subsequent prompts?).
11. G1 d426 "consistently declines": consistently across what? Probably content, call and note. Say so.
12. "Recorded completion tokens average 128 per decision for Sol and 4,041 for Grok" gives only two of four configurations.
13. Related work: the claim that FinBoardBench's bankruptcy treatment sells buildings to the bank should carry the App. C.3 pinpoint, as §3.2 and App. E already do.
14. The G15 green statement "Greens arrive only through the terminal estate" is loose, because one green blocker reached Gemini at the first elimination. Should be "The green group completes only through the terminal estate."
15. The G13 probability correction ("the roll is 4/36") is right for a single roll summing to nine. A doubles chain adds a little probability, so "a single roll of nine is 4/36" is more precise.
16. The appendix's quote-verification sentence ("Original checks verify supplementary G2/G11/G15/G16 quote fields") understates what was checked if all 35 used cards were rechecked.

## Optional / style

- The G7 bluff as a main incident: G2 already contains an unquoted public-final/private-ceiling contrast (Opus $450 final, $475 ceiling). G7's marginal value is its settled outcome. I lean toward keeping it but trimming. Not blocking.
- Hedging density is high in places ("These are conditional descriptions, not an identified effect" appears in many variants). Some can be cut without loss.
- "Much of this pooled contrast changes when negotiation stage is separated" is vague. "About half the pooled contrast remains within each stage (13 vs 28 points)" is concrete.
- Figure 2: the G7 segment overlaps other debt-750 points, and the caption's "Squares mark four automatic eliminations" has five square glyphs because G7 has two endpoints.

## Verification plan (existing records only)

Retained ledgers and check outputs in `integrated/data`, `integrated/qa`, and the canonical saved games for: the counter predicates; the G1/G16 redemption prompts (whether the charge was displayed); the full G12 d249 note; the G7 d339 menu and engine sale validation source; the G20 Sol statement; the G3 d176 channel; the seed-block/game consistency counts; the price cuts; the elimination/estate counts.
