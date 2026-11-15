# Opus xhigh: whole-paper review of the integrated manuscript

11 November 2026. Target: `integrated/manuscript.pdf` (33 pages, SHA-256 `8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5`), `integrated/manuscript.tex` and all `integrated/sections/*.tex`. All 38 pinned hashes pass. My initial position (`initial_position.md`) was recorded before I read `final_review/astra/root_review.md` or `integration_decisions.md`. Findings are in `findings.json`, prose fixes in `replacement_prose.tex`, and checks in `verification.md`.

Conflict disclosure: I am Claude Opus 5.5, the same model identifier as the evaluated Opus configuration. I checked every Opus-related statement against ledgers. I have not softened any of them, and my one proposed abstract change about Opus (OPF-04) is more specific about its defaults, not less.

## Verdict

The integrated paper is a sound observational account and does not need another full rewrite. Its organizing claim holds up under re-tabulation. Completing a group, financing it, executing a build, collecting rent, meeting a debt and receiving an estate are distinct events, and the corpus can follow each one. The headline numbers I re-derived are all correct: the stage-split offer table, the counter comparison, the price cuts, the first-window decomposition, the estate concentration and the elimination ledger. Response and information conditions now precede results and are carried into the populations where they matter.

I found one blocking error and four material issues. The blocking error is an appendix sentence that attributes an engine overcharge to Grok as an arithmetic error (OPF-01). The material issues are:
- the paper omits that management, trade and liquidation prompts carry no prices, rents, mortgage values or redemption charges (OPF-02);
- the G7 hotel lock is described without saying that it comes from the engine's sale menu rather than its plan validator, so the appendix's bundled-sale caveat appears to contradict it (OPF-03);
- the abstract's lead numbers are unlabeled, and its gap sentence over-describes "deferred financing" (OPF-04);
- an unquantified "often" stands where a precise 57/60 count is available, and that count currently sits as an orphan sentence in the appendix (OPF-05).

Each fix is one to four sentences and needs no new evaluation. I therefore disagree with root's statement that "No unresolved factual defect was found." OPF-01 is a factual defect, and it entered during integration.

## What the paper now does well

