#!/usr/bin/env python3
"""Re-tabulate the retained 920-row offer ledger (existing data only).

Input : ../../data/agenda_offers.json (shared, read-only)
Output: data/offer_retabulation.json
No engine, model, or game execution. Pure counting over retained rows.
"""
import json, collections, statistics as st, pathlib, hashlib
HERE = pathlib.Path(__file__).resolve().parent.parent
SRC = HERE.parent.parent / "data" / "agenda_offers.json"
rows = json.loads(SRC.read_text())
C = collections.Counter
RESP = ["accept_trade", "counter_trade", "reject_trade"]
CELLS = ["neither", "author_only", "recipient_only", "both"]
BLOCK = lambda g: (g - 1) // 4 + 1

def tab(rr):
    c = C(r["response"] for r in rr)
    return {"n": len(rr), "accept": c["accept_trade"], "counter": c["counter_trade"], "reject": c["reject_trade"]}

def med(xs):
    xs = list(xs)
    return st.median(xs) if xs else None

legal = [r for r in rows if r["accept_available"]]
out = {"source": str(SRC.relative_to(HERE.parent.parent)), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
       "n_rows": len(rows), "n_accept_legal": len(legal)}
out["all_responses"] = tab(rows)
out["excluded_rows"] = [{k: r[k] for k in ("game", "decision", "author_model", "recipient_model", "response", "completion_cell")} for r in rows if not r["accept_available"]]

# 1. completion cells, legal offers
cells = {}
for c in CELLS:
    rr = [r for r in legal if r["completion_cell"] == c]
    t = tab(rr)
    net = [r["net_cash_author_to_recipient"] for r in rr]
    t["median_net_cash_to_recipient"] = med(net)
    t["net_positive"] = sum(1 for x in net if x > 0)
    t["net_zero"] = sum(1 for x in net if x == 0)
    t["net_negative"] = sum(1 for x in net if x < 0)
    t["q1_q3_net"] = [st.quantiles(net, n=4)[0], st.quantiles(net, n=4)[2]] if len(net) >= 4 else None
    cells[c] = t
out["cells_legal"] = cells

# 2. response style by recipient configuration, all 920 and legal 918
out["recipient_style_all"] = {m: tab([r for r in rows if r["recipient_model"] == m]) for m in ["Sol", "Gemini", "Opus", "Grok"]}
out["recipient_style_legal"] = {m: tab([r for r in legal if r["recipient_model"] == m]) for m in ["Sol", "Gemini", "Opus", "Grok"]}
out["author_counts_all"] = {m: tab([r for r in rows if r["author_model"] == m]) for m in ["Sol", "Gemini", "Opus", "Grok"]}

# 3. cell x recipient configuration
out["cell_by_recipient"] = {m: {c: tab([r for r in legal if r["recipient_model"] == m and r["completion_cell"] == c]) for c in CELLS} for m in ["Sol", "Gemini", "Opus", "Grok"]}
out["cell_by_author"] = {m: {c: tab([r for r in legal if r["author_model"] == m and r["completion_cell"] == c]) for c in CELLS} for m in ["Sol", "Gemini", "Opus", "Grok"]}
# 4. cell x seed block
out["cell_by_block"] = {str(b): {c: tab([r for r in legal if BLOCK(r["game"]) == b and r["completion_cell"] == c]) for c in CELLS} for b in range(1, 6)}
# 5. cell x game
out["cell_by_game"] = {str(g): {c: tab([r for r in legal if r["game"] == g and r["completion_cell"] == c]) for c in CELLS} for g in range(1, 21)}

# 6. direction-of-contrast checks: author_only vs recipient_only
def rate(t, k):
    return t[k] / t["n"] if t["n"] else None
def contrast(group):
    a, r = group["author_only"], group["recipient_only"]
    return {"author_only_n": a["n"], "recipient_only_n": r["n"],
            "accept_rate_author_only": rate(a, "accept"), "accept_rate_recipient_only": rate(r, "accept"),
            "reject_rate_author_only": rate(a, "reject"), "reject_rate_recipient_only": rate(r, "reject")}
