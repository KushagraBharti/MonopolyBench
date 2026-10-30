"""Read-only analysis for the Fable novelty review (2026-10-29).

Inputs: frozen draft exports only (data/t03_trade_groups.json, data/t09_entry_nonbuild_records.json,
data/t06_eliminations.json, data/t01_cohort.json) and contracts/data/board.json.
Outputs: analysis/results.json. No canonical file is modified.

1. Decompose the per-configuration first-window outcome that Figure 2 shows but the prose never states.
2. Recheck the appendix rounding claim for all sixteen board principals.
3. Tabulate eliminations by configuration and classification, and winners by seed block.
"""
from __future__ import annotations
import json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[5]
DRAFT = ROOT / "docs/research_raw/paper_adversarial_2026-10-29/baseline/monopolybench-first-draft"
OUT = Path(__file__).resolve().parent / "results.json"

res: dict = {}

# 1. First-window decomposition
rows = json.load(open(DRAFT / "data/t03_trade_groups.json"))
dec = {}
for r in rows:
    g, e, b = r["trade_groups"], r["eligible_during_window"], r["first_management_built"]
    ne, nb = r["entry_eligible"], r["entry_eligible_built"]
    dec[r["configuration"]] = {
        "trade_completed_groups": g,
        "built_in_first_window": b,
        "never_buildable_in_window": g - e,
        "buildable_in_window_not_built": e - b,
        "entry_buildable": ne,
        "entry_buildable_built": nb,
        "entry_buildable_not_built": ne - nb,
        "became_buildable_later_not_built": (e - b) - (ne - nb),
    }
tot = {k: sum(v[k] for v in dec.values()) for k in next(iter(dec.values()))}
assert tot["trade_completed_groups"] == 63 and tot["built_in_first_window"] == 43
assert tot["entry_buildable"] == 42 and tot["entry_buildable_built"] == 34
res["first_window_by_configuration"] = dec
res["first_window_totals"] = tot

nonbuild = json.load(open(DRAFT / "data/t09_entry_nonbuild_records.json"))
res["entry_nonbuild_categories_by_configuration"] = {
    m: dict(Counter(r["category"] for r in nonbuild if r["model"] == m)) for m in dec
}
assert len(nonbuild) == 8

# 2. Rounding recheck
board = json.load(open(ROOT / "contracts/data/board.json"))
if isinstance(board, dict):
    board = board.get("spaces") or board.get("board") or next(v for v in board.values() if isinstance(v, list))
principals = sorted({s["price"] // 2 for s in board if s.get("price")})
rounding = []
for m in principals:
    interest, exact_i = int(math.ceil(m * 0.1)), -(-m // 10)
    redeem, exact_r = int(math.ceil(m * 1.1)), -(-(m * 11) // 10)
    rounding.append({"principal": m, "trade_interest": interest, "trade_interest_exact": exact_i,
                     "redemption": redeem, "redemption_exact": exact_r,
                     "redemption_overcharge": redeem - exact_r})
res["rounding_check"] = {
    "principals": principals,
    "trade_interest_mismatches": [r["principal"] for r in rounding if r["trade_interest"] != r["trade_interest_exact"]],
    "redemption_overcharged_principals": [r["principal"] for r in rounding if r["redemption_overcharge"]],
    "rows": rounding,
}

# 3. Eliminations and winners
elims = json.load(open(DRAFT / "data/t06_eliminations.json"))
by_model = defaultdict(Counter)
for e in elims:
    cls = "payable" if e.get("avoidable") else ("hotel_lock" if e.get("full", 0) >= e["owed"] else "insolvent_under_bound")
    by_model[e["model"]][cls] += 1
    by_model[e["model"]]["total"] += 1
res["eliminations_by_configuration"] = {m: dict(c) for m, c in by_model.items()}
assert sum(c["total"] for c in by_model.values()) == 60

cohort = json.load(open(DRAFT / "data/t01_cohort.json"))
rows_c = cohort if isinstance(cohort, list) else cohort.get("rows") or cohort.get("games")
by_seed = defaultdict(list)
for r in rows_c:
    by_seed[str(r.get("seed"))].append(r.get("winner"))
res["winners_by_seed_block"] = dict(by_seed)
res["seed_blocks_with_single_winner"] = [s for s, w in by_seed.items() if len(set(w)) == 1]

json.dump(res, open(OUT, "w"), indent=2)
print(json.dumps(res, indent=2))
