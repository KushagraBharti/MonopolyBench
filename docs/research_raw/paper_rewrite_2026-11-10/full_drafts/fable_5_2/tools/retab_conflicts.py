#!/usr/bin/env python3
"""Join the retained Grok action-name conflict ledger to the negotiation ledgers (existing data only).

Inputs : ../../data/resolution_conditions.json, ../../data/agenda_offers.json, ../../data/agenda_threads.json
Output : data/conflict_join.json
"""
import json, collections, pathlib
HERE = pathlib.Path(__file__).resolve().parent.parent
D = HERE.parent.parent / "data"
C = collections.Counter
res = json.loads((D / "resolution_conditions.json").read_text())
offers = json.loads((D / "agenda_offers.json").read_text())
threads = json.loads((D / "agenda_threads.json").read_text())
sc = res["selected_grok_conflicts"]
out = {"selected_conflicts": len(sc), "content_to_received": {f"{a} -> {b}": n for (a, b), n in sorted(C((x["content_name"], x["received_tool_name"]) for x in sc).items(), key=lambda kv: -kv[1])},
       "received_name": dict(C(x["received_tool_name"] for x in sc)), "all_in_nonstreamed_raw_json": all(x["nonstreamed_request"] and x["raw_body_json"] and x["raw_names_match_decision_record"] for x in sc),
       "end_provenance": res["counts"]}
ids = {x["decision_id"] for x in sc}
key = {(x["game"], int(x["decision_id"][-6:])) for x in sc}
resp = [r for r in offers if r["decision_id"] in ids]
out["trade_responses_with_conflict"] = {"n": len(resp), "by_response": dict(C(r["response"] for r in resp)), "by_response_cell": {f"{a}|{b}": n for (a, b), n in C((r["response"], r["completion_cell"]) for r in resp).items()},
                                        "accept_rows": [{"game": r["game"], "decision": r["decision"], "offer_writer": r["author_model"], "cell": r["completion_cell"], "writer_new_groups": r["author_new_groups"]} for r in resp if r["response"] == "accept_trade"]}
g = [t for t in threads if t["initiator_model"] == "Grok"]
gc = [t for t in g if (t["game"], t["start_decision"]) in key]
out["grok_threads"] = {"initiated": len(g), "settled": sum(1 for t in g if t["terminal"] == "TRADE_ACCEPTED"), "initiated_by_conflict_call": len(gc),
                       "conflict_initiated_settled": sum(1 for t in gc if t["terminal"] == "TRADE_ACCEPTED"), "games_with_conflict_initiation": len({t["game"] for t in gc})}
legal = [r for r in offers if r["accept_available"] and r["decision_id"] not in ids]
def tab(rr):
    c = C(r["response"] for r in rr); return {"n": len(rr), "accept": c["accept_trade"], "counter": c["counter_trade"], "reject": c["reject_trade"]}
out["cells_excluding_conflict_responses"] = {c: tab([r for r in legal if r["completion_cell"] == c]) for c in ["neither", "author_only", "recipient_only", "both"]}
grok_resp = [r for r in offers if r["recipient_model"] == "Grok"]
out["grok_responses"] = {"all": tab(grok_resp), "excluding_conflicts": tab([r for r in grok_resp if r["decision_id"] not in ids])}
(HERE / "data" / "conflict_join.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
