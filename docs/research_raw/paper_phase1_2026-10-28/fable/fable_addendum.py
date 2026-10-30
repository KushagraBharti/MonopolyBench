"""Fable phase-1 addendum checks (fable_phase1_v1).

Three independent checks that reuse only this directory's reducer helpers:

1. Common-random-number horizon in *turn* units and the cause of the first seat
   divergence per within-block pair (bankruptcy skip, utility-card extra draw,
   or jail bankruptcy without a roll).
2. Legal-but-unbuilt management turns restricted to the period *before the first
   build* on each non-inherited group episode, by route and model. The whole-
   episode count in fable_results.json is dominated by post-development turns.
3. Provider refusal text for every refused Opus attempt, so the refusal
   condition is described by what the provider actually returned.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict

from fable_reducer import BUILD_EVENTS, COLLECTIONS, MANAGEMENT, NAMES, OUT, Board, ROOT, dice_uses, load_rows


def refusal_text(raw):
    """Collect provider-side refusal strings without inferring refusal from prose."""
    out = []
    if not isinstance(raw, dict):
        return out
    if raw.get("stop_reason") == "refusal":
        out.append("stop_reason=refusal")
    details = raw.get("stop_details")
    if isinstance(details, dict) and details.get("type") == "refusal":
        out.append(f"stop_details={details}")
    for ch in raw.get("choices") or []:
        fr, nfr = ch.get("finish_reason"), ch.get("native_finish_reason")
        msg = ch.get("message") or {}
        out.append(f"finish_reason={fr};native_finish_reason={nfr}")
        if msg.get("refusal"):
            out.append(f"message.refusal={msg['refusal']}")
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            out.append(f"content={content.strip()}")
    err = raw.get("error")
    if err:
        out.append(f"error={err}")
    return out


def main():
    board = Board(json.loads((ROOT / "contracts/data/board.json").read_text())["spaces"])
    episodes = [json.loads(line) for line in (OUT / "fable_group_episodes_all_routes.jsonl").open()]
    by_game_events = {}
    seat_by_game = {}
    names_by_game = {}
    refusal_strings = Counter()
    refusal_by_game = defaultdict(Counter)
    menus_by_game = {}
    for collection in COLLECTIONS:
        with (collection / "game-index.csv").open() as f:
            index = list(csv.DictReader(f))
        for row in index:
            game = int(row["collection_game"])
            run = collection / row["package"] / "run"
            cfg = json.loads((run / "run_config.json").read_text())
            names_by_game[game] = {p["player_id"]: NAMES[p["openrouter_model_id"]] for p in cfg["players"]}
            seat_by_game[game] = (cfg["seed"], {s["player_id"]: s["seat_index"] for s in cfg["seat_assignment"]})
            by_game_events[game] = list(load_rows(run / "events.jsonl"))
            menus = {}
            for d in load_rows(run / "decisions.jsonl"):
                if d["phase"] == "decision_started":
                    st = d["prompt_payload"]["action_state"]
                    menus[d["decision_id"]] = (st["available_actions"],
                                               st.get("scenario", {}).get("options", {}).get("buildable_space_keys", []))
                elif names_by_game[game][d["player_id"]] == "Opus":
                    for a in d["attempts"]:
                        if a.get("outcome") == "refused":
                            key = " | ".join(refusal_text(a.get("raw_response")))
                            refusal_strings[key] += 1
                            refusal_by_game[game][a.get("response_condition")] += 1
            menus_by_game[game] = menus
    # 1. CRN horizon in turns and cause
    blocks = defaultdict(list)
    for game, (seed, seat_of) in seat_by_game.items():
        blocks[seed].append((game, dice_uses(by_game_events[game], seat_of), by_game_events[game]))
    rows = []
    for seed, lst in blocks.items():
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                ga, ua, ea = lst[a]
                gb, ub, eb = lst[b]
                n = min(len(ua), len(ub))
                k_seat = next((k for k in range(n) if ua[k]["seat"] != ub[k]["seat"]), None)
                k_land = next((k for k in range(n) if (ua[k]["seat"], ua[k]["landing"]) != (ub[k]["seat"], ub[k]["landing"])), None)
                cause = None
                if k_seat is not None:
                    # look at the draw just before divergence in both games
                    prev_a, prev_b = ua[k_seat - 1], ub[k_seat - 1]
                    if "CARD_UTILITY_RENT" in {ua[k_seat]["reason"], ub[k_seat]["reason"], prev_a["reason"], prev_b["reason"]}:
                        cause = "utility_card_extra_draw"
                    else:
                        # bankruptcy before the divergent draw in either game?
                        ta, tb = ua[k_seat]["turn"], ub[k_seat]["turn"]
                        ba = any(e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY" and e["turn_index"] <= ta for e in ea)
                        bb = any(e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY" and e["turn_index"] <= tb for e in eb)
                        cause = "bankrupt_seat_skipped" if (ba or bb) else "other"
                rows.append({"seed": seed, "game_a": ga, "game_b": gb, "shared_prefix_draws": n,
                             "first_seat_divergence_draw": k_seat,
                             "first_seat_divergence_turn_a": ua[k_seat]["turn"] if k_seat is not None else None,
                             "first_seat_divergence_turn_b": ub[k_seat]["turn"] if k_seat is not None else None,
                             "first_landing_divergence_draw": k_land,
                             "first_landing_divergence_turn_a": ua[k_land]["turn"] if k_land is not None else None,
                             "first_landing_divergence_turn_b": ub[k_land]["turn"] if k_land is not None else None,
                             "seat_divergence_cause": cause,
                             "turns_a": ea[-1]["turn_index"], "turns_b": eb[-1]["turn_index"]})
    with (OUT / "fable_crn_horizon_turns.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    # 2. pre-first-build legal-but-unbuilt management turns
    pre = defaultdict(Counter)
    for ep in episodes:
        if ep["route"] == "creditor_inheritance":
            continue
        g, pid = ep["game"], ep["player_id"]
        events, menus = by_game_events[g], menus_by_game[g]
        idx = set(board.groups[ep["group"]])
        keys = {board.index_to_key[i] for i in idx}
        lo, hi = ep["settlement_end_seq"], ep["end_seq_exclusive"]
        first_build = next((e for e in events if lo < e["seq"] < hi and e["type"] in BUILD_EVENTS
                            and e["payload"]["player_id"] == pid and e["payload"]["space_index"] in idx), None)
        first_build_seq = first_build["seq"] if first_build else hi
        first_build_turn = first_build["turn_index"] if first_build else None
        legal_turns, all_turns = set(), set()
        for e in events:
            if lo < e["seq"] < first_build_seq and e["type"] == "LLM_DECISION_REQUESTED" \
                    and e["payload"]["player_id"] == pid and e["payload"]["decision_type"] == MANAGEMENT \
                    and e["turn_index"] != first_build_turn:
                # The menu that leads to the first build sits in the same turn as that build;
                # a turn counts as skipped only if it ended without any build on the group.
                acts, bk = menus[e["payload"]["decision_id"]]
                all_turns.add(e["turn_index"])
                if "build_houses_or_hotel" in acts and keys & set(bk):
                    legal_turns.add(e["turn_index"])
        key = (ep["model"], "trade" if ep["route"] == "trade" else "purchase_or_auction")
        pre[key]["episodes"] += 1
        pre[key]["legal_mgmt_turns_before_first_build"] += len(legal_turns)
        pre[key]["mgmt_turns_before_first_build"] += len(all_turns)
        pre[key]["episodes_with_any_legal_skip_before_first_build"] += bool(legal_turns)
        pre[key]["never_built"] += not ep["ever_built"]
    pre_out = {f"{m}|{r}": dict(c) for (m, r), c in sorted(pre.items())}
    # 3. refusal text
    report = {
        "crn_horizon_turn_units": {
            "pairs": len(rows),
            "first_landing_divergence_turn_min_median_max": _mmm([min(r["first_landing_divergence_turn_a"], r["first_landing_divergence_turn_b"]) for r in rows]),
            "first_seat_divergence_turn_min_median_max": _mmm([min(r["first_seat_divergence_turn_a"], r["first_seat_divergence_turn_b"]) for r in rows]),
            "seat_divergence_cause": dict(Counter(r["seat_divergence_cause"] for r in rows)),
            "shortest_game_turns_in_pair_min_median_max": _mmm([min(r["turns_a"], r["turns_b"]) for r in rows]),
        },
        "legal_unbuilt_turns_before_first_build": pre_out,
        "opus_refused_attempts": sum(refusal_strings.values()),
        "opus_refusal_distinct_provider_strings": len(refusal_strings),
        "opus_refusal_strings": [{"n": n, "text": k} for k, n in refusal_strings.most_common()],
        "opus_refused_by_game_and_condition": {g: dict(c) for g, c in sorted(refusal_by_game.items())},
    }
    (OUT / "fable_addendum.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


def _mmm(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    med = xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
    return {"min": xs[0], "median": med, "max": xs[-1]}


if __name__ == "__main__":
    main()
