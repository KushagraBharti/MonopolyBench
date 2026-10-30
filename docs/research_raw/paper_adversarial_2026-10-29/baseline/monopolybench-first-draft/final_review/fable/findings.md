# Fable final integration review: setup, references and PDF integrity (2026-10-29)

Bounded review of the integrated first manuscript as it stood at 15:35 (sources under `sections/`, `references.bib`, `build/manuscript.log`, `manuscript.pdf`, 33 pages). Focus: title/abstract, `setup.tex`, `related_work.tex`, `limitations.tex`, `appendix.tex` (with `cohort_table.tex`), the derived bibliography and the rendered PDF. Nothing outside `final_review/fable/` was written. No game, provider call, engine, prompt or canonical artifact was touched. No subagents, no messages to peers, no external fetches.

Revision note. Root reported source fixes during this review (G20 d235 wording, Gemini acceptance as participation, "recur in several reviewed games", 44-reversal linkage, Grok 139 comparability, four regenerated figures, old copied figures removed) with the PDF rebuild pending. Those edits are in `economic_results.tex`, `social_results.tex` and `validation.tex`, outside my focus, and I did not read their post-15:35 state. Finding F1 concerns a figure label and must be re-checked in the rebuilt PDF; every other finding is in a file root did not list as changed.

Abstract revision. `sections/abstract.tex` was rewritten on disk after my read. I checked the new text once: its counts (6,989; 8,679; 43 of 63; 42 and 8 as 3 + 3 + 2; 3 of 60 plus one hotel-locked; 20 replays; 6,989 memory windows) are the same figures verified below, and "one configuration operates almost entirely under a provider-refusal recovery condition" matches 1,604 of 1,696 Opus decisions. No finding below is affected.

Appendix revision. `sections/appendix.tex` was also edited on disk (15:46, 64 bytes added). I re-located the sentences cited in F2, F6 and F7: they are unchanged and still at lines 8, 34 and 80, as are the lines quoted in the passed checks (4, 30, 32).

Line numbers refer to the section files; page numbers refer to the 15:35 `manuscript.pdf`.

## Findings, most severe first

### F1 (high, figure rendering). Figure 4 G7 annotation loses its dollar signs

- Where: page 12, Figure 4 (`assets/financing.pdf`); source `tools/build_exhibits.py` line 125.
- Evidence: the label string is `"G7 Opus: hotel lock\n$440 accessible / $1,310 nominal"`. Matplotlib mathtext treats `$440 accessible / $` as a math span, so the PDF text layer reads `440accessible/1,310 nominal` and the render shows "accessible /" in italics with no dollar signs (confirmed by pymupdf text extraction and a 200 dpi crop, `render/p12_fig4_zoom.png`).
- Fix: escape as `\$440 accessible / \$1,310 nominal` (or set `text.parse_math` false for that call). Audit every annotation, tick-label and legend string in `build_exhibits.py` for unescaped `$`; I found no other instance in the four figures. Regenerate, update `figure_manifest.json` hashes, and re-inspect the annotation in the rebuilt PDF, because the regeneration root announced may or may not include this change.

### F2 (medium, disclosure). Coauthor stream names coincide with evaluated participants without saying so

- Where: `appendix.tex` line 80 ("Four model coauthor streams ... Astra, Sol, Opus and Fable"); Table 1 short labels "Sol" and "Opus" (`setup.tex` lines 20 and 22); byline "MonopolyBench project" (`manuscript.tex` line 4).
- Evidence: `coauthors/opus/initial_position.md` line 3 identifies the Opus coauthor stream as `claude-opus-5-5`, the same model family as the evaluated participant `anthropic/claude-opus-5.5`. The Sol stream shares its name with `openai/gpt-6.1-sol`; I did not find an explicit model identifier in `coauthors/sol/`, so that identity is inferred from the name only. The manuscript nowhere states that review streams run on the same models as two of the four evaluated agents, and a reader of Table 1 will read "Sol" and "Opus" in Appendix D as the players.
- Fix: add one sentence to Appendix D: "The review-stream names refer to coauthor models, not to the configured agents of Table 1; two streams run on the same model families as the evaluated participants Sol and Opus, and review assignments were not blinded to that overlap." Also decide before release whether the byline should name the four streams, since the request was for a coauthored manuscript and the title page currently carries only the project name.

