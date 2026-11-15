"""Check 6. The three "distress sale" populations (Opus 14 of 22, Fable 20 of 43,
Sol 21 of 48) rebuilt from one ledger so their definitions can be compared.

Existing-record arithmetic on the frozen Fable offer ledger (920 rows, equal to
the Opus rebuild on every field this check uses, see c1).
"""
import json, hashlib, statistics as st
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
OUT = HERE.parent / "data/c6_distress_populations.json"
acc = [r for r in json.load(open(LED)) if r["response"] == "accept_trade"]
assert len(acc) == 113


def sides(r):
    """Return (seller, buyer) views for the party that receives net cash."""
    net = r["net_cash_author_to_recipient"]  # positive: author pays recipient
    if net > 0:
        return {"receiver": "recipient", "payer": "author", "net": net,
                "receiver_cash": r["recipient_cash_before"], "receiver_model": r["recipient_model"],
                "payer_new": r["author_new_groups"], "receiver_new": r["recipient_new_groups"],
                "receiver_gives": r["recipient_gives"], "payer_gives": r["author_gives"]}
    if net < 0:
        return {"receiver": "author", "payer": "recipient", "net": -net,
                "receiver_cash": r["author_cash_before"], "receiver_model": r["author_model"],
                "payer_new": r["recipient_new_groups"], "receiver_new": r["author_new_groups"],
                "receiver_gives": r["author_gives"], "payer_gives": r["recipient_gives"]}
    return None


def pure_cash_for_deed(v):
    return (v["receiver_gives"]["properties"] and not v["payer_gives"]["properties"]
            and v["receiver_gives"]["cash"] == 0
            and not v["receiver_gives"]["get_out_of_jail_cards"] and not v["payer_gives"]["get_out_of_jail_cards"])


def cell(vs, label):
    lo = [v for v in vs if v["receiver_cash"] < 100]
    return {"definition": label, "n": len(vs), "receiver_under_100": len(lo),
            "median_receiver_cash": st.median(v["receiver_cash"] for v in vs) if vs else None,
            "by_receiver_model": dict(Counter(v["receiver_model"] for v in vs)),
            "under_100_by_receiver_model": dict(Counter(v["receiver_model"] for v in lo)),
            "n_without_opus_receiver": sum(v["receiver_model"] != "Opus" for v in vs),
            "under_100_without_opus_receiver": sum(v["receiver_model"] != "Opus" for v in lo)}


views = [(r, sides(r)) for r in acc]
cashv = [v for r, v in views if v]
res = {"input": {str(LED.relative_to(ROOT)): hashlib.sha256(LED.read_bytes()).hexdigest()},
       "accepted_offers": len(acc), "accepted_with_net_cash": len(cashv),
       "accepted_by_cell": dict(Counter(r["completion_cell"] for r in acc))}

# Opus: settled pure cash-for-deed sales, deed completes the buyer's group or completes nothing
pure = [v for v in cashv if pure_cash_for_deed(v)]
res["opus_definition_pure_cash_completing_buyer"] = cell([v for v in pure if v["payer_new"] and not v["receiver_new"]],
    "accepted, cash one way and deeds the other way only, completes the paying side")
res["opus_definition_pure_cash_completing_nobody"] = cell([v for v in pure if not v["payer_new"] and not v["receiver_new"]],
    "accepted, cash one way and deeds the other way only, completes nobody")
# Sol: cash settlements completing the paying side's group (any bundle with net cash), and all cash-receiving settlements
res["sol_definition_net_cash_completing_payer"] = cell([v for v in cashv if v["payer_new"]],
    "accepted, net cash flows to one side, completes the paying side (the receiver may also complete)")
res["sol_definition_all_net_cash_settlements"] = cell(cashv, "accepted, any net cash")
# Fable: one-sided completing sales, any bundle; holder is the party that does not complete
one = []
for r in acc:
    if r["completion_cell"] in ("author_only", "recipient_only"):
        holder_is_author = r["completion_cell"] == "recipient_only"
        one.append({"receiver_cash": r["author_cash_before"] if holder_is_author else r["recipient_cash_before"],
                    "receiver_model": r["author_model"] if holder_is_author else r["recipient_model"],
                    "net_to_holder": (-1 if holder_is_author else 1) * r["net_cash_author_to_recipient"]})
res["fable_definition_one_sided_completion"] = cell(one, "accepted, completes exactly one party; cash is the non-completing party's")
res["fable_one_sided_net_cash_sign"] = dict(Counter("holder_receives_cash" if v["net_to_holder"] > 0 else "holder_pays_cash" if v["net_to_holder"] < 0 else "no_net_cash" for v in one))
both = [r for r in acc if r["completion_cell"] == "both"]
res["mutual_completion_settlements"] = {"n": len(both),
    "either_party_under_100": sum(min(r["author_cash_before"], r["recipient_cash_before"]) < 100 for r in both)}
# comparison: accepted offers completing nobody, cash of the net cash receiver
res["neither_net_cash_settlements"] = cell([v for r, v in views if v and r["completion_cell"] == "neither"],
    "accepted, completes nobody, any net cash")
OUT.write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print(k, json.dumps(v))