out["contrast_by_recipient"] = {m: contrast(v) for m, v in out["cell_by_recipient"].items()}
out["contrast_by_block"] = {b: contrast(v) for b, v in out["cell_by_block"].items()}
gm = {}
for g, v in out["cell_by_game"].items():
    gm[g] = contrast(v)
out["contrast_by_game"] = gm
both_present = [g for g, v in gm.items() if v["author_only_n"] > 0 and v["recipient_only_n"] > 0]
out["games_with_both_cells"] = len(both_present)
out["games_reject_rate_higher_author_only"] = sum(1 for g in both_present if gm[g]["reject_rate_author_only"] > gm[g]["reject_rate_recipient_only"])
out["games_reject_rate_equal"] = sum(1 for g in both_present if gm[g]["reject_rate_author_only"] == gm[g]["reject_rate_recipient_only"])
out["games_accept_rate_lower_author_only"] = sum(1 for g in both_present if gm[g]["accept_rate_author_only"] < gm[g]["accept_rate_recipient_only"])
out["games_accept_rate_equal"] = sum(1 for g in both_present if gm[g]["accept_rate_author_only"] == gm[g]["accept_rate_recipient_only"])

# 7. cash direction: who pays when a completion is on offer
def pay(rr):
    net = [r["net_cash_author_to_recipient"] for r in rr]
    return {"n": len(net), "author_pays": sum(x > 0 for x in net), "no_net_cash": sum(x == 0 for x in net), "recipient_pays": sum(x < 0 for x in net), "median": med(net)}
out["cash_direction"] = {c: pay([r for r in legal if r["completion_cell"] == c]) for c in CELLS}
out["cash_direction_accepted"] = {c: pay([r for r in legal if r["completion_cell"] == c and r["response"] == "accept_trade"]) for c in CELLS}

# 8. first offers vs later exchanges
out["cells_first_offer"] = {c: tab([r for r in legal if r["completion_cell"] == c and r["exchange_index"] == 0]) for c in CELLS}
out["cells_later_offer"] = {c: tab([r for r in legal if r["completion_cell"] == c and r["exchange_index"] > 0]) for c in CELLS}

# 9. groups lost
out["recipient_completion_with_loss"] = tab([r for r in legal if r["recipient_new_groups"] and r["recipient_lost_groups"]])
out["recipient_completion_any"] = tab([r for r in legal if r["recipient_new_groups"]])
out["author_completion_any"] = tab([r for r in legal if r["author_new_groups"]])

# 10. threads
threads = collections.defaultdict(list)
for r in rows:
    threads[r["thread_id"]].append(r)
out["n_threads"] = len(threads)
settled = [t for t, rr in threads.items() if any(r["response"] == "accept_trade" for r in rr)]
out["n_settled_threads"] = len(settled)
out["threads_by_initiator_model"] = {}
for m in ["Sol", "Gemini", "Opus", "Grok"]:
    ts = [t for t, rr in threads.items() if min(rr, key=lambda r: r["exchange_index"])["author_model"] == m]
    out["threads_by_initiator_model"][m] = {"threads": len(ts), "settled": sum(1 for t in ts if t in settled)}
# response condition
out["response_condition"] = dict(C(r["response_condition"] for r in rows))
out["response_condition_by_recipient"] = {m: dict(C(r["response_condition"] for r in rows if r["recipient_model"] == m)) for m in ["Sol", "Gemini", "Opus", "Grok"]}
out["retry_used"] = sum(1 for r in rows if r["retry_used"]); out["fallback_used"] = sum(1 for r in rows if r["fallback_used"])
(HERE / "data").mkdir(exist_ok=True)
(HERE / "data" / "offer_retabulation.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ["cells_legal", "recipient_style_all", "contrast_by_recipient", "contrast_by_block", "games_with_both_cells", "games_reject_rate_higher_author_only", "games_reject_rate_equal", "games_accept_rate_lower_author_only", "games_accept_rate_equal", "cash_direction", "cash_direction_accepted", "cells_first_offer", "cells_later_offer", "recipient_completion_with_loss", "threads_by_initiator_model", "response_condition_by_recipient", "retry_used", "fallback_used", "excluded_rows"]}, indent=1))
