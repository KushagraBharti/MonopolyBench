"""Check 3b. Where the opening rejection gap sits, by offer type.

Existing-record arithmetic on the frozen offer ledger. Splits acceptance-legal
offers that ask the recipient for a deed into
  cash bid   : the author gives cash only and receives deeds only
  with deeds : the author gives at least one deed (swap or swap plus cash)
  other      : anything else that asks for a deed (jail cards, cash both ways)
and compares author-completing with neither-completing offers inside each type.
"""
import json, hashlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
OUT = HERE.parent / "data/c3b_offer_type.json"
led = [r for r in json.load(open(LED)) if r["accept_available"]]


def otype(r):
    ag, rg = r["author_gives"], r["recipient_gives"]
    if not rg["properties"]:
        return "no_deed_asked"
    if ag["properties"]:
        return "with_deeds"
    if ag["cash"] > 0 and rg["cash"] == 0 and not ag["get_out_of_jail_cards"] and not rg["get_out_of_jail_cards"]:
        return "cash_bid"
    return "other_deed_request"


def tab(rows):
    n = len(rows)
    a = sum(r["response"] == "accept_trade" for r in rows)
    c = sum(r["response"] == "counter_trade" for r in rows)
    j = sum(r["response"] == "reject_trade" for r in rows)
    return {"n": n, "A": a, "C": c, "R": j, "reject_pct": round(100 * j / n, 1) if n else None,
            "accept_pct": round(100 * a / n, 1) if n else None}


res = {"input": {str(LED.relative_to(ROOT)): hashlib.sha256(LED.read_bytes()).hexdigest()}}
for scope, rows in (("opening", [r for r in led if r["opening"]]), ("later", [r for r in led if not r["opening"]]), ("all", led)):
    s = {}
    for t in ("cash_bid", "with_deeds", "other_deed_request", "no_deed_asked"):
        sub = [r for r in rows if otype(r) == t]
        ao = [r for r in sub if r["completion_cell"] == "author_only"]
        ne = [r for r in sub if r["completion_cell"] == "neither"]
        e = {"author_only": tab(ao), "neither": tab(ne)}
        e["gap"] = round(e["author_only"]["reject_pct"] - e["neither"]["reject_pct"], 1) if ao and ne else None
        e["by_recipient"] = {m: {"author_only": tab([r for r in ao if r["recipient_model"] == m]),
                                 "neither": tab([r for r in ne if r["recipient_model"] == m])} for m in ("Sol", "Gemini", "Opus", "Grok")}
        e["by_block"] = {b: {"author_only": tab([r for r in ao if r["block"] == b]),
                             "neither": tab([r for r in ne if r["block"] == b])} for b in range(1, 6)}
        e["no_opus_either"] = {"author_only": tab([r for r in ao if "Opus" not in (r["recipient_model"], r["author_model"])]),
                               "neither": tab([r for r in ne if "Opus" not in (r["recipient_model"], r["author_model"])])}
        e["by_author"] = {m: {"author_only": tab([r for r in ao if r["author_model"] == m]),
                              "neither": tab([r for r in ne if r["author_model"] == m])} for m in ("Sol", "Gemini", "Opus", "Grok")}
        s[t] = e
    res[scope] = s
OUT.write_text(json.dumps(res, indent=1))
f = lambda t: f'{t["R"]}/{t["n"]} rej {t["reject_pct"]}% acc {t["A"]}' if t["n"] else "-"
for scope in ("opening", "later", "all"):
    print("==", scope)
    for t, e in res[scope].items():
        print(f'  {t:20s} author_only {f(e["author_only"]):28s} neither {f(e["neither"]):28s} gap {e["gap"]}')
        if scope == "opening" and t in ("cash_bid", "with_deeds"):
            for m, v in e["by_recipient"].items():
                print(f'      recipient {m:7s} {f(v["author_only"]):28s} {f(v["neither"])}')
            for b, v in e["by_block"].items():
                print(f'      block {b}        {f(v["author_only"]):28s} {f(v["neither"])}')
            v = e["no_opus_either"]; print(f'      no Opus either   {f(v["author_only"]):28s} {f(v["neither"])}')
            for m, v in e["by_author"].items():
                print(f'      author {m:7s}    {f(v["author_only"]):28s} {f(v["neither"])}')
