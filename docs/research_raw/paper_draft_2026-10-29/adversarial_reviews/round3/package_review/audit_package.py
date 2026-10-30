"""Independent frozen-package checks. Writes only this review directory."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import pymupdf

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "baseline"
REPO = HERE.parents[4]
SUITE = HERE / "certificate_extracted/historical-claim-audit"
PDF = pymupdf.open(HERE / "build_copy/manuscript.pdf")
report = {"checks": {}, "rendered_table_rows": {}}


def read(path):
    return json.loads(path.read_text())


def data(name):
    return read(BASE / "data" / f"{name}.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_rows(page, low, high):
    words = [w for w in PDF[page - 1].get_text("words") if low < w[1] < high]
    lines = []
    while words:
        y = min(w[1] for w in words)
        line = sorted([w for w in words if abs(w[1] - y) < 2], key=lambda w: w[0])
        words = [w for w in words if abs(w[1] - y) >= 2]
        lines.append([w[4] for w in line])
    return lines


def table(number, actual, expected):
    assert actual == expected, (number, actual, expected)
    report["rendered_table_rows"][str(number)] = actual


# Table 1: derive decision/attempt counts from the original canonical histories.
decisions, attempts, defaults = Counter(), Counter(), []
source_hashes_checked = 0
model_names = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini",
               "anthropic/claude-opus-5.5": "Opus", "x-ai/grok-4.7": "Grok"}
for game in read(SUITE / "games.json"):
    folder = REPO / game["source_run"]
    for name, value in game["source_hashes"].items():
        assert sha(folder / name) == value, (folder, name)
        source_hashes_checked += 1
    for line in (folder / "decisions.jsonl").read_text().splitlines():
        row = json.loads(line)
        if row["phase"] != "decision_resolved":
            continue
        name = model_names[row["openrouter_model_id"]]
        decisions[name] += 1
        attempts[name] += len(row["attempts"])
        if row["fallback_used"]:
            defaults.append((game["game"], row["decision_id"]))
expected = [[name, model, f"{decisions[name]:,}", f"{attempts[name]:,}"]
            for model, name in model_names.items()]
table(1, [r[:4] for r in pdf_rows(3, 97, 165) if r[0] in model_names.values()], expected)
assert sum(decisions.values()) == 6989 and sum(attempts.values()) == 8679
report["checks"]["original_histories"] = {"source_hashes_checked": source_hashes_checked,
    "decisions": dict(decisions), "attempts": dict(attempts), "defaults": len(defaults)}

# Table 3: calculate displayed proportions from the retained integer denominators.
table(3, pdf_rows(9, 404, 443), [[r["configuration"], str(r["proposals"]),
    f'{r["proposing_turns"]}/{r["eligible_turns"]}',
    f'{100 * r["proposing_turns"] / r["eligible_turns"]:.1f}%',
    f'{r["proposals"] / r["proposing_turns"]:.2f}', f'{r["eligible_decisions"]:,}']
    for r in data("t02_negotiation")])

# Table 4: recompute END partitions from the record-level ledger, not its counts.
conditions = data("resolution_conditions")
end_records = conditions["end_records"]
assert len(end_records) == 663
assert len({(r["game"], r["decision_id"]) for r in end_records}) == 663
rows = []
for name in model_names.values():
    part = [r for r in end_records if r["model"] == name]
    c = Counter(r["category"] for r in part)
    c2 = conditions["counts"][name]
    assert len(part) == c2["applied_end"]
    assert all(c[key] == c2.get(key, 0) for key in c)
    rows.append([name, str(c2["construction_tool_listed"]), str(len(part)),
                 str(c["engine_default"]), str(c["received_name_conflict"]),
                 str(c["no_detected_name_conflict"])])
table(4, pdf_rows(11, 87, 125), rows)
assert sum(c["construction_tool_listed"] for c in conditions["counts"].values()) == 1225
assert Counter(r["category"] for r in end_records) == {
    "engine_default": 66, "received_name_conflict": 24, "no_detected_name_conflict": 573}
assert sum(r["model"] == "Opus" and r["category"] != "engine_default"
           and r["response_condition"] == "same_model_without_private_thought"
           for r in end_records) == 42
assert {(r["game"], r["decision_id"]) for r in end_records if r["category"] == "engine_default"} == set(defaults)
report["checks"]["END_partition"] = {"records": 663, "default": 66, "conflict": 24, "remainder": 573}

# Table 5: all native cells vs retained recovery records.
keys = ["uneven_rejection_decisions", "some_legal_build_same_decision", "same_purchase_multiset",
        "changed_purchase_multiset", "ended_in_default"]
table(5, pdf_rows(11, 271, 310), [[r["configuration"], *[str(r[k]) for k in keys]]
                               for r in data("t07_build_recovery")])

# Table 6: amounts against freshly executed witness output, including cash left.
fresh = read(HERE / "reproduced_certificates.json")
assert fresh == read(SUITE / "results.json") == data("certificate_results")
elims = [r for r in fresh["results"] if r["kind"] == "elimination"]
special = [(12, 190), (12, 249), (17, 234), (7, 339)]
actual = pdf_rows(13, 87, 125)
for line, (game, decision) in zip(actual, special):
    r = next(r for r in elims if r["game"] == game and r["decision_id"].endswith(f"{decision:06}"))
    assert line[:5] == [f"G{game}", f"d{decision}", model_names[r["model"]],
                        f'${r["debt"]:,}', f'${r["bound"]["full_upper"]:,}']
    if "witness" in r:
        assert f'${r["witness"]["cash_after"]}' in line
    else:
        assert r["search"]["state_count"] == 1 and r["search"]["exhausted"]
        assert r["bound"]["cash"] + 50 == 440
report["rendered_table_rows"]["6"] = actual

# Table 8: every cohort row, including seeds, turns, seats and rotations.
table(8, pdf_rows(27, 247, 506), [[str(r[k]) for k in
      ["game", "seed", "rotation", "turns", "winner", "winner_seat"]] for r in data("t01_cohort")])

# Table 12 and the 80-cell ledger: independent reaggregation with zero cells.
windows = data("first_management_windows")["rows"]
ledger, expected = [], []
for game in range(1, 21):
    group = [r for r in windows if r["game"] == game]
    cases = [r for r in fresh["results"] if r["game"] == game]
    certs = Counter(r["certificate"] for r in cases if r["kind"] == "elimination")
    assert sum(certs.values()) == 3
    built, entry, entry_built = (sum(r[key] for r in group) for key in
                                ["built_first_mgmt_turn", "entry_legal", "entry_legal"])
    entry_built = sum(r["entry_legal"] and r["built_first_mgmt_turn"] for r in group)
    expected.append([str(game), str((game - 1) // 4 + 1), f"{built}/{len(group)}",
        f"{entry_built}/{entry}", str(sum(r["kind"] == "default" for r in cases)),
        str(certs["upper_bound_impossibility"]), str(certs["legal_payment_witness"]),
        str(certs["exhaustive_financing_impossibility"])])
    for name in model_names.values():
        sub = [r for r in group if r["model"] == name]
        ledger.append({"game": game, "seed_block": (game-1)//4+1, "model": name,
            "groups": len(sub), "built_in_window": sum(r["built_first_mgmt_turn"] for r in sub),
            "entry_eligible": sum(r["entry_legal"] for r in sub),
            "entry_built": sum(r["entry_legal"] and r["built_first_mgmt_turn"] for r in sub),
            "resolution": dict(Counter(r["cause"] for r in sub))})
table(12, pdf_rows(32, 97, 327), expected)
assert ledger == data("opportunity_ledger")["rows"]
for name, value in data("opportunity_ledger")["source_sha256"].items():
    assert sha(BASE / "data" / name) == value
report["checks"]["opportunity_ledger"] = {"cells": len(ledger),
    "zero_group_cells": sum(r["groups"] == 0 for r in ledger),
    "zero_entry_cells": sum(r["entry_eligible"] == 0 for r in ledger)}

# All figure inputs and every published image are tied to the stored manifest.
manifest = read(BASE / "figure_manifest.json")
for group in ["inputs", "outputs"]:
    for name, value in manifest[group].items():
        assert sha(BASE / name) == value
report["checks"]["figure_manifest"] = {k:len(v) for k,v in manifest.items()}

# Standalone artifact completeness, including source provenance and license.
manifest = read(SUITE / "artifact_manifest.json")
for name, value in manifest.items():
    assert sha(SUITE / name) == value, name
inputs = read(SUITE / "inputs_manifest.json")
for name, item in inputs["copied_engine_sources"].items():
    assert sha(SUITE / name) == sha(REPO / item["source"]) == item["sha256"]
assert sha(SUITE / "LICENSE") == sha(REPO / "LICENSE")
report["checks"]["certificate_package"] = {"manifest_hashes": len(manifest),
    "input_hashes": len(inputs["files"]), "source_copies": len(inputs["copied_engine_sources"]),
    "results_exact_match": True, "license_matches": True}

report["status"] = "pass"
(HERE / "independent_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"status": "pass", "tables": list(report["rendered_table_rows"]),
                  "checks": report["checks"]}, indent=2))
