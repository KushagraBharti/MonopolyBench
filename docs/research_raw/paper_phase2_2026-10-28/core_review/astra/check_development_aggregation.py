"""Independent event aggregation challenging Opus B2/B3/B4 units and timing.

Peer-informed questions; no peer code imported. Canonical artifacts unchanged.
"""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from check_g13_claims import ROOT, rows

HERE = Path(__file__).resolve().parent
PACKETS = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_packets"


def main():
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {s["index"]: s for s in board["spaces"]}
    keys = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): i for i, s in spaces.items()}
    groups = defaultdict(list)
    for i, s in spaces.items():
        if s["kind"] == "PROPERTY":
            groups[s["group"]].append(i)
    costs = board["house_cost_by_group"]
    rents = {int(k): v for k, v in board["property_rent_tables"].items()}
    units, eliminations, game_reports, hashes, packet_hashes = [], [], [], {}, {}
    for game in range(1, 21):
        decisions = {}
        run = None
        for path in sorted(PACKETS.glob(f"game-{game:02d}-*.jsonl")):
            packet_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
            for x in rows(path):
                payload = x["initial_prompt"]["payload"]
                decisions[x["decision_id"]] = {
                    "state": payload["game_state"], "menu": payload["action_state"],
                    "model": x["model"], "action": x["applied_action_record"],
                }
                run = ROOT / x["source_run"]
        assert run is not None
        event_path = run / "events.jsonl"
        ev = rows(event_path)
        hashes[str(event_path.relative_to(ROOT))] = hashlib.sha256(event_path.read_bytes()).hexdigest()
        winner = next(e["payload"]["winner_player_id"] for e in ev if e["type"] == "GAME_ENDED")
        houses, hotels, owner, latest_route = Counter(), Counter(), {}, {}
        bank, minimum, observed_minimum = 32, 32, 32
        spend, sales, developed_rent = Counter(), Counter(), Counter()
        paid_events = defaultdict(list)
        first_build, first_house, full_group_intervals = {}, {}, Counter()
        held_groups = set()
        build_routes = {}
        current = None
        requests = 0
        winner_trades = 0
        game_eliminations = []
        for e in ev:
            t, p = e["type"], e["payload"]
            if t == "LLM_DECISION_REQUESTED":
                current = decisions[p["decision_id"]]
                assert current["state"]["bank"]["houses_remaining"] == bank, (game, e["seq"], bank)
                observed_minimum = min(observed_minimum, bank)
                requests += 1
            elif t == "PROPERTY_PURCHASED":
                if p["price"] == 0:
                    assert current["menu"]["decision_type"] == "LIQUIDATION_DECISION"
                    assert game_eliminations and game_eliminations[-1]["decision_id"] == current["action"]["decision_id"]
                owner[p["space_index"]] = p["player_id"]
                latest_route[p["space_index"]] = "inheritance" if p["price"] == 0 else "purchase_or_auction"
            elif t == "PROPERTY_TRANSFERRED":
                owner[p["space_index"]] = p["to_player_id"]
                latest_route[p["space_index"]] = "trade"
            elif t == "TRADE_ACCEPTED":
                winner_trades += winner in {p["initiator_player_id"], p["counterparty_player_id"]}
            elif t in {"HOUSE_BUILT", "HOTEL_BUILT"}:
                i, pid, count = p["space_index"], p["player_id"], p.get("count", 1)
                group = spaces[i]["group"]
                key = (pid, group)
                assert all(owner[j] == pid for j in groups[group])
                if key not in first_build:
                    first_build[key] = e["seq"]
                    build_routes[key] = {j: latest_route[j] for j in groups[group]}
                if t == "HOUSE_BUILT":
                    first_house.setdefault(key, e["seq"])
                    houses[i] += count
                    bank -= count
                else:
                    bank += houses[i]
                    houses[i] = 0
                    hotels[i] += count
                spend[key] += count * costs[group]
            elif t in {"HOUSE_SOLD", "HOTEL_SOLD"}:
                i, count = p["space_index"], p.get("count", 1)
                group = spaces[i]["group"]
                sales[p["player_id"], group] += count * (costs[group] // 2)
                if t == "HOUSE_SOLD":
                    houses[i] -= count
                    bank += count
                else:
                    houses[i] += 4 * count
                    hotels[i] -= count
                    bank -= 4 * count
            elif t == "RENT_PAID" and spaces[p["space_index"]]["kind"] == "PROPERTY":
                i = p["space_index"]
                built = houses[i] > 0 or hotels[i] > 0
                assert built == (p["amount"] > 2 * rents[i][0]), (game, e)
                if built:
                    key = (p["to_player_id"], spaces[i]["group"])
                    developed_rent[key] += p["amount"]
                    paid_events[key].append((e["seq"], p["amount"]))
            elif t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY":
                assert current is not None
                scenario = current["menu"]["scenario"]
                creditor = scenario.get("owed_to_player_id")
                idx = keys[current["state"]["you"]["position"]]
                colour_rent = scenario["reason"] == "RENT" and spaces[idx]["kind"] == "PROPERTY"
                if colour_rent:
                    assert owner[idx] == creditor and (houses[idx] or hotels[idx]), (game, e)
                row = {"game": game, "decision_id": current["action"]["decision_id"],
                       "event_seq": e["seq"], "debtor": p["player_id"], "creditor": creditor,
                       "winner_creditor": creditor == winner, "reason": scenario["reason"],
                       "owed": scenario["owed_amount"], "space_index": idx,
                       "creditor_built_colour_rent": colour_rent}
                eliminations.append(row)
                game_eliminations.append(row)
            elif t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK":
                pid = p["player_id"]
                for i in [j for j, who in owner.items() if who == pid]:
                    bank += houses[i]
                    houses[i] = hotels[i] = 0
                    owner[i] = None
                    latest_route.pop(i, None)
            # A trade's sequential deed events can briefly complete a set that
            # is relinquished by the next transfer in that same settlement.
            # Count observed holding intervals at decision/terminal boundaries.
            if t in {"LLM_DECISION_REQUESTED", "GAME_ENDED"}:
                complete = {(pid, gr) for gr, indices in groups.items()
                            if (pid := owner.get(indices[0])) is not None
                            and all(owner.get(j) == pid for j in indices)}
                for key in complete - held_groups:
                    full_group_intervals[key] += 1
                held_groups = complete
            assert 0 <= bank <= 32, (game, e["seq"], bank)
            minimum = min(minimum, bank)
        assert requests == len(decisions)
        cash_spend = Counter()
        cash_sales = Counter()
        for e in ev:
            if e["type"] == "CASH_CHANGED":
                p = e["payload"]
                if p["reason"] == "BUILD":
                    cash_spend[p["player_id"]] -= p["delta"]
                elif p["reason"] == "SELL_BUILDING":
                    cash_sales[p["player_id"]] += p["delta"]
        for pid in {p for p, _ in spend} | {p for p, _ in sales}:
            assert sum(v for (p, _), v in spend.items() if p == pid) == cash_spend[pid]
            assert sum(v for (p, _), v in sales.items() if p == pid) == cash_sales[pid]
        for key in sorted(spend):
            pid, gr = key
            before = sum(v for seq, v in paid_events[key] if seq < first_build[key])
            lethal = sum(r["creditor"] == pid and r["creditor_built_colour_rent"]
                         and spaces[r["space_index"]]["group"] == gr for r in game_eliminations)
            units.append({"game": game, "player": pid, "group": gr, "winner": pid == winner,
                          "spend": spend[key], "sale_proceeds": sales[key],
                          "developed_rent_whole_game": developed_rent[key],
                          "developed_rent_before_first_own_build": before,
                          "developed_rent_from_first_own_build": developed_rent[key] - before,
                          "first_build_seq": first_build[key], "first_house_seq": first_house.get(key),
                          "latest_deed_routes_at_first_build": build_routes[key],
                          "observed_complete_ownership_intervals": full_group_intervals[key], "eliminations": lethal})
        game_reports.append({"game": game, "winner": winner, "winner_trades": winner_trades,
                             "event_minimum_bank_houses": minimum, "initial_prompt_minimum_bank_houses": observed_minimum,
                             "decision_bank_states_matched": requests})
    built_winners = [u for u in units if u["winner"]]
    first_built = [min((u for u in built_winners if u["game"] == g), key=lambda u: u["first_build_seq"])
                   for g in range(1, 21)]
    summary = {
        "unit": "One game/player/colour-group with any HOUSE_BUILT or HOTEL_BUILT; not an incrementally isolated investment return.",
        "built_units": len(units), "winner_built_units": len(built_winners),
        "winner_built_units_containing_inherited_deed": sum("inheritance" in u["latest_deed_routes_at_first_build"].values() for u in built_winners),
        "spend": sum(u["spend"] for u in units),
        "developed_rent_whole_game": sum(u["developed_rent_whole_game"] for u in units),
        "rent_before_first_own_build": sum(u["developed_rent_before_first_own_build"] for u in units),
        "zero_developed_rent_units": sum(u["developed_rent_whole_game"] == 0 for u in units),
        "zero_developed_rent_and_no_elimination": sum(u["developed_rent_whole_game"] == 0 and u["eliminations"] == 0 for u in units),
        "winner_units_with_no_house_build": [u for u in built_winners if u["first_house_seq"] is None],
        "built_units_with_observed_reacquisition": [u for u in units if u["observed_complete_ownership_intervals"] > 1],
        "prebuild_inherited_rent_units": [u for u in units if u["developed_rent_before_first_own_build"]],
        "winners_with_trades": sum(r["winner_trades"] > 0 for r in game_reports),
        "winner_first_built_routes": [{"game": u["game"], "group": u["group"], "routes": u["latest_deed_routes_at_first_build"]} for u in first_built],
        "winner_creditor": sum(r["winner_creditor"] for r in eliminations),
        "terminal_winner_creditor": sum([r for r in eliminations if r["game"] == g][-1]["winner_creditor"] for g in range(1, 21)),
        "colour_rent_eliminations": sum(r["creditor_built_colour_rent"] for r in eliminations),
        "bank_zero_games": [r["game"] for r in game_reports if r["event_minimum_bank_houses"] == 0],
        "initial_prompt_bank_zero_games": [r["game"] for r in game_reports if r["initial_prompt_minimum_bank_houses"] == 0],
        "decision_bank_states_matched": sum(r["decision_bank_states_matched"] for r in game_reports),
    }
    out = {"summary": summary, "units": units, "eliminations": eliminations, "games": game_reports,
           "event_source_hashes": hashes, "packet_source_hashes": packet_hashes,
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "limits": "Peer-informed independent implementation. No strategy-optimality, incremental return, intention or counterfactual-winner inference. Bank exhaustion does not establish a binding or chosen-action effect."}
    (HERE / "development_aggregation_check.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
