# Literature read for this draft, and what I took from it

11 November 2026. This file records exactly what I opened, how much of it I read, what I took for argument or presentation, and which sentences in the manuscript rest on it. I cite nothing for a claim I did not read. Web pages were fetched through a summarising fetch tool, so for those sources I saw a model-written summary with short verbatim excerpts, not the raw page. Two sources I read directly: the first four pages of Jehiel and Moldovanu (PDF text layer) and the full Anthropic documentation page (returned verbatim).

I imported no venue or acceptance claim from the outside reviews. Where an arXiv page lists no venue, I cite the arXiv version.

## Primary sources studied for argument and method

### Jehiel and Moldovanu (1995), "Negative Externalities May Cause Delay in Negotiation", Econometrica 63(6), 1321 to 1335

- **Read.** Pages 1321 to 1323 of the published article, from the PDF hosted by the University of Bonn (SHA-256 `746ff4f6...8037a`). Abstract, introduction, the economic situation and the start of the negotiation game. I also read the RePEc record.
- **What it says, in my words.** A seller holds one indivisible object. If buyer j obtains it, each other buyer i suffers a loss that depends on both identities. In long finite games the unique subgame-perfect equilibrium can show delay, or one buyer who obtains the object almost surely. Without externalities delay is impossible in their model. Willingness to pay changes along the path because small losses are better than large ones, which produces war-of-attrition behavior. They note that delay need not mean inefficiency. They tie the result to "Rubinstein's (1982) message that it is the cost of rejecting the proposer's offer that determines the proposer's payoff" (p. 1322).
- **What I took.** The frame for the whole paper. A completing deed is an object whose sale hurts third parties and, in Monopoly, the seller as well. The paper predicts refusal and delay without any appeal to irrationality, which is the right prior for reading Sections 3 and 4.
- **Where cited.** Introduction, first paragraph. Discussion, "Two results from bargaining theory".
- **Limit.** Their seller does not suffer the externality. Ours does. I say "a stronger version of that position" and do not claim their theorem applies.

### Shleifer and Vishny (1992), "Liquidation Values and Debt Capacity", Journal of Finance 47(4), 1343 to 1366

- **Read.** RePEc record and abstract summary only.
- **What it says.** When a distressed firm sells assets, the natural buyers in its industry are often constrained too, so assets sell below value in best use. Asset illiquidity is a cost of leverage.
- **What I took.** The idea that the price of a forced sale depends on who the natural buyer is. In our games the natural buyer of a completing deed is one rival. That predicts low distress prices. The records show them for Opus and not for the other three systems, which I report as a finding against the simple prediction.
- **Where cited.** Introduction, first paragraph. Discussion.
- **Limit.** Abstract-level reading. I make no claim about the model's details.

### Shleifer and Vishny (2011), "Fire Sales in Finance and Macroeconomics", Journal of Economic Perspectives 25(1), 29 to 48

- **Read.** AEA article page and abstract summary. The PDF returned HTTP 403.
- **What it says.** A fire sale is "essentially a forced sale of an asset at a dislocated price", with a seller who must pay creditors and constrained natural buyers.
- **Where cited.** Discussion, next to the 1992 paper, for the definition.

### Rubinstein (1982), "Perfect Equilibrium in a Bargaining Model", Econometrica 50(1), 97 to 109

- **Read.** RePEc bibliographic record only. The record has no abstract.
- **How I use it.** Only through Jehiel and Moldovanu's one-sentence summary quoted above, and I word the manuscript sentence so that the characterisation is theirs.

### Cosentino, Shekkizhar, Earle and Savarese (2026), "Counterparty Modeling is Not Strategy", arXiv:2605.16575v1

- **Read.** arXiv abstract page and the HTML version, first 100,000 of about 104,000 characters, through the fetch tool with section-level questions.
- **What it says.** A bilateral car-purchase negotiation over ten terms with private linear utilities. Informed agents get a three-tier ranked summary of the counterparty's preferences. Belief accuracy is extracted from reasoning text. Agents model the counterparty accurately (signed accuracy above about 0.7 by mid-negotiation for informed buyers), yet information does not reliably help the informed side, own gain on concession turns is near zero or negative, and final prices track opening anchors. A trade-plan template improves legibility more than outcomes. The authors conclude that social understanding and strategic interaction are separable.
- **What I took.** The cleanest prior statement of the distinction my paper observes in play: modeling the other side is not the same as using that model well. Their design has what ours lacks, a utility function and a controlled information condition. It also gave me the phrase structure "attention is common, conversion is not" without borrowing their words.
- **Where cited.** Related work.

### Li, Petersson, Acquisti and Bakker (2026), "Emergent Misaligned Communication in Long-Horizon Multi-Agent LLM Commerce", arXiv:2608.14825v3

- **Read.** arXiv abstract page (v1 14 August 2026, v3 21 August 2026, no venue line) and the HTML version, first 100,000 of about 161,000 characters.
- **What it says.** 2,583 inter-agent emails from 20 year-long Vending-Bench Arena runs, 13 models, 79 agent-runs. A frozen codebook, an LLM judge, deterministic checks of extracted claims against the simulator log, a 50-email reference set labeled by one author (92% raw agreement, called codebook consistency), cross-judge replication with two other model families, cluster bootstrap intervals at the run level, mixed-effects logistic models. 12.58% of emails misaligned [8.88, 16.61]. Low inventory raises the odds of a misaligned email (OR 1.58). The prompts contain no conduct instruction. One corpus example appears in the main text as a figure.
- **What I took for method.** This paper has the same number of runs as ours. It is my model for how to state the unit, where to put uncertainty (the run), how to describe label validation without overclaiming, and how to separate descriptive per-model rows from tested contrasts. I could not copy its statistics, because we have five seed blocks and no validated labels, so I report block counts and leave-one-block-out ranges and say why.
- **What I took for presentation.** State the conduct instruction in the setup. Ours invites deception, theirs is silent, so I say early that a public bluff is authorized conduct.
- **Where cited.** Related work.
- **Limit.** I did not read the last third of the page (appendices). I state nothing about them.

