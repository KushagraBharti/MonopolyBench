"""Independent event accounting after full source and fixed-sample adjudication.

Source counts remain descriptive. This script never assigns semantic verdicts.
"""

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {s["index"]: s for s in board["spaces"]}
    keys = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): i
            for i, s in spaces.items()}
    colors = defaultdict(set)
    for index, space in spaces.items():
        if space["kind"] == "PROPERTY":
            colors[space["group"]].add(index)
    costs = board["house_cost_by_group"]
    spend = defaultdict(int)
    salvage = defaultdict(int)
    receipts = defaultdict(list)
    elimination_credit = Counter()
    first_spend = {}
    deed_routes_at_first_spend = {}
    completions = {}
    complete_intervals = Counter()
    retained_completions = set()
    last_owner_change = {}
    design = []
    eliminations = []
    zero_games = set()
    stock_checks = 0
    decisions = Counter()
    postturn = Counter()
    proposal_eligible = Counter()
    proposals = Counter()
    accepts = Counter()
    source_hashes = {}

    for game in range(1, 21):
        source = units(game)
        sample = next(iter(source.values()))[0]
        run = ROOT / sample["source_run"]
        config = json.loads((run / "run_config.json").read_text())
        summary = json.loads((run / "summary.json").read_text())
        events = read_rows(run / "events.jsonl")
        players = {p["player_id"]: p["name"] for p in config["players"]}
        winner = summary["winner_player_id"]
        design.append({"game": game, "seed": config["seed"], "seats": players,
                       "winner": winner, "winner_name": players[winner],
                       "turns": summary["turn_count"], "treatment_fingerprint": config["treatment_fingerprint"],
                       "max_turns": config["max_turns"], "response_policy": config["response_policy"]})
        source_hashes[game] = {name: hashlib.sha256((run / name).read_bytes()).hexdigest()
                               for name in ("run_config.json", "events.jsonl", "actions.jsonl", "summary.json")}
        by_id = {u["decision_id"]: (u, ref) for u, ref in source.values()}
        ownership = {index: None for index in spaces}
        levels = {index: 0 for index in spaces}
        player_cash = dict.fromkeys(players, 1500)
        response_action = None
        winner_trades = 0
        all_trades = 0
        for event in events:
            payload = event["payload"]
            kind = event["type"]
            seq = event["seq"]
            if kind in {"LLM_DECISION_REQUESTED", "GAME_ENDED"}:
                for actor in players:
                    for group, group_indices in colors.items():
                        entry = (game, actor, group)
                        complete = all(ownership[i] == actor for i in group_indices)
                        if complete and entry not in retained_completions:
                            complete_intervals[entry] += 1
                            latest = max((last_owner_change[i] for i in group_indices), key=lambda row: row["seq"])
                            completions.setdefault(entry, {"boundary_seq": seq, "route": latest["route"],
                                                           "closing_event": latest["seq"]})
                            retained_completions.add(entry)
                        elif not complete:
                            retained_completions.discard(entry)
                if kind == "GAME_ENDED":
                    continue
                unit, ref = by_id[payload["decision_id"]]
                state = unit["initial_prompt"]["payload"]["game_state"]
                for observed in [state["you"], *state["others"]]:
                    actor = observed["player_id"]
                    assert observed["cash"] == player_cash[actor], (game, seq, actor, "cash")
                    expected = {keys[s["space_key"]]: 5 if s["hotel"] else s["houses"]
                                for s in observed["holdings"]["owned"]}
                    actual = {i: levels[i] for i, owner in ownership.items() if owner == actor}
                    assert actual == expected, (game, seq, actor, "holdings")
                bank_houses = 32 - sum(level for level in levels.values() if level < 5)
                bank_hotels = 12 - sum(level == 5 for level in levels.values())
                assert (bank_houses, bank_hotels) == (state["bank"]["houses_remaining"], state["bank"]["hotels_remaining"]), (game, seq)
                stock_checks += 1
                if not bank_houses:
                    zero_games.add(game)
                actor = payload["player_id"]
                name = players[actor]
                decisions[name] += 1
                act_state = unit["initial_prompt"]["payload"]["action_state"]
                action = unit["applied_action_record"]["action"]["action"]
                if payload["decision_type"] == "POST_TURN_ACTION_DECISION":
                    postturn[name] += 1
                    if "propose_trade" in act_state["available_actions"]:
                        proposal_eligible[name] += 1
                if action == "propose_trade":
                    proposals[name] += 1
                elif action == "accept_trade":
                    accepts[name] += 1
                response_action = (unit, ref)
            elif kind == "PROPERTY_PURCHASED":
                index = payload["space_index"]
                actor = payload["player_id"]
                route = "inheritance" if payload["price"] == 0 and ownership[index] is not None else "bank_purchase"
                ownership[index] = actor
                last_owner_change[index] = {"seq": seq, "route": route}
            elif kind == "PROPERTY_TRANSFERRED":
                index = payload["space_index"]
                ownership[index] = payload["to_player_id"]
                last_owner_change[index] = {"seq": seq, "route": "trade"}
            elif kind == "TRADE_ACCEPTED":
                all_trades += 1
                winner_trades += winner in {payload["initiator_player_id"], payload["counterparty_player_id"]}
            elif kind in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"}:
                index = payload["space_index"]
                actor = payload["player_id"]
                group = spaces[index]["group"]
                entry = (game, actor, group)
                count = payload["count"]
                if kind.endswith("BUILT"):
                    spend[entry] += costs[group] * count
                    deed_routes_at_first_spend.setdefault(entry, {i: last_owner_change[i]["route"]
                                                                  for i in colors[group]})
                    first_spend.setdefault(entry, seq)
                    levels[index] = 5 if kind == "HOTEL_BUILT" else levels[index] + count
                else:
                    salvage[entry] += costs[group] // 2 * count
                    levels[index] = 4 if kind == "HOTEL_SOLD" else levels[index] - count
                assert 0 <= levels[index] <= 5
            elif kind == "RENT_PAID":
                index = payload["space_index"]
                if spaces[index]["kind"] == "PROPERTY" and levels[index] > 0:
                    entry = (game, payload["to_player_id"], spaces[index]["group"])
                    receipts[entry].append({"seq": seq, "amount": payload["amount"], "payer": payload["from_player_id"]})
            elif kind == "CASH_CHANGED":
                player_cash[payload["player_id"]] += payload["delta"]
                if payload.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK":
                    for index, owner in list(ownership.items()):
                        if owner == payload["player_id"]:
                            ownership[index] = None
                            levels[index] = 0
                            last_owner_change.pop(index, None)
                if payload.get("reason") != "BANKRUPTCY":
                    continue
                unit, ref = response_action
                scenario = unit["initial_prompt"]["payload"]["action_state"]["scenario"]
                creditor = scenario.get("owed_to_player_id")
                position = unit["initial_prompt"]["payload"]["game_state"]["you"]["position"]
                index = keys[position]
                built_color = spaces[index]["kind"] == "PROPERTY" and levels[index] > 0 and scenario["reason"] == "RENT"
                if built_color:
                    elimination_credit[(game, creditor, spaces[index]["group"])] += 1
                eliminations.append({"game": game, "seq": seq, "source": ref,
                                     "debtor": payload["player_id"], "creditor": creditor,
                                     "winner_creditor": creditor == winner,
                                     "built_color_rent": built_color, "owed": scenario["owed_amount"],
                                     "reason": scenario["reason"], "space_index": index})
        cash_build = -sum(e["payload"]["delta"] for e in events
                          if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BUILD")
        cash_sale = sum(e["payload"]["delta"] for e in events
                        if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "SELL_BUILDING")
        assert cash_build == sum(v for k, v in spend.items() if k[0] == game)
        assert cash_sale == sum(v for k, v in salvage.items() if k[0] == game)
        design[-1].update({"winner_accepted_trade_participations": winner_trades,
                           "all_accepted_trades": all_trades, "winner_final_cash": player_cash[winner],
                           "winner_final_deed_count": sum(owner == winner for owner in ownership.values())})
        [r for r in eliminations if r["game"] == game][-1]["terminal_elimination"] = True

    records = []
    for entry, amount in sorted(spend.items()):
        game, actor, group = entry
        paid = receipts[entry]
        first = first_spend[entry]
        records.append({"game": game, "actor": actor, "group": group, "spend": amount,
                        "salvage": salvage[entry], "whole_game_developed_rent": sum(r["amount"] for r in paid),
                        "developed_rent_after_first_own_spend": sum(r["amount"] for r in paid if r["seq"] > first),
                        "rent_events": paid, "first_own_spend_event": first,
                        "eliminations_as_creditor_on_built_group": elimination_credit[entry],
                        "winner_actor": design[game - 1]["winner"] == actor,
                        "first_complete_route": completions.get(entry),
                        "deed_routes_at_first_own_spend": deed_routes_at_first_spend[entry],
                        "observed_complete_ownership_intervals": complete_intervals[entry],
                        "unit": "game/player/color with positive own construction expenditure"})
    winners = [r for r in records if r["winner_actor"]]
    totals = {
        "decisions": sum(decisions.values()), "spending_units": len(records),
        "own_construction_spend": sum(r["spend"] for r in records),
        "whole_game_developed_rent_for_spending_units": sum(r["whole_game_developed_rent"] for r in records),
        "developed_rent_after_first_own_spend": sum(r["developed_rent_after_first_own_spend"] for r in records),
        "zero_paid_developed_rent_units": sum(not r["whole_game_developed_rent"] for r in records),
        "zero_paid_rent_and_zero_elimination_units": sum(not r["whole_game_developed_rent"] and not r["eliminations_as_creditor_on_built_group"] for r in records),
        "eliminations": len(eliminations), "winner_creditor_eliminations": sum(r["winner_creditor"] for r in eliminations),
        "built_color_rent_eliminations": sum(r["built_color_rent"] for r in eliminations),
        "nonterminal_winner_creditor_eliminations": sum(r["winner_creditor"] for r in eliminations if not r.get("terminal_elimination")),
        "nonterminal_eliminations": sum(not r.get("terminal_elimination", False) for r in eliminations),
        "terminal_winner_creditor_eliminations": sum(r["winner_creditor"] for r in eliminations if r.get("terminal_elimination")),
        "terminal_bank_creditor_eliminations": sum(r["creditor"] is None for r in eliminations if r.get("terminal_elimination")),
        "initial_prompt_stock_checks": stock_checks, "zero_house_stock_games": sorted(zero_games),
        "winner_spending_groups": len(winners),
        "winner_spending_groups_first_completed_by_inheritance": sum(r["first_complete_route"]["route"] == "inheritance" for r in winners),
        "winner_spending_groups_containing_inherited_deed_at_first_spend": sum("inheritance" in r["deed_routes_at_first_own_spend"].values() for r in winners),
        "spending_units_with_multiple_complete_ownership_intervals": [
            [r["game"], r["actor"], r["group"]] for r in records if r["observed_complete_ownership_intervals"] > 1],
        "seed_blocks": dict(Counter(str(g["seed"]) for g in design)),
        "wins_by_name": dict(Counter(g["winner_name"] for g in design)),
        "winner_games_without_accepted_trade": [g["game"] for g in design if not g["winner_accepted_trade_participations"]],
        "seat_counts_by_name": {name: dict(Counter(actor for g in design for actor, n in g["seats"].items() if n == name)) for name in decisions},
        "postturn_by_name": dict(postturn), "propose_eligible_by_name": dict(proposal_eligible),
        "applied_proposals_by_name": dict(proposals), "applied_accepts_by_name": dict(accepts),
    }
    assert totals["decisions"] == stock_checks == 6989
    assert totals["eliminations"] == 60
    report = {"totals": totals, "design": design, "spending_units": records,
              "eliminations": eliminations, "source_hashes": source_hashes,
              "method": "Canonical event accounting, independently written after reading all catalog and sample sources. Ownership and physical development update event by event; complete-color acquisition is observed only at decision or terminal boundaries to avoid atomic-settlement artifacts. Every initial prompt cash, ownership, development and bank-stock field cross-checks the event reconstruction. Cash BUILD/SELL totals independently match building-event costs. Any HOUSE or HOTEL purchase creates a spending unit. First completion by inheritance and any inherited deed at first spending are separate measures.",
              "limits": "Peer numerical targets known beforehand. No human annotation, blind replication or experiment. Whole-game receipts include pre-investment inherited development receipts; later receipts remain observational, not incremental returns. Group units overlap within games and players. Five seeds, each with four seat rotations, do not give20independent random-board draws; unequal fingerprints do not identify which code changed or its effect. Completion route describes first observed stable complete ownership, not every later source of value.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "corpus_economics_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