- **Conversion is the right lead.** The 17/18/15/13 → 16/17/7/3 contrast is the strongest finding in the corpus, and the first-window decomposition (9 no-option, 4 defaults, 4 conflicts, 3 valid ends; 42 entry-buildable → 34 built) reproduces exactly from `first_management_windows.json`.
- **The bargaining section no longer overreaches.** The opening/later split cuts the pooled 28-point rejection contrast to about 13 points within each stage. The Opus exception is visible. The same-predicate counter comparison (92/111 and 79/111 versus 87/110 and 81/110) is presented as neither a control nor an equivalence result. All of this reproduces, including 5/5 seed blocks and 17/19 games for the rejection contrast.
- **Estate concentration is stated in the right unit.** The nonterminal populations (35/40 eliminations, 202/227 deeds, first estate to the winner in 18 games, all three in 16, and G13's terminal estate to the bank) reproduce from the original event streams.
- **The finance section's local claims are well bounded.** The 56 bound negatives follow from arithmetic, three positives are inherited witnesses, and the static budgets for the nine no-option windows are explicitly not executed witnesses. The two-cash/five-mortgage/two-short split recomputes. Root's correction of my earlier B&O→Baltic mapping and developed-sibling collateral is right; I confirmed the G1 d298 menu, which excludes Atlantic and gives $205 of outside collateral.
- **Incidents are tied to populations.** The G13 and G18 chronologies are accurate against original events: next roll to Marvin; event 1911 is the $650 North Carolina auction purchase; $200 at B&O on turn 146; Short Line bankruptcy at turn 150 with the yellows to Sol; G18 assurances at d423/425/427/431 followed by the turn-188 collapse and withdrawal. The readings stop at what the records show.

## Blocking

**OPF-01: Grok's redemption figures are not arithmetic errors** (`appendix.tex:112`). The sentence says that "their arithmetic is not uniformly correct" because Grok quotes $198, $220 and $110 instead of $200, $221 and $111. Grok's figures are the exact ten-percent charges. The implemented ones come from `ceil(value*1.1)`, which overcharges by $1 on principals 50/90/100/110/200 (the paper documents this in Appendix C). No post-turn prompt in the corpus (0 of 4,081) carries a redemption charge or any price field, and the unmortgage tool description gives no cost. The sentence charges a participant with the paper's own implementation artifact. It traces to my OPR-24 and Fable's FX-C05, but OPR-24 called $220 "the standard-rule figure", not an error. The integration decisions record should be corrected too. The fix is in `replacement_prose.tex`.

## Major

**OPF-02: Missing information condition** (`setup.tex:44`). A census of all 6,989 initial prompts finds the following. Only purchase prompts (547) state the landed deed's price, house cost, rent and group, and auction prompts (854) state its group. Post-turn (4,081), trade-response (920), jail (249) and liquidation (338) prompts list space keys and menus with no economic parameters. Every agent calculation the paper evaluates therefore rests on recalled board values: G2's nine houses, G13's probability, G15's $600 layer, G19's colour error, the omitted collateral at G12/G17, and the redemption figures. Agents also cannot see implementation-specific charges. The paper says it places material information conditions before results, and this one belongs in §2.4.

**OPF-03: State why G7 is locked** (`finance_inheritance.tex:16`, `appendix.tex:135`). The original G7 d339 request offers only `mortgage_property` and `declare_bankruptcy`, and `sellable_building_space_keys` is empty. In the engine, the sale menu lists only highest-built deeds, and lists a hotel only when four bank houses remain. The sell-plan validator checks evenness and stock only after the whole plan, so it would accept a group-clearing bundle worth $650 that pays the $750 debt, if any sale action were offered. Appendix C already says that bundled sales can be valid and that G7 is a "mortgage-only state", but never connects the two. A careful reader will conclude that a bundled sale pays the debt. The classification is correct relative to the legal menu, and the text should say so. This is a source-reading inference about the validator; I executed nothing.

**OPF-04: Abstract lead and per-configuration residuals** (`manuscript.tex:13`, `development.tex:6`). "17, 18, 15 and 13 … 16, 17, 7 and 3" and "one participant" are unlabeled in the abstract. "Construction gaps mix deferred financing, engine defaults and received actions conflicting with accompanying text" fits only four of the twenty residuals for deferral. The retained per-configuration split is more informative and is never stated for Grok, the lowest converter:
- Grok's ten: four no-option windows with stated deferrals, four received-call conflicts and two stated holds.
- Opus's eight: five action-only no-option windows without notes, and three defaults.
- Sol's single residual is a default, and Gemini's is a valid end.

**OPF-05: Quantify "often"** (`finance_inheritance.tex:55`, `temporal_discussion.tex:23`, orphan at `appendix.tex:92`). From the original event streams, 57 of 60 eliminations, and 38 of the 40 nonterminal ones, follow a landing on the creditor's developed colour deed. This is the same 57 that appears without context in Appendix B. It is the paper's actual reason that estate concentration does not isolate inheritance's contribution, and it should be stated as a number.

## Minor (local precision; exact text in findings.json and replacement_prose.tex)

- OPF-06: G3 d176's reserve preference comes from action-only assistant content, not a note. Name the channel.
- OPF-07: "Sol had already stated its own reason" comes from Sol's private note at G20 d95. Opus's later offers explicitly pitch cash as house funding, and Grok rejects or counters them, which supports the no-cartel reading.
- OPF-08: "the later private-memory window" should become "ten-note private-memory field: empty in 1,108, only synthetic fallback in 286 (1,394 of 1,696)".
- OPF-09: The two counter predicates select the same 92 counters (0 records differ), but the text and Table 4 use different names. "Eighty-five" is out of the 88.
- OPF-10: The 5/36 belongs to the d250 opening appeal and note, which count Short Line as an eight. The self-contradiction is in the d252 provider text. The current "Its opening" is ambiguous.
- OPF-11: The G12 "arithmetic errors" are in unquoted text: "cannot cover", and five remaining houses where two would remain. Say so.
- OPF-12: Add the App. C.3 pinpoint for FinBoardBench's building liquidation.
- OPF-13: All three opening author-only acceptances are Grok's. The 34 concentrated reason records come from G1 and G15.
- OPF-18: The introduction lists seven of the eight incidents and omits G2.
- OPF-19: Name Sol at G20 d327–336 and Gemini at G16 d602.
- OPF-20: The green group *completes* only through the terminal estate; one green arrived earlier.
- OPF-21: The appendix understates the quote check. All 35 used cards and 37 spans were reloaded from 12 original files.

## Optional

- OPF-14 (G7): I withdraw my earlier request to demote G7. Eight incidents are not a defect. G7's justification is the contrast with G2's refused final offer, but that half is only paraphrased. The exact cards (`g2-d127-final`, `g2-d127-ceiling`, `g2-d128-keep`) already exist and were root-checked, so using them makes the contrast evidential. I test-compiled them under the integrated preamble.
- OPF-15 (hedging): The general-auditor disclaimer appears three times and the not-a-ranking disclaimer at least five. `bargaining.tex:52` is a paragraph of negatives that limitations already covers. Keep one of each; the paper reads more confidently without losing a caveat.
- OPF-16: Report token averages for all four configurations or give a range.
- OPF-17: Figure 2 shows five square glyphs because G7 has two. Adjust the caption.
- OPF-22: G2 does not illustrate "cash direction is not a premium". Say that it illustrates two of the three distinctions.

## Research-question coverage (Table 6)

The scope map is honest, and none of its "Not established" entries is overstated. Two adjustments follow from the findings above. Q8 (validity and generalization) should name the economic-parameter information condition (OPF-02) beside the response and history conditions. Q6 (economics and risk) is well served once OPF-03 makes clear that the hotel lock is a menu fact. Q2 (opponent modelling) and A (talk versus action) rely on selected Grok-heavy incidents; the limitations section says so (six of eight involve Grok). B is correctly "Not evaluated". C's seat/seed paragraph does not turn the seven shared purchase paths into a dice claim, which I agree with.

## Remaining weaknesses that are not editing defects

The scientific limits stand: a fixed confounded cohort, a provider refusal condition affecting 1,604 Opus decisions, Grok channel conflicts of unresolved origin, retrospective LLM-assisted selection and coding (Astra readers on a population dominated by Grok and Gemini refusals), no causal tactic evaluation, and no learning or transfer evidence. The paper states all of these. None can be fixed by rewriting, and none requires more hedging than the paper already has.

## Explicit positions and dissent

1. **Disagreement with root's closing claim.** OPF-01 is an unresolved factual defect introduced at integration. OPF-03 and OPF-05 are material clarity gaps where the appendix holds the answer but the main text does not use it.
2. **G7.** I no longer dissent on inclusion. My residual request (OPF-14) is optional.
3. **Agreement with root's rejections.** I agree that the seven shared early purchase paths do not show that dice decided seven games, and that the close counter proportions do not show equivalent repricing across deed types.
4. **My earlier errors.** I accept root's corrections to my prior review: the B&O→Baltic key mapping, counting collateral on deeds with developed siblings, the jail-card bundles in my price filter, and "twenty terminal winner creditors" (it is 19 plus G13 to the bank, which I recounted from events).
5. **Scope of my verification.** Inherited items remain inherited: the engine witnesses, full replays, memory reconstruction, the 139/15/5 conflict census, the semantic coding, the 614-entry catalog and the AgentMonopoly prompt-policy sentence. I re-derived the populations and focal records listed in `verification.md` and did not re-fetch FinBoardBench.
