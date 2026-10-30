# Sol round 2, research challenge and co-writing

2026-10-28, with verification completed in the following UTC date. All new work is under this directory. I read the repository AGENTS.md, the prior Sol phase-one memo and outputs, Astra's methods draft and review contract v2, the current Opus reports and tests, and relevant prompting and response-policy code. I debated the new findings directly with Astra, Opus and Fable during their running turns. No agents, games, provider calls, commits, deployment, canonical artifact changes, prompt changes or rules changes were made.

## Research framing

The question should remain broad and concrete: how agents sustain economic capability and social behavior across extended competitive interactions, how those behaviors affect other participants, and how to evaluate the relationship as capabilities improve. Acquisition, liquidity, development, bargaining, assurances, targeting, deception and adaptation all concern the same evolving game. Social conduct is a central subject of the review. Missing private reasoning does not justify restricting the paper to economics or a single anecdote.

The cohort supports descriptive analysis of configured agents. It does not identify a capability-growth trend, general model intelligence, or a scalar alignment ordering. These limits should specify the claim, rather than overwhelm it. The paper can lead with an observed profile and a sourced interaction, then explain which records permit inspection. Detailed response chains belong in the supplement unless needed to interpret a finding.

The capability profile should retain the whole trajectory: assembly, liquidity, access choices, deployment, receipts, loss and outcome. Opus reports early first non-inherited group assembly and slower conversion relative to Sol and Gemini. That is a useful candidate finding. It is not a claim that Opus deploys least, since Grok's entry-eligible rate is lower. An unbuilt group can reflect restraint, competing objectives, scarce capital, an interface discrepancy, or an execution failure. The G13 Opus win despite 38 legal light-blue turns without development is an essential counterexample to treating each missed building opportunity as an error.

The observed response-policy interaction deserves concise main-text treatment. A provider block changes recovery instructions and the tool schema, which changes note production, later memory context, and retry handling. The mechanics are evidenced. Their effect on economic capability is not identified. This is research content about the configured system, not simply an implementation disclosure. It must not become the paper's main story before the exhaustive economic and social review establishes its findings.

The retained instruction permits public deception and requests honest private notes. Alignment-relevant analysis can therefore ask about factual misrepresentation, misleading framing, assurances, commitment breaches, coordination and effects on other participants. It must state the norm being evaluated and distinguish it from instructions actually imposed. Legal aggressive play is not automatically misalignment. A game score is not an alignment score. A generated private note can support an interpretation but cannot certify honest reasoning or reveal latent computation.

## New finding, public speech and actual delivery differ before eviction

`public_delivery_audit.py` attaches occurrence provenance externally to the existing `PromptMemory`. The production memory dictionaries remain unchanged. The audit matches the saved initial public and private memory at all 6,989 decisions and checks each attributed displayed message against its canonical source's speaker, turn and exact text. Four focused tests independently specify the relevant merge and bankruptcy behavior. The generated source manifest includes canonical input hashes, prompting source hash and analysis code hashes.

The 6,989 canonical public-message events include 6,882 nonempty utterances. Among these:

- 6,733 enter public timeline memory at least once.
- 94 are omitted when consecutive same-player, same-turn building summaries merge and retain an earlier nonempty message.
- 55 are omitted after a bankruptcy message is claimed at a `CASH_CHANGED` event with reason `BANKRUPTCY_CASH`. That event is not summarized; the later `BANKRUPTCY` marker no longer has the message attached.
- Of the 6,733 inserted occurrences, 6,720 have an observed later delivery to at least one opponent through timeline memory. Thirteen inserted occurrences have no such observed opponent delivery. This audit does not attribute all thirteen to a single mechanism.

The units are source message occurrences. They are not unique strings, distinct summary items, social findings or instances of recipient awareness. Window eviction is not the only reason a canonical statement can be missing from a recipient's prompt. Conversely, an omitted occurrence can have its text or meaning repeated elsewhere, including another utterance or a private note. The audit does not claim total semantic nonexposure.

The bankruptcy mechanism matters to the social review. In G1, Opus decision ending `dec-000315`, public event ending `evt-002177`, says, "Vermont hotel finishes me. GG all. p2 and p4, p3 is the one to stop. Work together." Its source occurrence never enters the timeline. This remains a recorded anti-leader appeal, pending semantic review of its context. The event by itself cannot establish that p2 or p4 received it, coordinated because of it, or that the speaker intended kingmaking. Its message and full references are retained in `public_delivery.jsonl`.

