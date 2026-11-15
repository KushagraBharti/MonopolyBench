# Handoff

Fable 5.2, final whole-paper review of the integrated candidate, 15 November 2026. Complete. Nothing is pending on my side.

## Result

The paper can be released after one factual sentence is corrected and six small changes are made. No count, table or proof is wrong. Both pins match before and after.

## Read in this order

1. `review.md` for the judgment.
2. `findings.json` for exact passages and evidence: one factual, seven material, six optional.
3. `replacement_prose.tex` (or the PDF) for paste-ready text, R1 to R11.
4. `verification.md` for what I checked and what I inherited.
5. `initial_position.md` for my view before I saw the decision log.

## The seven changes

| # | Change | Where | Replacement |
|---|---|---|---|
| 1 | G13: the buyer's counter cites solvency. Its estate weighing comes after the reply | `main.tex:149` | R1 |
| 2 | G12 d249: show that two channels first count only the listed sale target | `main.tex:110`, `final_supplement.tex:104` | R2 |
| 3 | Give the denominator for the six above-bound starts | `main.tex:112` | R3 |
| 4 | 28 of 30: say "pattern", state that mortgage is listed first and a sale was offered in 29 | `main.tex:74` | R4 |
| 5 | Add the listed-total observation and the 37-episode result | `main.tex:103`, `main.tex:107`, new supplement paragraphs after `final_supplement.tex:83` | R5 |
| 6 | Arena study: model judges and a 50-message single-annotator check | `main.tex:162` | R6 |
| 7 | Package: unused sections, set ordering in `refresh_records.py`, README, stale QA record, commit name | see R-list at the end of `replacement_prose.tex` | none |

The main-text additions total about 230 words. The main text ends on page 7.

## Where I disagree with the integration

- The 37-episode result was declined because 37 is not every entry with unlisted collateral. The population has an exact definition (U0 below the debt, M* above M0), and I read all 21 unpayable members. It is the broadest evidence the paper has on its own first question.
- G12 d249 should not be called "not an omitted-resource case."
- The main text needs one sentence with the stop-decision counts.

I agree with the rest of the log, including the three corrections to my own draft.

## What the integrator should check before applying R5

- The 16, 2 and 3 split of the 21 rests on my reading of the contexts in `checks/totals_checks.json`. Another author should read the three listed-only cases (Sol G3 d426, Opus G5 d309, Grok G8 d280) and the two itemized ones (Opus G2 d215, Sol G10 d188).
- If R5 goes in, `check_stated_totals.py` could assert the 27 and 21 split so the build covers it.
- R2 adds no quotation macro. If the integrator prefers to quote the opening of the G12 d249 note, it needs a manifest entry.

## Decisions for the owner

- Commit and tag the package, then name the commit in Appendix I.
- Decide whether a person will read the sixteen selected fields and the 21 locked contexts. No assistant can supply that.

## Not done

- No evaluation of any kind, no subagent, no commit or push, no memory write.
- No pinned file edited. No other reviewer's final review read.
- `verify_document.py` not run (it needs PyMuPDF). Text compared with Ghostscript.
