# Public-review handoff: independent reference audit and first adjudications

2026-10-29. This is Astra's review of the completed public-only handoff, separate from the original reviewer's labels. Canonical games and reviewer files are unchanged. The reproducible checks are in [public_handoff_audit.py](public_handoff_audit.py) and [public_handoff_audit.json](public_handoff_audit.json).

## What is complete

The public coverage ledger contains exactly the 6,989 canonical decision IDs, without duplicates or omissions. All 441 candidate IDs are unique. Every candidate decision reference has the correct game and display number. All 1,220 quotations marked as exact substrings match the cited applied action's public message. There are no dangling candidate references in the coverage ledger. The 36 numbered shortlist entries reference 64 distinct existing candidates.

These checks establish reference integrity, not correctness of every interpretation or independent proof of semantic reading. The candidate priorities remain a single reviewer's judgments. Several narrative mistakes were corrected during extraction; all substantive paper claims still require adjudication.

The pass began with Sonnet and finished with Haiku. The coverage ledger attributes 1,367 decisions to Sonnet and 5,622 to Haiku. The directory and shortlist retain the historical Sonnet name. Cite this as a Sonnet-started, Haiku-completed public-only pass, not an all-Sonnet independent annotation. The universal notes contain the final game sections, while `progress.json` still marks game narratives 3–20 unfinished; reconcile that bookkeeping before release.

## Resolved or narrowed handoff questions

1. **G20-C019's alleged mortgage-state inconsistency is false.** At game 20 decision 310, the original prompt explicitly marks both Indiana and Illinois `mortgaged: true`. The reviewer's own compact line also contains `IND~0,ILL~0`. The mortgage events and menu agree with those records. Retain the bankruptcy arithmetic if independently supported, but remove the state-inconsistency claim. This was a review interpretation error, not a demonstrated state-builder fault.

2. **House scarcity is supported at the cited boundaries.** For G04-C015, the original prompts at decisions 189, 208, 215 and 228 show zero bank houses. These are four observations of an empty supply, not by themselves four distinct depletion episodes. For G05-C028, decision 298 starts with six houses and the build leaves five; decision 302 starts with five and leaves two; decision 305 starts with one and leaves zero. Applied `HOUSE_BUILT` events and subsequent original prompts agree. The last-house statement is supported. Claims about strategic denial or its effects need separate evidence.

3. **G20-C010 is present before engine application.** Game 20 decision 1 contains the JSON-like `private_thought` fragment in the parsed tool's `public_message`, and the applied action preserves it. A literal scan of all 6,989 applied public messages finds exactly one containing that key. This is a literal-key screen, not a semantic search for all disclosures. It does not identify whether the model, provider, or another interface component caused the malformed field, nor establish intentional disclosure or recipient reliance.

4. **G20-C003 does not establish a private-contact channel.** The action contract has no direct-message action. The prompt-memory code delivers each player's private notes only to that player. The public “DM me” invitation is real, but an invitation alone does not establish that any DM was possible or occurred. The first public $400 reference before decision 78 is Grok's decision 77 statement. The absence of an earlier recorded offer does not supply evidence of a hidden exchange. Preserve the utterance as a possible mistaken assumption about the interface; do not turn “cannot be ruled out” into a collusion finding.

5. **G12-C015 already has a constructive legal check.** The earlier [liquidation reconstruction](feasible_liquidation.json) replays the original prefix and executes five legal house-sale actions at game 12 decision 249, paying the $250 debt and leaving $43. No new owner decision is needed to establish feasibility. The full-channel mismatch evidence still prevents attributing the applied bankruptcy to a deliberate strategic choice. A feasible payment is not a counterfactual win or an optimality result.

## Rule interpretation from the implementation

The following are questions about what the recorded environment implements; they do not require changing its rules or seeking approval to interpret the code. Whether any implementation should change is a separate benchmark task, outside this audit.

- Mortgage transfer interest: `engine.py` `_trade_interest_cost` charges recipients ceil(10% of mortgage value). `_handle_bankruptcy` transfers creditor-bound deeds, their mortgage flags and buildings without that trade-interest path. The phase-1 reducers already reconciled accepted settlements and bankruptcies. Describe the implemented variant accurately; do not label agents' resulting balances as mistakes.
- Unmortgaging: `_unmortgage_cost` uses `ceil(value * 1.1)` with binary floating-point arithmetic. For values 100 and 110, the products exceed 110 and 121 by floating-point error, yielding charges 111 and 122. The report records the exact products beside integer-arithmetic expectations. This is a concrete implementation explanation, not an unresolved strategic motive. No engine fix or historical correction was made.
- Utility rent: `_count_owned` counts owned utilities regardless of their mortgage status, and `_calculate_rent` uses that count for the multiplier. Thus a mortgaged second utility can contribute to the multiplier on an unmortgaged utility. This identifies the implemented rule; it is not an external official-rule comparison.
- Chairman card: the implementation creates one $50 payment per solvent opponent. `_process_payment_queue` presents liquidation for the current unpaid entry and retains subsequent payments; `_resolve_pending_payment` processes the rest after financing. A current $50 liquidation followed by two $50 transfers is consistent with sequential payments. It does not prove a lost charge or incorrect total. Whether the prompt adequately communicates the remaining queue is a separate information-design question. The public pass's assertion that the outcome “is not changed” is not a tested counterfactual.
- An inherited building need not create a new `HOUSE_BUILT` event. A change of ownership carries the existing deed state; do not interpret an absence of construction events as missing construction without inspecting transfer semantics. The phase-1 ownership and snapshot reconciliation is relevant here.

The five accept-with-refusal cases should be linked to the existing content/tool mismatch audit, with applied actions authoritative and cause unresolved. No duplicate causal interpretation is warranted merely because the same cases were rediscovered in a public-only pass.

## Separate completed full-channel handoff: games 7–13

The [games 7–13 review](../reviewers/astra_parallel_b/index.md) reports 823 pages, 2,074 decisions, 2,696 attempts and 105 ranked candidates. Astra independently read every coverage row, checked the exact canonical decision-ID set, rehashed every cited original packet line, compared every applied action, and checked attempt counts. All matched. The reviewer's broader checks are saved in its `verification.json`; those are attributed to that reviewer rather than claimed as newly rerun here.

This completes acceptance of two review deliverables, not the overall full-channel corpus analysis or joint coauthor adjudication. Games 7–13 candidates overlap the public candidates and must not be added as independent behavioral event counts.

## Reproduction and limits

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase2_2026-10-28/astra/public_handoff_audit.py
python/.venv/bin/ruff check docs/research_raw/paper_phase2_2026-10-28/astra/public_handoff_audit.py
```

Both pass. This audit adds only downstream research files, makes no provider calls, and changes no engine, prompt, game or original annotation. The saved report hashes its source files. Exhaustive semantic adjudication of the 441 public candidates, all other reviewers' candidates, social-label denominators, recipient exposure and cross-game synthesis remain separate work.
