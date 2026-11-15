# Opus: initial position for the 11 November full-paper revision

Written on 11 November 2026, before drafting any manuscript prose and without reading the other authors' drafts in this revision (`full_drafts/astra`, `full_drafts/sol`, `full_drafts/fable_5_2` were listed, not opened). Before writing this I read the revision contract, both critique attachments, `user_review.md`, all four core assessments, the previous integrated manuscript and its evidence map, and ran a first round of existing-record tabulations (scripts in `tools/`). I record those first results here because they shaped the position; they are re-run and documented in `findings_and_limits.md` and `evidence_map.md`.

Conflict disclosure: I am Claude Opus 5.5, the same model identifier as one evaluated configuration. My earlier 11 November assessment contained one wrong figure (Sol reasoning tokens "null in 1,292 records"); the field is present in all 1,991 Sol records, with 1,296 zeros. Astra's correction stands.

## What I think the paper should claim

**Central claim (provisional): LLM agents in this four-player economy bargain defensively over the deed that would complete a rival's colour group.** The deed's value depends on who holds the rest of its group, which makes it an identity-dependent externality in the sense of Jehiel, Moldovanu and Stacchetti (1996). The agents attend to that externality, and the most consistent behavioural trace of that attention is denial, not calibrated pricing:

1. Opening offers that would complete only the proposer's group are rejected more often than opening offers that complete nobody: 138/187 versus 152/238 (+9.9 points). The sign holds in all five seed blocks, in every leave-one-block-out cut, and for each of the three recipients playing under the standard response condition. It reverses for Opus, which plays mostly under action-only recovery.
2. When a proposer repeats the same non-cash bundle with more cash for the recipient, the concession is accepted in 9/58 cases if the bundle completes the proposer's group, against 24/86 if it completes nobody. Holders counter instead.
3. Pooled asking prices are higher when the deed completes the buyer's group (median 1.63 versus 1.08 times list), and the gap is larger among standard-condition sellers (2.29 versus 1.39). The pattern is **not robust**: it holds in three of five seed blocks, and same-seller, same-game, same-deed comparisons are mixed. Buyers do not bid consistently more for deeds that complete their own group. I will present this as a heterogeneous pricing regularity, not a premium.
4. Refusals of offers that would complete the *recipient's* group cite a consequence for the rival in 61/74 records and the recipient's own cost or liquidity in 41/74 (inherited LLM-assisted codes; Cohen's kappa 0.79 and 0.78 between the two readers, recomputed from the retained ledgers). That is stated attention, not measured cognition.
5. The quantity the agents cite most, the rival's post-trade building cash, does not produce a response gradient: opening rejection of proposer-completing offers is about 75% whether or not the proposer would keep enough cash for a full layer of houses. Attention to the category (a rival completes a group) is visible; graded sensitivity to the cited quantity is not.
6. Completing deeds change hands mainly when their holder is short of cash: 14 of 22 completing cash-for-deed sales have a seller holding less than $100, against 7 of 31 other sales. Without Opus sellers it is 6/11 against 4/22. Standard-condition distressed sellers still charge a high median (2.25 times list); Opus sells near list.

This is a claim about strategic **attention and behaviour**, not effectiveness. No value reference exists to say whether a refusal or a markup was wise.

## Why this and not the alternatives

- **Rent, estate and insolvency totals** mostly follow from the rules plus exposure. They become supporting context: developed landings on trade-completed groups yield about $374 each versus $20 undeveloped; the first creditor was already the asset leader before the first estate in 15 of 20 games (and wins 18 of 20); 128 of 188 debt episodes were paid, and only 3 of 131 demonstrably payable debts ended in elimination.
- **A seller premium** is promising but not identified; I subordinate it to the denial pattern, where several independent traces agree.
- **Opponent standing** (rejecting the current leader) shows no meaningful pattern (rejection 42–47% whether author, recipient or a third party leads). I will report it briefly as a null.
- **An execution or audit paper** is not what the user asked for. Response conditions, prompt facts and defects go in a concise setup and appendices.

## Conditions that must be stated up front

- Opus: 1,604 of 1,696 decisions follow a first-attempt provider refusal with a single verbatim message about "reverse engineering or duplicating model outputs". The action-only retry keeps "Deception in public chat is allowed" and the "bluff, deceive" line. It removes the private-note field, the request that private thoughts reflect true reasoning, and the corrective retry. Refusal shares in G1–G4 are 0.76, 0.67, 0.57 and 0.73. From 16:40 UTC on 25 October every first attempt is refused. Anthropic's current Opus 5.5 page says requests that push the model to reproduce internal reasoning in response text "might be declined with the `reasoning_extraction` category". Our OpenRouter records lack the category field, so this is a plausible explanation, not a confirmed trigger. Opus still saw state and public history. Its condition also changes its opponents' market.
- Agents never receive the rules. Prices and rents appear only in purchase prompts. House variants (intact creditor inheritance, no bank auction, entry-wise build validation, no trading developed deeds) are not stated to them.
- Grok sometimes has received calls that contradict its content; history summaries are misattributed in 2,054 prompts.
- Reported reasoning tokens and the "medium" label are not a common compute measure. Recorded cost: $141.39 under a BYOK-aware single-field rule; adding the two cost fields double-counts.

## Plan

A native LaTeX paper of about 6,500–7,000 main-text words: finding-led abstract; introduction with explicit contributions; concise setup; measures; results (defensive bargaining → distress sales → development, debts, estates); eight contextual incidents placed where they illuminate mechanisms (G2, G15, G20, G13, G18, G7, G19, G12); discussion and limits; appendices with the full prompt, rules, condition details, supplementary tables and research-question coverage. All new numbers come from scripts in `tools/` that read saved records only. Quotes come from previously checked definitions, re-verified against original fields.
