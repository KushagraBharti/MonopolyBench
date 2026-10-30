# Fable step-15 record: corrections, original checks, challenges and proposals (2026-10-29)

Scope: my coauthor contribution for the first complete manuscript draft. Files in this folder: `setup_related.tex` (environment, instructions, participants, artifacts; related work; limitations and release status), `evidence_map.md`, `abstract_title_proposal.tex`, this record, and `build/` (standalone compile of my prose against the root preamble and root `references.bib`; last build clean, no overfull lines, no undefined citations). No file outside this folder was written. No game, provider call, prompt, engine or canonical artifact was touched. The locked outline and its LaTeX body are unchanged.

## 1. Corrections accepted into my own prose

| Raised by | Issue | Resolution in `setup_related.tex` | Check |
|---|---|---|---|
| Opus (step-15 critique §3.2) | I wrote that Opus's initial response was refused in 1,605 of 1,696 decisions | 1,605 refused attempts over 1,605 decisions; 1,604 first-attempt refusals; one second-attempt refusal at G2 d129 after an invalid first attempt | `phase1_results.json` (`refused_attempts` 1605, `standard -> same_model_without_private_thought` 1604); `opus_response_audit.json` (`standard:illogical -> standard:refused`: 1) |
| Opus (on root's setup; applies to mine) | The action-only recovery prompt removes the private-honesty sentence, not only the note field | Stated in §2.2 prose and in the contracts-table cell; most Opus decisions were resolved without the private-honesty clause | `prompting.py` lines 1226–1245; `docs/model_response_policy.md` step 2 |
| Root (integration note) | "No houses in the bank" wording implied no further development at all | Now: the immediate house purchase is blocked and a hotel cannot be sold back; own sales and hotel conversions elsewhere can return houses | `engine.py` `_buildable_space_indices`, `_sellable_building_space_indices`; Sol's G12 d312 restructuring route |
| Root | "Redemption costs +10% rounded up" invites a mathematical-ceiling reading | Now discloses the floating-point `ceil(1.1 × principal)` implementation and the $111-for-$100 effect; rules table row updated | My check over all 16 board principals (below) |
| Root | A false private note is not automatically a breach; the request concerns honest reasoning, not factual accuracy; it applies under the standard condition only | §2.2 rewritten accordingly; contracts-table cell rewritten | `SYSTEM_PROMPT_V1`: "private thoughts should reflect true reasoning" |
| Root | Grok's cost is also a lower bound (3 uncosted attempts) | Table shows ≥55.60; caption names both gaps | `opus/exhibits/cost_usage.csv` `attempts_missing_cost` |
| Sol (integration message) | G15 Gemini's first completed group is orange (e711, d094 turn 47; first build e718 d095; $3,250 developed orange rent); green only terminal (e1994–1995) | Not used in my sections; recorded so the superseded "natural green" wording never returns | Sol's fresh event reduction, `coauthors/sol/verification.json` `g15_winner_group_sequence` |
| Sol | G19 Gemini cumulative own dark-blue spend is $2,000; $1,200 is one later step | Not used in my sections; recorded | Sol's reduction |
| Sol | Winner spending units 58/34/30, not 57/33 | My text uses only the 58/34/30 convention where relevant | Sol's reduction; Astra R15 |
| Self (compile) | Conditions table overflowed by 46 pt | Converted to a `tabular` with 3 pt column separation and shorter headers; compile clean | `build/fable_standalone.log` |
| Self (wording) | "median-free latency" and an over-specific Vending-Bench 2 model claim | "mean latency per decision"; VB2 sentence names only models verified on the page (Gemini 4 Argon, Grok 4.7) | My phase-3 page read |

## 2. Original checks performed in this step (not inherited from phase 2/3)

- **Engine rules re-read from source on 2026-10-29**: starting cash and stock constants; jail fine and house limit; auction order and the `NO_BIDS` outcome; `max_trade_exchanges` 20 and `TRADE_EXPIRED`; the developed-group trade prohibition; trade interest `ceil(0.1 × mortgage)`; liquidation menu contents (no `propose_trade`); automatic elimination when neither a mortgageable deed nor a sellable building remains, and on jail-fine insolvency; creditor inheritance with mortgage flags, cash and jail cards; bank bankruptcy returning buildings; no management phase when the player remains in jail; building sale at half cost; hotel sale requiring four bank houses. Line anchors are in `evidence_map.md`.
- **Floating-point rounding**: for every board price, the engine's `int(math.ceil(m * 1.1))` redemption exceeds the exact ceiling of 11m/10 by one dollar for m ∈ {50, 90, 100, 110, 200} (board prices 100, 180, 200, 220, 400). Trade interest `int(math.ceil(m * 0.1))` equals the exact value for all 16 principals. The manuscript should describe redemption as implemented, not as "110%".
- **Sampling parameters**: no `temperature`, `top_p` or `max_tokens` is set anywhere in `player_config.py` or `openrouter_client.py`; the roster records `top_p: null`. Provider defaults applied. The paper should not claim temperature control.
- **Model names visible to agents**: the delivered game-state payload's `name` field is the configured model name (`seat_assignment.json` `player_name`, e.g. `gpt-6.1-sol`). Each agent could identify its opponents' model families. This belongs in setup and in limitations; it is in both of my sections and in neither root section I read.
- **Source diff between run commits** re-run: 18 files, 281 insertions, 210 deletions; within engine/arena/contracts only `campaign_setup.py`, `execution_policy.py`, `supervisor.py`, one test and `cloud.schema.json`.
- **Standalone compile** of my prose with the root preamble and bibliography (LuaLaTeX, TeX Live 2026): clean.

## 3. Challenges to Sol's methods and economics prose (`sections/economic_methods.tex`, `sections/economic_results.tex`)

Sol's reductions and bounds are correct where I could check them (acquisition routes, completion routes, 60/43/10, 103 units and totals, 58/34/30, the four-row financing table, G14's $215 mortgage arithmetic, 19/20 terminal creditor plus 35/40 nonterminal = 54/60). The challenges below concern interpretation, denominators and readability.

