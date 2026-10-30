"""Original-source checks for G13 bargaining claims and extraction errors.

Replays stop after immediate offered trades and financing/build operations.
They do not infer persuasion, future rent receipts, or alternative winners.
"""

import hashlib
import json
import re
from pathlib import Path

from monopoly_engine import Engine
from monopoly_engine.engine import HOUSE_COST_BY_GROUP
from monopoly_engine.replay import canonical_event_lines

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEDGER = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl"


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def restore(run, target):
    config = json.loads((run / "run_config.json").read_text())
    engine = Engine(**{k: config[k] for k in ["seed", "players", "run_id", "max_turns",
                                            "max_trade_exchanges", "max_auction_actions"]})
    prefix = []
    for record in rows(run / "actions.jsonl"):
        _, events, decision, _ = engine.advance_until_decision(max_steps=100_000)
        prefix.extend(events)
        assert decision["decision_id"] == record["decision_id"]
        if record["decision_id"] == target:
            break
        _, events, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
        prefix.extend(events)
    assert canonical_event_lines(prefix) == canonical_event_lines(rows(run / "events.jsonl")[:len(prefix)])
    return engine, decision


def apply(engine, decision, name, args):
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": name, "args": args}
    assert engine.validate_action_for_decision(action, decision) == []
    _, events, next_decision, _ = engine.apply_action(action)
    return next_decision, {"action": action, "events": events, "snapshot": engine.get_snapshot()}


