"""For every Opus engine-fallback decision, take the last attempt's build plan (if any), convert it to target
levels per deed, and re-apply it as interleaved single-unit steps under the engine's per-entry checks
(engine.py ~2740-2800: evenness max-min<=1 after each entry, bank houses/hotels never negative mid-plan,
hotel needs four houses, total cash >= cost, deeds in buildable menu). Reports any plan that would still fail.
Read-only. Answers Fable S6 Q4."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, game_dirs, decisions, action_state, ALIAS

board = json.load(open(os.path.join(ROOT, "contracts", "data", "board.json")))
HC = board["house_cost_by_group"]
import re
GRP = {}
for s in board["spaces"]:
    if s.get("kind") == "PROPERTY":
        GRP[re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_")] = s["group"]
GROUPS = collections.defaultdict(list)
for k, g in GRP.items():
    GROUPS[g].append(k)

rows = []
for g, run in game_dirs().items():
    st, rs = decisions(run)
    for d, s in sorted(st.items()):
        if ALIAS[s["openrouter_model_id"]] != "Opus":
            continue
        r = rs.get(d) or {}
        if not r.get("fallback_used"):
            continue
        atts = r.get("attempts") or []
        plan = None
        last_err = None
        for at in atts:
            tc = at.get("parsed_tool_call") or {}
            if tc.get("name") == "build_houses_or_hotel":
                a = tc.get("arguments")
                if isinstance(a, str):
                    try:
                        a = json.loads(a)
                    except Exception:
                        a = {}
                plan = (a or {}).get("build_plan")
                last_err = at.get("validation_errors")
        a, gs = action_state(s)
        you = gs["you"]
        row = dict(game=g, decision=d[-10:], chain=[f"{at.get('response_condition')}:{at.get('outcome')}" for at in atts],
                   has_plan=plan is not None, last_error=last_err)
        if plan is None:
            rows.append(row); continue
        lv = {h["space_key"]: (5 if h["hotel"] else h["houses"]) for h in you["holdings"]["owned"]}
        target = dict(lv)
        for item in plan:
            k = item.get("space_key"); kind = item.get("kind"); c = int(item.get("count", 1) or 1)
            if k not in target:
                target[k] = None
                continue
            target[k] = 5 if kind == "HOTEL" else target[k] + c
        menu = set((a.get("scenario") or {}).get("options", {}).get("buildable_space_keys", []))
        bank_h = gs["bank"]["houses_remaining"]; bank_H = gs["bank"]["hotels_remaining"]
        problems = []
        if any(v is None for v in target.values()):
            problems.append("plan names a deed not owned")
        touched = {k for k in target if target.get(k) != lv.get(k)}
        if not touched <= menu:
            problems.append(f"deeds outside buildable menu: {sorted(touched - menu)}")
        cost = 0; cur = dict(lv); peak_ok = True
        groups = {GRP[k] for k in touched if k in GRP}
        for grp in groups:
            ks = GROUPS[grp]
            tl = {k: target.get(k, cur.get(k)) for k in ks}
            if max(tl.values()) - min(tl.values()) > 1:
                problems.append(f"final target uneven in {grp}: {tl}")
        # interleave: repeatedly raise the lowest deed (below target) in each touched group by one level
        progress = True
        while progress:
            progress = False
            for grp in sorted(groups):
                ks = GROUPS[grp]
                cand = [k for k in ks if cur[k] < target.get(k, cur[k])]
                if not cand:
                    continue
                k = min(cand, key=lambda x: cur[x])
                if cur[k] == 4:   # hotel step
                    bank_H -= 1; bank_h += 4
                else:
                    bank_h -= 1
                cur[k] += 1; cost += HC[grp]; progress = True
                levels = [cur[x] for x in ks]
                if max(levels) - min(levels) > 1:
                    problems.append(f"interleave uneven {grp} {levels}"); progress = False; break
                if bank_h < 0 or bank_H < 0:
                    problems.append("bank exhausted mid-plan"); peak_ok = False; progress = False; break
        if cost > you["cash"]:
            problems.append(f"cost {cost} > cash {you['cash']}")
        row.update(plan_entries=len(plan), max_entry_count=max(int(i.get('count', 1) or 1) for i in plan),
                   cost=cost, cash=you["cash"], bank_houses=gs["bank"]["houses_remaining"], interleaved_ok=not problems,
                   problems=problems)
        rows.append(row)
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "..", "interleave_check.json"), "w"), indent=1)
print("Opus fallbacks:", len(rows), "with plan:", sum(r["has_plan"] for r in rows))
print("interleaved OK:", sum(r.get("interleaved_ok", False) for r in rows))
for r in rows:
    if not r["has_plan"] or not r.get("interleaved_ok"):
        print(r["game"], r["decision"], r["chain"], r.get("last_error"), r.get("problems"))
print("errors on last attempt:", collections.Counter(json.dumps(r.get("last_error")) for r in rows).most_common(5))
print("max entry count dist:", collections.Counter(r.get("max_entry_count") for r in rows if r["has_plan"]))
