"""Read-only cohort reconstruction. Derived outputs stay beside this script.

This is exploratory analysis, not a replacement for the benchmark's engine.
No prompts, provider calls, or canonical artifacts are written.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COLLECTIONS = [
    ROOT / "saved_games/railway-research-12-games-2026-10-25",
    ROOT / "saved_games/railway-research-8-games-2026-10-26",
]
NAMES = {
    "anthropic/claude-opus-5.5": "Opus",
    "openai/gpt-6.1-sol": "Sol",
    "google/gemini-4-argon": "Gemini",
    "x-ai/grok-4.7": "Grok",
}
BOARD = json.loads((ROOT / "contracts/data/board.json").read_text())["spaces"]
GROUPS = defaultdict(list)
for s in BOARD:
    if s["kind"] == "PROPERTY":
        GROUPS[s["group"]].append(s["index"])
GROUP_OF = {i: g for g, indices in GROUPS.items() for i in indices}


def read(path):
    return json.loads(path.read_text())


def jsonl(path):
    return [json.loads(x) for x in path.read_text().splitlines()]


def complete(owners, pid):
    return {g for g, indices in GROUPS.items() if all(owners.get(i) == pid for i in indices)}


def write_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    games, players, trades, groups, sources = [], [], [], [], []
    dice_by_seed = defaultdict(list)
    for collection in COLLECTIONS:
        for index in csv.DictReader((collection / "game-index.csv").open()):
            package = collection / index["package"]
            run = package / "run"
            config, summary = read(run / "run_config.json"), read(run / "summary.json")
            names = {p["player_id"]: NAMES[p["openrouter_model_id"]] for p in config["players"]}
            es, actions = jsonl(run / "events.jsonl"), jsonl(run / "actions.jsonl")
            game = int(index["collection_game"])
            for name in ["events.jsonl", "actions.jsonl", "decisions.jsonl", "run_config.json", "summary.json"]:
                p = run / name
                sources.append({"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
            winner = summary["winner_player_id"]
            own = {s["index"]: None for s in BOARD if s["price"] is not None}
            cash = {p: 1500 for p in names}
            stats = {p: Counter() for p in names}
            current = None
            auction = False
            group_rows = []
            first_build = None
            dice = []

            def finish_trade():
                nonlocal current
                if current is None:
                    return
                gained = {p: sorted(complete(own, p) - current["before"][p]) for p in names}
                a, b = current["a"], current["b"]
                row = {
                    "game": game, "seed": config["seed"], "event_id": current["event"]["event_id"],
                    "seq": current["event"]["seq"], "turn": current["event"]["turn_index"],
                    "initiator": names[a], "recipient": names[b],
                    "initiator_new_groups": ",".join(gained[a]), "recipient_new_groups": ",".join(gained[b]),
                    "kind": "mutual" if gained[a] and gained[b] else "one_side" if gained[a] or gained[b] else "neither",
                    "initiator_cash_before": current["cash_before"][a], "recipient_cash_before": current["cash_before"][b],
                    "initiator_cash_after": cash[a], "recipient_cash_after": cash[b],
                    "initiator_net_trade_cash": current["flow"][a], "recipient_net_trade_cash": current["flow"][b],
                    "transfers": json.dumps(current["transfers"], sort_keys=True),
                }
                trades.append(row)
                for p in [a, b]:
                    for g in gained[p]:
                        group_rows.append({
                            "game": game, "seed": config["seed"], "player_id": p, "model": names[p], "group": g,
                            "event_id": row["event_id"], "seq": row["seq"], "turn": row["turn"],
                            "cash_before": current["cash_before"][p], "cash_after": cash[p], "win": p == winner,
                            "initiated": p == a,
                        })
                current = None

            for e in es:
                typ, p = e["type"], e["payload"]
                if current is not None and typ not in {"CASH_CHANGED", "PROPERTY_TRANSFERRED"}:
                    finish_trade()
                if typ == "TRADE_ACCEPTED":
                    a, b = p["initiator_player_id"], p["counterparty_player_id"]
                    stats[a]["accepted_initiated"] += 1
                    stats[b]["accepted_received"] += 1
                    current = {"event": e, "a": a, "b": b, "before": {x: complete(own, x) for x in names},
                               "cash_before": dict(cash), "flow": Counter(), "transfers": []}
                elif typ == "TRADE_PROPOSED":
                    stats[p["initiator_player_id"]]["proposals"] += 1
                    stats[p["counterparty_player_id"]]["offers_received"] += 1
                elif typ == "TRADE_COUNTERED":
                    stats[e["actor"]["player_id"]]["counters"] += 1
                elif typ == "DICE_ROLLED":
                    stats[e["actor"]["player_id"]]["rolls"] += 1
                    dice.append((p["d1"], p["d2"]))
                elif typ == "CASH_CHANGED":
                    cash[p["player_id"]] += p["delta"]
                    if current:
                        current["flow"][p["player_id"]] += p["delta"]
                    if p.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK":
                        own = {i: None if owner == p["player_id"] else owner for i, owner in own.items()}
                elif typ == "AUCTION_STARTED":
                    auction = True
                elif typ == "AUCTION_ENDED":
                    auction = False
                elif typ == "PROPERTY_PURCHASED":
                    pid, i = p["player_id"], p["space_index"]
                    before = complete(own, pid)
                    own[i] = pid
                    method = "inheritance" if p["price"] == 0 else "auction" if auction else "buy"
                    stats[pid][method + "_deeds"] += 1
                    stats[pid][method + "_groups"] += len(complete(own, pid) - before)
                elif typ == "PROPERTY_TRANSFERRED":
                    own[p["space_index"]] = p["to_player_id"]
                    if current:
                        current["transfers"].append(p)
                elif typ in {"HOUSE_BUILT", "HOTEL_BUILT"}:
                    if first_build is None:
                        first_build = e
                    stats[p["player_id"]][typ.lower()] += p["count"]
                elif typ == "RENT_PAID":
                    stats[p["to_player_id"]]["rent_received"] += p["amount"]
                    stats[p["from_player_id"]]["rent_paid"] += p["amount"]
            finish_trade()
            # Episode follow-up stops when any constituent deed leaves its owner.
            # First management turn is recipient-aware; it does not prove build legality.
            for row in group_rows:
                pid, g = row["player_id"], row["group"]
                future = [e for e in es if e["seq"] > row["seq"]]
                lost = next((e["seq"] for e in future if
                             e["type"] == "PROPERTY_TRANSFERRED" and e["payload"]["space_index"] in GROUPS[g]
                             and e["payload"]["from_player_id"] == pid or
                             e["type"] == "PROPERTY_PURCHASED" and e["payload"]["space_index"] in GROUPS[g]
                             and e["payload"]["player_id"] != pid or
                             e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY_ASSETS_TO_BANK"
                             and e["payload"]["player_id"] == pid), len(es))
                future = [e for e in future if e["seq"] < lost]
                window = next((e for e in future if e["type"] == "LLM_DECISION_REQUESTED"
                               and e["payload"].get("player_id") == pid
                               and e["payload"].get("decision_type") == "POST_TURN_ACTION_DECISION"), None)
                build = next((e for e in future if e["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"}
                              and e["payload"]["player_id"] == pid and e["payload"]["space_index"] in GROUPS[g]), None)
                row.update({"first_management_turn": window["turn_index"] if window else None,
                            "first_management_decision": window["payload"]["decision_id"] if window else None,
                            "first_build_turn": build["turn_index"] if build else None,
                            "first_build_event": build["event_id"] if build else None,
                            "built_first_management_turn": bool(window and build and build["turn_index"] == window["turn_index"]),
                            "rent_after_acquisition_until_loss": sum(e["payload"]["amount"] for e in future
                                if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == pid
                                and e["payload"].get("space_index") in GROUPS[g]), "end_seq_exclusive": lost})
                stats[pid]["trade_groups"] += 1
                groups.append(row)
            # Read only the 20 known decision ledgers and retain the requested
            # management windows. Availability comes from the saved engine menu.
            windows = {(r["player_id"], r["first_management_turn"]) for r in group_rows}
            details = {}
            with (run / "decisions.jsonl").open() as f:
                for line in f:
                    d = json.loads(line)
                    if d.get("phase") != "decision_started" or (d.get("player_id"), d.get("turn_index")) not in windows:
                        continue
                    if d.get("decision_type") != "POST_TURN_ACTION_DECISION":
                        continue
                    payload = d["prompt_payload"]
                    action_state, state = payload["action_state"], payload["game_state"]
                    options = action_state.get("scenario", {}).get("options", {})
                    details[d["decision_id"]] = {
                        "cash": state["you"]["cash"], "mortgaged": state["you"]["holdings"]["mortgaged"],
                        "bank_houses": state["bank"]["houses_remaining"],
                        "buildable_keys": options.get("buildable_space_keys", []),
                        "available_actions": action_state.get("available_actions", []),
                    }
            for row in group_rows:
                g, pid = row["group"], row["player_id"]
                # Names in the engine use this normalization for these streets.
                keys = {BOARD[i]["name"].upper().replace(" ", "_").replace(".", "") for i in GROUPS[g]}
                first = details.get(row["first_management_decision"])
                requests = [e for e in es if row["seq"] < e["seq"] < row["end_seq_exclusive"]
                            and e["turn_index"] == row["first_management_turn"] and e["type"] == "LLM_DECISION_REQUESTED"
                            and e["payload"].get("player_id") == pid
                            and e["payload"].get("decision_type") == "POST_TURN_ACTION_DECISION"]
                eligible = lambda d: bool(d and keys.intersection(d["buildable_keys"])
                                          and "build_houses_or_hotel" in d["available_actions"])
                row.update({"cash_at_first_management": first["cash"] if first else None,
                            "mortgaged_at_first_management": json.dumps(first["mortgaged"]) if first else None,
                            "bank_houses_at_first_management": first["bank_houses"] if first else None,
                            "build_legal_at_first_management": eligible(first),
                            "build_legal_during_first_management_turn": any(eligible(details.get(e["payload"]["decision_id"])) for e in requests)})
            terminal_path = sorted((run / "state").glob("*.json"))[-1]
            terminal = read(terminal_path)
            assert terminal["phase"] == "GAME_OVER", (game, terminal_path)
            assert own == {s["index"]: s["owner_id"] for s in terminal["board"] if s["price"] is not None}, game
            assert [e["seq"] for e in es] == list(range(len(es))), game
            assert [e["payload"]["decision_id"] for e in es if e["type"] == "LLM_DECISION_REQUESTED"] == [a["decision_id"] for a in actions], game
            for pid in names:
                assert cash[pid] == summary["players"][pid]["cash"], (game, pid, cash[pid])
                players.append({"game": game, "seed": config["seed"], "model": names[pid], "player_id": pid,
                                "win": pid == winner, **{k: stats[pid][k] for k in [
                                    "proposals", "offers_received", "accepted_initiated", "accepted_received", "counters", "rolls",
                                    "rent_received", "rent_paid", "house_built", "hotel_built", "buy_deeds", "auction_deeds",
                                    "inheritance_deeds", "buy_groups", "auction_groups", "inheritance_groups", "trade_groups"]}})
            games.append({"game": game, "seed": config["seed"], "source_sha": index["git_sha"],
                          "winner": names[winner], "winner_seat0": int(winner[1:]) - 1, "turns": summary["turn_count"],
                          "events": len(es), "decisions": len(actions), "reason": summary["reason"],
                          "first_builder": names[first_build["payload"]["player_id"]] if first_build else None,
                          "first_build_seq": first_build["seq"] if first_build else None,
                          "first_build_turn": first_build["turn_index"] if first_build else None,
                          "package": str(package.relative_to(ROOT)), "model_order": ",".join(names.values())})
            dice_by_seed[config["seed"]].append((game, dice))
    dice_checks = []
    for seed, rows in dice_by_seed.items():
        for (a, ad), (b, bd) in itertools.combinations(rows, 2):
            dice_checks.append({"seed": seed, "game_a": a, "game_b": b, "common_length": min(len(ad), len(bd)),
                                "differing_dice_pairs": sum(x != y for x, y in zip(ad, bd))})
    aggregates = []
    for model in NAMES.values():
        rows = [x for x in players if x["model"] == model]
        aggregates.append({"model": model, **{k: sum(x[k] for x in rows) for k in rows[0] if k not in {"game", "seed", "model", "player_id"}},
                           "player_games_without_trade_group": sum(x["trade_groups"] == 0 for x in rows),
                           "player_games_without_earned_group": sum(x["trade_groups"] + x["buy_groups"] + x["auction_groups"] == 0 for x in rows)})
    for name, rows in [("sol_games.csv", games), ("sol_player_games.csv", players), ("sol_model_totals.csv", aggregates),
                       ("sol_trades.csv", trades), ("sol_trade_groups.csv", groups), ("sol_dice_checks.csv", dice_checks),
                       ("sol_source_hashes.csv", sources)]:
        write_csv(name, rows)
    print(json.dumps({"games": games, "model_totals": aggregates, "trade_kinds": dict(Counter(x["kind"] for x in trades)),
                      "trade_groups": len(groups), "dice_pairs": len(dice_checks),
                      "dice_pair_mismatches": sum(x["differing_dice_pairs"] for x in dice_checks)}, indent=2))


if __name__ == "__main__":
    main()
