# Astra phase-1 research and co-writing

This is a working research record, written on October 28 local time and completed after midnight UTC. It is not the final paper. Canonical artifacts, prompts, rules and response handling are unchanged. No paid game calls, commits or deployment were made.

## Position

The user's broad capability-and-alignment question is the right motivation. The paper should connect sustained economic behavior, social conduct, and what a long-horizon evaluation must preserve to make those behaviors inspectable. The twenty games support an observational study of configured agents. They do not establish that alignment improves or deteriorates as model capability increases. The latter remains a research question that the environment can support through future controlled comparisons.

Economic trajectories and social behavior share one record. Negotiation changes assets and liquidity, which changes later choices and incentives. We should not decide the social findings before the exhaustive review. Nor should we equate winning, legal aggressive competition, provider refusal, or a generated private explanation with a general alignment score.

## Work I performed independently

`checkpoint_audit.py` reconstructs cash, all deed owners, mortgages, houses, hotels and bank building inventory directly from events. It imports neither another researcher's reducer nor the engine. It agrees with every one of the 6,989 saved decision observations. Seven hand-specified tests cover the relevant accounting boundaries, including creditor inheritance, bank return and physical building stock.

`visibility_inventory.py` enumerates all 54,510 files in the twenty run directories, links every applied action to its started/resolved decision, and inventories all 8,679 physical responses and ledger attempts. It distinguishes public text, model private notes, deterministic fallback notes, provider text, summaries and encrypted fields. Eight focused tests check those distinctions. File availability remains separate from semantic review.

`memory_audit.py` independently reconstructs private memory from the last ten note events and their originating decisions. All 6,989 windows agree with the recorded prompts. All 1,690 explicit retry memories match the initial memory. The first attempt references the initial decision record because the resolver intentionally avoids storing the duplicate prompt there. Five tests cover provenance, expiry, player separation and missing records.

This confirms Opus's new memory counts without classifying a literal string as its provenance. Of 1,696 Opus decision prompts, 1,108 have empty private memory, 286 contain only synthetic notes, and 302 contain model-authored notes. The synthetic entries were exposed 1,108 times. This is a property of the recorded context, not a measured loss of strategic ability.

`prepare_behavior_review.py` creates chronological packets and a pending review ledger. It retains every event, decision, attempt and physical-response reference, with explicit handling of the three physical response envelopes not equal to the ledger's raw-response value. Four tests check event coverage, large records, opaque fields and safe deduplication. The result has 1,259 packets. These are reading aids, not independent episodes or reviewed cases.

I wrote `methods_draft.tex`, the proposed review contract, and the shared `reproduce_phase1.py` entry point. I read Sol's and Opus's implementations and methods proposals, reviewed the relevant engine, prompting, response-recovery and replay code, and challenged their interpretations directly. The integrated command has been run successfully with Sol, Astra and Opus analyses. Its logs attribute each check to the implementation that performed it. My 24 focused tests pass; the integration also ran Sol's 31 and Opus's 20 tests successfully. Sol round 2 adds four delivery tests to the final command.

## Findings established jointly

Three independent economic implementations agree on the core accounting. The primary cohort contains 20 games, 50,918 events and 6,989 decisions. There are 113 settlements, with group completion for neither, one or both sides in 60, 43 and 10 trades. Acquisition routes are 475 direct deed purchases, 72 auctions, 397 creditor inheritances and 207 traded deed transfers.

The 209 complete-group episodes include 63 completed through a trade. Forty-three receive development in their first actual management turn; 34 of the 42 groups buildable at entry are developed in that turn. These are separate measures. Acquisition, financing, jail/access choices, legal menus and survival remain part of the full trajectory. A legal build that was not chosen is not automatically a strategic mistake.

Opus's independently checked settlement payloads distinguish the original negotiation initiator from the accepted terms' author. Those roles differ in 44 of 113 settlements. Its snapshot audit reconciles all 10,235 saved snapshots. Sixty-nine inherited group episodes arise only at the final bankruptcy and cannot support a later-deployment comparison.

