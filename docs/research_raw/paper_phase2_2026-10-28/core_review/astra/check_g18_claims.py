"""G18 accounting, standing-offer exposure, and exact liquidation checks."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 18]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {s["index"]: s for s in board["spaces"]}
    costs = board["house_cost_by_group"]
    houses, hotels, spending, sales = Counter(), Counter(), Counter(), Counter()
    receipts = defaultdict(list)
    bank = 32
    stock = []
    for e in events:
        t, p = e["type"], e["payload"]
        if t == "LLM_DECISION_REQUESTED":
            n = int(p["decision_id"][-6:])
            assert packets[n]["initial_prompt"]["payload"]["game_state"]["bank"]["houses_remaining"] == bank
        elif t in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"}:
            i, count = p["space_index"], p.get("count", 1)
            key = p["player_id"], spaces[i]["group"]
            if t == "HOUSE_BUILT":
                houses[i] += count
                bank -= count
            elif t == "HOTEL_BUILT":
                bank += houses[i]
                houses[i] = 0
                hotels[i] += count
            elif t == "HOUSE_SOLD":
                houses[i] -= count
                bank += count
            else:
                houses[i] += 4 * count
                hotels[i] -= count
                bank -= 4 * count
            if t.endswith("BUILT"):
                spending[key] += costs[key[1]] * count
            else:
                sales[key] += costs[key[1]] * count // 2
            stock.append({"event": e, "bank_houses_after": bank})
        elif t == "RENT_PAID" and spaces[p["space_index"]]["kind"] == "PROPERTY":
            i = p["space_index"]
            if houses[i] or hotels[i]:
                receipts[p["to_player_id"], spaces[i]["group"]].append(
                    {"event": e, "houses": houses[i], "hotel": bool(hotels[i])})
    profiles = [{"player": pid, "group": group, "own_build_cost": spending[pid, group],
                 "sales": sales[pid, group], "developed_rent_events": receipts[pid, group],
                 "paid_house_rent": sum(r["event"]["payload"]["amount"] for r in receipts[pid, group] if not r["hotel"]),
                 "paid_hotel_rent": sum(r["event"]["payload"]["amount"] for r in receipts[pid, group] if r["hotel"])}
                for pid, group in sorted(spending)]
    for pid in ("p1", "p2", "p3", "p4"):
        assert sum(v for (p, _), v in spending.items() if p == pid) == -sum(
            e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
            and e["payload"]["player_id"] == pid and e["payload"]["reason"] == "BUILD")
        assert sum(v for (p, _), v in sales.items() if p == pid) == sum(
            e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
            and e["payload"]["player_id"] == pid and e["payload"]["reason"] == "SELL_BUILDING")
    orange = next(p for p in profiles if p["player"] == "p1" and p["group"] == "ORANGE")
    assert (orange["own_build_cost"], orange["sales"], orange["paid_house_rent"], orange["paid_hotel_rent"]) == (1600, 550, 2700, 0)
    assert spending["p3", "DARK_BLUE"] == 1000 and not receipts["p3", "DARK_BLUE"]

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def state(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]

    assert [action(n)["args"]["bid_amount"] for n in range(197, 242)] == list(range(77, 122))
    assert action(242)["action"] == "drop_out"
    assert len({packets[n]["turn_index"] for n in range(188, 243)}) == 1
    quote = action(431)["public_message"]
    assert "offer still stands" in quote
    exposure = {}
    for n in (441, 442):
        memory = state(n)["memory"]["public_timeline_last_20"]
        assert any(row.get("message") == quote and row["player_id"] == "p4" for row in memory)
        exposure[n] = memory
    assert action(421)["args"]["offer"]["cash"] == action(441)["args"]["request"]["cash"] == 250
    assert action(441)["args"]["offer"]["properties"] == ["PACIFIC_AVENUE"]
    assert action(442)["action"] == "reject_trade"
    assert "previously offered" in action(441)["private_thought"]
    assert action(344)["action"] == "mortgage_property"
    assert any(e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY"
               for e in packets[344]["canonical_event_segment"])
    assert not any(e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "MORTGAGE_TRANSFER_INTEREST"
                   for e in packets[344]["canonical_event_segment"])
    estate = [e for e in packets[344]["canonical_event_segment"] if e["type"] == "CASH_CHANGED"
              and e["payload"].get("reason") == "BANKRUPTCY_CASH"]
    assert [e["payload"]["delta"] for e in estate] == [-382, 382]
    selected = {61, 83, 84, 91, 155, 167, 168, 169, 170, 171, 172, 174, 178, 179, 184,
                186, 188, 196, 197, 241, 242, 260, 280, 300, 301, 302, 303, 306, 307, 308,
                309, 310, 322, 336, 344, 349, 358, 360, 363, 364, 366, 419, 421, 423, 425,
                427, 431, 437, 439, 441, 442, 453, 455, 457, 460, 461, 463}
    report = {"scope": "Selected original accounting and exact local ceilings, not a full original-channel reread or winner counterfactual.",
              "group_profiles": profiles, "stock_changes": stock,
              "standing_offer": {"source431": action(431), "attempted_invocation441": action(441),
                                 "withdrawal442": action(442), "exact_recipient_and_speaker_memories": exposure,
                                 "limits": "Observable withdrawal after repeated standing assurances and explicit invocation. No demonstrated costly reliance, initial deceptive intent, binding contract or causal effect on elimination."},
              "automatic_gemini_estate": estate,
              "liquidation_ceilings": [check(18, 344, 382), check(18, 360, 264), check(18, 463, 679)],
              "selected_originals": {n: {"action": action(n), "payload": packets[n]["initial_prompt"]["payload"],
                                          "canonical_event_segment": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "packet_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "canonical_hashes": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                                   for n in ("events.jsonl", "actions.jsonl", "run_config.json")},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g18_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"profiles": [{k: v for k, v in p.items() if k != "developed_rent_events"} for p in profiles],
                      "standing_offer_delivered": [441, 442], "liquidation_ceilings": [382, 264, 679]}))


if __name__ == "__main__":
    main()
