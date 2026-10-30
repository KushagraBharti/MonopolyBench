"""Read-only adversarial checks; outputs stay beside this script."""
from collections import Counter
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
AUDIT = OUT / "portable_original" / "historical-claim-audit"
sys.dont_write_bytecode = True
sys.path.insert(0, str(AUDIT))
import run_audit as audit
from test_certificates import restore


def h(data):
    return hashlib.sha256(data).hexdigest()


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def original_checks():
    cases = audit.read(AUDIT / "cases.json")
    games = audit.read(AUDIT / "games.json")
    manifest = audit.read(AUDIT / "inputs_manifest.json")
    checks, original_hashes = [], {}
    observed = set()
    for game in games:
        n = game["game"]
        run = ROOT / game["source_run"]
        for name, expected in game["source_hashes"].items():
            path = run / name
            actual = h(path.read_bytes())
            assert actual == expected, (n, name, actual, expected)
            original_hashes[str(path.relative_to(ROOT))] = actual
        frozen = AUDIT / "inputs" / f"g{n:02d}"
        assert (run / "actions.jsonl").read_bytes() == (frozen / "actions.jsonl").read_bytes()
        config = audit.read(run / "run_config.json")
        frozen_config = audit.read(frozen / "config.json")
        assert frozen_config == {k: config[k] for k in frozen_config}
        events = rows(run / "events.jsonl")
        assert [h(canonical(e)) for e in events] == audit.read(frozen / "event_hashes.json")
        raw_decisions = (run / "decisions.jsonl").read_text().splitlines()
        decisions = [json.loads(line) for line in raw_decisions]
        starts = {d["decision_id"]: d for d in decisions if d["phase"] == "decision_started"}
        resolved = {d["decision_id"]: d for d in decisions if d["phase"] == "decision_resolved"}
        actions = rows(run / "actions.jsonl")
        relevant = [c for c in cases if c["game"] == n]
        defaults = {d["decision_id"] for d in resolved.values() if d.get("fallback_used")}
        assert defaults == {c["decision_id"] for c in relevant if c["kind"] == "default"}
        markers = [e for e in events if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY"]
        assert {e["seq"] for e in markers} == {c["event_seq"] for c in relevant if c["kind"] == "elimination"}
        assert len(markers) == 3
        for case in relevant:
            assert case["case_id"] not in observed
            observed.add(case["case_id"])
            start = starts[case["decision_id"]]
            resolution = resolved[case["decision_id"]]
            assert start["player_id"] == case["actor"]
            assert start["openrouter_model_id"] == case["model"]
            assert resolution["final_action"]["action"] == case["applied_action"]
            for field, expected in [("source_start", start), ("source_resolution", resolution)]:
                ref = case[field]
                line = raw_decisions[ref["line"] - 1]
                assert h(line.encode()) == ref["line_sha256"]
                assert json.loads(line) == expected
            prefix = events[:case["prefix"]["event_count"]]
            assert prefix[-1]["type"] == "LLM_DECISION_REQUESTED"
            assert prefix[-1]["payload"]["decision_id"] == case["decision_id"]
            assert h(b"".join(canonical(e) + b"\n" for e in prefix)) == case["prefix"]["canonical_prefix_sha256"]
            if case["kind"] == "elimination":
                marker = next(e for e in markers if e["seq"] == case["event_seq"])
                assert marker["payload"]["player_id"] == case["actor"]
                assert h(canonical(marker)) == case["elimination_event_sha256"]
                prior_response = next(e for e in reversed(events[:events.index(marker)]) if e["type"] == "LLM_DECISION_RESPONSE")
                assert prior_response["payload"]["decision_id"] == case["decision_id"]
                assert case["classification"] == ("declared" if case["applied_action"] == "declare_bankruptcy" else "automatic")
            else:
                assert case["applied_action"] == "end_turn"
                assert len(case["attempts"]) == len(resolution["attempts"])
                for saved, original in zip(case["attempts"], resolution["attempts"]):
                    assert saved["outcome"] == original.get("outcome")
                    assert saved["condition"] == original.get("response_condition")
                    assert saved["recorded_errors"] == original.get("validation_errors")
                    call = original.get("parsed_tool_call")
                    assert saved["tool_name"] == (call.get("name") if isinstance(call, dict) else None)
                    if "plan" in saved:
                        args = call["arguments"]
                        if isinstance(args, str):
                            args = json.loads(args)
                        assert saved["plan"] == args["build_plan"]
        checks.append({"game": n, "events": len(events), "actions": len(actions),
                       "eliminations": len(markers), "defaults": len(defaults)})
    for name, source in manifest["copied_engine_sources"].items():
        path = ROOT / source["source"]
        assert path.read_bytes() == (AUDIT / name).read_bytes()
        assert h(path.read_bytes()) == source["sha256"]
        original_hashes[source["source"]] = h(path.read_bytes())
    source_manifest = ROOT / "docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json"
    assert h(source_manifest.read_bytes()) == manifest["source_manifest_sha256"]
    assert [(g["game"], g["run"]) for g in audit.read(source_manifest)["games"]] == [(g["game"], g["source_run"]) for g in games]
    (OUT / "original_hashes.json").write_text(json.dumps(original_hashes, indent=2) + "\n")
    return {"games": checks, "unique_cases": len(observed), "original_files_and_vendor_sources": len(original_hashes)}


def synthetic_bundle_counterexample(expect_unresolved=False):
    config = audit.read(AUDIT / "inputs/g01/config.json")
    config["run_id"] = "synthetic-bundled-sales-counterexample"
    engine = audit.Engine(**config)
    engine._started = True
    engine.state.phase = "RUNNING"
    debtor = engine.state.players[0]
    debtor.cash = 0
    debtor.position = 24
    # Inventory-conserving and evenly built synthetic estate, not a historical case.
    for index in [1, 3]:
        s = engine.state.board[index]
        s.owner_id = debtor.player_id
        s.houses = 1
    for index in [37, 39]:
        s = engine.state.board[index]
        s.owner_id = debtor.player_id
        s.hotel = True
    for indices in [[6, 8, 9], [16, 18, 19], [21, 23, 24]]:
        for index, houses in zip(indices, [4, 3, 3]):
            s = engine.state.board[index]
            s.owner_id = engine.state.players[1].player_id
            s.houses = houses
    engine.state.bank.houses_remaining = 0
    engine.state.bank.hotels_remaining = 10
    assert sum(s.houses for s in engine.state.board) == 32
    assert sum(s.hotel for s in engine.state.board) + engine.state.bank.hotels_remaining == 12
    events = []
    debt = engine._calculate_rent(engine.state.board[24], engine.state.players[1], 6)
    assert debt == 750
    payment = {"amount": debt, "reason": "RENT", "kind": "RENT", "to_player_id": "p2", "space_index": 24}
    decision = engine._request_payment(debtor, payment, events, turn_index=0, rolled_double=False)
    engine._activate_debt_decision(decision, events)
    case = {"case_id": "synthetic-bundled-sales", "kind": "elimination", "game": 0,
            "model": "synthetic", "actor": debtor.player_id, "decision_id": decision["decision_id"], "classification": "declared"}
    try:
        certificate = audit.check_elimination(engine, decision, case)
    except ValueError as exc:
        if not expect_unresolved:
            raise
        assert "bundled building sales are not enumerated" in str(exc)
        certificate = {"refused": str(exc)}
    else:
        assert not expect_unresolved, "The revised runner still issued a false certificate"
        assert certificate["certificate"] == "exhaustive_financing_impossibility"
    plan = []
    for key in ["PARK_PLACE", "BOARDWALK"]:
        plan += [{"space_key": key, "kind": "HOTEL", "count": 1}, {"space_key": key, "kind": "HOUSE", "count": 4}]
    move = audit.action(decision, "sell_houses_or_hotel", {"sell_plan": plan})
    assert engine.validate_action_for_decision(move, decision) == []
    branch = copy.deepcopy(engine)
    _, result = audit.apply_checked(branch, decision, "sell_houses_or_hotel", {"sell_plan": plan})
    assert audit.payment_in(result["events"], debtor.player_id, debt)
    assert audit.actor(branch, debtor.player_id).cash == 250
    return {"certificate": certificate, "legal_bundled_witness": result,
            "cash_after": audit.actor(branch, debtor.player_id).cash,
            "description": "Atomic financing certifies impossibility but a single engine-accepted bundled sale pays the debt."}


def hotel_lock_scope():
    engine, decision, case = restore("G07-dec-000339-elimination")
    legal_names = [a["action"] for a in decision["legal_actions"]]
    assert legal_names == ["mortgage_property", "declare_bankruptcy"]
    # Even a plan selling every hotel and its replacement houses has an unoffered action name.
    plan = []
    for s in engine.state.board:
        if s.owner_id == case["actor"] and s.hotel:
            key = audit.SPACE_KEY_BY_INDEX[s.index]
            plan += [{"space_key": key, "kind": "HOTEL", "count": 1}, {"space_key": key, "kind": "HOUSE", "count": 4}]
    errors = engine.validate_action_for_decision(audit.action(decision, "sell_houses_or_hotel", {"sell_plan": plan}), decision)
    assert errors == ["Action not legal for decision"]
    search = audit.exhaustive_financing(engine, decision, case["actor"], decision["liquidation"]["owed_amount"])
    assert not search["paid"] and search["exhausted"] and search["state_count"] == 1
    return {"legal_action_names": legal_names, "bundled_sale_rejected": errors, "graph": search}


def fresh_certificates():
    fresh = audit.read(OUT / "fresh_results.json")
    inherited = audit.read(AUDIT / "results.json")
    assert fresh == inherited
    checked = []
    for result in fresh["results"]:
        engine, decision, case = restore(result["case_id"])
        assert h(canonical(engine.get_snapshot())) == result["initial_snapshot_sha256"]
        if case["kind"] == "default":
            for attempt in result["attempts"]:
                if attempt["diagnostic"] != "reachable_target":
                    continue
                plan = attempt["plan"]
                atomic = attempt["atomic_plan"]
                requested = Counter()
                for p in plan:
                    requested[(p["space_key"], p["kind"])] += p["count"]
                observed = Counter((p["space_key"], p["kind"]) for p in atomic)
                assert requested == observed
                assert all(p["count"] == 1 for p in atomic)
                branch = copy.deepcopy(engine)
                before = branch.get_snapshot()
                _, step = audit.apply_checked(branch, decision, "build_houses_or_hotel", {"build_plan": atomic})
                assert step == attempt["atomic_execution"]["operation"]
                actual_builds = Counter()
                for event in step["events"]:
                    if event["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"}:
                        kind = "HOUSE" if event["type"] == "HOUSE_BUILT" else "HOTEL"
                        actual_builds[(audit.SPACE_KEY_BY_INDEX[event["payload"]["space_index"]], kind)] += event["payload"].get("count", 1)
                assert actual_builds == requested
                expected_cost = sum(audit.HOUSE_COST_BY_GROUP[engine.state.board[next(i for i, k in audit.SPACE_KEY_BY_INDEX.items() if k == key)].group] * count for (key, kind), count in requested.items())
                assert audit.actor(branch, case["actor"]).cash == audit.actor(engine, case["actor"]).cash - expected_cost
            checked.append({"case_id": case["case_id"], "checked": "construction event purchases, exact per-deed/kind multiset, cash, prefix"})
        elif result["certificate"] == "legal_payment_witness":
            payment = copy.deepcopy(engine._pending_payment["payment"])
            matched = []
            for step in result["witness"]["steps"]:
                decision, actual = audit.apply_checked(engine, decision, step["action"], step["args"])
                assert step == actual
                matched += [e for e in actual["events"] if e["type"] == "CASH_CHANGED" and e["payload"].get("player_id") == case["actor"] and e["payload"].get("delta") == -payment["amount"] and e["payload"].get("reason") == payment["reason"]]
            assert len(matched) == 1
            assert not audit.actor(engine, case["actor"]).bankrupt
            assert audit.actor(engine, case["actor"]).cash == result["witness"]["cash_after"]
            checked.append({"case_id": case["case_id"], "checked": "all witness actions/events re-executed; original debt reason/amount paid", "payment": payment})
        else:
            player = audit.actor(engine, case["actor"])
            upper = player.cash
            for s in engine.state.board:
                if s.owner_id == player.player_id:
                    upper += (0 if s.mortgaged else s.price // 2)
                    upper += (5 if s.hotel else s.houses) * (audit.HOUSE_COST_BY_GROUP.get(s.group, 0) // 2)
            assert upper == result["bound"]["full_upper"]
            if result["certificate"] == "upper_bound_impossibility":
                assert upper < decision["liquidation"]["owed_amount"]
            checked.append({"case_id": case["case_id"], "checked": "prefix and independent estate arithmetic", "upper": upper})
    return {"saved_output_equals_fresh_output": True, "independently_checked_cases": checked}


def main():
    result = {"original_checks": original_checks(), "certificate_checks": fresh_certificates(),
              "false_negative_counterexample": synthetic_bundle_counterexample(),
              "historical_hotel_lock": hotel_lock_scope()}
    (OUT / "adversarial_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"canonical_cases": result["original_checks"]["unique_cases"],
                      "canonical_and_vendor_hashes": result["original_checks"]["original_files_and_vendor_sources"],
                      "fresh_results_equal": True,
                      "counterexample": result["false_negative_counterexample"]["description"],
                      "false_negative_states": result["false_negative_counterexample"]["certificate"]["search"]["state_count"],
                      "historical_g7_affected": False}, indent=2))


if __name__ == "__main__":
    main()