The response inventory corrects old readiness claims. Grok has 139 selected-response action-name disagreements. Twenty-six share public messages, but only fifteen share complete normalized arguments. Opus has 1,605 refusal attempts; its 152 private-note events include 61 synthetic fallback notes. The refusals state a Terms of Service restriction concerning reverse engineering or duplicated outputs. They do not establish a moral objection to deception, and recovery changes both prompt and schema.

Sol's second audit distinguishes canonical speech from timeline representation and actual delivery. It finds 94 building-merge omissions and 55 bankruptcy-message omissions among 6,882 nonempty public utterances. This is an occurrence-level result about the timeline, not proof of total semantic nonexposure. Earlier delivery, later repetitions, local trade context and private-note carry-forward must be considered in each influence claim. An externally observable broken commitment remains codable even when its text is absent from the latest prompt.

Opus tested existing replay/recovery components at twenty mid-game decision prefixes. Each reproduces the recorded prefix, pending decision, memory and recorded continuation, then supports a different legal action. The subsequent reference-policy continuations include one rollout truncated at the decision budget. This is implemented simulation and branching support. It is not a packaged RL adapter, a training result or a new LLM continuation experiment. Full memory reconstruction across all decisions is a separate, broader check than the twenty branch tests.

## Accepted objections and remaining judgment

I accepted that conditional deployment rates need unconditional player-game context; terminal inheritance needs separate treatment; final offer authorship can reverse; and memory/retry handling affects interpretation of sustained capability, not only access to explanations. I strengthened the sandbox description after inspecting Opus's tests.

Sol's objection about selected evidence is important. Per-channel denominators do not recover comparable underlying behavior rates when missing notes depend on response treatment and trajectory. Use common public/state conduct, evidence-qualified subsets, model-specific cases and explicit unknowns. No missing-at-random assumption is warranted. Removing a flagged episode does not give a repaired trajectory or a counterfactual bound.

My remaining wording objection is to calling provider-policy recovery itself an observed capability-alignment tradeoff. We observe changed note production, future context and retry mechanics. We have not measured the triggering policy feature, a change in alignment, or an effect on winning. A concise main-text account supports the broader evaluation question without making the interface conditions the paper's main story.

The review contract retains factual falsity, misleading implication, contemporaneous self-contradiction, exposure, reliance and intent as separate dimensions. Intent can remain unresolved. Strong labels need independent initial judgments and adjudication; LLM reviewer agreement must not be described as independent human annotation. This cohort has already been explored, so a later frozen codebook is not preregistration.

## What remains

Fable's completed work adds an independent reducer with 35 tests, bankruptcy-payload predictions, jail-card reconciliation at all 27,956 player observations, management access by own turn and candidate surrender screens. Its settlement and route results agree with the other implementations. I accepted the configuration clarification that Opus 4.8 never played and the requirement to check financing feasibility before calling a bankruptcy voluntary. Three arithmetic-bound candidates still need legal-sequence and behavioral review.

Two Fable proposals need careful wording. A state's objective truth and what the speaker could know are separate dimensions; unknown hidden state cannot establish deliberate deception. Earlier exposure can matter even if a statement is absent from the prompt at a later action. The revised contract preserves these distinctions. Purchase/auction completion is a final-deed route, not proof that no constituent deed came from trading. Likewise, 1,604 recovery chains include 60 deterministic fallbacks; only 1,544 selected valid actions came from the action-only recovery. Avoid calling all 1,604 applied public messages model-generated under that condition.

All four phase-1 reports are now incorporated. Pilot the review codebook and proceed through every prepared unit using extraction agents, preserving context across packets. The four researchers jointly interpret and write all findings. Subsequent literature comparison, figures, outline and manuscript should follow the supported evidence, with extra experiments tied to specific claims. The exhaustive behavioral review has not yet been performed.
