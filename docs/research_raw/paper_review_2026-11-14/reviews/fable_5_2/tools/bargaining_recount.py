"""Recount the opening-offer contrasts from raw decisions. Reuses the offer classifier written for the 12 November final review (read-only import)."""
import sys, json, collections
from pathlib import Path
OLD = Path(__file__).resolve().parents[4] / "paper_revision_2026-11-12/final_review/fable_5_2/tools"
sys.path.insert(0, str(OLD))
import rebuild  # noqa: E402  (imports lib from the old folder; both are read-only helpers)
offs = rebuild.offers()
C = collections.Counter
print("responses", len(offs), C(o["response"] for o in offs), "accept legal", sum(o["accept_available"] for o in offs))
op = [o for o in offs if o["exchange_index"] == 0 and o["accept_available"]]
def cell(rows, form, comp):
    r = [o for o in rows if o["form"] == form and o["completion_cell"] == comp]
    return sum(o["response"] == "reject_trade" for o in r), len(r)
def gap(rows, form):
    a, b = cell(rows, form, "author_only"); c, d = cell(rows, form, "neither")
    return f"{a}/{b} vs {c}/{d} = {100*(a/b-c/d):.2f} pp"
print("all swaps", gap(op, "Swap"))
print("no Grok authors", gap([o for o in op if o["author_model"] != "Grok"], "Swap"))
print("no conflicting openings", gap([o for o in op if not o["opening_call_conflicts"]], "Swap"))
print("cash bids", gap(op, "Cash bid"))
for m in ("Sol", "Gemini", "Opus", "Grok"):
    rows = [o for o in op if o["recipient_model"] == m]
    print("  recipient", m, "swaps", gap(rows, "Swap"), "| cash bids", gap(rows, "Cash bid"))
neither = [o for o in op if o["form"] == "Swap" and o["completion_cell"] == "neither"]
acc = [o for o in neither if o["response"] == "accept_trade"]
print("neither-completing opening swaps", len(neither), "by Grok", sum(o["author_model"] == "Grok" for o in neither), "accepted", len(acc), "accepted Grok-authored", sum(o["author_model"] == "Grok" for o in acc), "of which opened by a conflicting call", sum(1 for o in acc if o["author_model"] == "Grok" and o["opening_call_conflicts"]))
