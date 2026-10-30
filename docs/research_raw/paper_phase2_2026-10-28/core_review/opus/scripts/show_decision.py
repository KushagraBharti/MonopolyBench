"""Print one canonical decision compactly: observation summary, legal actions, every attempt
(condition, outcome, tool name/args, public/private text, assistant content and provider reasoning,
truncated), applied action and emitted events. Usage: show_decision.py GAME DEC [DEC...] [--full]. Read-only."""
import json, sys, os
from common import game_dirs, decisions, action_state, events, ALIAS
args = [a for a in sys.argv[1:] if not a.startswith("--")]
FULL = "--full" in sys.argv
T = 100000 if FULL else int(os.environ.get("SD_TRUNC", "900"))
g = int(args[0]); run = game_dirs()[g]
st, rs = decisions(run)
ev = None
def trunc(s, n=T):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f"...[+{len(s)-n}]"
for d in args[1:]:
    did = [k for k in st if k.endswith(f"dec-{int(d):06d}")][0]
    s, r = st[did], rs[did]
    a, gs = action_state(s)
    you = gs["you"]
    print("=" * 90)
    print(did[-10:], s["decision_type"], s["player_id"], ALIAS[s["openrouter_model_id"]], "turn", s["turn_index"], "cash", you["cash"], "pos", you["position"])
    print(" holdings:", json.dumps(you["holdings"]))
    print(" others:", "; ".join(f'{o["player_id"]} ${o["cash"]} {o["position"]} own={o["holdings"].get("owned")} mort={o["holdings"].get("mortgaged")}' for o in gs["others"]))
    print(" legal:", a.get("available_actions"), trunc(a.get("scenario"), 1200))
    for i, at in enumerate(r.get("attempts") or []):
        tc = at.get("parsed_tool_call") or {}
        rr = (at.get("raw_response") or {}).get("choices", [{}])[0].get("message", {}) if at.get("raw_response") else {}
        reas = rr.get("reasoning") or ""
        print(f" [att{i}] {at.get('response_condition')}:{at.get('outcome')} tool={tc.get('name')} args={trunc(tc.get('arguments'), 1500 if not FULL else 100000)}")
        if at.get("validation_errors"): print("   val:", at.get("validation_errors"))
        if at.get("assistant_content"): print("   content:", trunc(at.get("assistant_content")))
        if reas: print("   reasoning:", trunc(reas))
    fa = r.get("final_action") or {}
    print(" APPLIED:", fa.get("action"), json.dumps(fa.get("args")), "| pub:", trunc(fa.get("public_message") or "", 600), "| priv:", trunc(fa.get("private_thought") or "", 600), "| fallback:", r.get("fallback_used"))
    print(" events:", r.get("emitted_event_seq_start"), "-", r.get("emitted_event_seq_end"), r.get("emitted_event_types"))
