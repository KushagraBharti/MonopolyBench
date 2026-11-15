# Additional referee feedback supplied by the user

Received 11 November 2026. The following is the supplied review, preserved as feedback rather than independently verified findings. Its scores, venue predictions, external-source claims and proposed experiments are the reviewer's assertions. See `assessment.md` for the team's disposition. The manuscript is not changed by archiving this review.

---

I'll read the manuscript end to end first, then benchmark it against the published literature and write a referee-style review.

**Verdict: reject at NeurIPS, ICML, ICLR and AAAI. Overall 3/10 (a 2 on a NeurIPS-style six-point scale), reviewer confidence 4/5.** The bookkeeping is excellent. The science on top of it is not a paper yet: 20 games, one of four arms broken by your own prompt, no statistics, no baselines, and two of three headline results restate Monopoly's rules.

Dimension scores (1 to 4): Quality 2, Clarity 2, Significance 1, Originality 2.

| Venue | Decision as written |
|---|---|
| NeurIPS (main or E&D), ICML, ICLR | Reject |
| AAAI, IJCAI, AAMAS | Reject |
| IEEE Transactions on Games, IEEE CoG | Major revision; your most receptive home |
| Workshop | Accept after cutting to 8 pages |

I read all 33 pages, recomputed every table, checked all 15 references, then cloned your public repo and scanned the 8,679 saved responses and raw event logs. arXiv rate-limited the full texts of AgentMonopoly and DECE, so those comparisons use their abstracts, and I read about three quarters of the Li et al. PDF.

## What holds up

- **The accounting reproduces.** I rebuilt the 526 threads (240/136/132/18 by proposer) and the 32/138/356 opening outcomes from raw events. Every table sum checks, and I found no arithmetic errors in roughly 150 numbers.
- **The references and models are real.** All 15 references exist, and the four model IDs are live OpenRouter listings.
- **The infrastructure is the asset.** Deterministic replay and the full artifact trail are better than anything in the comparison set below.

## Fatal problems

1. **The Opus arm is an artifact of your prompt, and the paper misdescribes it.**
   - All 1,605 refused Opus responses carry the same provider message: blocked for "reverse engineering or duplicating model outputs".
   - Anthropic documents a `reasoning_extraction` refusal for prompts that make the model write its internal reasoning into the reply. Your system prompt requires a `private_thought` field on every tool call and says to "reason honestly" there.
   - The manuscript never says this and calls the cause unidentified, so readers will assume Claude refused to deceive.
   - It is two regimes, not one: refusal rates are 76%, 67%, 57% and 73% in G1 to G4, then 100% in G5 to G20.
   - The switch is by wall clock, not your commit boundary. In G1 to G4 the last non-refused first attempt lands between 16:14 and 16:38 UTC on Oct 25, while those games ran until 16:38 to 18:09.
   - Net effect: Opus played 16 of 20 games with no notes, no memory and one attempt. Its 7-of-15 build rate, its 61 build defaults (all executable once reordered, by your own check) and its 240 thread openings are harness outcomes.
   - 88 of those 240 openings re-pitch a deed bundle Opus had already offered the same player that game.

2. **"Medium reasoning" is not one condition.**
   - Per-response reasoning tokens in your logs: Sol averages 38 and returns zero on 65% of calls; Gemini 254; Opus 259; Grok 3,589.
   - That is a 94x spread, with one 69,595-token Grok response and no `max_tokens` set.
   - The model that thinks least wins most. That is either your most interesting finding or proof the outcomes are dice, and you don't test which.

3. **Grok's call/text mismatch contaminates the negotiation corpus.** By your numbers, 64 of 526 threads (12%) and 17 of 113 settlements (15%) start from a Grok tool call that Grok's own text says it wasn't making. That is 47% of Grok's threads, and six of your eight showcase transcripts involve Grok.

4. **Twenty games can't carry claims about systems.**
   - Wins are 8/7/3/2 by model (exact multinomial p ≈ 0.18) and 7/7/3/3 by seat, so seat predicts the winner about as well as model does.
   - In block 3, seat 2 wins all four rotations.
   - Twenty independent games give 25% power to detect a true 40% win rate against the 25% null, and yours are not independent.
   - Your logs show about $218 in recorded charges for the whole corpus (refused Opus calls unpriced), roughly $11 a game. n = 20 was a $200 decision.

5. **No inferential statistics anywhere.**
   - There are zero p-values, intervals or models in 33 pages.
   - Naive Fisher tests on your Table 2 give p = 0.08 (opening) and 0.014 (later) for the rejection gap, before clustering by thread, recipient or game.
   - The paper hides behind "declared finite populations", then generalizes to "these configured systems" in the abstract.
   - You built a duplicate-style design (same dice, rotated seats) and never ran the paired analysis it exists for.
   - Only one cyclic order is used (Opus, Sol, Gemini, Grok), so who moves after whom is fully confounded.
   - No cell is replicated, so dice variance and sampling variance can't be separated.

