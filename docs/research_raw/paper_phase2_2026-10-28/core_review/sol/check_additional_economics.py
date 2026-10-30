"""Original applied-flow and prompt reference checks, without model experiments."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PACKETS = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_packets"


def units(game):
    result = {}
    for path in sorted(PACKETS.glob(f"game-{game:02d}-part-*.jsonl")):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            unit = json.loads(line)
            result[int(unit["decision_id"].rsplit("-", 1)[-1])] = (unit, {"packet": path.relative_to(ROOT).as_posix(), "line": number, "sha256": hashlib.sha256(line.encode()).hexdigest()})
    return result


def main():
    g1, g3, g4 = units(1), units(3), units(4)
    run3 = ROOT / g3[0][0]["source_run"]
    events3 = [json.loads(line) for line in (run3 / "events.jsonl").read_text().splitlines()]
    builds = [event for event in events3 if event["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"}]
    # Every actual purchase is retained. The output lets readers verify which
    # groups appear, rather than accepting the source's green-build assertion.
    argon_builds = [event for event in builds if event["actor"].get("player_id") == "p1"]
    assert argon_builds
    assert not any(event["payload"]["space_index"] in {31, 32, 34} for event in argon_builds)
    railroad_redemptions = [event for event in events3 if event["type"] == "PROPERTY_UNMORTGAGED" and event["payload"].get("space_index") in {5, 15, 25, 35}]
    run1 = ROOT / g1[0][0]["source_run"]
    events1 = [json.loads(line) for line in (run1 / "events.jsonl").read_text().splitlines()]
    bw_trade = [event for event in events1 if event["turn_index"] == 69 and event["type"] in {"TRADE_ACCEPTED", "PROPERTY_TRANSFERRED", "CASH_CHANGED"}]
    g4_sources = []
    for decision in [128, 130, 133, 134, 165, 189, 208, 215, 228, 279, 348]:
        unit, source = g4[decision]
        g4_sources.append({**source, "decision_id": unit["decision_id"], "applied": unit["applied_action_record"], "input_state": unit["initial_prompt"]["payload"], "events": unit["canonical_event_segment"]})
    assert g4[134][0]["applied_action_record"]["action"]["action"] == "accept_trade"
    assert g4[165][0]["applied_action_record"]["action"]["action"] == "accept_trade"
    for decision in [189, 208, 215, 228]:
        assert g4[decision][0]["initial_prompt"]["payload"]["game_state"]["bank"]["houses_remaining"] == 0
    result = {"g3_argon_build_events": argon_builds, "g3_railroad_redemptions": railroad_redemptions, "g1_turn69_boardwalk_flow": bw_trade, "g4_original_sources": g4_sources,
              "limits": "Applied events and exact decision inputs only. No full model-channel intent adjudication or counterfactual future rollout."}
    (HERE / "additional_economics_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print("G3 Argon building event positions/counts", json.dumps([(event["seq"], event["type"], event["payload"]["space_index"], event["payload"].get("count")) for event in argon_builds]))
    print("G3 railroad redemptions", json.dumps(railroad_redemptions))
    print("G1 turn69 accepted/transfer/cash", json.dumps(bw_trade))
    for item in g4_sources:
        print(item["decision_id"], json.dumps(item["applied"]["action"]), json.dumps([event for event in item["events"] if event["type"] in {"PROPERTY_TRANSFERRED", "CASH_CHANGED", "RENT_PAID", "PLAYER_BANKRUPT", "PROPERTY_MORTGAGED"}]))
    print("G4 all four reported zero-house input counts verified")


if __name__ == "__main__":
    main()
