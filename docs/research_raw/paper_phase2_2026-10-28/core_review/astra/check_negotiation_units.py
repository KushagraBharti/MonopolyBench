"""Reconstruct initiation units and trade-memory roles from canonical records.

No prompt edits, repaired trajectories, reliance labels, or provider calls.
The rejected-summary hypothesis was supplied by Opus before this implementation.
"""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from monopoly_arena.prompting import _trade_action_text

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PHASE1 = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra"
TRADE_VERBS = {"TRADE_PROPOSED": "proposed", "TRADE_COUNTERED": "countered",
               "TRADE_ACCEPTED": "accepted", "TRADE_REJECTED": "rejected"}


def rows(path):
    with path.open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def identity(item):
    return tuple(item.get(k) for k in ["turn_index", "player_id", "event_type", "action", "message"])


def bundle(value):
    parts = []
    if value.get("cash"):
        parts.append(f"${value['cash']}")
    if value.get("properties"):
        parts.append(", ".join(value["properties"]))
    cards = value.get("get_out_of_jail_cards", 0)
    if cards:
        parts.append(f"{cards} Get Out of Jail Free card" + ("s" if cards != 1 else ""))
    return " + ".join(parts) or "nothing"


def main():
    manifest = json.loads((PHASE1 / "visibility_manifest.json").read_text())
    cases, stats, sources = [], [], {}
    total_prompts, transitions, ambiguous_identities = 0, 0, []
    for game in manifest["games"]:
        run = ROOT / game["package"] / "run"
        names = {p["player_id"]: p["name"] for p in game["players"]}
        actions = {r["decision_id"]: r for r in rows(run / "actions.jsonl")}
        active, did, message = None, None, None
        request_seq = {}
        indexed = defaultdict(list)
        for e in rows(run / "events.jsonl"):
            p, kind = e["payload"], e["type"]
            if kind == "LLM_DECISION_REQUESTED":
                request_seq[p["decision_id"]] = e["seq"]
            elif kind == "LLM_DECISION_RESPONSE":
                did, message = p["decision_id"], None
            elif kind == "LLM_PUBLIC_MESSAGE":
                assert did == p["decision_id"]
                message = p.get("message") or None
            elif kind in TRADE_VERBS:
                actor = e["actor"]["player_id"]
                pair = {p["initiator_player_id"], p["counterparty_player_id"]}
                assert actor in pair and len(pair) == 2
                other = next(x for x in pair if x != actor)
                action = actions[did]["action"]
                if kind == "TRADE_PROPOSED":
                    assert actor == p["initiator_player_id"]
                    assert action["action"] == "propose_trade"
                    assert action["args"]["to_player_id"] == other
                else:
                    assert active is not None and active["author"] == other
                    transitions += 1
                if kind in {"TRADE_PROPOSED", "TRADE_COUNTERED"}:
                    assert action["args"]["offer"] == p["offer"]
                    assert action["args"]["request"] == p["request"]
                    active = {"author": actor, "offer": p["offer"], "request": p["request"]}
                    if kind == "TRADE_COUNTERED":
                        correct = f"countered trade with {other}: offer {bundle(p['offer'])}; request {bundle(p['request'])}"
                    else:
                        correct = f"proposed trade to {other}: offer {bundle(p['offer'])}; request {bundle(p['request'])}"
                else:
                    assert active["offer"] == p["offer"] and active["request"] == p["request"]
                    if kind == "TRADE_ACCEPTED":
                        correct = f"accepted trade with {other}: {other} gives {bundle(p['offer'])}; {actor} gives {bundle(p['request'])}"
                    else:
                        correct = f"rejected trade with {other}: {other} offered {bundle(p['offer'])} for {bundle(p['request'])}"
                    active = None
                rendered = _trade_action_text(TRADE_VERBS[kind], p)
                item = {"turn_index": e["turn_index"], "player_id": actor, "event_type": kind,
                        "action": rendered, "message": message}
                role_error = (kind == "TRADE_COUNTERED" and other != p["counterparty_player_id"]) or (
                    kind in {"TRADE_ACCEPTED", "TRADE_REJECTED"} and other != p["initiator_player_id"])
                assert (correct != rendered) == role_error
                case = {"game": game["game"], "decision_id": did, "event_seq": e["seq"],
                        "event_type": kind, "actor": actor, "other_party": other,
                        "exchange_index": p["exchange_index"], "recorded_item": item,
                        "correct_role_text": correct, "role_mismatch": role_error,
                        "prompt_exposures": []}
                indexed[identity(item)].append(case)
                cases.append(case)
        eligible, propose_turns, eligible_decisions, proposals = defaultdict(set), defaultdict(set), Counter(), Counter()
        for record in rows(run / "decisions.jsonl"):
            if record.get("phase") != "decision_started":
                continue
            total_prompts += 1
            actor, did = record["player_id"], record["decision_id"]
            payload = record["prompt_payload"]
            timeline = payload["game_state"]["memory"]["public_timeline_last_20"]
            occurrences = Counter(identity(item) for item in timeline if item.get("event_type") in TRADE_VERBS)
            for key, n_items in occurrences.items():
                matches = [c for c in indexed[key] if c["event_seq"] < request_seq[did]]
                assert len(matches) >= n_items, (game["game"], did, key)
                assert len({(m["role_mismatch"], m["correct_role_text"]) for m in matches}) == 1
                if len(indexed[key]) > 1:
                    ambiguous_identities.append({"game": game["game"], "decision_id": did,
                                                 "earlier_matching_event_seqs": [m["event_seq"] for m in matches],
                                                 "matched_event_seqs": [m["event_seq"] for m in matches[-n_items:]],
                                                 "rule": "Trade items never merge; retain latest matching occurrences before this prompt in the chronological suffix."})
                for m in matches[-n_items:]:
                    m["prompt_exposures"].append({"decision_id": did, "player_id": actor,
                                                   "model": names[actor], "turn_index": record["turn_index"]})
            state = payload["action_state"]
            chosen = actions[did]["action"]["action"]
            is_eligible = state["decision_type"] == "POST_TURN_ACTION_DECISION" and "propose_trade" in state["available_actions"]
            if chosen == "propose_trade":
                assert is_eligible
            if is_eligible:
                eligible[actor].add(record["turn_index"])
                eligible_decisions[actor] += 1
                if chosen == "propose_trade":
                    proposals[actor] += 1
                    propose_turns[actor].add(record["turn_index"])
        for actor, name in names.items():
            stats.append({"game": game["game"], "player_id": actor, "model": name,
                          "eligible_decisions": eligible_decisions[actor], "proposals": proposals[actor],
                          "eligible_turns": len(eligible[actor]), "proposing_turns": len(propose_turns[actor]),
                          "eligible_turn_indices": sorted(eligible[actor]),
                          "proposing_turn_indices": sorted(propose_turns[actor])})
        for name in ["events.jsonl", "actions.jsonl", "decisions.jsonl"]:
            p = run / name
            sources[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    assert total_prompts == 6989 and transitions == 920
    counts = Counter(c["event_type"] for c in cases)
    assert counts == {"TRADE_PROPOSED": 526, "TRADE_COUNTERED": 394, "TRADE_ACCEPTED": 113, "TRADE_REJECTED": 413}
    totals = defaultdict(Counter)
    for s in stats:
        for k in ["eligible_decisions", "proposals", "eligible_turns", "proposing_turns"]:
            totals[s["model"]][k] += s[k]
        totals[s["model"]]["zero_proposal_games"] += s["proposals"] == 0
    mismatches, affected = {}, {}
    for kind in TRADE_VERBS:
        selected = [c for c in cases if c["event_type"] == kind and c["role_mismatch"]]
        mismatches[kind] = len(selected)
        affected[kind] = sorted({x["decision_id"] for c in selected for x in c["prompt_exposures"]})
    accepted_rejected_union = set(affected["TRADE_ACCEPTED"]) | set(affected["TRADE_REJECTED"])
    summary = {"event_counts": counts, "role_mismatches": mismatches,
               "affected_initial_prompts_by_type": {k: len(v) for k, v in affected.items()},
               "accepted_rejected_union": len(accepted_rejected_union),
               "all_four_types_union": len(set().union(*map(set, affected.values()))),
               "repeated_identities_resolved_chronologically": len(ambiguous_identities), "initiation": totals}
    out = {"scope": "Mechanical source reconstruction. Initial recorded timelines only. Exposure is not reliance or a causal performance effect.",
           "peer_provenance": "Opus proposed the rejection extension and supplied expected counts before this independent implementation; no Opus code imported or read.",
           "summary": summary, "player_games": stats, "cases": cases,
           "affected_prompt_ids": affected, "repeated_identity_joins": ambiguous_identities,
           "source_sha256": sources, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "negotiation_units.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
