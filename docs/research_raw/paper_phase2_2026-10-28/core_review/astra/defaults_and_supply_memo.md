# Construction attempts, defaults and scarce houses

Status: targeted original-artifact adjudication, not completion of the full candidate review. This audit was prompted by Opus's new results, which I read before implementing the checks. The implementation is independent of Opus's code; the hypothesis and expected counts were peer-informed. No blind-replication claim is made.

## Defaulted construction requests

I selected all fallback resolutions directly from the original decision packets, reconstructed their recorded engine prefixes and verified canonical event equality. There are 66 decisions: 61 Opus, four Sol and one Gemini. Every one is a post-turn decision with construction available, contains a parsed build request, and ends with the deterministic `end_turn` and synthetic private note `fallback`.

For each parsed build plan, `check_default_build_plans.py` expands purchases into single-piece operations. A finite search keeps every requested house/hotel purchase and its property unchanged, preserves the within-property house-before-hotel order, and uses the engine to validate each cumulative prefix. For successful sequences, a deep-copied exact engine executes the final plan. The check asserts the exact cost, final development levels and purchase multiset. It stops immediately after building. This does not repair the historical trajectory or predict the next model action or winner.

**All 61 Opus requested allocations execute legally after reordering/splitting operations.** The smallest cash margin after construction is $11. Their rejected plans are therefore feasible immediate allocations at the recorded states, even though their submitted operation sequences are invalid. The observed chain is an attempted construction followed by validation failure and a default, not a model-chosen decision to refrain from construction. The original outcomes remain part of the configured-agent evaluation.

The other five decisions show why this check is necessary. Of eight Sol build attempts across four defaults, seven requested unaffordable allocations. At G4 d174, the initial seven-house allocation costs $700 against $705 cash and is feasible after interleaving; the corrective response instead requests twelve houses costing $1,200 and remains invalid. G4 d136 and G5 d276/d278 each contain unaffordable nine-house pink plans. Gemini G19 d231 has a feasible seven-house first allocation, followed by a malformed corrective plan. The first validation error can mask further faults. A logged uneven-building error does not by itself establish that reordering is sufficient.

The full output is `default_build_plans.json`, with original attempt arguments, error chains, legal alternatives, branch events and source hashes. All replay and construction assertions pass; Ruff passes. No engine, prompt, retry policy or saved run changed.

## Counting repeated opportunities

I challenged Opus's initial 94/98 skipped-turn aggregate because separate groups can share the same own turn, and a failed plan need not mention every buildable group. Opus accepted and reported the following corrected units in `../opus/h1_episode_skips_v2.log`: 98 skipped group-turns correspond to 65 distinct own turns; 61 distinct turns contain defaults; 94 group-turns contain defaults; 87 of those include an attempted purchase in the focal group. In trade-completed groups, 42 of 44 default-containing group-turns include the focal group. These are peer-derived joins, not yet independently reproduced here. Do not present 94 as a count of separate decisions or apply its denominator to a decision-level rate.

A group can remain undeveloped because an attempt on that group failed, because another group's failed action terminated the shared turn, or because the agent ended its turn without an attempted build. These have different behavioral interpretations. Retain full observed trajectories and report the mechanism separately; deleting default turns would condition away part of configured-agent capability.

The G5 comparison of actual $12 Oriental receipts with a three-house $270 schedule is a local rent-schedule comparison on observed landings. It is not counterfactual realized income: construction would change cash, rents, decisions and potentially the later path.

## House-supply constraint versus competing causes

Sol challenged housing-denial examples where cash, mortgages or a pre-existing hotel-sale restriction might explain the result. `check_supply_constraint.py` restores two exact prefixes and tests narrowly specified predicates.

- **G4 d252:** Grok holds pinks at two houses each, $472 cash, and an empty bank house supply. One additional Virginia house fails with `Bank houses exhausted during build plan`. In an explicitly artificial diagnostic copy, changing bank supply from zero to one makes the same $100 purchase legal. Grok itself holds 18 of the 32 houses and could consider releasing its own orange houses via hotels; its note explicitly favors retention to constrain competitors. This is mutual scarcity and a chosen tradeoff, not proof it lacks every possible path to more pink houses.
- **G14 d220:** Grok has $642 and mortgaged Park Place, so its entry state does not offer dark-blue construction even if we only inspect house supply. However, Park Place redemption is legally available and costs $193. Executing that redemption in memory leaves $449 and another post-turn decision. One $200 Park Place house then fails only on house supply; the artificial one-house relaxation makes it legal. Thus this is a supply constraint after feasible financing, not entry-menu eligibility. Its actual note names both supply and the risks of deploying its cash. The audit does not establish it would build if supply returned.

The artificial supply relaxation is deliberately not described as a valid alternative historical game: it adds a bank house without a corresponding player transaction. It is a local predicate diagnostic. No action is applied after that artificial change. The paper may use it to distinguish rule constraints, not estimate an opponent's causal contribution or a different winner. Actual supply holders, possible hotel conversions, self-liquidation, liquidity preferences and preceding choices remain necessary context.

An exploratory mechanical scan of public-state predicates produced `supply_screen.json`. Those hits are group/decision candidates, including agents constrained by their own holdings; they are neither distinct denial episodes nor new semantic labels. The two exact checks above are the adjudicated scope.

## Proposed interpretation

Long-horizon economic performance requires more than acquiring a set or naming a profitable development plan. The agent must express a legal operation sequence, receive useful feedback and retain access to cash and physical inventory. This corpus illustrates each layer, but it does not isolate their causal contributions or estimate performance under a repaired harness. Applied outcomes remain authoritative; attempted actions, validation feedback and legal alternatives explain why superficially similar end-turns can mean different things.