The instrumentation imports current prompting code. Exact equality to all saved memory windows supports its use on this corpus. It is an audit of delivered representations, not a new engine, an independent proof of production correctness, or evidence that changing delivery would change winners. No canonical fix was made or proposed for these finished games.

## Direct debate and changes of position

Astra's strongest objection to my early denominator proposal was that equal channels do not imply equal strategic opportunities, and a carefully sourced model-specific case remains valid without comparable private evidence from other models. Accepted. Common public, action and state evidence supports a common recorded-conduct layer. It does not justify a latent prevalence comparison. Report raw counts, trajectories, opportunities and evidence-qualified subsets distinctly. Keep private/provider channels as corroboration and as sources of model-specific cases.

Opus's strongest objection was that our caveats were obscuring the capability-and-alignment question and understating implemented branching. Accepted in part. Existing recovery reconstructs the live engine, hidden RNG/decks and prompt memory through action/event replay. My prior memo discussed snapshot-only restore too narrowly. Opus's new checks at twenty representative prefixes reproduce prefixes, memory and recorded next events, and execute an alternate legal action. Nineteen reference-policy rollouts reach bankruptcy; G6 reaches the 20,000-decision test budget. These are positive implemented simulation affordances. They do not need stochastic LLM experiments to count as implemented affordances. A packaged branch interface, RL adapter, training gains, universal empirical prefix coverage, full prompt equivalence and provider continuations remain separate claims.

I challenged Opus's initial phrase that a provider safety response rejected a prompt licensing deception. Opus checked all refused attempts and withdrew that attribution. The reported identical refusal text concerns a provider Terms of Service restriction on reverse engineering or duplication of model outputs. The triggering feature remains unidentified. Recovery changes instructions and schema together. Seed block and source overlap with refusal frequency. The records support the recovery and memory mechanics, not moral motivation, a single-feature trigger, or a causal capability deficit.

I also challenged a proposed Grok sensitivity range. Removing flagged decisions or episodes changes the selected population. It does not bound what a repaired Grok would do. Opus accepted reporting an episode-level flag table, original denominators and selected-subset descriptions without repairing outcomes. Preserve the actual applied path. Content/tool discrepancies are neither intended actions nor a substitute counterfactual.

Opus independently tested a possible provenance objection: stale end-turn queues might attach a message under the wrong actor or turn. Its saved-prompt audit found every one of 6,725 distinct displayed message items matched canonical speaker, turn and action type. It also found the opening proposal message present at all 920 trade-response decisions. These are distinct units from this audit's occurrence counts. They support local attribution and observed within-thread opening exposure; they do not settle later cross-thread commitments or semantic reliance.

Two remaining interpretive objections to Opus are retained here because its turn ended before my attempted reply could be delivered. I did not restart it. First, a timeline omission is not proof that a message was never model-visible anywhere. The speaker authored it, and notes or later messages may repeat its content. Second, an observable inconsistency or broken commitment does not cease to exist because the previous statement is absent from the speaker's latest prompt. Current availability matters to claims of knowing breach, forgetting and mechanism. Requiring it for the conduct label would erase some long-horizon failures by definition. I delivered both points to Astra and Fable for joint integration.

Exposure is a temporal record. A recipient may receive a statement in an earlier prompt and act on it through intervening choices, notes or changed incentives after the text has left the latest prompt. Record first and last relevant delivery, current availability, and possible carry-forward paths separately. Earlier delivery alone is not proof of reliance. Latest-prompt absence alone does not rule out influence.

## Measures and validation that still need restraint

Conditional first-management deployment is descriptive of reached opportunities. Access, survival, financing and group assembly can depend on earlier agent choices. Pair the conditional quantity with elapsed access choices and all player-games, including those with no non-inherited group. Do not statistically adjust away these choices and then call the remainder general capability. Entry eligibility means at least one legal purchase, not full-plan affordability or optimality.

Final-acquisition routes identify the event that completes a group. They do not summarize all constituent acquisition histories. Keep original negotiation initiator, final-terms author, acceptor and per-asset transfer roles. Interest-inclusive settlements, terminal inheritance, pre-existing development, ownership loss and reacquisition remain part of the ledger. The 69 terminal inheritance episodes cannot supply deployment follow-up; the 52 midgame inheritance episodes are not a homogeneous comparison group, and 14 already have development. Realized rent has endogenous exposure and observation length. Neither group completion nor eventual rents alone validate trade quality or an economically optimal strategy.

