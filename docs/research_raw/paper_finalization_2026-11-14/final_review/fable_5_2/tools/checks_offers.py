"""Re-tabulate the stored 920-response ledger and the 61/74 coding join (read-only arithmetic).
The completion classification itself is inherited from the preserved ledger."""
import json, collections
from lib import *
C = collections.Counter
off = json.loads((INT / "data/offers.json").read_text())
res = {}
res["responses"] = dict(C(o["response"] for o in off)); res["threads"] = len({o["thread_id"] for o in off})
res["accept_available"] = sum(o["accept_available"] for o in off)
res["no_accept"] = [(o["game"], o["decision"], o["response"]) for o in off if not o["accept_available"]]
res["by_recipient"] = {m: dict(C(o["response"] for o in off if o["recipient_model"] == m)) for m in ("Sol", "Gemini", "Opus", "Grok")}
def form(o):
    a, b = o["offer"], o["request"]
    if a.get("get_out_of_jail_cards") or b.get("get_out_of_jail_cards"): return "other"
    ap, bp, ac, bc = bool(a["properties"]), bool(b["properties"]), a.get("cash", 0), b.get("cash", 0)
    if ap and bp: return "swap"
    if (not ap) and bp and ac > 0 and bc == 0: return "cash_bid"
    if ap and (not bp) and bc > 0 and ac == 0: return "cash_ask"
    return "other"
legal = [o for o in off if o["accept_available"]]
tab = C((("opening" if o["exchange_index"] == 0 else "later"), form(o), o["completion_cell"], o["response"]) for o in legal)
def cell(stage, f, comp, pop=legal):
    xs = [o for o in pop if ("opening" if o["exchange_index"] == 0 else "later") == stage and form(o) == f and o["completion_cell"] == comp]
    return len(xs), sum(o["response"] == "reject_trade" for o in xs), sum(o["response"] == "accept_trade" for o in xs), sum(o["response"] == "counter_trade" for o in xs)
res["completion_cells_seen"] = sorted({o["completion_cell"] for o in off})
for name, f in (("opening_swap", "swap"), ("opening_cash_bid", "cash_bid"), ("opening_cash_ask", "cash_ask")):
    res[name] = {c: cell("opening", f, c) for c in res["completion_cells_seen"]}
res["later_swap"] = {c: cell("later", "swap", c) for c in res["completion_cells_seen"]}
nog = [o for o in legal if o["author_model"] != "Grok"]
res["opening_swap_no_grok"] = {c: cell("opening", "swap", c, nog) for c in res["completion_cells_seen"]}
osw_n = [o for o in legal if o["exchange_index"] == 0 and form(o) == "swap" and o["completion_cell"] == "neither"]
res["neither_swap_authors"] = dict(C(o["author_model"] for o in osw_n))
res["neither_swap_accept_authors"] = dict(C(o["author_model"] for o in osw_n if o["response"] == "accept_trade"))
cb = [o for o in legal if o["exchange_index"] == 0 and form(o) == "cash_bid"]
res["cash_bid_authors"] = dict(C(o["author_model"] for o in cb)); res["cash_bids_n"] = len(cb)
# recipient-completing rejections and the coding join
rc = json.loads((INT / "data/reason_comparison.json").read_text())["categories"]["D"]
cod = json.loads((INT / "data/rejection_reason_coding.json").read_text())
rows = cod.get("rows_data") or cod["rows"]
key = lambda g, d: f"G{g:02d}d{d}"
cellof = {key(r["game"], r["decision"]): r["completion_cell"] for r in rows}
res["coding_population"] = dict(C(cellof.values()))
common = set(rc["common_positive_keys"])
res["common_positive_by_cell"] = dict(C(cellof[k] for k in common))
res["coding_counts"] = {k: rc[k] for k in ("reviewer_positive", "first_pass_positive", "common_positive", "either_positive", "both_negative", "disagreement_rows")}
ledger_rc_rej = [o for o in legal if o["response"] == "reject_trade" and o["completion_cell"] in ("recipient_only", "both", "recipient only")]
res["ledger_recipient_completing_rejections"] = dict(C(o["completion_cell"] for o in ledger_rc_rej))
res["coding_keys_match_ledger"] = set(cellof) == {key(o["game"], o["decision"]) for o in ledger_rc_rej}
# disjointness from proposer-only / neither comparison
res["coded_population_cells_disjoint_from_contrast"] = not (set(cellof.values()) & {"proposer_only", "neither", "author_only"})
(OUT / "offer_checks.json").write_text(json.dumps(res, indent=1, default=list) + "\n")
for k, v in res.items(): print(k, "=", json.dumps(v, default=list)[:700])