### Wu, Li, Marsault, Huang and Cheng (2026), "AgentMonopoly", arXiv:2610.29330v2

- **Read.** arXiv abstract page (v2, 22 October 2026, "14 pages, 8 figures, 5 tables") and the HTML version through the fetch tool.
- **What it says.** Four-player Monopoly on a modified board, four model families at two sizes, seeds 42 to 46, same-model, mixed-size, cross-family and persona conditions. Trade proposals per 100 rolls and acceptance rates by model, rent waivers, minimum cash. A player is eliminated when its cash balance becomes negative. The prompt encourages bluffing and forbids public messages that contradict actions. Larger models do not consistently win more.
- **What I took.** The nearest competitor. It measures trade frequency and acceptance. It does not follow a traded deed into development or default. That is the gap my paper fills.
- **Where cited.** Related work.
- **Limit.** The fetch summary could not confirm whether trades allow counteroffers, so I do not say they do not.

### Hu et al. (2026), "FinBoardBench", arXiv:2605.27896v1

- **Read.** arXiv abstract page ("Preprint") and the HTML version through the fetch tool.
- **What it says.** Three financial board games including Monopoly, nine LLMs against three fixed opponents, 108 matches in total. Monopoly negotiation offers accept, reject and counter. Models buy assets when short of cash (cash below $500 after 47 purchases) and are said to overvalue asset accumulation and undervalue liquidity. Up to five action failures before a system-enforced fallback.
- **What I took.** A prior liquidity finding in the same game. Theirs is about acquisition (buying while short of cash). Ours is about what happens after acquisition (what holders do with a completed group or with sale proceeds). I position the two as complementary.
- **Where cited.** Related work.
- **Limit.** I make no statement about its bankruptcy rule for buildings. The summary I saw says only that property passes to a player-creditor and that bank-owed property is demolished and auctioned.

### Bianchi et al. (2024), "How Well Can LLMs Negotiate? NegotiationArena", PMLR 235:3935 to 3951

- **Read.** PMLR proceedings page and abstract summary.
- **What it says.** Ultimatum, trading and price-negotiation scenarios with multi-turn dialogue. "By pretending to be desolate and desperate, LLMs can improve their payoffs by 20%" against GPT-4.
- **What I took.** A precedent for distress as a bargaining tactic, which is what Grok does in G13 with real collateral at stake.
- **Where cited.** Related work.

### Müller and Müller (2026), "Cattle Trade", arXiv:2605.14537v1

- **Read.** arXiv abstract page (comments: "malgai workshop at ICLR 2026").
- **What it says.** 242 games, seven LLMs and three deterministic code agents. Two rule-based agents beat most LLMs. Strategic coherence (spending efficiency, resource discipline) tracks rank more closely than any single skill.
- **What I took.** Independent support for the idea that resource discipline, more than any single bargaining skill, separates outcomes, and a reminder that our cohort has no scripted baseline.
- **Where cited.** Related work. I cite the arXiv version and not the workshop.

### Abdelnabi et al. (2024), arXiv:2309.17234v2, and Lewis et al. (2017), arXiv:1706.05125v1

- **Read.** arXiv abstract pages only.
- **Use.** One sentence of background in Related work, limited to what the abstracts state: scorable multi-party negotiation with greedy and adversarial players, and end-to-end negotiation with hidden reward functions. The Lewis abstract does not mention deception, so I do not attribute a deception finding to it.

### Anthropic (2026), "What's new in Claude Opus 5.5", documentation page

- **Read.** The full page as returned on 11 November 2026.
- **What it says.** Under "Behavior differences": "requests that push it to reproduce its internal reasoning in the response text might be declined with the `reasoning_extraction` category." Under "Refusals and fallback": a declined request returns `stop_reason: "refusal"` with a `stop_details` object naming the policy area. It also says forced tool use is not supported on this model.
- **Use.** Appendix B and one clause in Section 2.3. I say the documented behavior fits the logs and that the saved responses, which pass through OpenRouter, carry no category field.

## Inherited citations not re-read

Turpin et al. (2023) and Lanham et al. (2023) are cited once each for the standard point that stated explanations need not reflect internal computation. The entries are copied unchanged from the earlier versioned library. I did not re-read them in this session.

## Sources suggested by the outside reviews that I did not use

GTBench, GAMA, MERIT, MindGames, DECE, HAL, SOTOPIA, AucArena, CICERO, TERMS-Bench, Bonjour et al. (2022), Davidson et al. (2024), Xia et al. (2024), Jehiel, Moldovanu and Stacchetti (1996), Kahneman, Knetsch and Thaler (1990). I did not read them for this draft and do not cite them. Some may deserve a place in the integrated paper after someone reads them. I would add Jehiel, Moldovanu and Stacchetti first, for sales with externalities among buyers.

## What the reading changed in the paper

1. The paper opens with the economics of the object (a veto with externalities) and not with the game's pipeline.
2. Uncertainty is stated at the block level, following Li et al.'s choice of the run as the unit, and without their models.
3. The conduct instruction is printed in the setup.
4. The headline distinction (attention against conversion) is aligned with Cosentino et al.'s distinction between modeling and strategy, and with Cattle Trade's finding on resource discipline.
5. Distress prices are reported as a test of the fire-sale prediction that only one system fits.
