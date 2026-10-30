"""G02 event and local replay checks; peer-nominated targets independently checked."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 2]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def state(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]

    assert "St Charles is the missing piece" in action(26)["private_thought"]
    assert "St. Charles is pink, not orange" in action(36)["private_thought"]
    assert "The Ventnor trade went through" in action(62)["private_thought"]
    assert "The trade for Ventnor went through" in packets[62]["attempts"][0]["assistant_content"]
    assert "Probe only" in action(247)["private_thought"]
    assert json.loads(packets[247]["attempts"][0]["assistant_content"])["name"] == "end_turn"
    assert action(247)["action"] == "propose_trade"
    gemini135 = next(p for p in state(135)["others"] if p["player_id"] == "p2")
    assert [h["houses"] for h in gemini135["holdings"]["owned"] if h["space_key"] in {"PARK_PLACE", "BOARDWALK"}] == [3, 3]
    assert state(198)["you"]["cash"] == 435 and state(199)["you"]["cash"] == 309
    assert state(200)["you"]["cash"] == 429
    paid = [e for e in events if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == "p4"
            and e["payload"]["space_index"] in {6, 8, 9}]
    assert [e["payload"]["amount"] for e in paid] == [6, 12, 16]
    assert max(e["seq"] for e in paid) < 943

    # Correction succeeds with less construction, although all seven original houses are feasible.
    first = json.loads(packets[243]["attempts"][0]["parsed_tool_call"]["arguments"])["build_plan"]
    assert sum(x["count"] for x in first) == 7
    assert sum(x["count"] for x in action(243)["args"]["build_plan"]) == 3
    assert sum(x["count"] for x in action(244)["args"]["build_plan"]) == 3
    engine, decision = restore(run, packets[243]["decision_id"])
    plan = [{"space_key": x["space_key"], "kind": "HOUSE", "count": 1}
            for level in range(max(x["count"] for x in first)) for x in first if x["count"] > level]
    decision, branch = apply(engine, decision, "build_houses_or_hotel", {"build_plan": plan})
    player = next(p for p in engine.state.players if p.player_id == "p2")
    assert player.cash == 208
    assert [engine.state.board[i].houses for i in (26, 27, 29)] == [2, 2, 3]

    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [u for u in aggregation["units"] if u["game"] == 2]
    selected = {16, 17, 18, 19, 26, 27, 28, 36, 37, 41, 44, 45, 46, 61, 62, 63, 67,
                69, 71, 72, 75, 81, 99, 114, 118, 122, 123, 124, 128, 129, 133, 134,
                135, 140, 143, 145, 158, 175, 198, 199, 200, 201, 209, 212, 213, 214,
                215, 216, 218, 239, 243, 244, 247, 256, 258, 259, 278}
    report = {"scope": "Complete extraction narrative and 15 entries; selected original actions, prompts and attempts. No whole-game original reread claimed.",
              "light_blue_paid_to_opus_before_first_build_only": paid,
              "quantity_changing_recovery": {"first_plan": first, "applied243": action(243), "applied244": action(244),
                                             "same_seven_houses_interleaved": branch, "alternative_cash": 208,
                                             "limits": "Local legal construction only. No subsequent rent or winner effect tested."},
              "terminal_ceilings": [check(2, 215, 927), check(2, 239, 77), check(2, 278, 203)],
              "profiles": profiles,
              "originals": {n: {"action": action(n), "payload": packets[n]["initial_prompt"]["payload"],
                                  "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
              "selected_attempts": {n: [{"outcome": a["outcome"], "content": a["assistant_content"],
                                           "parsed_tool_call": a["parsed_tool_call"], "errors": a["validation_errors"]}
                                          for a in packets[n]["attempts"]] for n in (62, 75, 129, 243, 247)},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "canonical_event_sha256": digest,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g02_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"terminal_ceilings": [927, 77, 203], "first_build_has_3_house_dark_blues": True,
                      "seven_house_alternative_cash": 208, "profiles": profiles}))


if __name__ == "__main__":
    main()
