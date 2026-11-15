"""Corpus-level counts from raw decisions.jsonl and events.jsonl, plus the cohort map.

Read-only. Writes data/corpus_summary.json and sections/gen_cohort_rows.tex.
"""
import collections
import json

from lib import *

C = collections.Counter
S = {"games": 20}
events = 0
decisions = C()
attempts = C()
first_refusals = C()
later_refusals = C()
refusal_messages = C()
refusal_by_game = {}
recovery_refused = 0
conditions = C()
fallbacks = C()
named = C()
conflict = C()
conflict_by_type = C()
provider_present = C()
provider_types = collections.defaultdict(C)
liq_named = C()
liq_conflict = []
liq_decisions = C()
liq_instruction = 0
winners = {}
turns = {}
cohort = []
decision_types = C()

for g in range(1, 21):
    rd = run_dir(g)
    with open(rd / "events.jsonl") as f:
        last_turn = 0
        winner = None
        for line in f:
            events += 1
            e = json.loads(line)
            last_turn = max(last_turn, e.get("turn_index", 0))
            if e["type"] == "GAME_ENDED":
                winner = e["payload"].get("winner_id") or e["payload"].get("winner_player_id")
    players = json.loads((rd / "players.json").read_text())
    plist = players if isinstance(players, list) else players.get("players", [])
    pmap = {p["player_id"]: NAME.get(p.get("name") or p.get("player_name"), p.get("name")) for p in plist}
    man = json.loads((rd / "experiment_manifest.json").read_text())
    st, rs, _ = load(g)
    g_first = g_ref = 0
    for i, r in rs.items():
        m = who(r)
        decisions[m] += 1
        decision_types[r["decision_type"]] += 1
        attempts[m] += len(r["attempts"])
        if r.get("fallback_used"):
            fallbacks[m] += 1
        for j, a in enumerate(r["attempts"]):
            msg = message(a)
            conditions[(m, a.get("response_condition"))] += 1
            if msg.get("refusal"):
                refusal_messages[msg["refusal"]] += 1
                if j == 0:
                    first_refusals[m] += 1
                    if m == "Opus":
                        g_ref += 1
                else:
                    later_refusals[m] += 1
                if a.get("response_condition") != "standard":
                    recovery_refused += 1
        if m == "Opus":
            g_first += 1
        fa = r["final_action"]
        last = r["attempts"][-1]
        n = named_action(last.get("assistant_content"))
        if n and not r.get("fallback_used"):
            named[m] += 1
            if n != fa["action"]:
                conflict[m] += 1
                conflict_by_type[(m, r["decision_type"])] += 1
        if provider_text(r):
            provider_present[m] += 1
        for t in provider_detail_types(r):
            provider_types[m][t] += 1
        if r["decision_type"] == "LIQUIDATION_DECISION":
            liq_decisions[m] += 1
            note = st[i]["prompt_payload"]["action_state"]["scenario"].get("note", "")
            if note.startswith("Choose exactly one liquidation action now."):
                liq_instruction += 1
            n2 = named_action(last.get("assistant_content"), FIN_ACTIONS)
            if n2:
                liq_named[m] += 1
                if n2 != fa["action"]:
                    liq_conflict.append(dict(game=g, d=i, model=m, named=n2, applied=fa["action"]))
    refusal_by_game[g] = [g_ref, g_first]
    cohort.append(dict(game=g, run=GAME_MAP[str(g)], turns=last_turn + 1, winner=pmap.get(winner), winner_id=winner,
                       experiment_id=man.get("experiment_id"), seats={pid: pmap[pid] for pid in sorted(pmap)}))
    winners[g] = pmap.get(winner)

S["events"] = events
S["decisions"] = sum(decisions.values())
S["attempts"] = sum(attempts.values())
S["decisions_by_model"] = dict(decisions)
S["attempts_by_model"] = dict(attempts)
S["decision_types"] = dict(decision_types)
S["fallback_decisions_by_model"] = dict(fallbacks)
S["first_attempt_refusals"] = dict(first_refusals)
S["later_attempt_refusals"] = dict(later_refusals)
S["refused_recovery_attempts"] = recovery_refused
S["refusal_messages"] = {k: v for k, v in refusal_messages.items()}
S["opus_first_refusals_by_game"] = refusal_by_game
S["conditions"] = {f"{m}|{c}": v for (m, c), v in conditions.items()}
S["content_names_action"] = dict(named)
S["content_action_conflicts"] = dict(conflict)
S["content_action_conflicts_by_type"] = {f"{m}|{t}": v for (m, t), v in conflict_by_type.items()}
S["provider_text_present"] = dict(provider_present)
S["provider_detail_types"] = {m: dict(v) for m, v in provider_types.items()}
S["liquidation_decisions_by_model"] = dict(liq_decisions)
S["liquidation_decisions"] = sum(liq_decisions.values())
S["liquidation_instruction_present"] = liq_instruction
S["liquidation_content_names_action"] = dict(liq_named)
S["liquidation_named_conflicts"] = liq_conflict
S["wins"] = dict(C(winners.values()))
S["cohort"] = cohort
write_json("corpus_summary.json", S)
for k, v in S.items():
    if k != "cohort":
        print(k, "=", v)
for c in cohort[:3]:
    print(c)
