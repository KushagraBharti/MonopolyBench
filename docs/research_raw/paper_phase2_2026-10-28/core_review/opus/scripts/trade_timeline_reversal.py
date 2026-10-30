"""Count model-facing timeline lines that reverse trade direction after a counter.

Engine TRADE_* payloads carry initiator/counterparty and the *current* offer/request,
but not which side authored the current exchange. arena prompting._trade_action_text
renders accepted/rejected lines as if the initiator authored the offer. With strict
alternation, exchange_index odd => the counterparty authored the current offer, so
the rendered "X gives ...; Y gives ..." (accepted) and "X offered ... for ..." (rejected)
lines invert who gives what. Holdings/cash in game_state remain correct.

Read-only. Output: per-game counts of affected events and of prompts that carried the
reversed line in recent events (exact string match of the rendered line).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import game_dirs, events, jl, ALIAS


def bundle(b):
    parts = []
    c = b.get("cash", 0)
    if c:
        parts.append(f"${c}")
    if b.get("properties"):
        parts.append(", ".join(b["properties"]))
    j = b.get("get_out_of_jail_cards", 0)
    if j:
        parts.append(f"{j} Get Out of Jail Free card" + ("" if j == 1 else "s"))
    return " + ".join(parts) if parts else "nothing"


def main():
    tot = {"accepted": 0, "accepted_odd": 0, "rejected": 0, "rejected_odd": 0, "prompts_with_reversed": 0,
           "prompts_by_model": {}, "accepted_odd_by_game": {}}
    rows = []
    for g, run in game_dirs().items():
        ev = events(run)
        players = {}
        for r in jl(os.path.join(run, "decisions.jsonl")):
            players.setdefault(r["player_id"], ALIAS.get(r.get("openrouter_model_id"), r.get("openrouter_model_id")))
        reversed_lines = []
        for e in ev:
            if e["type"] not in ("TRADE_ACCEPTED", "TRADE_REJECTED"):
                continue
            p = e["payload"]
            kind = "accepted" if e["type"] == "TRADE_ACCEPTED" else "rejected"
            tot[kind] += 1
            if p["exchange_index"] % 2 == 1:
                tot[kind + "_odd"] += 1
                ini, cp = p["initiator_player_id"], p["counterparty_player_id"]
                if kind == "accepted":
                    line = f"accepted trade with {ini}: {ini} gives {bundle(p['offer'])}; {cp} gives {bundle(p['request'])}"
                    tot["accepted_odd_by_game"][g] = tot["accepted_odd_by_game"].get(g, 0) + 1
                else:
                    line = f"rejected trade with {ini}: {ini} offered {bundle(p['offer'])} for {bundle(p['request'])}"
                reversed_lines.append((e["seq"], kind, line))
        # exposure: prompts containing the reversed line
        dec = os.path.join(run, "decisions.jsonl")
        for r in jl(dec):
            if r["phase"] != "decision_started":
                continue
            content = r["prompt_messages"][1]["content"]
            hits = [s for s, k, l in reversed_lines if l in content]
            if hits:
                tot["prompts_with_reversed"] += 1
                pid = r.get("player_id")
                m = players.get(pid, pid)
                tot["prompts_by_model"][m] = tot["prompts_by_model"].get(m, 0) + 1
                rows.append({"game": g, "decision_id": r["decision_id"][-10:], "player": pid, "model": m,
                             "reversed_event_seqs": hits})
        for s, k, l in reversed_lines:
            print(f"G{g} seq {s} {k}: {l}")
    print(json.dumps({k: v for k, v in tot.items()}, indent=1))
    json.dump(rows, open(os.path.join(os.path.dirname(__file__), "..", "trade_timeline_reversal_rows.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
