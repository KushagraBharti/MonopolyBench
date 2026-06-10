# MonopolyBench — Research Feedback & Publication Readiness Review

**Reviewer:** Claude (acting as research mentor)
**Date:** June 10, 2026
**Scope:** Full repository audit (code, tests, artifacts, paper draft), `research_direction.md` review, and a fresh related-work search to validate novelty claims.
**Method note:** Everything below is based on what I verified directly — I ran the test suites, inspected the run directories, read the paper draft, and searched the current literature. I did not take `implementation_status.md` or other planning docs at face value (though, notably, they turned out to be accurate).

---

## 1. Executive Summary

**The platform is genuinely research-grade and the niche is real — there is still no dedicated LLM Monopoly benchmark as of June 2026.** The engineering quality is well above what most published benchmark repositories ship with.

**But the paper, as it stands, is not publishable yet — and the gap is not code, framing, or design. It is data.** The entire empirical base today is:

- two real frontier full games (one of which has a replay mismatch),
- one complete micro-suite pass for a single model.

Everything else in the repository is well-built, well-tested scaffolding waiting for experiment spend.

**Bottom-line verdicts:**

| Target | Verdict | What it takes |
|---|---|---|
| AAAI-style workshop paper | **Reachable with high confidence** | ~$300–800 of structured runs + 2–3 weeks of execution |
| Main track / NeurIPS Datasets & Benchmarks | **A genuine maybe (~coin flip per attempt)** | Statistically powered leaderboard, human-validated rubrics, baselines, public artifact release — and a crisp empirical finding |
| Public traction (leaderboard attention) | **Plausible, not guaranteed** | Frontier models on the board, clickable artifacts, one screenshot-able finding, and sustained updates across model release cycles |

The distance to a credible paper is measured in **OpenRouter dollars and a few weeks of campaign execution, not months of building**. Stop building. Start running.

---

## 2. What I Verified (Ground Truth, Not Self-Reporting)

### 2.1 The engineering is real, not aspirational

- **~19,200 lines of Python source** across `engine` / `arena` / `telemetry` / `microbench`, plus ~2,800 lines of tests.
- **96 tests pass live** (I ran engine + arena + microbench suites myself; they completed clean in ~2 minutes).
- A **3,233-line deterministic rules engine** with seeded RNG, event sourcing, and legal-action generation.
- **Contracts-first architecture**: JSON Schemas + TypeScript types + validated examples, with `validate-contracts.mjs` enforcement.
- **130 frozen micro scenarios** with research-only metadata, counterfactual pair registry, bias/safety/campaign suite overlays.
- Seat-permutation campaign planner (Latin square / full / seeded random), deterministic baseline bots, replay verification artifacts, OpenRouter cost accounting from actuals, failure taxonomy, model cards, human review queue infrastructure.
- `implementation_status.md` is **accurate, not inflated** — a rarity worth noting.

This is more rigorous infrastructure than most published benchmark repos. Treat it as a settled asset.

### 2.2 The data is thin — this is the entire problem

- `runs/` is almost entirely **mock runs**.
- Real artifacts in `saved_games/`:
  - **Run A** — GPT-5.5 wins by bankruptcy at turn 191. ~$27.71 total cost, 3.52M tokens, 583 model calls. **Replay mismatch at index 669** — currently unusable as headline quantitative evidence for a benchmark whose core pitch is deterministic replay.
  - **Run B** — Gemini 3 Flash wins at turn 273. **Replay-clean** (4,102/4,102 events), $4.24, 2.95M tokens, 0 fallbacks. This is your strongest artifact.
- One complete **micro-v1 pass for `openai/gpt-oss-120b`**: average score 0.702, retry rate 6.2%, fallback 0%. Strong on `BUY_OR_AUCTION` and `JAIL`; weak on `TRADE_RESPONSE` and `LIQUIDATION`.
- The `monopoly-long-v1-smoke` campaign directory under `campaigns/` is **config only — no execution artifacts**.
- Heuristic baselines (`random_legal`, `always_buy`, `cash_conservative`, `builder`, `auction_aggressive`, `no_trade`) **exist in code with passing tests but have never been run against an LLM in a full game**.

### 2.3 The paper draft

`monopolybench_ieee_draft_v0_1.tex` is a well-framed skeleton. (Note: `monopolybench.tex` at the root is the **untouched blank IEEE template** — delete or ignore it to avoid confusion.)