def main():
    chosen = {60, 105, 121, 124, 159, 167, 170, 172, 174, 208, 209,
              213, 243, 250, 251, 252, 253, 284, 285, 286, 302, 303, 355}
    packets, source_units, hashes = {}, {}, {}
    for unit in rows(LEDGER):
        suffix = int(unit["decision_id"][-6:])
        if unit["game"] != 13 or suffix not in chosen:
            continue
        path = ROOT / unit["packet"]
        packets[suffix] = rows(path)[unit["packet_line"] - 1]
        source_units[suffix] = unit
        hashes[unit["packet"]] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(packets) == len(chosen)
    run = ROOT / packets[252]["source_run"]
    engine, decision = restore(run, packets[252]["decision_id"])
    assert decision["player_id"] == "p4"
    decision, accepted = apply(engine, decision, "accept_trade", {})
    assert decision["player_id"] == "p4"
    assert next(p["cash"] for p in accepted["snapshot"]["players"] if p["player_id"] == "p4") == 165
    assert accepted["snapshot"]["board"][34]["owner_id"] == "p1"
    decision, mortgaged = apply(engine, decision, "mortgage_property", {"space_key": "VENTNOR_AVENUE"})
    assert next(p["cash"] for p in mortgaged["snapshot"]["players"] if p["player_id"] == "p4") == 295
    assert mortgaged["snapshot"]["board"][27]["mortgaged"]

    engine, decision = restore(run, packets[121]["decision_id"])
    decision, atlantic = apply(engine, decision, "accept_trade", {})
    assert decision["player_id"] == "p1"
    assert next(p["cash"] for p in atlantic["snapshot"]["players"] if p["player_id"] == "p1") == 224
    decision, built = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": "ST_JAMES_PLACE", "kind": "HOUSE", "count": 1},
        {"space_key": "TENNESSEE_AVENUE", "kind": "HOUSE", "count": 1}]})
    assert next(p["cash"] for p in built["snapshot"]["players"] if p["player_id"] == "p1") == 24
    assert [built["snapshot"]["board"][i]["houses"] for i in [16, 18, 19]] == [2, 2, 1]
    assert HOUSE_COST_BY_GROUP["ORANGE"] == 100

    board_path = ROOT / "contracts/data/board.json"
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s
              for s in json.loads(board_path.read_text())["spaces"]}
    assert spaces["B_O_RAILROAD"]["index"] == 25
    assert packets[243]["initial_prompt"]["payload"]["game_state"]["you"]["position"] == "VIRGINIA_AVENUE"
    assert packets[250]["initial_prompt"]["payload"]["game_state"]["you"]["position"] == "ATLANTIC_AVENUE"
    bo_distance = spaces["B_O_RAILROAD"]["index"] - spaces["VIRGINIA_AVENUE"]["index"]
    short_distance = spaces["SHORT_LINE"]["index"] - spaces["ATLANTIC_AVENUE"]["index"]
    def ways(distance):
        return sum(a + b == distance for a in range(1, 7) for b in range(1, 7))

    assert (bo_distance, ways(bo_distance), short_distance, ways(short_distance)) == (11, 2, 9, 4)
    others = packets[167]["initial_prompt"]["payload"]["game_state"]["others"]
    assert next(p for p in others if p["player_id"] == "p4")["position"] == "B_O_RAILROAD"
    assert spaces["NORTH_CAROLINA_AVENUE"]["index"] - spaces["B_O_RAILROAD"]["index"] == 7
    blue_cash = packets[172]["initial_prompt"]["payload"]["game_state"]["you"]["cash"]
    assert blue_cash == 754
    assert blue_cash - 500 - 18 - 193 == 43
    assert HOUSE_COST_BY_GROUP["DARK_BLUE"] == 200
    redemption_cash = []
    for i in [208, 209]:
        before = packets[i]["initial_prompt"]["payload"]["game_state"]["you"]["cash"]
        changes = [e["payload"]["delta"] for e in packets[i]["canonical_event_segment"]
                   if e["type"] == "CASH_CHANGED" and e["payload"]["player_id"] == "p1"]
        redemption_cash.append([before, before + sum(changes)])
    assert redemption_cash == [[1045, 989], [989, 933]]
    debtor = packets[213]["initial_prompt"]["payload"]["game_state"]["you"]
    assert all(not s["houses"] and not s["hotel"] for s in debtor["holdings"]["owned"])
    collateral = {s["space_key"]: spaces[s["space_key"]]["price"] // 2
                  for s in debtor["holdings"]["owned"] if not s["mortgaged"]}
    assert collateral == {"KENTUCKY_AVENUE": 110, "BOARDWALK": 200}
    assert debtor["cash"] + sum(collateral.values()) == 538
    tax_debtor = packets[355]["initial_prompt"]["payload"]["game_state"]["you"]
    assert all(not s["houses"] and not s["hotel"] for s in tax_debtor["holdings"]["owned"])
    tax_collateral = {s["space_key"]: spaces[s["space_key"]]["price"] // 2
                      for s in tax_debtor["holdings"]["owned"] if not s["mortgaged"]}
    assert tax_collateral == {"MEDITERRANEAN_AVENUE": 30, "BALTIC_AVENUE": 30}
    assert tax_debtor["cash"] + sum(tax_collateral.values()) == 76
    report = {
        "scope": "Selected claim verification; not full decision-channel or game review",
        "omission_branch": {"accept_130": accepted, "mortgage_ventnor": mortgaged,
                            "cash_available": 295, "hypothetical_200_rent_residual": 95,
                            "qualification": "The 200 bill is prospective, not paid in this branch. No later action or outcome simulated."},
        "cash_threshold_branch": {"accept_140": atlantic, "two_house_build": built,
                                  "qualification": "Recipient has 84 already; 224 can finance two 100 houses. This does not predict whether it would do so."},
        "probabilities": {"virginia_to_bo_distance": bo_distance, "direct_roll_bo_ways_of_36": ways(bo_distance),
                          "atlantic_to_short_line_distance": short_distance, "direct_roll_short_line_ways_of_36": ways(short_distance)},
        "g13_d213": {"cash": debtor["cash"], "collateral": collateral, "ceiling": 538, "owed": 950},
        "g13_d167": {"grok_position": "B_O_RAILROAD", "distance_to_north_carolina": 7},
        "g13_d172": {"cash": blue_cash, "proposed_payment": 500,
                      "transfer_interest": 18, "redemption": 193,
                      "remaining_cash_without_additional_financing": 43,
                      "one_house_price": 200,
                      "qualification": "Whole quote joins redemption and construction. This cash-only check does not exhaust other financing."},
        "redemption_cash_before_after": redemption_cash,
        "g13_d355": {"cash": tax_debtor["cash"], "collateral": tax_collateral,
                      "ceiling": 76, "owed": 100},
        "source_units": source_units, "packet_sha256": hashes,
        "source_sha256": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                          for n in ["run_config.json", "actions.jsonl", "events.jsonl"]},
        "board_sha256": hashlib.sha256(board_path.read_bytes()).hexdigest(),
        "engine_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g13_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G13 checks passed: feasible $130 acceptance plus mortgage; $140 funds two houses with existing cash; B&O 2/36; Short Line 4/36; debtor ceiling $538.")


if __name__ == "__main__":
    main()