Long-horizon evaluation needs units and linked behavior. Global turn index, own turns, decisions and management opportunities differ. A long game record alone does not establish long-term planning. Record an earlier plan or commitment, an intervening challenge, the information subsequently available, the later choice and its consequences. Failure and successful restraint both belong in the review. Do not infer a memory failure solely because a later action contradicts a note or a declaration.

The five seed blocks and cyclic rotations balance absolute seats in this roster. They preserve relative opponent order, contain one realization per cell, and do not isolate seed/source effects. Shared raw dice prefixes can have different uses after choices diverge. Thousands of decisions are not independent replications. Game and block-level context should precede any uncertainty calculation or generalization. No additional paid games are needed merely to describe this fixed corpus. A stronger causal or capability-growth claim would need its own design.

Accounting reconciliation validates agreement among retained economic records. Prompt equality validates delivered context reconstruction. These do not validate social labels, strategic optimality, transfer to real institutions or arbitrary code security. Describe this as an inspectable economic game sandbox. Specify its rules variant and observation limits. Do not claim rules-complete classic Monopoly, a secure arbitrary-agent execution system, or an empirically validated real-world economy.

## Exhaustive review and joint writing

Keep the full scope of the planned phase-two extraction: all twenty games, all applied decisions, every attempt, all available public/private/provider fields, and linked events and consequences. Maintain a neutral chronological ledger and a separate candidate-salience field. A processed file or generated packet is not a completed semantic review. Stable case IDs must survive chunk overlap, cross-thread links, later consequences and disagreements. An attempt that never becomes an applied action still has an explicit status.

The category set should remain open to planning and adaptation, auctions, liquidity, acquisition and development, cooperation, coordination, assurances, breaches, factual falsity, misleading framing, targeting, manipulation, collusion, kingmaking, failures, restraint and unexpected behavior. These are candidate labels with different evidence requirements, not assertions that every category exists. Silent messages, unsuccessful attempts, honored promises, ordinary competition and successful non-trade routes are part of the evidence.

Freeze definitions after a pilot, preserve independent first judgments, and double-code strong or disputed cases plus a declared sample of initially unflagged records across models, phases and decision types. Record missed candidates and reasons for adjudication changes. If a definition changes, recode affected earlier cases. Do not describe LLM extraction/researcher agreement as independent human annotation or call a codebook frozen after seeing these games preregistered. Four researchers jointly interpret and write every part; extraction agents do not own final labels or sections.

No venue is assumed. Keep the central contribution tied to an evidenced combination of inspectable trajectories, social/economic analysis and tested simulation affordances. A later related-work pass should verify each claimed comparison using primary sources. This round does not make a new priority or superiority claim over other benchmarks.

For future RL, distinguish the acting policy's observation from hidden simulator state and analyst evidence. Define actions, reward, opponent policy, termination/truncation and train/evaluation separation before training. A terminal winning reward supports competition under the stated rules; it does not make all learned conduct aligned. Social labels used in reward construction need held-out evaluation and must not silently become acting-policy context. Exact reset supports experiments; demonstration of training improvement requires an actual training study. These are proposals, not new work performed here.

## Concrete handoff and verification

`methods_revisions.tex` supplies insertable prose for Astra's methods draft, rather than silently editing a peer-owned draft. `review_contract_additions.json` supplies a proposed delta to contract v2. It adds speech/summary/delivery distinctions, temporal exposure, same-speaker availability, selected-population rules, norm provenance, completeness states and adjudication records. Both retain the whole economic and social scope.

`public_delivery.jsonl` contains all 6,989 message occurrences and first observed opponent timeline prompts. `merged_public_messages.jsonl` contains the 94 merge omissions with source and retained-message references. `public_delivery_summary.json` retains aggregate counts and hashes. `verification.log` records four passing focused tests and clean Ruff output; `reproduction.log` records the audit run. The JSON delta parses successfully. Full repository behavioral tests were not rerun because no engine, arena, protocol or canonical artifact was edited.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python -m pytest -q -p no:cacheprovider docs/research_raw/paper_phase1_2026-10-28/sol_round2
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase1_2026-10-28/sol_round2/public_delivery_audit.py
python/.venv/bin/ruff check --no-cache docs/research_raw/paper_phase1_2026-10-28/sol_round2
```

The exhaustive behavioral review remains pending. The useful next work is complete extraction and joint interpretation under the revised evidence rules. Further experiments should follow from the specific claim that survives that review.
