"""usage: peek.py GAME LINE [LINE...] -> legal actions + raw scenario for those decisions (no big output)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
g = int(sys.argv[1]); rows = load_game(g)
for ln in map(int, sys.argv[2:]):
    r = rows[ln - 1]
    print("#%d %s %s avail=%s" % (ln, r["player_id"], r["decision_type"], r["action_state"]["available_actions"]))
    print("   scenario:", json.dumps(r["action_state"].get("scenario"))[:700])
    print("   applied:", json.dumps(r["applied_action"])[:400])
