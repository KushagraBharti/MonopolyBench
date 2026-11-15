"""Read entry holdings and check premises of a written argument. No transitions or policy runs."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "contracts").is_dir())
entry_file = HERE / "record_checks.json"
board_file = ROOT / "contracts/data/board.json"
entries = json.loads(entry_file.read_text())["rows"]
board = json.loads(board_file.read_text())
spaces = {
    re.sub("[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s
    for s in board["spaces"]
}
groups = defaultdict(set)
for key, s in spaces.items():
    if s["kind"] == "PROPERTY":
        groups[s["group"]].add(key)

payable_declarations = {(12, 190), (12, 249), (17, 234)}
rows = []
for r in entries:
    if r["outcome"] != "paid" and (r["game"], r["decision"]) not in payable_declarations:
        continue
    owned = {h["space_key"]: h for h in r["holdings"]}
    developed = sorted({
        spaces[k]["group"] for k, h in owned.items() if h["houses"] or h["hotel"]
    })
    complete = all(groups[g] <= owned.keys() for g in developed)
    even = all(
        max(5 if owned[k]["hotel"] else owned[k]["houses"] for k in groups[g])
        - min(5 if owned[k]["hotel"] else owned[k]["houses"] for k in groups[g]) <= 1
        for g in developed
    ) if complete else False
    hotels_by_group = {
        g: sum(owned[k]["hotel"] for k in groups[g]) for g in developed
    } if complete else {}
    hotels = sum(hotels_by_group.values())
    free_houses = sum(
        owned[k]["houses"] for g in developed if hotels_by_group[g] == 0 for k in groups[g]
    ) if complete else 0
    bank = r["bank"]["houses_remaining"]
    sufficient = r["Ustar"] >= r["debt"]
    if hotels == 0:
        support = "hotel_free"
    elif r["cash"] + r["M0"] >= r["debt"]:
        support = "initial_mortgages_suffice"
    elif bank >= 4 * hotels:
        support = "all_downgrades_stocked"
    elif all(n <= 1 for n in hotels_by_group.values()) and bank + free_houses >= 4:
        support = "single_hotel_per_group_with_recyclable_stock"
    else:
        support = "not_covered"
    rows.append({
        "game": r["game"], "decision": r["decision"], "debt": r["debt"],
        "cash": r["cash"], "Ustar": r["Ustar"], "complete": complete,
        "even": even, "bound_sufficient": sufficient, "hotels": hotels,
        "bank_houses": bank, "houses_in_hotel_free_groups": free_houses,
        "hotels_by_group": hotels_by_group, "support": support,
    })
assert len(rows) == 131
assert all(r["complete"] and r["even"] and r["bound_sufficient"] for r in rows)
assert all(r["support"] != "not_covered" for r in rows)
result = {
    "method": "Arithmetic on recorded entry holdings; premises of a source-based proof, not a policy evaluation",
    "counts": dict(Counter(r["support"] for r in rows)),
    "input_sha256": {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [entry_file, board_file]
    },
    "rows": rows,
}
(HERE / "continuation_premises.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result["counts"]))
print(json.dumps([r for r in rows if r["support"].startswith("single_hotel")], indent=2))
