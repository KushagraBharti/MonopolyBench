"""Source reads for the nine no-option windows, price cuts and Grok conflicts (no engine).

Usage: python3 -I check_windows_prices_conflicts.py <repo_root> <out_json>
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

repo, out_path = Path(sys.argv[1]), Path(sys.argv[2])
pkg = repo / "docs/research_raw/paper_rewrite_2026-11-10"
board = json.loads((repo / "contracts/data/board.json").read_bytes())
offers = json.loads((pkg / "data/agenda_offers.json").read_bytes())
windows = json.loads((pkg / "data/first_management_windows.json").read_bytes())["rows"]
rc = json.loads((pkg / "data/resolution_conditions.json").read_bytes())
runs = {r["game"]: repo / r["source_run"] for r in offers}


def key(name):
    k = "".join(ch if ch.isalnum() else "_" for ch in name.upper())
    while "__" in k:
        k = k.replace("__", "_")
    return k.strip("_")


spaces = {key(s["name"]): s for s in board["spaces"] if s.get("price") is not None}
assert len(spaces) == 28, len(spaces)
out = {"board_key_check": {k: spaces[k]["price"] for k in ("B_O_RAILROAD", "BALTIC_AVENUE", "PARK_PLACE", "BOARDWALK")}}

# float ceilings (pure arithmetic)
principals = sorted({s["price"] // 2 for s in spaces.values()})
out["redemption_overcharge_principals"] = [p for p in principals if math.ceil(p * 1.1) != (p * 11 + 9) // 10]
out["transfer_interest_mismatch_principals"] = [p for p in principals if math.ceil(p * 0.1) != (p + 9) // 10]
out["principals"] = principals

cache = {}


def recs(g):
    if g not in cache:
        cache[g] = [json.loads(line) for line in (runs[g] / "decisions.jsonl").read_bytes().splitlines()]
    return cache[g]


def idx(r):
    return int(r["decision_id"].rsplit("-", 1)[1])


def started(g, i):
    return next(r for r in recs(g) if r["phase"] == "decision_started" and idx(r) == i)


def resolved(g, i):
    return next(r for r in recs(g) if r["phase"] == "decision_resolved" and idx(r) == i)


def selected_attempt(res):
    valid = [a for a in res["attempts"] if a["outcome"] == "valid"]
    return valid[-1] if valid else res["attempts"][-1]


def note_of(res):
    a = selected_attempt(res)
    call = a.get("parsed_tool_call") or {}
    args = call.get("arguments") or call.get("args") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {}
    return args.get("private_thought"), a.get("assistant_content"), call.get("name")


# ---- nine no-option windows
access = []
for w in windows:
    if w["cause"] != "never_legal_in_window":
        continue
    g = w["game"]
    first = int(w["first_mgmt_decision"].rsplit("-", 1)[1])
    st = started(g, first)
    pay = st["prompt_payload"]
    you = pay["game_state"]["you"]
    owned = {o["space_key"]: o for o in you["holdings"]["owned"]}
    opts = pay["action_state"]["scenario"]["options"]
    target = {k for k, s in spaces.items() if s.get("group") == w["group"]}
    mort_t = sorted(k for k in target if owned[k]["mortgaged"])
    red = {k: math.ceil((spaces[k]["price"] // 2) * 1.1) for k in mort_t}
    outside = {k: spaces[k]["price"] // 2 for k in opts.get("mortgageable_space_keys", []) if k not in target}
    house = board["house_cost_by_group"][w["group"]]
    # every decision of the window: menu and applied action, with any buildable keys
    menu_rows = []
    for d in w["decisions"]:
        di = int(d["decision_id"].rsplit("-", 1)[1])
        s2, r2 = started(g, di), resolved(g, di)
        o2 = s2["prompt_payload"]["action_state"]["scenario"].get("options", {})
        note, content, name = note_of(r2)
        menu_rows.append({"d": di, "turn": s2["turn_index"], "cash": s2["prompt_payload"]["game_state"]["you"]["cash"],
                          "available": [a["action"] if isinstance(a, dict) else a
                                        for a in s2["prompt_payload"]["action_state"]["available_actions"]],
                          "buildable": o2.get("buildable_space_keys", []),
                          "mortgageable": o2.get("mortgageable_space_keys", []),
                          "unmortgageable": o2.get("unmortgageable_space_keys", []),
                          "applied": r2["final_action"]["action"], "applied_args": r2["final_action"].get("args"),
                          "condition": (r2.get("sequence_meta") or {}).get("response_condition"),
                          "note": note, "content_head": (content or "")[:300]})
    access.append({"game": g, "d": first, "model": w["model"], "group": w["group"], "cash": you["cash"],
                   "target_mortgaged": mort_t, "R": sum(red.values()), "house": house, "outside": outside,
                   "M": sum(outside.values()), "remainder": you["cash"] + sum(outside.values()) - sum(red.values()) - house,
                   "bank_houses": pay["game_state"]["bank"]["houses_remaining"],
                   "other_complete_groups_at_risk": sorted({spaces[k].get("group") for k in outside}),
                   "private_memory_len": len(pay["game_state"]["memory"]["your_private_thoughts_last_10"]),
                   "window": menu_rows})
out["access"] = access

# ---- price table
legal = [r for r in offers if r["accept_available"]]


def direction(r):
    o, q = r["offer"], r["request"]
    if o["get_out_of_jail_cards"] or q["get_out_of_jail_cards"]:
        return None
    if not o["properties"] and q["properties"] and q["cash"] == 0 and o["cash"] > 0:
        return "bid", q["properties"], o["cash"]
    if o["properties"] and not q["properties"] and o["cash"] == 0 and q["cash"] > 0:
        return "ask", o["properties"], q["cash"]
    return None


pure = []
for r in legal:
    d = direction(r)
    if d:
        pure.append({"kind": d[0], "cell": r["completion_cell"], "ratio": d[2] / sum(spaces[k]["price"] for k in d[1]),
                     "mortgaged": r["author_interest_if_accepted"] + r["recipient_interest_if_accepted"] > 0,
                     "opening": r["exchange_index"] == 0, "n_deeds": len(d[1]),
                     "author": r["author_model"], "recipient": r["recipient_model"]})
table = {}
for kind, cell in (("bid", "author_only"), ("bid", "neither"), ("ask", "recipient_only"), ("ask", "neither")):
    for lab, f in (("All", lambda x: True), ("Unmortgaged", lambda x: not x["mortgaged"]),
                   ("Opening", lambda x: x["opening"]), ("Later", lambda x: not x["opening"])):
        rows = [x for x in pure if x["kind"] == kind and x["cell"] == cell and f(x)]
        table[f"{lab}/{kind}/{cell}"] = [round(median(x["ratio"] for x in rows), 3), len(rows)]
out["price_table"] = table
out["price_other_cells"] = {f"{k}/{c}": n for (k, c), n in Counter((x["kind"], x["cell"]) for x in pure).items()}
out["price_authors"] = {f"{k}/{c}": dict(Counter(x["author"] for x in pure if x["kind"] == k and x["cell"] == c))
                        for k, c in (("bid", "author_only"), ("bid", "neither"), ("ask", "recipient_only"), ("ask", "neither"))}
out["jail_card_offers_excluded"] = sum(
    1 for r in legal if (r["offer"]["get_out_of_jail_cards"] or r["request"]["get_out_of_jail_cards"])
    and ((not r["offer"]["properties"] and r["request"]["properties"] and r["request"]["cash"] == 0 and r["offer"]["cash"] > 0)
         or (r["offer"]["properties"] and not r["request"]["properties"] and r["offer"]["cash"] == 0 and r["request"]["cash"] > 0)))

# ---- Grok conflicts
conf = rc["selected_grok_conflicts"]
cid = {(c["game"], int(c["decision_id"].rsplit("-", 1)[1])): c for c in conf}
out["conflicts_total"] = len(conf)
out["conflict_name_pairs"] = {f"{a}->{b}": n for (a, b), n in
                              Counter((c["content_name"], c["received_tool_name"]) for c in conf).most_common()}
resp_conf = Counter(r["response"] for r in offers if r["recipient_model"] == "Grok" and (r["game"], r["decision"]) in cid)
out["grok_response_conflicts"] = dict(resp_conf)
openings = [r for r in offers if r["exchange_index"] == 0 and r["author_model"] == "Grok"]
by_thread = defaultdict(list)
for r in offers:
    by_thread[r["thread_id"]].append(r)
conf_open = [r for r in openings if (r["game"], r["offer_decision"]) in cid]
out["grok_openings"] = len(openings)
out["grok_conflicting_openings"] = len(conf_open)
out["grok_conflicting_openings_content_names"] = dict(Counter(cid[(r["game"], r["offer_decision"])]["content_name"] for r in conf_open))
out["grok_conflicting_opening_threads_settled"] = sum(
    any(x["response"] == "accept_trade" for x in by_thread[r["thread_id"]]) for r in conf_open)
out["grok_nonconflicting_opening_threads_settled"] = [
    sum(any(x["response"] == "accept_trade" for x in by_thread[r["thread_id"]]) for r in openings if r not in conf_open),
    len(openings) - len(conf_open)]
acc_conf = [r for r in offers if r["recipient_model"] == "Grok" and r["response"] == "accept_trade"
            and (r["game"], r["decision"]) in cid]
out["grok_conflicting_accepts"] = [(r["game"], r["decision"], r["author_model"], r["completion_cell"], r["author_new_groups"],
                                    cid[(r["game"], r["decision"])]["content_name"]) for r in acc_conf]
out["end_records"] = {m: v for m, v in rc["counts"].items()}

# ---- first-window ledger summary
out["first_window_causes"] = dict(Counter(w["cause"] for w in windows))
out["first_window_entry_legal"] = dict(Counter((w["entry_legal"], w["cause"]) .__str__() for w in windows))
out["first_window_conflict_rows"] = [(w["game"], w["model"], w["group"], w["first_mgmt_decision"], w["entry_legal"],
                                      [(d["decision_id"], d["applied"], d["conflict"]) for d in w["decisions"]])
                                     for w in windows if w["cause"] == "received_conflict"]
out["first_window_other_rows"] = [(w["game"], w["model"], w["group"], w["first_mgmt_decision"], w["entry_legal"], w["cause"],
                                   [(d["decision_id"], d["applied"], d["default"]) for d in w["decisions"]])
                                  for w in windows if w["cause"] in ("valid_end", "default_other", "default_after_refusal")]
out_path.write_text(json.dumps(out, indent=1, default=str) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "access"}, indent=1, default=str))
