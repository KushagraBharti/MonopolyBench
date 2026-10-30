"""Reading aid for the common public-unflagged sample (read-only). For each sampled decision in GAME:
brief chronology (the previous 3 and next 2 decisions' applied actions/messages), then the full decision via
show_decision.py (all attempts/channels/events). Usage: sample_view.py GAME"""
import json, os, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from common import game_dirs, decisions, ALIAS

HERE = os.path.dirname(os.path.abspath(__file__))
CR = os.path.dirname(os.path.dirname(HERE))
g = int(sys.argv[1])
sample = [json.loads(l) for l in open(os.path.join(CR, "public_unflagged_sample.jsonl")) if l.strip()]
mine = [s for s in sample if s["game"] == g]
run = game_dirs()[g]
st, rs = decisions(run)
order = sorted(st)


def brief(d):
    s, r = st[d], rs.get(d) or {}
    fa = r.get("final_action") or {}
    return (f"   d{d[-6:]} {s['player_id']}/{ALIAS[s['openrouter_model_id']]} {s['decision_type'][:14]} -> {fa.get('action')} "
            f"{json.dumps(fa.get('args'))[:120]} | {str(fa.get('public_message') or '')[:140]}")


for smp in sorted(mine, key=lambda x: x["decision_id"]):
    d = smp["decision_id"]
    i = order.index(d)
    print("#" * 100)
    print("SAMPLE", d[-10:], "player", smp["player_id"], "rank", smp["selection_rank"], "eligible_in_stratum", smp["eligible_in_stratum"])
    print(" context before:")
    for x in order[max(0, i - 3):i]:
        print(brief(x))
    sys.stdout.flush()
    subprocess.run([sys.executable, os.path.join(HERE, "show_decision.py"), str(g), str(int(d[-6:]))], cwd=HERE)
    print(" context after:")
    for x in order[i + 1:i + 3]:
        print(brief(x))
    sys.stdout.flush()
