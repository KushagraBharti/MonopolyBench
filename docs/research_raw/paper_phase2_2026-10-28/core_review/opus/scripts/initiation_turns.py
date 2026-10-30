"""Per-model trade initiation with three denominators (read-only).

1. proposals / eligible post-turn decisions (propose_trade legal) -- endogenous: every proposal or
   other optional action returns the player to another post-turn menu, so active players add
   eligible decisions.
2. propensity: eligible own turns with >=1 applied proposal / eligible own turns (distinct
   turn_index where the player had >=1 post-turn decision with propose_trade legal).
3. intensity: applied proposals / turns with >=1 proposal.
Also reports eligible decisions per eligible turn (menu inflation).
"""
import json, sys, collections, os
sys.path.insert(0, os.path.dirname(__file__))
from common import game_dirs, decisions, action_state, ALIAS

per_game = {}
tot = collections.defaultdict(collections.Counter)
for g, run in game_dirs().items():
    st, rs = decisions(run)
    el_dec = collections.Counter(); props = collections.Counter()
    el_turns = collections.defaultdict(set); prop_turns = collections.defaultdict(set)
    for d, s in sorted(st.items()):
        m = ALIAS[s["openrouter_model_id"]]
        if s["decision_type"] != "POST_TURN_ACTION_DECISION":
            continue
        a, _ = action_state(s)
        if "propose_trade" not in a["available_actions"]:
            continue
        t = s["turn_index"]
        el_dec[m] += 1; el_turns[m].add(t)
        fa = ((rs.get(d) or {}).get("final_action") or {}).get("action")
        if fa == "propose_trade":
            props[m] += 1; prop_turns[m].add(t)
    row = {}
    for m in sorted(set(el_dec) | set(props)):
        row[m] = dict(eligible_decisions=el_dec[m], proposals=props[m], eligible_turns=len(el_turns[m]),
                      proposing_turns=len(prop_turns[m]))
        for k, v in row[m].items():
            tot[m][k] += v
    per_game[g] = row


def fmt(v):
    ed, p, et, pt = v["eligible_decisions"], v["proposals"], v["eligible_turns"], v["proposing_turns"]
    return (f"props/elig_dec {p}/{ed}={p/ed:.3f} | propensity {pt}/{et}={pt/et:.3f} | "
            f"intensity {p}/{pt}={(p/pt if pt else 0):.2f} | elig_dec/elig_turn {ed/et:.2f}")


for g, row in per_game.items():
    print(f"G{g}", {m: f"{v['proposals']}/{v['eligible_decisions']} turns {v['proposing_turns']}/{v['eligible_turns']}" for m, v in row.items()})
print()
for m in sorted(tot):
    print(m, fmt(tot[m]))
# per-game propensity range
print()
for m in sorted(tot):
    vals = [r[m]["proposing_turns"] / r[m]["eligible_turns"] for r in per_game.values() if m in r and r[m]["eligible_turns"]]
    zero = sum(1 for r in per_game.values() if m in r and r[m]["proposals"] == 0)
    print(m, f"per-game propensity min {min(vals):.3f} median {sorted(vals)[len(vals)//2]:.3f} max {max(vals):.3f}; games with 0 proposals {zero}/20")
json.dump({"per_game": per_game, "total": {m: dict(v) for m, v in tot.items()}},
          open(os.path.join(os.path.dirname(__file__), "..", "initiation_turns.json"), "w"), indent=1)
