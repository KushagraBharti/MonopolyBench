"""Additional local checks independent of bundled certificate tests."""
from collections import defaultdict
import copy
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from adversarial_checks import AUDIT, OUT, audit, restore


def arm(engine, amount):
    engine._started = True
    engine.state.phase = "RUNNING"
    player = engine.state.players[0]
    payment = {"amount": amount, "reason": "TAX", "to_player_id": None}
    events = []
    decision = engine._request_payment(player, payment, events, turn_index=0, rolled_double=False)
    engine._activate_debt_decision(decision, events)
    return decision


def dedup_diamond():
    engine = audit.Engine(**audit.read(AUDIT / "inputs/g01/config.json"))
    player = engine.state.players[0]
    player.cash = 0
    for index in [1, 3, 5]:
        engine.state.board[index].owner_id = player.player_id
    decision = arm(engine, 1000)
    exhaustive = audit.exhaustive_financing(engine, decision, player.player_id, 1000)
    signatures, paths, terminal = defaultdict(list), 0, 0
    stack = [(engine, decision)]
    while stack:
        current, pending = stack.pop()
        paths += 1
        key = audit.reachable_state_key(current, player.player_id)
        signature = {"menu": pending["liquidation"], "payment": current._pending_payment,
                     "actions": pending["legal_actions"]}
        signatures[key].append(signature)
        for name, args in audit.liquidation_actions(current, pending):
            successor = copy.deepcopy(current)
            nxt, step = audit.apply_checked(successor, pending, name, args)
            assert not audit.payment_in(step["events"], player.player_id, 1000)
            if audit.actor(successor, player.player_id).bankrupt:
                terminal += 1
            else:
                stack.append((successor, nxt))
    assert len(signatures) == exhaustive["state_count"] == 7
    for group in signatures.values():
        assert all(s == group[0] for s in group)
    assert not exhaustive["paid"] and exhaustive["exhausted"]
    return {"nonterminal_paths_without_dedup": paths, "unique_states": len(signatures),
            "terminal_paths": terminal, "equal_keys_have_equal_menus_and_pending_debt": True}


def bound_at_historical_successors():
    count, sale_count, mortgage_count = 0, 0, 0
    for case in audit.read(AUDIT / "cases.json"):
        if case["kind"] != "elimination":
            continue
        engine, decision, _ = restore(case["case_id"])
        before = audit.bound(engine, case["actor"])["full_upper"]
        debt = decision["liquidation"]["owed_amount"]
        for name, args in audit.liquidation_actions(engine, decision):
            successor = copy.deepcopy(engine)
            _, step = audit.apply_checked(successor, decision, name, args)
            count += 1
            sale_count += name == "sell_houses_or_hotel"
            mortgage_count += name == "mortgage_property"
            after = audit.bound(successor, case["actor"])["full_upper"]
            paid = audit.payment_in(step["events"], case["actor"], debt)
            if not audit.actor(successor, case["actor"]).bankrupt:
                assert after == before - (debt if paid else 0), (case["case_id"], before, after, debt, name)
            else:
                assert after <= before
    return {"historical_prefix_successors": count, "sale_successors": sale_count,
            "mortgage_successors": mortgage_count, "potential_never_increases": True}


def malformed_and_payment_predicate():
    engine, decision, case = restore("G02-dec-000075-default")
    source = next(a["plan"] for a in case["attempts"] if "plan" in a)
    rejected = {}
    for label, value in [("boolean", True), ("float", 3.0), ("zero", 0), ("negative", -1), ("string", "3")]:
        plan = copy.deepcopy(source)
        plan[0]["count"] = value
        try:
            audit.multiset(plan)
        except ValueError as error:
            rejected[label] = str(error)
        else:
            raise AssertionError(label)
    plan = copy.deepcopy(source)
    plan[0]["space_key"] = "NOT_A_DEED"
    altered = copy.deepcopy(case)
    altered["attempts"] = [{"plan": plan}]
    result = audit.check_default(engine, decision, altered)
    assert result["attempts"][0]["diagnostic"] == "malformed_target"
    # This helper is not an independent certificate verifier. It relies on live
    # financing execution for event provenance and the payment reason.
    invented = [{"type": "CASH_CHANGED", "payload": {"player_id": "p1", "delta": -500, "reason": "BUILD"}}]
    assert audit.payment_in(invented, "p1", 500)
    assert not audit.payment_in([{ "type": "CASH_CHANGED", "payload": {"player_id": "p1", "delta": -500, "reason": "BANKRUPTCY_CASH"}}], "p1", 500)
    return {"malformed_counts_rejected": rejected, "unknown_deed_rejected": True,
            "payment_helper_accepts_unrelated_same_amount_cash_debit": True,
            "scope": "Not exploitable by the checked live mortgage/sale witnesses; not suitable for validating arbitrary supplied event lists."}


if __name__ == "__main__":
    result = {"dedup": dedup_diamond(), "bound": bound_at_historical_successors(),
              "input_rejection_and_payment_scope": malformed_and_payment_predicate()}
    (OUT / "extra_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
