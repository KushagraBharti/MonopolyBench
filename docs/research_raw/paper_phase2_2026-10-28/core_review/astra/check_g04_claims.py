"""G4 source checks and bounded immediate branches; no provider calls."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 4]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def payload(n):
        return packets[n]["initial_prompt"]["payload"]

    def state(n):
        return payload(n)["game_state"]

    def cash(n, player=None):
        s = state(n)
        return next(p["cash"] for p in [s["you"], *s["others"]]
                    if p["player_id"] == (player or s["you"]["player_id"]))

    def houses(n, group):
        return {h["space_key"]: h["houses"] for h in state(n)["you"]["holdings"]["owned"]
                if h["space_key"] in group}

    pink = {"ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"}
    yellow = {"ATLANTIC_AVENUE", "VENTNOR_AVENUE", "MARVIN_GARDENS"}
    assert set(houses(134, pink)) == pink - {"VIRGINIA_AVENUE"}
    assert set(houses(135, pink)) == pink
    assert set(houses(244, pink)) == pink and sum(houses(244, pink).values()) == 4
    assert "ORIENTAL_AVENUE" not in {h["space_key"] for h in state(244)["you"]["holdings"]["owned"]}
    assert action(165)["action"] == "accept_trade"
    assert payload(165)["action_state"]["scenario"]["current_offer"]["if_you_accept"]["you_receive"]["properties"] == ["KENTUCKY_AVENUE"]

    park_offers = [n for n, p in packets.items() if p["player_id"] == "p2"
                   and action(n)["action"] == "propose_trade"
                   and "PARK_PLACE" in action(n)["args"].get("request", {}).get("properties", [])]
    assert park_offers == [49, 71, 97, 115]
    assert "end the turn without attempting a deal" in packets[49]["attempts"][1]["raw_response"]["choices"][0]["message"]["reasoning"]
    assert action(49)["action"] == "propose_trade"
    assert "If p1 insists on taking Orange instead" in action(148)["private_thought"]
    assert "$150/house" in action(148)["private_thought"]
    assert "$200 a house" in action(149)["public_message"]
    assert "actual house cost on Yellow is $150, not $200" in packets[150]["attempts"][0]["raw_response"]["choices"][0]["message"]["reasoning"]
    assert action(149)["public_message"] in [r["message"] for r in state(150)["memory"]["public_timeline_last_20"]]
    assert (cash(152), cash(153, "p4"), cash(153, "p1")) == (523, 560, 448)

    # Same intended final allocation, interleaved into legal single-house entries.
    engine, decision = restore(run, packets[174]["decision_id"])
    plan = [{"space_key": key, "kind": "HOUSE", "count": 1}
            for _ in range(2) for key in ["ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"]]
    plan.append({"space_key": "VIRGINIA_AVENUE", "kind": "HOUSE", "count": 1})
    decision, corrected_seven = apply(engine, decision, "build_houses_or_hotel", {"build_plan": plan})
    assert next(p.cash for p in engine.state.players if p.player_id == "p3") == 5
    assert [engine.state.board[i].houses for i in [11, 13, 14]] == [2, 2, 3]
    assert [a["outcome"] for a in packets[174]["attempts"]] == ["illogical", "illogical"]
    assert packets[174]["resolution"]["fallback_used"]

    bank_checks = {n: state(n)["bank"]["houses_remaining"] for n in [189, 196, 208, 215, 228]}
    assert set(bank_checks.values()) == {0}
    assert houses(208, yellow) == {"ATLANTIC_AVENUE": 2, "VENTNOR_AVENUE": 3, "MARVIN_GARDENS": 3}
    assert "accept_trade" not in payload(219)["action_state"]["available_actions"]
    assert cash(219) == 156
    assert action(218)["args"]["request"]["cash"] == 150
    # 150 settlement plus 5 + 6 mandatory mortgage-transfer interest exceeds 156.
    assert 150 + 5 + 6 > cash(219)
    assert "cannot build evenly" in action(223)["private_thought"]
    assert action(224)["args"]["build_plan"] == [{"count": 1, "kind": "HOUSE", "space_key": "ILLINOIS_AVENUE"}]
    assert [state(n)["bank"]["houses_remaining"] for n in [223, 224, 225]] == [2, 2, 1]

    # Executed liquidation at 270-273 disproves the prior inability forecast.
    liquidation_events = [e for e in events if 1988 <= e["seq"] <= 2016]
    assert cash(270) == 276 and cash(274) == 86
    rent750 = [e for e in liquidation_events if e["type"] == "RENT_PAID"]
    assert len(rent750) == 1 and rent750[0]["payload"]["amount"] == 750
    assert 276 + 4 * 75 + 260 - 750 == 86

    # Original renewed terms match but are a new negotiation, not an accepted promise.
    assert action(321)["args"]["offer"] == action(332)["args"]["request"]
    assert action(321)["args"]["request"] == action(332)["args"]["offer"]
    assert (cash(321), cash(333), cash(332)) == (2014, 1914, 60)
    assert action(343)["args"]["offer"]["cash"] == 50
    assert action(344)["args"]["request"]["cash"] == 150
    assert action(345)["action"] == "reject_trade"
    hotel_events = [e for e in events if e["type"] == "HOTEL_BUILT"]
    assert not hotel_events
    assert all(action(n)["action"] == "end_turn" for n in [346, 347])
    assert cash(348, "p1") == 2314
    terminal_cash = [e for e in packets[348]["canonical_event_segment"] if e["type"] == "CASH_CHANGED"]
    assert cash(348, "p1") + sum(e["payload"]["delta"] for e in terminal_cash
                                if e["payload"]["player_id"] == "p1") == 2524

    # Hotel plans were possible despite the zero house bank; no continuation is run.
    engine, decision = restore(run, packets[346]["decision_id"])
    tool_content = json.loads(packets[346]["attempts"][0]["assistant_content"])
    hotel_args = tool_content.get("arguments", tool_content.get("parameters"))
    assert hotel_args and "build_plan" in hotel_args
    decision, hotel_branch = apply(engine, decision, "build_houses_or_hotel", {"build_plan": hotel_args["build_plan"]})
    assert engine.state.bank.houses_remaining == 12

    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    selected = {0, 49, 50, 60, 72, 83, 85, 98, 116, 134, 135, 136, 142, 143, 146, 147,
                148, 149, 150, 151, 152, 153, 155, 161, 163, 165, 166, 174, 175, 176,
                178, 179, 183, 184, 188, 189, 196, 203, 207, 208, 210, 211, 214, 215,
                218, 219, 221, 223, 224, 227, 228, 231, 232, 244, 248, 249, 250, 251,
                252, 268, 269, 270, 271, 272, 273, 274, 279, 288, 289, 290, 293, 295,
                299, 300, 301, 308, 309, 310, 311, 312, 321, 322, 332, 333, 343, 344,
                345, 346, 347, 348}
    report = {
        "scope": "All 24 extraction entries and full extraction trajectories read; selected original channels and bounded branches. Not all G4 provider bundles reread.",
        "limits": "No winner counterfactual, causal persuasion or optimality claim. Provider statements remain channel-attributed.",
        "park_offer_decisions": park_offers, "bank_at_claimed_empty_decisions": bank_checks,
        "sol174_seven_house_interleaving": corrected_seven, "grok346_hotel_content_branch": hotel_branch,
        "terminal_ceilings": [check(4, 244, 469), check(4, 279, 256), check(4, 348, 210)],
        "actual_yellow_liquidation": liquidation_events,
        "profiles": [u for u in aggregation["units"] if u["game"] == 4],
        "originals": {n: {"action": action(n), "payload": payload(n), "attempts": packets[n]["attempts"],
                          "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
        "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in units if int(u["decision_id"][-6:]) in selected},
        "canonical_event_sha256": digest,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g04_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "bank_checks": bank_checks,
                      "final_cash": 2524, "terminal_ceilings": [469, 256, 210]}))


if __name__ == "__main__":
    main()
