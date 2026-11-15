"""Print every stored text channel, the menu and the carried memory for one decision.

Read-only. Usage: python3 dump.py GAME DECISION [--notes] [--timeline] [--holdings]
"""
import sys, json
from lib import *

def dump(g, d, notes=True, timeline=False, holdings=True, out=sys.stdout):
    st, rs = load(g)
    s, r = st[d], rs[d]
    pp = s["prompt_payload"]
    p = lambda *a: print(*a, file=out)
    p(f"===== G{g} d{d} {who(r)} {r['decision_type']} turn {r['turn_index']} player {r['player_id']}")
    you = pp["game_state"]["you"]
    p("cash", you["cash"], "position", you["position"])
    sc = pp["action_state"].get("scenario", {})
    p("scenario:", json.dumps({k: v for k, v in sc.items() if k != "note"}))
    p("available_actions:", [a if isinstance(a, str) else a.get("action") for a in pp["action_state"]["available_actions"]])
    p("bank:", {k: v for k, v in pp["game_state"]["bank"].items() if k != "unowned_space_keys"})
    if holdings:
        for h in you["holdings"]["owned"]:
            p("  own", json.dumps(h))
        for o in pp["game_state"]["others"]:
            p("  other", o["player_id"], NAME.get(o["name"], o["name"]), "cash", o["cash"], "bankrupt", o["bankrupt"])
    mem = pp["game_state"].get("memory", {})
    if notes:
        p("--- carried own notes (your_private_thoughts_last_10):")
        for n in mem.get("your_private_thoughts_last_10", []):
            p("   ", json.dumps(n, ensure_ascii=False))
    if timeline:
        p("--- public timeline:")
        for n in mem.get("public_timeline_last_20", []):
            p("   ", json.dumps(n, ensure_ascii=False))
    p("--- attempts:", len(r["attempts"]), "retry_used", r["retry_used"], "fallback_used", r["fallback_used"], r.get("fallback_reason"))
    for i, a in enumerate(r["attempts"]):
        m = message(a)
        p(f"  [attempt {i}] condition={a.get('response_condition')} outcome={a.get('outcome')} reason={a.get('reason')} errors={a.get('validation_errors')}")
        p("   assistant_content:", json.dumps(a.get("assistant_content"), ensure_ascii=False))
        for tc in a.get("parsed_tool_calls") or []:
            p("   tool_call:", tc["name"], tc["arguments"])
        p("   provider reasoning:", json.dumps(m.get("reasoning"), ensure_ascii=False))
        rd = m.get("reasoning_details") or []
        p("   reasoning_details types:", [(x.get("type"), x.get("format")) for x in rd])
        if m.get("refusal"):
            p("   refusal:", m.get("refusal"))
        u = (a.get("raw_response") or {}).get("usage") or {}
        p("   usage:", {k: u.get(k) for k in ("prompt_tokens", "completion_tokens")}, (u.get("completion_tokens_details") or {}))
    fa = r.get("final_action") or {}
    p("--- final_action:", fa.get("action"), json.dumps(fa.get("args"), ensure_ascii=False))
    p("    public_message:", json.dumps(fa.get("public_message"), ensure_ascii=False))
    p("    private_thought:", json.dumps(fa.get("private_thought"), ensure_ascii=False))
    p("    events:", r.get("emitted_event_types"))

if __name__ == "__main__":
    g, d = int(sys.argv[1]), int(sys.argv[2])
    dump(g, d, notes="--no-notes" not in sys.argv, timeline="--timeline" in sys.argv, holdings="--no-holdings" not in sys.argv)