6. **No baselines and no value reference.**
   - There is no random or scripted bot, no same-model table and no human, although your repo ships `baselines.py`.
   - In Cattle Trade, two heuristic code agents beat most of the LLMs tested, and a hybrid PPO Monopoly agent posted a 91% win rate against fixed-policy opponents in IEEE TETCI in 2022.
   - Nothing in your paper can call one decision good or bad. Was Grok's triple refusal in G15 a blunder? You can't say.
   - Your engine is deterministic, so a rollout oracle is sitting there unused.

7. **Two of three headline results are Monopoly's rules.**
   - "Early-built groups collect $53,810 of $57,378": houses multiply rent and early builders have more exposure.
   - "Winners receive 202 of 227 inherited deeds": the strongest rent position is the creditor and usually the winner.
   - "56 of 60 debts exceed the bound": bankrupt players were insolvent.
   - Each is hedged in the text, then promoted to the abstract.

8. **The semantic evidence won't survive a methods reviewer.**
   - The 61-of-74 result comes from two GPT-6 Astra instances, one partly unblinded, with no codebook, no kappa and no human label. The coders share a vendor with a subject.
   - 34 of the 61 come from two games.
   - 36 of the 74 are both-complete offers where refusing is unremarkable. The interesting cell is 27 of 38 recipient-only refusals.
   - The planning sample is 240 decisions coded by one instance from an unexplained "public-message-unflagged" pool, and 53 of Opus's 60 have no note.
   - The eight transcripts take ten pages, were picked post hoc and estimate nothing.

9. **The environment has validity holes you document instead of fixing.**
   - The system prompt contains no rules. Agents are never told the house variants: buildings pass intact to creditors, no bank auction, per-entry build validation, no hotel sale without four bank houses.
   - Agents get no prices outside purchase prompts, yet Transcript 1 marks Sol down for a house-count error.
   - 29% of prompts (2,054) carried misattributed trade histories, and 149 public messages never reached the timeline.
   - A float bug overcharges redemption by $1 at five principals.
   - A menu bug bankrupted Opus in G7 holding $1,310 against a $750 debt.
   - Opponents see brand names.
   - The prompt lists "deceptive, manipulative, hostile" as personalities and says to "bluff, deceive, intimidate". Nothing you observed is emergent. Li et al. confirmed from archived payloads that their agents received no conduct instruction either way.

10. **Novelty is thin.** This is the third LLM-Monopoly paper in six months. You position against AgentMonopoly, but FinBoardBench already has accept, reject and counter negotiation and makes debtors mortgage or sell buildings before elimination. What's left is a house rule and the depth of your audit.

## How it stacks up

| Paper | Scale | What it has that yours lacks |
|---|---|---|
| Li et al. (in the NeurIPS 2026 program) | 20 runs, 13 models, 2,583 emails | Hand-labeled reference set, three judge families, mixed-effects models, run-level cluster bootstrap |
| MindGames (NeurIPS 2026) | 29,571 games | Ratings and a frozen reference pool |
| DECE | 480 matches, 12 model-harness configurations | Matched harness contrasts |
| Cattle Trade | 242 games, seven LLMs, three code agents | Scripted baselines, TrueSkill |
| AgentMonopoly | Eight model variants, five seeds per configuration | Same-model matchups, a controlled manipulation |
| FinBoardBench | Nine LLMs, 108 matches | Nothing: no baselines, no tests. You beat it on rigor. |
| Yours | 20 games, 4 models, 1 roster | |

Li et al. is the one to study. It has the same n = 20 as you and got in on method.

## Writing and presentation

- **Title and abstract:** the title has no finding and no "LLM". The abstract uses Sol, Gemini, Opus and Grok undefined and makes no claim.
- **Contribution:** there is no contributions list. "To connect bargaining to…" is an activity, not a result.
- **Length:** about 10,200 words of main text over 22 pages. NeurIPS E&D caps main content at nine.
- **Hedging:** about one sentence in nine disclaims an inference (75 of 674 by my count). Hedge once, in Limitations.
- **Private vocabulary:** witness, certificate, retained historical checks, received-call conflict, action-only recovery, spending unit. Define or delete.
- **Outline leaks:** §8.3 cites "eight motivating questions and three broader questions" that never appear earlier. Table 6 has a row reading "Not evaluated".
- **Figures:** two, a five-number bar chart and a scatter of a non-finding. There is no system diagram, no prompt and no example payload.
- **References:** 15. Missing at minimum: Lewis 2017, He 2018, Davidson 2024, Xia 2024, Abdelnabi 2024, AucArena, GTBench, CICERO, Cattle Trade, MindGames, TERMS-Bench, Bonjour 2022. The paper also needs the economics it is reinventing: Rubinstein bargaining, Jehiel and Moldovanu on sales with externalities, the holdout problem, Shleifer and Vishny on fire sales.
- **Authorship:** Appendix E says four LLM assistants each wrote a full manuscript, two of them the evaluated models, under the byline "MonopolyBench project". NeurIPS makes authors answerable for every word and bars LLMs from the author list. Name the humans and own the text.
- **Anonymity and repo:** the repo URL and CITATION.cff carry your name. The repo is 5.4 GB and 180,977 files with conflict copies (`README-Kush-Omen.md`), a 94 MB video and `tmp/`.