### F3 (medium, missing comparator caveat). AgentMonopoly scope differences understated

- Where: `related_work.tex` line 8; page 25.
- Evidence: my phase-3 source read (`paper_phase3_2026-10-29/fable/literature.md` line 33, from the paper's section 3 and Appendix A.1) records a 150-step cap with a net-worth winner, eight open-weight 8B to 32B models at temperature zero, and renamed streets. The integrated paragraph keeps only the bankruptcy rule and the public/action prohibition. The termination difference matters because `setup.tex` line 34 and the validation section make "uncapped, ends only by bankruptcy" a feature of this cohort, and the model-scale difference matters for any reader tempted to compare behaviors.
- Fix: insert after the bankruptcy sentence: "Its games run eight open-weight 8B to 32B models at temperature zero and stop at 150 steps with a net-worth winner, whereas our four frontier configurations play to uncapped bankruptcy under provider-default sampling."

### F4 (medium-low, missing comparator caveat). Arena study validation and release status dropped

- Where: `related_work.tex` line 5; `appendix.tex` Table 9 (page 32).
- Evidence: `literature.md` line 27 (Arena paper section 6 and Appendix D) records single-author-labeler validation on 50 emails and an environment "maintained by Andon Labs and not publicly redistributed". The manuscript calls the study "the closest communication comparison" and borrows its coding distinctions in Table 9, but no longer states either limit. My step-15 draft carried both.
- Fix: add one clause to line 5: "its label validation is a single-author consistency check and its environment and logs are not redistributed, so the comparison is to its reported coding, not to re-runnable data."

### F5 (medium-low, accuracy). Response-policy sentence implies Opus lacks the corrective retry

- Where: `setup.tex` line 30 ("Sol, Gemini and Grok use the ordinary corrective retry after invalid output; Grok additionally uses required tool selection. Opus has a refusal-recovery path ...").
- Evidence: the G2 d129 chain (`appendix.tex` line 30; `economic_results.tex` line 40; `opus_response_audit.json` `standard:illogical -> standard:refused`) shows Opus receiving the ordinary corrective retry when its first attempt is invalid rather than refused. The following sentence explains the budget interaction correctly, but the first sentence's grouping excludes Opus.
- Fix: "All four configurations use the ordinary corrective retry after invalid output. Grok additionally uses required tool selection. Opus additionally has a refusal-recovery path that requests an action without a private note; this consumes the remaining retry opportunity ..."

### F6 (low, precision). Trade interest is also a floating-point ceiling

- Where: `appendix.tex` line 8 ("Trade interest uses an integer ceiling of ten percent of mortgage value. Redemption instead implements a floating-point ceiling ...").
- Evidence: `engine.py` line 1786 `int(math.ceil(self._mortgage_value(space) * 0.1))` and line 2490 `int(math.ceil(value * 1.1))` are the same construction. Rechecked today over all sixteen board principals (`contracts/data/board.json` prices): redemption exceeds the exact ceiling by one dollar for principals 50, 90, 100, 110 and 200 (engine 56, 100, 111, 122, 221 against exact 55, 99, 110, 121, 220); trade interest equals the exact value for every principal. The contrast is in outcome, not implementation.
- Fix: "Both charges are implemented as floating-point ceilings. For the sixteen board principals, the trade-interest ceiling of 0.1 times the mortgage value equals the exact ten percent, whereas the redemption ceiling of 1.1 times the principal charges one dollar more than the exact amount for five principals (\$50, \$90, \$100, \$110, \$200), for example \$111 for a \$100 principal."

### F7 (low, source naming). "Provider text" should be "readable provider reasoning"

- Where: `appendix.tex` line 34 ("Provider text is available on at least one attempt in 4,834 decisions").
- Evidence: the number is `decisions_with_readable_provider_reasoning_in_ledger` (`paper_phase1_2026-10-28/phase1_results.json` line 1949), computed in `astra/visibility_inventory.py` line 163 as "any attempt has a reasoning field marked readable". Assistant content is present far more widely than 4,834 decisions, so "provider text" overstates what the count excludes. The 4,016 opaque count (line 1946) is correctly described.
- Fix: "Readable provider reasoning is present on at least one attempt in 4,834 decisions; opaque reasoning fields occur in 4,016 decisions; ..."

### F8 (low, bibliography rendering). Entry [1] prints its URL twice and lowercases the title

- Where: page 27, reference [1]; `references.bib` entry `andon2026vb2` (lines 299 to 305).
- Evidence: `howpublished` contains `\url{...}` and a separate `url` field repeats the same address, so plainnat prints "Author evaluation page, https://andonlabs.com/evals/vending-bench-2, 2026. URL https://andonlabs.com/evals/vending-bench-2." The title `{Vending-Bench 2}` is single-braced, so plainnat renders "Vending-bench 2". The derived file is the right place to fix this; the frozen library stays untouched.
- Fix: `title = {{Vending-Bench 2}}` and drop the `url` field (or the `\url` inside `howpublished`). Entry [21] `agentmonopoly2026repo` has the same two-URL shape but the addresses differ (repository versus pinned commit), which is informative; keep it.

### F9 (low, unverified). DECE title singular "Eurogame"

- Where: `references.bib` line 41; page 29, reference [30].
- Evidence: carried over from the frozen library; flagged in my step-15 record (`coauthors/fable/critique_and_corrections.md` section 7) and still not checked against the arXiv page. Root is checking references, so I did not fetch.
- Fix: confirm the arXiv v1 title before camera-ready; change only the derived `references.bib`.

### F10 (low, layout). Table 4 hyphenates "re-mains" inside the narrow result column

- Where: `economic_results.tex` line 83; page 13 (`render/p13_tab4_zoom.png`).
- Fix: widen the last column to `p{0.38\linewidth}` or shorten the cell to "Sales and two mortgages pay; \$155 left."

### F11 (low, style). Mixed numeral styles in one rules sentence

- Where: `setup.tex` line 8 ("32 houses and twelve hotels").
- Fix: "32 houses and 12 hotels" (numerals, since 32 cannot be spelled comfortably), consistent with the appendix table.

### F12 (low, unsupported sentence). "Does not equalize compute" has no number behind it

- Where: `setup.tex` line 30; Table 1.
- Evidence: the retained `paper_phase3_2026-10-29/opus/exhibits/cost_usage.csv` gives completion tokens per decision 128 / 368 / 410 / 4,041 and mean latency 4.8 / 8.2 / 7.1 / 65.0 s for Sol / Gemini / Opus / Grok. The manuscript states the conclusion without them.
- Fix: add two columns to Table 1 (completion tokens per decision; mean latency, s) with a caption note that completion tokens include provider-reported reasoning tokens, or one sentence giving the two ranges.

### F13 (low, clarity). "Same named models" in limitations

- Where: `limitations.tex` line 5.
- Fix: "Each agent's opponents were the same three models throughout, and their configured names were visible in the delivered state."

## Checks that passed

Title and abstract. 6,989 decisions and 8,679 attempts (`phase1_results.json` visibility totals); 43 of 63 first-window builds and 42 entry-buildable with 34 built (`data/t03_trade_groups.json` sums); the eight non-builds split 3 defaults, 3 received conflicts, 2 stated holds (`data/t09_entry_nonbuild_records.json`); 3 payable, 56 insolvent, 1 hotel-locked of 60 eliminations and 56 declared plus 4 automatic (`data/t06_eliminations.json`); 20 replays and 6,989 memory windows (phase-1 sandbox checks, cited in my evidence map). Figures 2 and 4 legends and panel counts agree with these exports (16/17, 17/18, 7/15, 3/13; 45 plus 58 units; 56 circles, 4 squares).

Setup rules against the frozen engine. Start cash 1,500 and 32/12 stock (`models.py` lines 7 to 9); \$200 for Go; income and luxury taxes 200 and 100 (`board.json` `tax_amounts`); jail allows roll attempts while `jail_turns < 3` and only the fine afterwards, with automatic bankruptcy when the fine is unaffordable (`engine.py` lines 564 to 565, 1344 to 1353); deeds in a group with buildings cannot be mortgaged or traded (lines 1773, 2501); hotel sale needs four bank houses (line 2568); liquidation menu has no trade; four automatic eliminations follow a final `mortgage_property` action (t06); no turn cap, bankruptcy-only endings, turns 75 to 386; commits 42f85183 and d6808534 with the second fingerprint 9a15ddc8 in the 8-game index; the standard prompt wording and the refusal-retry bundle's removal of the private-note field and the honesty clause (`player_config.py` lines 11 to 41; `prompting.py` lines 1225 to 1245).

Configurations and costs. Table 1 identifiers, decisions and attempts match the roster and `cost_usage.csv`; recorded charges 18.72 + 18.59 + 48.80 + 55.60 = 141.71 USD with 1,600 Opus and 3 Grok uncosted attempts; `top_p: null` and no temperature in the roster; 1,605 refusals over 1,605 decisions, 1,604 first-attempt chains, one second-attempt refusal at G2 d129; 66 defaults equal the Table 3 default column (61 + 4 + 1 + 0).

Cohort table. 20/20 rows match `data/t01_cohort.json`; G13 to G20 match the 8-game index on seed, turns, winner and SHA; the G1 to G12 turns and SHA check against the 12-game index is recorded in `verification_log.md`. Winner tally 8/7/3/2 and seat tally 7/7/3/3 match Figure 1 and the economic section.

Related work against my phase-3 notes. Vending-Bench 2 page (simulated year, note-taking and reminder tools, adversarial suppliers); Arena study (20 runs, 2,583 emails, promise follow-through); AgentMonopoly (persona control, mixed-size setting, 140 versus 120 games, cash-negative elimination without liquidation, prohibition on public/action contradiction); FinBoardBench (three games, liquidity summary, judge-rated trades, buildings sold at bankruptcy); DECE (matched harness studies, persisted state, legal interfaces, replay, no dialogue); Cattle Trade (heuristic baselines). Table 9 cells agree with Opus's normative-contract ledger as I checked it in phase 3.

Bibliography. All 32 cited keys resolve; `andon2026arena` and `metr2026page` are unused and correctly absent from the rendered list. `references_source.bib` is byte-identical to the frozen phase-3 library (sha256 384444de...). `references.bib` differs from it only by removal of the 34 `note` fields; the 28 `url` lines are re-emitted unchanged and no other field is altered. Kwa et al. carries the v4 "Software" title. Final LuaLaTeX pass: zero warnings, no undefined references or citations, no overfull or underfull boxes; no "??" in the text layer; PDF title and author metadata set; bookmarks present for all sections.

PDF pages. All 33 pages inspected on contact sheets. Tables 1 to 10 fit the text width, including the two longtables with repeated headers; equations, figure placement and cross-reference links render correctly; game-dollar amounts use "\$" and the one real-world amount is labelled USD.

## Not verified

- The Sol coauthor stream's model identifier (F2 relies on the name match only).
- The DECE arXiv title (F9).
- Root's post-15:35 edits and the rebuilt PDF, including whether the regenerated `financing.pdf` still shows the F1 defect.
- Economic and social section numbers beyond their consistency with the abstract, setup and appendix; phase-2 semantic judgments were not re-run.
- Full-prompt reconstruction beyond memory, and anything requiring new games or provider calls.
