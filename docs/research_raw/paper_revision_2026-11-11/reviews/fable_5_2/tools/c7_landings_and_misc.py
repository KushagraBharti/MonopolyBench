"""Check 7. Small reconciliations across the frozen drafts.

(a) The 213 opponent landings on trade-completed groups are reported as 150 and
    63 under two different partitions (Sol and Fable: groups built in the first
    management turn against the rest; Opus: landings that found a building
    against landings that did not). Confirm both from the drafts' own rows.
(b) The concentration of the rejection-reason codes in G1 and G15 (34 of which
    population).
(c) The nine first-window groups with no legal build and mortgage status.
(d) Development timing definitions (first management turn, next owner turn,
    ever) by system.
Existing-record arithmetic only.
"""
import json, hashlib
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT.parent
OUT = HERE.parent / "data/c7_landings_and_misc.json"
sol = json.load(open(ROOT / "full_drafts/sol/data/development_exposure.json"))
opu = [e for e in json.load(open(ROOT / "full_drafts/opus/data/completion_episodes.json"))["episodes"] if e["route"] == "trade"]
fab = json.load(open(ROOT / "full_drafts/fable_5_2/data/a7_trade_groups.json"))
res = {}

# (a)
key = lambda g, p, c: (g, p, c)
S = {key(r["game"], r["player"], r["group"]): r for r in sol}
O = {key(r["game"], r["owner"], r["color"]): r for r in opu}
F = {key(r["game"], r["player"], r["group"]): r for r in fab}
assert set(S) == set(O) == set(F) and len(S) == 63
a = {
    "groups": 63,
    "landings_total": {"sol": sum(r["group_landings"] for r in sol), "opus": sum(r["opp_landings"] for r in opu), "fable": sum(r["landings"] for r in fab)},
    "per_group_landing_disagreements": sum(not (S[k]["group_landings"] == O[k]["opp_landings"] == F[k]["landings"]) for k in S),
    "per_group_rent_disagreements": sum(not (S[k]["rent"] == O[k]["rent"] == F[k]["rent"]) for k in S),
    "first_window_flag_disagreements_sol_fable": sum(S[k]["first_window"] != F[k]["inherited_built_first_window"] for k in S),
    "partition_first_window": {
        "groups": [sum(S[k]["first_window"] for k in S), sum(not S[k]["first_window"] for k in S)],
        "landings": [sum(S[k]["group_landings"] for k in S if S[k]["first_window"]), sum(S[k]["group_landings"] for k in S if not S[k]["first_window"])],
        "rent": [sum(S[k]["rent"] for k in S if S[k]["first_window"]), sum(S[k]["rent"] for k in S if not S[k]["first_window"])],
        "opponent_moves": [sum(S[k]["opponent_moves"] for k in S if S[k]["first_window"]), sum(S[k]["opponent_moves"] for k in S if not S[k]["first_window"])],
    },
    "partition_building_present_at_landing": {
        "landings": [sum(r["landings_developed"] for r in opu), sum(r["opp_landings"] - r["landings_developed"] for r in opu)],
        "rent": [sum(r["rent_developed"] for r in opu), sum(r["rent"] - r["rent_developed"] for r in opu)],
    },
    # cross table: landings on first-window groups that found no building, and the reverse
    "cross": {
        "first_window_groups_developed_landings": sum(O[k]["landings_developed"] for k in S if S[k]["first_window"]),
        "first_window_groups_undeveloped_landings": sum(O[k]["opp_landings"] - O[k]["landings_developed"] for k in S if S[k]["first_window"]),
        "other_groups_developed_landings": sum(O[k]["landings_developed"] for k in S if not S[k]["first_window"]),
        "other_groups_undeveloped_landings": sum(O[k]["opp_landings"] - O[k]["landings_developed"] for k in S if not S[k]["first_window"]),
    },
}
res["a_landings"] = a

# (d) development timing definitions by system
d = {}
for m in ("Sol", "Gemini", "Opus", "Grok"):
    ks = [k for k in S if S[k]["model"] == m]
    d[m] = {
        "groups": len(ks),
        "built_first_management_turn_inherited": sum(F[k]["inherited_built_first_window"] for k in ks),
        "built_by_owner_next_turn_opus": sum(O[k]["owner_turns_to_build"] is not None and O[k]["owner_turns_to_build"] <= 1 for k in ks),
        "ever_built": sum(O[k]["first_build_turn"] is not None for k in ks),
        "ever_built_fable": sum(F[k]["first_build_turn"] is not None for k in ks),
        "mortgaged_deed_at_completion": sum(F[k]["mortgaged_deeds_at_completion"] > 0 for k in ks),
        "landings": sum(F[k]["landings"] for k in ks),
        "undeveloped_landings": sum(O[k]["opp_landings"] - O[k]["landings_developed"] for k in ks),
        "rent": sum(F[k]["rent"] for k in ks),
    }
res["d_timing_by_system"] = d
res["d_totals"] = {k: sum(v[k] for v in d.values()) for k in next(iter(d.values()))}

# (c) first-window causes and mortgage status
causes = Counter(F[k]["inherited_first_window_cause"] for k in F)
noopt = [k for k in F if not F[k]["inherited_built_first_window"] and not F[k]["inherited_entry_legal"]]
res["c_first_window"] = {
    "causes": dict(causes),
    "no_legal_build_groups": len(noopt),
    "no_legal_build_with_mortgaged_deed_at_completion": sum(F[k]["mortgaged_deeds_at_completion"] > 0 for k in noopt),
    "never_built_groups": sum(F[k]["first_build_turn"] is None for k in F),
    "never_built_with_mortgaged_deed_at_completion": sum(F[k]["mortgaged_deeds_at_completion"] > 0 for k in F if F[k]["first_build_turn"] is None),
    "built_with_mortgaged_deed_at_completion": sum(F[k]["mortgaged_deeds_at_completion"] > 0 for k in F if F[k]["first_build_turn"] is not None),
    "no_legal_build_rows": [{"game": k[0], "model": F[k]["model"], "group": k[2], "mortgaged_deeds_at_completion": F[k]["mortgaged_deeds_at_completion"], "ever_built": F[k]["first_build_turn"] is not None} for k in sorted(noopt)],
}

# (b) reason codes
b = json.load(open(ROOT / "full_drafts/opus/data/bargaining.json"))["reason_codes"]
res["b_reason_codes_opus_join"] = {k: v for k, v in b.items() if not isinstance(v, list) or len(v) < 40}
OUT.write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print(k, json.dumps(v)[:2600])
