"""Execute the frozen finite-corpus audit using only this directory's inputs.

No model calls, new games, repaired historical suffixes, or prompt reconstruction.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
from monopoly_engine import Engine  # noqa: E402
from monopoly_engine.board import HOUSE_COST_BY_GROUP, SPACE_KEY_BY_INDEX  # noqa: E402


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    return json.loads(path.read_text())


def check_inputs():
    for name, expected in read(HERE / "inputs_manifest.json")["files"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Input hash mismatch: {name}")


def actor(engine, player_id):
    return next(p for p in engine.state.players if p.player_id == player_id)


def action(decision, name, args):
    return {"schema_version": "v1", "decision_id": decision["decision_id"],
            "action": name, "args": args}


def apply_checked(engine, decision, name, args):
    move = action(decision, name, args)
    errors = engine.validate_action_for_decision(move, decision)
    if errors:
        raise ValueError(json.dumps(errors))
    _, events, pending, _ = engine.apply_action(move)
    if any(e["type"] == "ACTION_REJECTED" for e in events):
        raise ValueError("Engine rejected a supposedly validated action")
    return pending, {"action": name, "args": args, "decision_id": move["decision_id"],
                     "events": events, "events_sha256": sha(events)}


def multiset(plan):
    if not isinstance(plan, list) or not plan:
        raise ValueError("Missing build-plan list")
    counts = Counter()
    for row in plan:
        if not isinstance(row, dict) or row.get("kind") not in {"HOUSE", "HOTEL"}:
            raise ValueError("Invalid construction operation")
        if type(row.get("count")) is not int or row["count"] < 1:
            raise ValueError("Invalid construction count")
        counts[(row["space_key"], row["kind"])] += row["count"]
    return sorted([key, kind, count] for (key, kind), count in counts.items())


def atomic_plan(engine, plan):
    """One constructive ordering, not a complete solver for arbitrary plans."""
    spaces = {SPACE_KEY_BY_INDEX[s.index]: s for s in engine.state.board}
    levels = {key: 5 if s.hotel else s.houses for key, s in spaces.items()}
    grouped = {}
    for row in plan:
        key = row["space_key"]
        group = grouped.setdefault(spaces[key].group, defaultdict(list))
        group[key].extend([row["kind"]] * row["count"])
    ordered = []
    for queue in grouped.values():
        while queue:
            key = min(queue, key=lambda item: (levels[item], item))
            kind = queue[key].pop(0)
            ordered.append({"space_key": key, "kind": kind, "count": 1})
            levels[key] = 5 if kind == "HOTEL" else levels[key] + 1
            if not queue[key]:
                del queue[key]
    if multiset(ordered) != multiset(plan):
        raise ValueError("Repair changed the purchase multiset")
    return ordered


def build_trial(engine, decision, plan):
    branch = copy.deepcopy(engine)
    try:
        _, result = apply_checked(branch, decision, "build_houses_or_hotel", {"build_plan": plan})
    except (ValueError, KeyError, TypeError) as exc:
        return {"legal": False, "error": str(exc)}
    return {"legal": True, "cash_after": actor(branch, decision["player_id"]).cash,
            "operation": result}


def check_default(engine, decision, case):
    player = actor(engine, case["actor"])
    spaces = {SPACE_KEY_BY_INDEX[s.index]: s for s in engine.state.board}
    attempts = []
    for saved in case["attempts"]:
        row = copy.deepcopy(saved)
        if "plan" not in row:
            row["diagnostic"] = "no_parseable_target"
        else:
            try:
                purchase_multiset = multiset(row["plan"])
                ordered = atomic_plan(engine, row["plan"])
                cost = sum(HOUSE_COST_BY_GROUP[spaces[key].group] * count
                           for key, _, count in purchase_multiset)
                row.update({"target_multiset": purchase_multiset, "target_cost": cost,
                            "cash_before": player.cash,
                            "as_encoded": build_trial(engine, decision, row["plan"]),
                            "atomic_plan": ordered,
                            "atomic_execution": build_trial(engine, decision, ordered)})
                if row["atomic_execution"]["legal"]:
                    row["diagnostic"] = "reachable_target"
                elif cost > player.cash:
                    row["diagnostic"] = "insufficient_cash_without_financing"
                else:
                    row["diagnostic"] = "unresolved_by_constructive_order"
            except (ValueError, KeyError, TypeError) as exc:
                row["diagnostic"] = "malformed_target"
                row["diagnostic_error"] = str(exc)
        attempts.append(row)
    alternative = None
    for key, space in spaces.items():
        if space.owner_id != case["actor"] or space.group is None:
            continue
        for kind in ("HOUSE", "HOTEL"):
            plan = [{"space_key": key, "kind": kind, "count": 1}]
            test = build_trial(engine, decision, plan)
            if test["legal"]:
                alternative = {"plan": plan, "execution": test}
                break
        if alternative:
            break
    return {"case_id": case["case_id"], "kind": case["kind"], "game": case["game"],
            "model": case["model"], "actor": case["actor"], "decision_id": case["decision_id"],
            "attempts": attempts, "any_recorded_target_reachable": any(
                row["diagnostic"] == "reachable_target" for row in attempts),
            "smaller_legal_construction": alternative,
            "claim_scope": "Same historical decision; split/reorder atomic purchases only, no added finance or changed target."}


def bound(engine, player_id):
    player = actor(engine, player_id)
    estate = []
    for space in engine.state.board:
        if space.owner_id != player_id:
            continue
        level = 5 if space.hotel else space.houses
        estate.append({"key": SPACE_KEY_BY_INDEX[space.index], "level": level,
                       "salvage": level * (HOUSE_COST_BY_GROUP.get(space.group, 0) // 2),
                       "unmortgaged_capacity": 0 if space.mortgaged else space.price // 2})
    return {"cash": player.cash, "estate": estate,
            "full_upper": player.cash + sum(s["salvage"] + s["unmortgaged_capacity"] for s in estate)}


def liquidation_actions(engine, decision):
    """Atomic candidates; not a complete generator of legal bundled sales."""
    options = decision["liquidation"]["options"]
    moves = []
    for index in options["sellable_building_space_indices"]:
        kind = "HOTEL" if engine.state.board[index].hotel else "HOUSE"
        moves.append(("sell_houses_or_hotel", {"sell_plan": [
            {"space_key": SPACE_KEY_BY_INDEX[index], "kind": kind, "count": 1}]}))
    for index in options["mortgageable_space_indices"]:
        moves.append(("mortgage_property", {"space_key": SPACE_KEY_BY_INDEX[index]}))
    return moves


def payment_in(events, player_id, debt):
    return any(e["type"] == "CASH_CHANGED" and e["payload"].get("player_id") == player_id
               and e["payload"].get("delta") == -debt
               and e["payload"].get("reason") not in {"BANKRUPTCY", "BANKRUPTCY_CASH"}
               for e in events)


def reachable_state_key(engine, player_id):
    # With no exogenous action or time advancement, these determine every allowed
    # financing successor. Event counters are deliberately excluded from the key.
    return sha({"cash": actor(engine, player_id).cash,
                "estate": [(s.index, s.owner_id, s.houses, s.hotel, s.mortgaged) for s in engine.state.board],
                "bank": engine.get_snapshot()["bank"]})


def greedy_payment(engine, decision, player_id, debt):
    branch = copy.deepcopy(engine)
    pending = copy.deepcopy(decision)
    steps = []
    while pending and pending["decision_type"] == "LIQUIDATION_DECISION" and pending["player_id"] == player_id:
        moves = liquidation_actions(branch, pending)
        if not moves:
            break
        # Houses return stock; hotels consume four bank houses; mortgages last.
        moves.sort(key=lambda move: (0 if move[0] == "sell_houses_or_hotel" and move[1]["sell_plan"][0]["kind"] == "HOUSE"
                                     else 1 if move[0] == "sell_houses_or_hotel" else 2,
                                     json.dumps(move[1], sort_keys=True)))
        pending, step = apply_checked(branch, pending, *moves[0])
        steps.append(step)
        if payment_in(step["events"], player_id, debt):
            return {"paid": True, "steps": steps, "cash_after": actor(branch, player_id).cash}
        if actor(branch, player_id).bankrupt:
            break
        if len(steps) > 200:
            raise ValueError("Unexpected nonmonotone financing path")
    return {"paid": False, "steps": steps}


def exhaustive_financing(engine, decision, player_id, debt):
    """Certify only mortgage-only graphs; refuse incomplete sale enumeration.

    The engine can accept a bundled sale unavailable as atomic operations.
    Atomic search failure therefore cannot prove impossibility when any visited
    state offers sell_houses_or_hotel. A positive greedy witness remains valid.
    """
    frontier = [(copy.deepcopy(engine), copy.deepcopy(decision), [])]
    visited, nodes = set(), []
    while frontier:
        branch, pending, path = frontier.pop()
        key = reachable_state_key(branch, player_id)
        if key in visited:
            continue
        visited.add(key)
        if any(a["action"] == "sell_houses_or_hotel" for a in pending["legal_actions"]):
            raise ValueError(
                "Unresolved: bundled building sales are not enumerated; "
                "no impossibility certificate issued"
            )
        moves = liquidation_actions(branch, pending)
        node = {"state_sha256": key, "cash": actor(branch, player_id).cash,
                "offered_liquidation": pending["liquidation"], "edges": []}
        for name, args in moves:
            successor = copy.deepcopy(branch)
            nxt, step = apply_checked(successor, pending, name, args)
            paid = payment_in(step["events"], player_id, debt)
            bankrupt = actor(successor, player_id).bankrupt
            edge = {"step": step, "paid": paid, "bankrupt": bankrupt,
                    "next_state_sha256": reachable_state_key(successor, player_id)}
            node["edges"].append(edge)
            if paid:
                return {"paid": True, "steps": path + [step], "nodes": nodes + [node]}
            if not bankrupt:
                if not nxt or nxt["decision_type"] != "LIQUIDATION_DECISION" or nxt["player_id"] != player_id:
                    raise ValueError("Financing left the declared phase without payment or elimination")
                frontier.append((successor, nxt, path + [step]))
        nodes.append(node)
        if len(nodes) > 100000:
            raise ValueError("Search bound exceeded; no impossibility certificate issued")
    return {"paid": False, "exhausted": True, "state_count": len(nodes), "nodes": nodes,
            "graph_scope": "Mortgage-only: no building-sale action offered at any expanded state."}


def check_elimination(engine, decision, case):
    if decision["decision_type"] != "LIQUIDATION_DECISION":
        raise ValueError("Elimination did not originate in a debt decision")
    debt = decision["liquidation"]["owed_amount"]
    components = bound(engine, case["actor"])
    row = {"case_id": case["case_id"], "kind": case["kind"], "game": case["game"],
           "model": case["model"], "actor": case["actor"], "decision_id": case["decision_id"],
           "classification": case["classification"], "debt": debt, "bound": components,
           "initial_liquidation_menu": decision["liquidation"],
           "claim_scope": "Own sales and mortgages at the current debt; no trade, help, construction or future random step."}
    if components["full_upper"] < debt:
        row["certificate"] = "upper_bound_impossibility"
    else:
        trial = greedy_payment(engine, decision, case["actor"], debt)
        if trial["paid"]:
            row["certificate"] = "legal_payment_witness"
            row["witness"] = trial
        else:
            search = exhaustive_financing(engine, decision, case["actor"], debt)
            row["certificate"] = "legal_payment_witness" if search["paid"] else "exhaustive_financing_impossibility"
            row["search"] = search
            if search["paid"]:
                row["witness"] = search
    return row


def run():
    check_inputs()
    cases, games = read(HERE / "cases.json"), read(HERE / "games.json")
    lookup = defaultdict(list)
    for case in cases:
        lookup[(case["game"], case["decision_id"])].append(case)
    results, replays = [], []
    for game in games:
        folder = HERE / "inputs" / f'g{game["game"]:02d}'
        engine = Engine(**read(folder / "config.json"))
        expected = read(folder / "event_hashes.json")
        count = 0
        running = hashlib.sha256()

        def compare(events):
            nonlocal count
            for event in events:
                if count >= len(expected) or sha(event) != expected[count]:
                    raise ValueError(f'G{game["game"]}: canonical event mismatch at {count}')
                running.update(canonical(event) + b"\n")
                count += 1

        for line in (folder / "actions.jsonl").read_text().splitlines():
            record = json.loads(line)
            _, events, decision, _ = engine.advance_until_decision(max_steps=100000)
            compare(events)
            if not decision or decision["decision_id"] != record["decision_id"]:
                raise ValueError("Historical decision identifier mismatch")
            for case in lookup[(game["game"], decision["decision_id"])]:
                if count != case["prefix"]["event_count"] or running.hexdigest() != case["prefix"]["canonical_prefix_sha256"]:
                    raise ValueError(f'{case["case_id"]}: prefix mismatch')
                if decision["player_id"] != case["actor"]:
                    raise ValueError("Actor mismatch")
                checked = check_default(engine, decision, case) if case["kind"] == "default" else check_elimination(engine, decision, case)
                checked["verified_prefix"] = case["prefix"]
                checked["initial_snapshot_sha256"] = sha(engine.get_snapshot())
                results.append(checked)
            _, events, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
            compare(events)
        if count != len(expected) or not engine.is_game_over():
            raise ValueError("Incomplete historical replay")
        replays.append({"game": game["game"], "canonical_events": count,
                        "canonical_event_stream_sha256": running.hexdigest(), "terminal": True})
        print(f'G{game["game"]:02d}: {count} original events match; diagnostics complete', flush=True)
    if len(results) != len(cases):
        raise ValueError("Not every frozen case was executed")
    defaults = [r for r in results if r["kind"] == "default"]
    eliminations = [r for r in results if r["kind"] == "elimination"]
    summary = {
        "frozen_cases": len(cases), "replayed_games": len(replays),
        "canonical_events": sum(r["canonical_events"] for r in replays),
        "elimination_certificates": dict(Counter(r["certificate"] for r in eliminations)),
        "default_decisions": len(defaults),
        "default_targets_reachable": sum(r["any_recorded_target_reachable"] for r in defaults),
        "defaults_with_some_legal_construction": sum(r["smaller_legal_construction"] is not None for r in defaults),
        "attempt_diagnostics": dict(Counter(a["diagnostic"] for r in defaults for a in r["attempts"])),
        "default_targets_reachable_by_model": dict(Counter(r["model"] for r in defaults if r["any_recorded_target_reachable"])),
    }
    report = {"summary": summary, "results": results, "historical_replays": replays,
              "input_manifest_sha256": hashlib.sha256((HERE / "inputs_manifest.json").read_bytes()).hexdigest(),
              "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Finite case census, not accuracy improvement or causal intervention on model behavior. Targets were known from prior audits. Prefixes and original streams newly replayed; no semantic reading of all provider text or full-prompt equivalence claimed."}
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "results.json")
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))
