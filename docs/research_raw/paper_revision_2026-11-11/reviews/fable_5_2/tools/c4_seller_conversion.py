"""Check 4. Seller conversion (9 of 14 against 1 of 29) by whether the seller
held a complete color group when it sold.

Existing-record arithmetic on the frozen Fable outputs. A seller can build only
on a complete group of its own. If nearly every seller who held a group built
and won, and nearly every seller who held none did neither, the published split
restates group ownership. This joins each of the 43 one-sided sales to the
seller's open group episodes at the sale turn.
"""
import json
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DY = ROOT / "full_drafts/fable_5_2/data/a6_dyads.json"
EP = ROOT / "full_drafts/fable_5_2/data/a3_group_episodes.json"
CV = ROOT / "full_drafts/fable_5_2/data/a7_conversion.json"
OUT = HERE.parent / "data/c4_seller_conversion.json"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

dy = [d for d in json.load(open(DY)) if d["settled"] and d.get("one_sided")]
eps = json.load(open(EP))
rows = json.load(open(CV))["seller_conversion"]["rows"]
assert len(dy) == 43 and len(rows) == 43

by_key = {(r["game"], r["group"], r["turn"]): r for r in rows}

out = []
for d in dy:
    r = by_key[(d["game"], d["group"], d["settle_turn"])]
    held = [e for e in eps if e["game"] == d["game"] and e["player"] == d["holder"]
            and e["start_turn"] <= d["settle_turn"] and e["end_turn"] >= d["settle_turn"]]
    # a group whose episode starts in the same turn at or after this sale does not count as held before it
    held_before = [e for e in held if e["start_turn"] < d["settle_turn"]]
    built = r["houses_built_within"]["8"] > 0
    out.append({
        "game": d["game"], "group_sold_completes": d["group"], "seller": d["holder_model"], "seller_player": d["holder"],
        "turn": d["settle_turn"], "seller_cash": d["settle_holder_cash"],
        "seller_held_complete_group_before_sale": bool(held_before),
        "seller_holds_complete_group_in_sale_turn": bool(held),
        "groups_held": sorted({e["group"] for e in held}),
        "seller_building_levels_at_sale": r["seller_building_levels_at_sale"],
        "built_within_8": built, "seller_won": r["seller_won"],
    })


def cell(rs):
    pg = {(r["game"], r["seller_player"]) for r in rs}
    pgw = {(r["game"], r["seller_player"]) for r in rs if r["seller_won"]}
    return {"sales": len(rs), "seller_won_sales": sum(r["seller_won"] for r in rs),
            "player_games": len(pg), "winning_player_games": len(pgw)}


def table(key):
    t = {}
    for h in (True, False):
        for b in (True, False):
            rs = [r for r in out if r[key] == h and r["built_within_8"] == b]
            t[f'{"held_group" if h else "no_group"}|{"built" if b else "not_built"}'] = cell(rs)
    t["held_group|all"] = cell([r for r in out if r[key]])
    t["no_group|all"] = cell([r for r in out if not r[key]])
    return t


res = {
    "inputs": {str(p.relative_to(ROOT)): sha(p) for p in (DY, EP, CV)},
    "published_split": {"built": cell([r for r in out if r["built_within_8"]]),
                        "not_built": cell([r for r in out if not r["built_within_8"]])},
    "by_group_held_in_sale_turn": table("seller_holds_complete_group_in_sale_turn"),
    "by_group_held_before_sale": table("seller_held_complete_group_before_sale"),
    "by_buildings_standing_at_sale": {
        "has_buildings|all": cell([r for r in out if r["seller_building_levels_at_sale"] > 0]),
        "no_buildings|all": cell([r for r in out if r["seller_building_levels_at_sale"] == 0]),
        "has_buildings|built": cell([r for r in out if r["seller_building_levels_at_sale"] > 0 and r["built_within_8"]]),
        "has_buildings|not_built": cell([r for r in out if r["seller_building_levels_at_sale"] > 0 and not r["built_within_8"]]),
        "no_buildings|built": cell([r for r in out if r["seller_building_levels_at_sale"] == 0 and r["built_within_8"]]),
        "no_buildings|not_built": cell([r for r in out if r["seller_building_levels_at_sale"] == 0 and not r["built_within_8"]]),
    },
    "by_seller_model": {m: {"built": cell([r for r in out if r["seller"] == m and r["built_within_8"]]),
                            "not_built": cell([r for r in out if r["seller"] == m and not r["built_within_8"]])}
                        for m in ("Sol", "Gemini", "Opus", "Grok")},
    "winner_games_with_built_sale": sorted({r["game"] for r in out if r["built_within_8"] and r["seller_won"]}),
    "rows": out,
}
# buyers: did the buyer of a one-sided completing sale win?
res["buyer_won"] = {"sales": len(rows), "buyer_won": sum(r["buyer_won"] for r in rows),
                    "seller_won": sum(r["seller_won"] for r in rows)}
OUT.write_text(json.dumps(res, indent=1))
for k in ("published_split", "by_group_held_in_sale_turn", "by_group_held_before_sale", "by_buildings_standing_at_sale", "by_seller_model", "buyer_won", "winner_games_with_built_sale"):
    print(k, json.dumps(res[k], indent=0).replace("\n", " "))
