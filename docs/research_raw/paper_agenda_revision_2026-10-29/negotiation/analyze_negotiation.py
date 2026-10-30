"""Read-only canonical trade-thread, offer-consequence and typed-flow census.

No engine execution, model call, semantic intent label or edited input.
The pending offer's actor determines bundle direction; initiator does not.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COLLECTIONS = ("railway-research-12-games-2026-10-25", "railway-research-8-games-2026-10-26")
ALIAS = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini",
         "x-ai/grok-4.7": "Grok", "anthropic/claude-opus-5.5": "Opus"}
RESPONSE = {"TRADE_ACCEPTED": "accept_trade", "TRADE_REJECTED": "reject_trade",
            "TRADE_COUNTERED": "counter_trade"}


def rows(path):
    with path.open() as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                yield number, json.loads(line)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def game_dirs():
    found = {}
    for collection in COLLECTIONS:
        for path in sorted((ROOT / "saved_games" / collection).glob("game-*/run")):
            game = int(path.parent.name.split("-")[1])
            assert game not in found
            found[game] = path
    assert set(found) == set(range(1, 21))
    return dict(sorted(found.items()))


def complete_groups(owned, groups):
    return {group for group, deeds in groups.items() if deeds <= owned}


def consequences(state, author, recipient, offer, request, spaces, groups):
    players = {p["player_id"]: p for p in [state["you"], *state["others"]]}
    owned = {p: {d["space_key"] for d in s["holdings"]["owned"]} for p, s in players.items()}
    props = {d["space_key"]: d for s in players.values() for d in s["holdings"]["owned"]}
    before = {p: complete_groups(owned[p], groups) for p in (author, recipient)}
    offered, requested = set(offer["properties"]), set(request["properties"])
    assert offered <= owned[author] and requested <= owned[recipient], "Bundle owner mismatch"
    after_owned = {author: owned[author] - offered | requested,
                   recipient: owned[recipient] - requested | offered}
    after = {p: complete_groups(after_owned[p], groups) for p in (author, recipient)}
    # Mirrors the documented charge, separately checked against actual settlements.
    def interest(deeds):
        return sum(math.ceil((spaces[k]["price"] // 2) * 0.1)
                   for k in deeds if props[k]["mortgaged"])
    interests = {author: interest(requested), recipient: interest(offered)}
    net = offer["cash"] - request["cash"]
    cash_after = {author: players[author]["cash"] - net - interests[author],
                  recipient: players[recipient]["cash"] + net - interests[recipient]}
    # The proposal/counter validates deed/card ownership; acceptance additionally
    # requires resulting nonnegative cash. Do not call a mere completion feasible.
    developed_groups = {spaces[k]["group"] for k, d in props.items()
                        if d["houses"] or d["hotel"]}
    valid_bundles = all(not props[k]["houses"] and not props[k]["hotel"]
                        and spaces[k]["group"] not in developed_groups
                        for k in offered | requested)
    cards_ok = (players[author]["get_out_of_jail_cards"] >= offer["get_out_of_jail_cards"]
                and players[recipient]["get_out_of_jail_cards"] >= request["get_out_of_jail_cards"])
    return {
        "author_new_groups": sorted(after[author] - before[author]),
        "recipient_new_groups": sorted(after[recipient] - before[recipient]),
        "author_lost_groups": sorted(before[author] - after[author]),
        "recipient_lost_groups": sorted(before[recipient] - after[recipient]),
        "author_cash_before": players[author]["cash"],
        "recipient_cash_before": players[recipient]["cash"],
        "author_cash_if_accepted": cash_after[author],
        "recipient_cash_if_accepted": cash_after[recipient],
        "author_interest_if_accepted": interests[author],
        "recipient_interest_if_accepted": interests[recipient],
        "net_cash_author_to_recipient": net,
        "accounting_acceptance_feasible": valid_bundles and cards_ok and min(cash_after.values()) >= 0,
        "author_holdings_if_accepted": sorted(after_owned[author]),
        "recipient_holdings_if_accepted": sorted(after_owned[recipient]),
    }


def group_cell(row):
    own, other = bool(row["recipient_new_groups"]), bool(row["author_new_groups"])
    return "both" if own and other else "recipient_only" if own else "author_only" if other else "neither"


def write_csv(path, records):
    if not records:
        return
    fields = sorted({k for row in records for k in row})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in records:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})


def main():
    board_path = ROOT / "contracts/data/board.json"
    board = json.loads(board_path.read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s
              for s in board["spaces"] if s["price"] is not None}
    by_index = {s["index"]: key for key, s in spaces.items()}
    groups = defaultdict(set)
    for key, space in spaces.items():
        if space["kind"] == "PROPERTY":
            groups[space["group"]].add(key)
    hashes = {str(board_path.relative_to(ROOT)): digest(board_path)}
    thread_rows, response_rows, flows, snapshots, games = [], [], [], [], []
    validation = Counter()
    manual_sources = []

    for game, run in game_dirs().items():
        for name in ("events.jsonl", "actions.jsonl", "decisions.jsonl", "run_config.json", "summary.json"):
            hashes[str((run / name).relative_to(ROOT))] = digest(run / name)
        config = json.loads((run / "run_config.json").read_text())
        summary = json.loads((run / "summary.json").read_text())
        models = {p["player_id"]: ALIAS[p["openrouter_model_id"]] for p in config["players"]}
        starts, resolved = {}, {}
        for line, row in rows(run / "decisions.jsonl"):
            if row["phase"] != "decision_started":
                resolved[row["decision_id"]] = {
                    "fallback_used": row["fallback_used"],
                    "retry_used": row["retry_used"],
                    "response_condition": row["sequence_meta"].get("response_condition"),
                    "attempt_count": len(row["attempts"]),
                }
                continue
            payload = row.get("prompt_payload") or json.loads(row["prompt_messages"][1]["content"])
            starts[row["decision_id"]] = {"player_id": row["player_id"], "line": line,
                                         "payload": payload}
        actions = {r["decision_id"]: r for _, r in rows(run / "actions.jsonl")}
        events = [r for _, r in rows(run / "events.jsonl")]
        assert len(starts) == len(actions)
        own, mort, levels = dict.fromkeys(spaces), dict.fromkeys(spaces, False), dict.fromkeys(spaces, 0)
        cash = dict.fromkeys(models, 1500)
        current_id = None
        active, pending, settled_check = None, None, None
        latest_bankrupt = None
        thread_n = 0
        game_bankruptcies = 0
        pair_prior = Counter()
        pair_last_turn = {}
        game_start_index, game_response_index, flow_start = len(thread_rows), len(response_rows), len(flows)

        def check_settlement():
            nonlocal settled_check
            if settled_check is None:
                return
            row = settled_check
            for role in ("author", "recipient"):
                player = row[role]
                assert cash[player] == row[f"{role}_cash_if_accepted"], (game, row["decision"], role, "cash")
                assert sorted(k for k, owner in own.items() if owner == player) == row[f"{role}_holdings_if_accepted"], (game, row["decision"], role, "holdings")
            validation["accepted_state_checks"] += 1
            settled_check = None

        for event in events:
            kind, payload, seq = event["type"], event["payload"], event["seq"]
            actor = event["actor"].get("player_id")
            if kind == "LLM_DECISION_REQUESTED":
                check_settlement()
                current_id = payload["decision_id"]
                state = starts[current_id]["payload"]["game_state"]
                for p in [state["you"], *state["others"]]:
                    player = p["player_id"]
                    assert p["cash"] == cash[player], (game, seq, "cash", player)
                    delivered = {d["space_key"]: (d["mortgaged"], 5 if d["hotel"] else d["houses"])
                                 for d in p["holdings"]["owned"]}
                    reconstructed = {k: (mort[k], levels[k]) for k, owner in own.items() if owner == player}
                    assert delivered == reconstructed, (game, seq, "deeds", player)
                validation["decision_state_checks"] += 1
                deed_counts = Counter(owner for owner in own.values() if owner is not None)
                n = sum(deed_counts.values())
                snapshots.append({"game": game, "seq": seq, "decision_id": current_id,
                                  "turn": event["turn_index"], "owned_deeds": n,
                                  "deed_hhi": sum((c / n) ** 2 for c in deed_counts.values()) if n else None,
                                  "largest_deed_share": max(deed_counts.values()) / n if n else None,
                                  "winner_deeds": deed_counts[summary["winner_player_id"]],
                                  "winner_deed_share": deed_counts[summary["winner_player_id"]] / n if n else None,
                                  "counts": {models[p]: deed_counts[p] for p in models}})
            if kind == "GAME_ENDED":
                check_settlement()
            if kind in RESPONSE:
                assert active is not None and pending is not None, (game, seq, "no active thread")
                assert actor != pending["actor"], (game, seq, "nonalternating author")
                assert current_id in actions
                action = actions[current_id]["action"]
                assert action["action"] == RESPONSE[kind], (game, seq, action["action"], kind)
                started = starts[current_id]
                action_state = started["payload"]["action_state"]
                scenario = action_state["scenario"]
                current_offer = scenario["current_offer"]
                assert current_offer["from_player_id"] == pending["actor"]
                delivered = current_offer["if_you_accept"]
                assert delivered["you_receive"] == pending["payload"]["offer"]
                assert delivered["you_give"] == pending["payload"]["request"]
                assert started["player_id"] == actor
                author = pending["actor"]
                cons = consequences(started["payload"]["game_state"], author, actor,
                                    pending["payload"]["offer"], pending["payload"]["request"], spaces, groups)
                legal = "accept_trade" in action_state["available_actions"]
                assert legal == cons["accounting_acceptance_feasible"], (game, seq, "accept legality mismatch")
                validation["offer_orientation_and_legality_checks"] += 1
                row = {"game": game, "thread_id": active["thread_id"],
                       "decision_id": current_id, "decision": int(current_id.rsplit("-", 1)[1]),
                       "decision_source_line": started["line"], "source_run": str(run.relative_to(ROOT)),
                       "offer_seq": pending["seq"], "response_seq": seq,
                       "offer_decision": pending["decision"], "turn": event["turn_index"],
                       "initiator": active["initiator"], "author": author, "recipient": actor,
                       "author_model": models[author], "recipient_model": models[actor],
                       "exchange_index": scenario["exchange_index"], "response": action["action"],
                       "accept_available": legal, "offer": pending["payload"]["offer"],
                       "request": pending["payload"]["request"], **cons,
                       **resolved[current_id],
                       "public_message": action.get("public_message", ""),
                       "applied_private_note": action.get("private_thought", "")}
                row["completion_cell"] = group_cell(row)
                response_rows.append(row)
                active["response_count"] += 1
                active["response_ids"].append(current_id)
                if kind in ("TRADE_ACCEPTED", "TRADE_REJECTED"):
                    active.update({"terminal": kind, "terminal_seq": seq,
                                   "terminal_decision": row["decision"],
                                   "elapsed_global_turns": event["turn_index"] - active["start_turn"],
                                   "elapsed_global_decisions": row["decision"] - active["start_decision"],
                                   "final_author": author, "final_author_model": models[author],
                                   "final_author_is_initiator": author == active["initiator"],
                                   "final_completion_cell": row["completion_cell"],
                                   "counter_count": scenario["exchange_index"]})
                    thread_rows.append(active)
                    if kind == "TRADE_ACCEPTED":
                        assert legal
                        settled_check = row
                        for giver, receiver, bundle in ((author, actor, row["offer"]), (actor, author, row["request"])):
                            if bundle["cash"]:
                                flows.append({"game": game, "seq": seq, "turn": event["turn_index"],
                                              "kind": "trade_cash", "from": giver, "to": receiver,
                                              "from_model": models[giver], "to_model": models[receiver],
                                              "amount": bundle["cash"], "unit": "game_currency",
                                              "thread_id": active["thread_id"]})
                    active, pending = None, None
            if kind == "TRADE_PROPOSED":
                assert active is None and pending is None
                assert actions[current_id]["action"]["action"] == "propose_trade"
                thread_n += 1
                pair = tuple(sorted([payload["initiator_player_id"], payload["counterparty_player_id"]]))
                active = {"game": game, "thread_id": f"G{game:02d}-T{thread_n:03d}",
                          "source_run": str(run.relative_to(ROOT)), "start_seq": seq,
                          "start_decision": int(current_id.rsplit("-", 1)[1]), "start_turn": event["turn_index"],
                          "initiator": actor, "initiator_model": models[actor],
                          "counterparty": payload["counterparty_player_id"],
                          "counterparty_model": models[payload["counterparty_player_id"]],
                          "prior_threads_same_pair": pair_prior[pair],
                          "turns_since_previous_pair_thread": event["turn_index"] - pair_last_turn[pair] if pair in pair_last_turn else None,
                          "response_count": 0, "response_ids": []}
                pair_prior[pair] += 1
                pair_last_turn[pair] = event["turn_index"]
            if kind in ("TRADE_PROPOSED", "TRADE_COUNTERED"):
                pending = {"actor": actor, "payload": payload, "seq": seq,
                           "decision": int(current_id.rsplit("-", 1)[1])}

            if kind == "CASH_CHANGED":
                cash[payload["player_id"]] += payload["delta"]
                if payload["reason"] == "BANKRUPTCY":
                    latest_bankrupt = payload["player_id"]
                    game_bankruptcies += 1
                    validation["bankruptcies"] += 1
                elif payload["reason"] == "BANKRUPTCY_ASSETS_TO_BANK":
                    player = payload["player_id"]
                    for key in list(own):
                        if own[key] == player:
                            own[key], mort[key], levels[key] = None, False, 0
                elif payload["reason"] == "BANKRUPTCY_CASH" and payload["delta"] < 0:
                    following = events[seq + 1]
                    to = following["payload"]["player_id"] if following["type"] == "CASH_CHANGED" and following["payload"]["reason"] == "BANKRUPTCY_CASH" and following["payload"]["delta"] == -payload["delta"] else "BANK"
                    flows.append({"game": game, "seq": seq, "turn": event["turn_index"], "kind": "estate_cash",
                                  "from": payload["player_id"], "to": to, "from_model": models[payload["player_id"]],
                                  "to_model": models.get(to, "BANK"), "amount": -payload["delta"], "unit": "game_currency",
                                  "elimination_index": game_bankruptcies + 1,
                                  "terminal_estate": game_bankruptcies + 1 == len(models) - 1})
            elif kind == "PROPERTY_PURCHASED":
                key = by_index[payload["space_index"]]
                former = own[key]
                if former is not None:
                    assert payload["price"] == 0 and former == latest_bankrupt, (game, seq, "estate owner")
                    flows.append({"game": game, "seq": seq, "turn": event["turn_index"], "kind": "estate_deed",
                                  "from": former, "to": payload["player_id"], "from_model": models[former],
                                  "to_model": models[payload["player_id"]], "amount": 1, "unit": "deeds", "space_key": key,
                                  "elimination_index": game_bankruptcies,
                                  "terminal_estate": game_bankruptcies == len(models) - 1})
                own[key] = payload["player_id"]
            elif kind == "PROPERTY_TRANSFERRED":
                key = by_index[payload["space_index"]]
                assert own[key] == payload["from_player_id"]
                assert mort[key] == payload["mortgaged"]
                own[key] = payload["to_player_id"]
                flows.append({"game": game, "seq": seq, "turn": event["turn_index"], "kind": "trade_deed",
                              "from": payload["from_player_id"], "to": payload["to_player_id"],
                              "from_model": models[payload["from_player_id"]], "to_model": models[payload["to_player_id"]],
                              "amount": 1, "unit": "deeds", "space_key": key})
            elif kind in ("PROPERTY_MORTGAGED", "PROPERTY_UNMORTGAGED"):
                mort[by_index[payload["space_index"]]] = kind == "PROPERTY_MORTGAGED"
            elif kind in ("HOUSE_BUILT", "HOUSE_SOLD", "HOTEL_BUILT", "HOTEL_SOLD"):
                key = by_index[payload["space_index"]]
                if kind == "HOUSE_BUILT": levels[key] += payload["count"]
                elif kind == "HOUSE_SOLD": levels[key] -= payload["count"]
                elif kind == "HOTEL_BUILT": levels[key] = 5
                else: levels[key] = 4
            elif kind == "RENT_PAID":
                flows.append({"game": game, "seq": seq, "turn": event["turn_index"], "kind": "paid_rent",
                              "from": payload["from_player_id"], "to": payload["to_player_id"],
                              "from_model": models[payload["from_player_id"]], "to_model": models[payload["to_player_id"]],
                              "amount": payload["amount"], "unit": "game_currency",
                              "space_key": by_index[payload["space_index"]]})
        assert active is None and pending is None
        local_threads, local_responses = thread_rows[game_start_index:], response_rows[game_response_index:]
        games.append({"game": game, "seed": config["seed"], "winner": summary["winner_player_id"],
                      "winner_model": models[summary["winner_player_id"]], "turns": summary["turn_count"],
                      "threads": len(local_threads), "settlements": sum(r["terminal"] == "TRADE_ACCEPTED" for r in local_threads),
                      "response_opportunities": len(local_responses), "counters": sum(r["response"] == "counter_trade" for r in local_responses),
                      "paired_flow_rows": len(flows) - flow_start, "decisions": len(starts)})

    assert len(response_rows) == len(thread_rows) + sum(r["response"] == "counter_trade" for r in response_rows)
    assert len({r["decision_id"] for r in response_rows}) == len(response_rows)
    assert sum(r["terminal"] == "TRADE_ACCEPTED" for r in thread_rows) == validation["accepted_state_checks"]
    summary = summarize(thread_rows, response_rows, flows, snapshots, games)
    summary["validation"] = dict(validation)
    summary["protocol_sha256"] = digest(HERE / "protocol.md")
    summary["script_sha256"] = digest(Path(__file__))
    summary["source_hashes"] = hashes
    for name, data in [("threads", thread_rows), ("offers", response_rows), ("flows", flows), ("concentration", snapshots), ("games", games)]:
        (HERE / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n")
        write_csv(HERE / f"{name}.csv", data)
    (HERE / "results.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in {"source_hashes", "script_sha256"}}, indent=2))


def summarize(threads, offers, flows, snapshots, games):
    table = []
    for legal in (False, True):
        for cell in ("neither", "author_only", "recipient_only", "both"):
            group = [r for r in offers if (not legal or r["accept_available"]) and r["completion_cell"] == cell]
            counts = Counter(r["response"] for r in group)
            table.append({"population": "acceptance_available" if legal else "all_received",
                          "completion": cell, "offers": len(group), **{a: counts[a] for a in RESPONSE.values()}})
    models = []
    for name in ("Sol", "Gemini", "Opus", "Grok"):
        initiated = [r for r in threads if r["initiator_model"] == name]
        responses = [r for r in offers if r["recipient_model"] == name]
        completers = [r for r in responses if r["accept_available"] and r["recipient_new_groups"]]
        models.append({"model": name, "threads_initiated": len(initiated),
                       "initiated_threads_settled": sum(r["terminal"] == "TRADE_ACCEPTED" for r in initiated),
                       "received_offers": len(responses),
                       "accepted": sum(r["response"] == "accept_trade" for r in responses),
                       "countered": sum(r["response"] == "counter_trade" for r in responses),
                       "rejected": sum(r["response"] == "reject_trade" for r in responses),
                       "legal_self_completers": len(completers),
                       "self_completers_accepted": sum(r["response"] == "accept_trade" for r in completers),
                       "self_completers_countered": sum(r["response"] == "counter_trade" for r in completers),
                       "self_completers_rejected": sum(r["response"] == "reject_trade" for r in completers)})
    edges = defaultdict(lambda: {"events": 0, "amount": 0})
    for r in flows:
        key = (r["kind"], r["from_model"], r["to_model"], r["unit"])
        edges[key]["events"] += 1
        edges[key]["amount"] += r["amount"]
    accepted = [r for r in offers if r["response"] == "accept_trade"]
    winners = {r["game"]: r["winner"] for r in games}
    flows_by_kind = []
    for kind in sorted({r["kind"] for r in flows}):
        group = [r for r in flows if r["kind"] == kind]
        amount = sum(r["amount"] for r in group)
        winner_receipts = sum(r["amount"] for r in group if r["to"] == winners[r["game"]])
        flows_by_kind.append({"kind": kind, "events": len(group), "unit": group[0]["unit"],
                              "amount": amount, "received_by_eventual_winner": winner_receipts})
    estate_stage = []
    for kind in ("estate_cash", "estate_deed"):
        for terminal in (False, True):
            group = [r for r in flows if r["kind"] == kind and r["terminal_estate"] == terminal]
            estate_stage.append({"kind": kind, "terminal": terminal, "events": len(group),
                                 "amount": sum(r["amount"] for r in group),
                                 "received_by_eventual_winner": sum(r["amount"] for r in group if r["to"] == winners[r["game"]])})
    settled = [r for r in threads if r["terminal"] == "TRADE_ACCEPTED"]
    response_strata = []
    for game in range(1, 21):
        for name in ("Sol", "Gemini", "Opus", "Grok"):
            subset = [r for r in offers if r["game"] == game and r["recipient_model"] == name]
            initiated = [r for r in threads if r["game"] == game and r["initiator_model"] == name]
            cs = Counter(r["response"] for r in subset)
            response_strata.append({"game": game, "model": name, "initiated": len(initiated),
                                    "initiated_settled": sum(r["terminal"] == "TRADE_ACCEPTED" for r in initiated),
                                    "received": len(subset), "accept_available": sum(r["accept_available"] for r in subset),
                                    "own_completion_available": sum(r["accept_available"] and bool(r["recipient_new_groups"]) for r in subset),
                                    **{a: cs[a] for a in RESPONSE.values()}})
    pair_rows = []
    for game in range(1, 21):
        for a in ("Sol", "Gemini", "Opus", "Grok"):
            for b in ("Sol", "Gemini", "Opus", "Grok"):
                if a >= b:
                    continue
                subset = [r for r in threads if r["game"] == game and {r["initiator_model"], r["counterparty_model"]} == {a, b}]
                pair_rows.append({"game": game, "model_a": a, "model_b": b, "threads": len(subset),
                                  "settlements": sum(r["terminal"] == "TRADE_ACCEPTED" for r in subset),
                                  "responses": sum(r["response_count"] for r in subset)})
    return {"scope": "Finite-cohort descriptive census, not intention, surplus, fairness, optimality or causal effectiveness.",
            "counts": {"games": len(games), "threads": len(threads), "settlements": len(settled),
                       "responses": len(offers), "acceptance_available": sum(r["accept_available"] for r in offers),
                       "counters": sum(r["response"] == "counter_trade" for r in offers),
                       "rejections": sum(r["response"] == "reject_trade" for r in offers),
                       "settled_without_counter": sum(r["counter_count"] == 0 for r in settled),
                       "settled_with_counter": sum(r["counter_count"] > 0 for r in settled),
                       "settled_final_author_not_initiator": sum(not r["final_author_is_initiator"] for r in settled),
                       "threads_with_counter": sum(r["counter_count"] > 0 for r in threads),
                       "max_counter_count": max(r["counter_count"] for r in threads),
                       "median_responses_per_thread": median(r["response_count"] for r in threads),
                       "max_elapsed_global_turns": max(r["elapsed_global_turns"] for r in threads),
                       "repeat_pair_threads": sum(r["prior_threads_same_pair"] > 0 for r in threads),
                       "response_defaults": sum(r["fallback_used"] for r in offers),
                       "response_retries": sum(r["retry_used"] for r in offers),
                       "legal_recipient_completion_rejections": sum(r["accept_available"] and bool(r["recipient_new_groups"]) and r["response"] == "reject_trade" for r in offers)},
            "completion_response_table": table, "models": models,
            "accepted_completion_cells": dict(Counter(r["completion_cell"] for r in accepted)),
            "accepted_new_groups_by_role": {"author": sum(len(r["author_new_groups"]) for r in accepted), "recipient": sum(len(r["recipient_new_groups"]) for r in accepted)},
            "flow_totals": flows_by_kind,
            "estate_stage_totals": estate_stage,
            "typed_model_edges": [{"kind": k[0], "from_model": k[1], "to_model": k[2], "unit": k[3], **v} for k, v in sorted(edges.items())],
            "game_model_strata": response_strata, "game_pair_strata": pair_rows,
            "games": games,
            "outlier_threads": sorted(threads, key=lambda r: (-r["counter_count"], r["game"], r["start_seq"]))[:10]}


if __name__ == "__main__":
    main()