## Errors and nits

- "All use the recorded medium reasoning setting" is contradicted by Sol's zero-token calls.
- "Unless identified as provider USD": no USD figure ever appears. Report cost.
- Transcript 7's "4/36, not 5/36" is first-roll only. With doubles it is about 11.7%.
- Your audit doc says estates transfer without mortgage interest and that developed groups can't be traded. Neither rule is in the paper.
- Table 5's "69 of 69 terminal estates to winners" is true by construction.
- "92" means two different things in one paragraph of §4.2.
- Numerals flip between "56 of 60", "Fifty-six of sixty" and "35 of forty".
- References [8] and [14] now have NeurIPS 2026 versions; cite those.
- 12 em dashes.

## Questions a referee will ask

1. Why 20 games at $11 each?
2. What does Opus do when the note is a planning memo and not a reasoning request?
3. Which Grok channel is authoritative, and does the mismatch survive `tool_choice: auto`?
4. Same seed, same seating, run twice: how often does the winner change?
5. What is the paired per-(seed, seat) comparison across models?
6. What are each coder's marginals on the 74, the kappa, and agreement with a human on 50 items?
7. Did the $1 overcharge or the G7 lock flip any outcome? You can replay it, so why leave it open?
8. Sellers ask 1.6x list for completing deeds while buyers bid no premium (Table 9). Does that asymmetry survive controls? It may be your best real finding, and it's buried in an appendix.
9. Does hiding model names change behavior?
10. What observation would falsify any claim here?

## What I'd do

1. **Don't post this version.** Fix the Opus description first.
2. **Merge your two planned papers into one.** The instrument plus an intent, feasibility and execution audit is the contribution. The bargaining results are its application.
3. **Fix the harness.**
   - Replace `private_thought` with a memory memo and confirm near-zero refusals on replayed prompts.
   - Reject call/text mismatches as invalid.
   - Auto-interleave build plans.
   - Use integer math for interest; fix the hotel menu and the history formatter.
   - Put rules and the board table in the prompt.
   - Hide names; cap and report reasoning budgets.
4. **Rerun at scale.** 25 to 30 seed blocks, about 100 to 120 games, is $1,100 to $1,300 at current cost. Randomize full seat order, replicate cells, and add same-model tables and scripted bots.
5. **Add ablations** for memory, names and the deception sentence. That is where causal claims come from.
6. **Add a rollout oracle** so trades get a win-probability delta.
7. **Add statistics.** Seed-block bootstrap intervals, and mixed-effects models with game and thread random effects.
8. **Fix the coding.** Two humans label 150 items; then use judges from at least two families outside the roster.
9. **Rewrite to nine pages** around one thesis, with two transcripts in the body.

Target NeurIPS 2027 E&D (2026's deadline was May 6). ICML 2027 hasn't posted dates; one tracker projects January 22, which is too soon for a rerun done properly.

Want this as a doc with a checklist you can work through?

Sources:
- [What's new in Claude Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5)
- [Emergent Misaligned Communication in Long-Horizon Multi-Agent LLM Commerce](https://arxiv.org/pdf/2608.14825) and its [NeurIPS 2026 listing](https://neurips.cc/virtual/2026/160064)
- [FinBoardBench](https://arxiv.org/pdf/2605.27896.pdf)
- [AgentMonopoly](https://arxiv.org/abs/2610.29330)
- [A Unified Arena for LLM Agents across Diverse Eurogames (DECE)](https://arxiv.org/abs/2610.35773)
- [Cattle Trade](https://arxiv.org/pdf/2605.14537)
- [MindGames, NeurIPS 2026](https://neurips.cc/virtual/2026/poster/139792)
- [Decision Making in Monopoly using a Hybrid Deep RL Approach](https://arxiv.org/pdf/2103.00683)
- [Measurement-First Auditing of Agentic Leaderboards, NeurIPS 2026](https://neurips.cc/virtual/2026/173736)
- [NeurIPS E&D 2026 reviewing guidelines](https://neurips.cc/Conferences/2026/EvaluationsDatasetsReviewerGuidelines) and [extended guidelines](https://neurips.cc/Conferences/2026/EvaluationsDatasetsExtendedReviewerGuidelines)
- [NeurIPS 2026 E&D call for papers](https://nips.cc/Conferences/2026/CallForEvaluationsDatasets)
- [ICML 2027 deadline tracker](https://www.opencurious.com/ai-conference-deadlines/icml-2027)
- [OpenRouter model list](https://mastra.ai/models/gateways/openrouter)

---

User instruction accompanying the review:

Please add all of the above to the feedback as well. Make your best judgement for what should and shouldnt stay.

Build on top of what we previously did and found

read and understand this with your team

and then tell me simply what the issues are