1. **The 44 is one fact, not two.** Sol reports that in 44 of 113 settlements the final offer's author differs from the thread initiator. Root's validation reports that the trade-history formatter reverses giving directions in 44 of 113 accepted-trade summaries because it assumes the initiator authored the current terms. These are the same 44 trades. State that once, explicitly, so readers do not count a design fact and a defect as independent findings, and so the role distinction is seen to matter for what agents were shown.
2. **"Recipient bargaining" from acceptances alone.** "Gemini's low initiation coexists with twenty-six applied acceptances" is read as evidence of recipient bargaining. Acceptance is not bargaining; counters authored by Gemini are. Either add Gemini's counter count from `negotiation_units.json` or soften to "recipient participation".
3. **Eligible turns versus eligible decisions.** The cohort denominators are own turns (766 for Gemini); the G15 sentence uses "fifty-three eligible management decisions". Both are legitimate, but the switch inside one subsection will confuse; say "management decisions" and, if available, give the turn count too.
4. **G20 New York paragraph.** Name the agent (Sol, seat 3, d235) and quote the public claim being tested, as Opus proposed; otherwise "the earlier assertion of no reachable development is too strong" has no visible referent. Give the branch file for the $41/$91/$64 figures.
5. **Universal statement needing a pointer.** "No spending unit in this cohort has a second complete-ownership interval at the observed decision or terminal boundaries" is a corpus-wide negative. Cite the check (Sol's `verify_economic_claims.py` or the phase-2 corpus audit) or qualify it.
6. **Through-line.** The economics section reads as a sequence of correctly bounded audits. It should open with the sustained story that the audits then support: position was built by the first developed set that opponents had to cross, financed early, and then by inheritance (creditor = eventual winner in 54/60 eliminations); capability showed most clearly in converting access into an executable sequence, whether a build, a liquidation or a trade; and two winners did this without any settled trade. Sol's own G14/G15/G19 paragraphs are the material for that opening. Opus made the same point independently; I endorse it.
7. **Outcomes in plain sight.** The win split (Sol 8, Gemini 7, Opus 3, Grok 2), the seat pattern (seats 1–2 win 14/20), turn lengths (75–386) and the outcome grid (F2) should appear once in the design section with the one sentence on why they are not a ranking. I placed a compact version at the end of my §2.3; root may move it to §3.1 but should not drop it.
8. **Upper-bound equation.** Equation `eq:sol-upper` should say that `V_all clear deed mortgages` counts each deed once (already-mortgaged deeds contribute nothing) and that railroads and utilities are mortgageable. One clause suffices.

## 4. Challenges to root's setup, methods and validation sections

1. **`setup.tex`, response policies.** "Sol and Gemini use the ordinary corrective retry after invalid output. Grok uses required tool selection." reads as if Grok lacks the corrective retry. Grok's attempt chains include `standard:illogical -> standard:valid` (14) and `standard:malformed -> standard:valid` (21). Say: all four have the ordinary corrective retry; Grok additionally uses required tool choice; Opus additionally has the refusal path.
2. **`setup.tex`, contract paragraph.** Add that the action-only prompt removes the private-honesty sentence (Opus's point) and that the request concerns honest reasoning rather than factual accuracy (root's own point to me). My §2.2 now carries both; take it.
3. **`setup.tex`, configuration table.** Lacks tool choice, cost, tokens and latency, which the user asked to have concretely right. My Table `tab:conditions` has them with lower bounds marked; recommend it replace or extend `tab:configurations`.
4. **`setup.tex` omissions that my §2.1–2.3 supply**: standard board names (the comparison with AgentMonopoly's renamed streets depends on it); auction mechanics and the no-bid outcome; the no-trade liquidation menu; automatic eliminations (four in cohort) and the jail-fine route; finite stock 32/12 with the hotel-downgrade rule stated as an immediate block; visible model names; sampling defaults; two source commits and fingerprints; the 130 micro scenarios and six reference policies as unused affordances.
5. **`methods.tex`.** Consistent with the catalog arithmetic (441 + 152 + 21 = 614; 240 = 20 × 4 × 3). The five adjudication questions duplicate Opus's evidence-chain table; keep one. I prefer root's prose plus Opus's table placed in methods.
6. **`validation.tex`.** New counts (10,235 snapshots; 27,956 player observations = 6,989 × 4; $431 interest over 30 settlements) need pointers in root's source map. The 149-omission decomposition there (94 building merge, 55 bankruptcy cash event) is finer than my "events the timeline does not summarize"; adopt root's wording in my §2.2 if the two sections are merged. My §2.4 replay paragraph overlaps root's §validation; keep root's counts and reduce mine to the five-operation distinction plus a cross-reference.

## 5. Challenges to Opus's social section (`sections/social_results.tex`, bounded)

The cases are original-checked and the labels are correctly separated. Two challenges and one request.

1. **The sustained story is scattered.** The user's instruction is that a figure or a conduct label must not stand in for the sustained economic/social story. Game 18 already contains the whole arc in Opus's text, in four separate places: d83 (Grok's received acceptance hands Opus its first monopoly), d335–336 (denial purchase of Illinois), d360 (Grok's bankruptcy passes Illinois and the dark blues to Sol, completing the reds the purchase was meant to block), d419–442 (standing offer invoked and withdrawn), and Opus's eventual win. One "Game 18 as a whole" paragraph or a single timeline panel would join economics and conduct across one trajectory. Game 20 offers a second arc (d1 private-note disclosure; d96 anti-leader appeal; the Illinois sale; refusals to fund; the d327–336 $1,400 survival; Gemini's win with nineteen inherited deeds).
2. **"Frequent and explicit" refusals.** "Refusals to fund a leader are frequent" is a prevalence word in a section that otherwise declines prevalence claims; the review did not code every trade response for leader-funding reasons (Opus says so two paragraphs later). "Recur in several games" is the supportable phrasing.
3. **Request.** The 40-character overlap scan (7 overlaps among 6,989) is a new corpus-wide analysis; its script and output should be named in Opus's evidence map and the scan rule stated (applied private note versus same-decision public message, case-sensitive or not).

I agree with Opus's own list of accepted corrections, with the G6 narrowing, and with the preference for two economic numbers in the abstract.

## 6. Main-narrative and reader-oriented proposals

1. **One method, two halves.** The distinctive move of the paper is that one exact-prefix legal-sequence procedure adjudicates economic claims (61 reorderable plans; 3/56/1 eliminations; the G7 lock) and social claims (G13's $130 route; G18's changed state) and corrects the analysts' own labels (G6 C021, G14 C014, G20 C024, the $1,233 versus $1,393 G16 bound). The introduction and conclusion should say this in one sentence each; otherwise the economic and social halves read as two papers. Opus proposed the same.
2. **Order.** Economics, then social conduct, then validation and the prospective design, as in the locked outline. Related work can be a short paragraph in the introduction plus my §7 with the comparison table.
3. **Define units once.** "Configured agent" for the evaluated unit, "participant" for the roster entry, seats 1–4 one-based, "game dollars" for `$` except in the cost table. My sections follow this; root should check the others.
4. **Visible model identities.** The G13 pitch itself names a model ("gpt inherits the yellows"). That the agents knew which models they faced is part of the setup and a limitation; it is now in both of my sections.
5. **Rules appendix.** Root's concise rules appendix should carry the floating-point redemption note and the automatic-elimination triggers verbatim from my §2.1, since both change small arithmetic in case studies.
6. **F5 caption.** Do not set $93,000 beside $103,450 in a way that invites a ratio; Opus and Sol already say this. I add: state in the caption that 57 of 60 eliminations arose from developed-color rent, so unpaid lethal demands are the largest consequence that paid-rent receipts cannot show.

## 7. Citation and metadata flags (root `references.bib`, identical to the phase-3 file)

- `ren2025mask`: no venue verified; cite as preprint.
- `empty_commitments_v2`, `commitment_standing`: no venue; author lists taken from arXiv; cite as preprints with versions.
- `andon2026arena`, `andon2026vb2`: live author pages, not peer reviewed; my prose says so and cites them for context only.
- `metr2026page`: page states it is no longer actively updated; `kwa2025timehorizons`: use the v4 title with "Software".
- `wu2026agentmonopoly`: 140 games by Table 3 versus 120 by README; both kept visible in my table and prose.
- `zhang2026dece`: the bib title reads "Diverse Eurogame" (singular); verify against the arXiv page before camera-ready. I did not edit the bibliography.
- `muller2026cattletrade`, `shi2026cheaptalk`, `shi2026agentslie`: workshop papers; my prose calls the two promise papers "workshop papers".
- Not in the root bibliography and therefore not cited by me: Baker et al. 2025 (CoT monitoring), Miller 2024 (error bars), Zhu et al. 2025 (agentic benchmark checklist), Kapoor et al. 2024 ("AI Agents That Matter"), Moloch's Bargain, Among Us, GovSim. Add only with verified entries.
- All literature facts in my related-work section are limited to the sections inspected in phase 3 and recorded in `reference_registry.json`; abstract-level sources receive abstract-level claims.

## 8. Release-status wording (proposed for the manuscript)

"At the time of writing, the twenty saved games with their events, actions, decisions, per-attempt prompts and responses, per-turn state and usage records, together with the audit scripts and their outputs, reside in the project repository under its saved-games and research directories; the original per-game archives are held outside the repository. A public release package with a hash manifest, a clean-environment reproduction check and a privacy review has not yet been produced. We will state the final release location, commit identifier and manifest hash before publication." Do not write "publicly available" or "released" anywhere in the draft until steps 17–18 finish.

## 9. Preserved disagreements

1. **Pre-manuscript codings.** I still prefer proposition coding of all false public claims, a stock-relaxed immediate-expansion count and leader-funding-denial coding before submission. Astra and Sol treat them as optional for a case-based paper. The draft is written so that it stands without them; the "frequent" wording in §5 point 2 is the kind of sentence that would become supportable with the third coding.
2. **Cost table placement.** Opus wanted it in the design section; I previously preferred an appendix. The user's instruction to get settings concretely right changed my view: a compact row per agent belongs in setup (my `tab:conditions`), with the full usage breakdown in an appendix.
3. **Related work as a section with a table.** Sol's and Opus's drafts distribute comparisons through the text. I provide both forms; I recommend keeping the table because reviewers will look for it and because "n.r." cells are where absence claims would otherwise creep in.
4. **Seat and win summary in setup.** I put one paragraph at the end of §2.3; root may move it to the design section but should keep the explicit numbers.

## 10. Title and abstract

See `abstract_title_proposal.tex`. The title keeps the locked outline's emphasis and adds "auditable" without a firstness claim. The abstract uses one financing result (3/56/1), the three-path non-building result and the G13-with-prior-motive social contrast, and ends with the boundary sentence. Sol's and Opus's abstracts are both accurate; the three differ mainly in how many economic numbers they carry (Sol one, Opus two, mine one plus the execution-path result).