The framing choices are unusually publication-savvy for a first paper:

- the **claim-gating table** (which claims require which evidence) preempts the most common benchmark-paper criticism;
- **descriptive trace analysis instead of a hidden heuristic oracle** is the right epistemic stance for a game where move value is context-dependent;
- **reliability treated as instrumentation, not headline** correctly avoids the trap of writing a tool-calling paper when the contribution is economic agency.

That self-discipline will read well to reviewers. Keep it.

---

## 3. Strengths (What Survives Review)

1. **The niche is genuinely unclaimed.** I searched specifically. No dedicated Monopoly LLM benchmark exists. The "Monopoly Game" in [Game-theoretic LLM](https://arxiv.org/html/2411.05990v1) is an abstract matrix game, not the board game. Prior Monopoly work is [2002-era negotiation agents](https://ieeexplore.ieee.org/document/1013210) and the Bonjour hybrid-DRL paper — neither is an LLM benchmark. The general game suites ([TextArena](https://arxiv.org/html/2504.11442v1), [GameBench](https://arxiv.org/abs/2406.06613), [Game Reasoning Arena](https://arxiv.org/html/2508.03368v1)) don't cover Monopoly's specific combination of negotiation + auctions + leverage + bankruptcy.

2. **Determinism + replay + complete artifact trails is a real differentiator.** Most game benchmarks cannot replay a run byte-for-byte or hand a reviewer the exact prompt and raw response for decision #412. You can. This is your credibility moat, it is already built and tested, and it maps directly onto what Datasets & Benchmarks reviewers reward.

3. **The micro + macro pairing is the right experimental design.** Full games give ecological validity; frozen scenarios give attribution. The Vending-Bench authors arrived at this lesson after the fact; you designed it in from the start. The counterfactual-pair registry (same EV, different framing) is genuinely good methodology.

4. **You already have candidate headline findings, even from this tiny pilot:**
   - *Tactical competence ≠ negotiation/crisis competence* — gpt-oss-120b aces buy/jail decisions but fails trade response and liquidation.
   - *Action reliability ≠ economic success* — in Run B, Claude Haiku produced zero invalid actions and still went bankrupt; Gemini Flash won through systematic set completion and rent-engine construction (+$6,828 net rent).
   - *Distinct strategic profiles* — Run A's winner won through negotiation-dominated accumulation and leverage (20 mortgaged properties at game end); Run B's winner through development and rent flow. Different models, different economic personalities.

   These are the kinds of sentences that make a benchmark paper a *findings* paper.

5. **Public/private channel divergence is your most attention-getting instrument.** A model publicly calling a trade "fair" while privately noting it exploits the opponent is screenshot-able, quotable, and unique to your design (most benchmarks don't record both channels). The instrumentation exists; you just need games.

---

## 4. Weaknesses (What a Reviewer Will Hit, In Order of Severity)

1. **n=2 full games, n=1 micro model.** No venue accepts rankings, strategic profiles, or hypotheses from this. The draft is honest about it ("pilot case studies"), but a results section consisting of two case studies and one model's micro scores reads as a systems demo. **This is the only blocker that actually matters; everything below is mitigation.**

2. **Cost is the unaddressed bottleneck.** Run A cost $27.71 for *one game*. A minimally credible leaderboard — 5 models × 8 seeds × seat rotation — is hundreds of games; with frontier models that is plausibly **$5K–15K**. `research_direction.md` demands "5–10 games per model minimum" without ever confronting the price tag. The mitigations need to become explicit experimental design, not improvisation:
   - mid-tier models for the powered comparisons (Run B proves a full game can cost ~$4);
   - heuristic bots filling seats so each game needs fewer paid players;
   - frontier models reserved for a small number of showcase games;
   - micro suite (cheap) carrying the statistical weight.

3. **The "why Monopoly?" objection.** Reviewers will say: heavily luck-driven, low strategy ceiling, a children's game — why not Diplomacy or Catan? Your counters are real but currently implicit. They need a dedicated subsection: full instrumentability (40 squares, discrete cash, enumerable actions), universal legibility, negotiation-decided midgames (the Markov-chain literature shows dice dominate early but trades/development decide outcomes), and the fact that high variance *strengthens* the case for the paired micro suite. Make the variance a feature you measure (run-to-run variance per model is itself a Vending-Bench-style metric), not a flaw you hide.

4. **Rubric validity.** All 130 scenarios' preferred/acceptable/trap labels are author-authored. The expert-label infrastructure (queues, schemas, import/export, validation) exists but holds **zero labels**. A reviewer can ask "who says dropping out of the Boardwalk auction is correct?" and today the answer is "the benchmark author." Even **two experienced-player labels on a 30-scenario subset**, with agreement statistics, defuses this almost entirely. This is days of effort, not weeks.

5. **No baselines in any result.** "Can a frontier LLM beat an always-buy bot?" is the first question every reader will ask. The bots are implemented, tested, deterministic, and nearly free to run. There is no excuse for this gap — it is the cheapest high-value experiment in the entire project.

6. **The adjacent space is crowding fast.** [Vending-Bench](https://arxiv.org/abs/2502.15840)/Arena, [EcoGym](https://arxiv.org/html/2602.09514v1), [Cattle Trade](https://arxiv.org/abs/2605.14537), [EconEvals](https://arxiv.org/pdf/2503.18825), and [AgenticPay](https://arxiv.org/abs/2602.06008) all occupy "long-horizon economic LLM agents," and Cattle Trade in particular overlaps on auctions/bluffing/bargaining. You are differentiated — multi-agent + natural-language negotiation + leverage/bankruptcy + deterministic replay + micro attribution in one familiar game — but the paper must answer "what does this measure that Vending-Bench and Cattle Trade don't?" **with a finding, not an architecture diagram.**

7. **Smaller but real:**
   - **Run A must be replay-reconciled or demoted** to a clearly-flagged qualitative case study. A benchmark whose pitch is deterministic replay cannot headline a replay-broken run.
   - **Trademark exposure**: "Monopoly" is a Hasbro mark. Academic papers using the name have never drawn fire, but a hosted public leaderboard with branding is more exposed than a paper. Worth a naming decision *before* you invest in the brand, not after.
   - **Model version drift**: your protocol already records exact IDs/dates/pricing snapshots — keep that discipline, it will matter when reviewers ask about reproducibility of API-served models.

---

## 5. Assessment of the Four Research Directions

Ranked by my honest read, not by the order in `research_direction.md`.

### Direction 3 — Targeted Scenario Suite: **strongest science per dollar; build Paper 1 around it**

This is where actual *findings* come from, and findings are what get cited. Single-decision scenarios cost fractions of a cent to a few cents, give clean statistics, and can be rerun on every model release. The counterfactual-pair design is the difference between "model scored 0.70" and **"models pay a measurable premium for Boardwalk because it is famous"** — a result people remember and repeat. Your single existing data point (strong buy/jail, weak trade-response/liquidation) is already more interesting than anything a leaderboard produces.

**Risks to manage:** rubric validity (§4.4); and bias probes reading as gimmicky if controls are sloppy — counterfactual pairs must be *actually* EV-equivalent, and you should expect a reviewer to check the arithmetic. Pre-register the pairs' equivalence in the scenario metadata.

### Direction 1 — Long-Horizon Full Games: **necessary spine, but it's the platform, not the finding**

Full games are what make this MonopolyBench rather than a quiz, and trajectory artifacts (rent engines, liquidity collapses, bankruptcy cascades) are your demo and traction material. But as a standalone contribution it is the weakest of the four: expensive, high-variance, and its natural output is a leaderboard — and leaderboards age badly and draw "so what" reviews unless paired with analysis. The draft already has the right instinct: **D1 supplies ecological evidence and case studies; D3 supplies attribution.** Keep them fused in one paper.

**One pushback on `research_direction.md`:** the giant scorecard (100+ metrics) is a liability for a paper, not an asset. Reviewers trust three well-defended metrics more than forty shallow ones. Pick a primary outcome (rank or normalized net worth), one risk/variance metric, and cost; relegate everything else to released artifacts.

### Direction 4 — Orchestration / Information Design: **most intellectually valuable; the right second paper**

This is the only direction that produces *generalizable* knowledge rather than model rankings: "curated information helps weak models and distracts strong ones," "auction caps eliminate catastrophic overbids at no performance cost," "structured memory reduces strategy drift." Those findings outlive every model on the leaderboard and speak directly to practitioners deploying agents. It is also your most differentiated angle — the GenAI Beer Game got HBR-level attention precisely because it was about *system design*, not model IQ.

**Why not now:** every prompt/guardrail/orchestrator condition multiplies run count, so D4 is only affordable after D1 has established baseline variance and you know how many seeds a comparison needs. Right direction, wrong moment. Sequence it as Paper 2.

### Direction 2 — Real Estate / Asset Management: **cut it, or demote to one future-work paragraph**

Being blunt, because this is where I'd worry about you most: this is a new project wearing MonopolyBench's architecture, and it has validity problems the other three don't.

- There is **no ground truth for "good" CRE decisions**. Monopoly hands you clear win conditions and a Markov-chain literature; cap-rate judgment calls have neither. You would inherit exactly the evaluation-validity problem that Monopoly currently solves for you.
- Your anchor list (Finsimco, HBS sims, ULI, Cesim) consists of **proprietary teaching products** — you cannot replicate them, compare against them, or cite their internals.
- Validating realism requires **domain experts you don't currently have access to**.
- The finance-agent space is **already crowding** (EconEvals, AgenticPay, trading-agent benchmarks).

If you ever return to it, the one tractable slice is the **capital-budgeting variant** (HBS-style, 27 projects over 5 years), because NPV/IRR ground truth is computable and claims become checkable. But building D2 before MonopolyBench has traction is diluting a focused project to chase a bigger-sounding one — the classic way solo research projects die.

### Recommended program shape

> **Paper 1** = D3 headline findings + D1 ecological evidence and case studies (matches your and Parth's current plan — correct).
> **Paper 2** = D4, only if Paper 1 lands.
> **D2** = a sentence in future work. Possibly forever.

---

## 6. Publishability, By Tier — The Direct Answer

### Workshop (AAAI workshop or similar — your mentor's target): **yes, with high confidence**

If you run micro-v1 across 5–8 models, add heuristic-bot baselines, complete one clean seat-rotated small campaign, and write the "why Monopoly" defense, you have a workshop paper **above** the typical bar. Workshop acceptance bars are modest, your infrastructure is unusually rigorous, and the niche is empty. The risk here is execution risk, not acceptance risk. Estimated spend: **$300–800**.

### Main track / NeurIPS Datasets & Benchmarks: **a genuine maybe — roughly a coin flip per attempt, and I won't pretend otherwise**

Even with everything executed well, you face headwinds unrelated to quality: "yet another game benchmark" reviewer priors, less benefit of the doubt for early-career submissions without a known lab, and ordinary reviewer lottery. What moves the probability is **not completing a checklist — it's whether the experiments surface a crisp, surprising finding.**

- "We built a rigorous benchmark" → borderline scores.
- "Models that ace tactical decisions systematically fail at adversarial negotiation, and here are 40 controlled scenarios proving it isn't noise" → accept territory.

You cannot fully control whether the data cooperates. You *can* control running enough breadth that interesting patterns have room to appear. Note that **D&B-style venues specifically reward what you've already built** (replay, artifact release, versioning, claim gating) — that track fits you better than a standard research track.

### Two caveats I need you to internalize

1. **The checklist is necessary, not sufficient.** My action items remove the reasons a reviewer rejects in the first ten minutes (n=2, no baselines, unvalidated rubrics, replay-broken headline run). They cannot manufacture the reason a reviewer *accepts*. That comes from results.
2. **The empty niche is also a timer.** Cattle Trade, EcoGym, and AgenticPay all appeared within roughly the last year; the space fills monthly. Nobody claiming Monopoly is partly opportunity, partly evidence others deprioritized it. Your edge is that your instrument is *already built* while any competitor starts from zero — but that edge decays. The AAAI deadline as a forcing function is exactly right: **ship the workshop paper, get the leaderboard and artifacts public, and the priority claim is yours** while you build toward the larger venue.

### And one framing distinction

**Publishable and worth doing are different questions — and the second has the cleaner answer.** Even in the downside case (workshop paper, no main-track acceptance), you end with: a public benchmark with your name on it, a real publication, demonstrated end-to-end research execution for grad school applications, and infrastructure that supports a second paper (D4) with a stronger acceptance profile. The downside scenario is still a good outcome. That asymmetry is the property I want in any research bet, and this one has it.

---

## 7. Traction & Attention — Honest Read

Benchmarks get traction from three things: **frontier model names on a leaderboard, a surprising or funny finding, and clickable artifacts.** Vending-Bench took off because Andon Labs ran GPT/Claude/Gemini head-to-head and the failure transcripts were entertaining.

You have the same ingredients available, plus one advantage: **Monopoly is universally legible** — a far better press/social-media substrate than vending machines. "Claude went bankrupt at turn 190 after Gemini built a hotel empire" writes its own headline. The private-thought-vs-public-message transcripts will produce screenshot-able deception examples no other benchmark can.

The risk side, stated plainly:

- **Solo-maintained benchmarks fade fast** unless someone keeps rerunning new models. Plan for 2–3 model-release update cycles or expect a spike-and-decay attention curve.
- **$25/game economics don't sustain a public leaderboard** without a lab partner, sponsor, or API credits. Worth raising with Parth whether his lab/department can support runs, and worth considering whether OpenRouter or a lab would sponsor credits for a public artifact release (benchmarks are marketing for them too).

Realistic ceiling as-is: a well-received workshop paper plus a niche-viral leaderboard launch. The ceiling rises substantially with sustained updates.

---

## 8. Prioritized Action Plan

In strict order of value per dollar/hour:

1. **Run micro-v1 across 5–8 models.** Cheapest path to a real results table and the tactical-vs-negotiation finding. Use exact model IDs (never the `-latest` aliases that caused HTTP 400s), fixed reasoning settings, full cost accounting. Include at least one open-weight model for reproducibility optics.
2. **Run heuristic-bot baselines vs. 2–3 LLMs in full games.** "Does the LLM beat always-buy?" is the anchor result every reader needs, and the bot side is free.
3. **One clean small full-game campaign**: 2–3 seeds × Latin-square seat rotation × 4 mid-tier models, replay-verified, executed through the existing `long_campaign` runner so the leaderboard/statistics/paper-report artifacts generate themselves.
4. **Reconcile Run A's replay mismatch or demote it** to a flagged qualitative case study.
5. **Collect a small human expert label set** (2 labelers × ~30 scenarios) for a rubric-validity appendix with agreement stats.
6. **Write the "Why Monopoly?" subsection** addressing luck, strategy ceiling, and the Diplomacy/Catan comparison head-on.
7. **Tighten the metric story**: one primary outcome, one variance/risk metric, cost. Everything else goes to released artifacts.
8. Housekeeping: delete or rename the blank `monopolybench.tex`; decide the trademark/naming question before public launch.

Items 1–3 are the paper. Items 4–6 are the armor. Items 7–8 are polish.

---

## 9. Closing Assessment

This is a worthy project with an unusually strong engineering foundation and a real, defensible, *time-limited* niche. What it is today is a **publishable instrument with an unpublished experiment**. The framing is right, the architecture is right, the paper skeleton is right, and the remaining distance is almost embarrassingly concrete: a few hundred dollars of API spend, a few weeks of campaign execution, and the discipline to stop building infrastructure and start generating evidence.

Stop polishing the telescope. Point it at something.

---

## Appendix: Related Work Verified During This Review

- [AgentBench](https://arxiv.org/abs/2308.03688) — general interactive agent evaluation
- [Vending-Bench](https://arxiv.org/abs/2502.15840) — long-horizon business coherence (closest framing ancestor)
- [EconEvals](https://arxiv.org/pdf/2503.18825) — economic decision-making litmus tests
- [EcoGym](https://arxiv.org/html/2602.09514v1) — long-horizon plan-and-execute in interactive economies
- [Cattle Trade](https://arxiv.org/abs/2605.14537) — auctions/bluffing/bargaining multi-agent benchmark (closest competitor)
- [AgenticPay](https://arxiv.org/abs/2602.06008) — buyer–seller negotiation benchmark
- [Game-theoretic LLM](https://arxiv.org/html/2411.05990v1) — includes a "Monopoly Game" that is an abstract matrix game, *not* the board game
- [MONOPOLY negotiation agents, IEEE 2002](https://ieeexplore.ieee.org/document/1013210) — pre-LLM Monopoly negotiation agents
- [GPT-Bargaining](https://arxiv.org/abs/2305.10142) — LLM negotiation self-play
- [TextArena](https://arxiv.org/html/2504.11442v1), [GameBench](https://arxiv.org/abs/2406.06613), [Game Reasoning Arena](https://arxiv.org/html/2508.03368v1) — general game suites; none cover Monopoly's negotiation + auction + bankruptcy combination
- [LLM agent evaluation survey](https://arxiv.org/abs/2507.21504)

**Novelty claim status: verified.** No dedicated LLM Monopoly benchmark exists as of this review.
