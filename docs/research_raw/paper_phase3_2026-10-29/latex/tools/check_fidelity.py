"""Final replay of Sol's independent ordered-cell checker; tok formatting added by Astra."""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
BASE = HERE.parent
parser = argparse.ArgumentParser()
parser.add_argument("--tag", default="first")
args = parser.parse_args()
PACKAGE = HERE


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clean(value):
    value = re.sub(r"\\(?:path|nolinkurl|texttt|tok)\{([^{}]*)\}", r"\1", value)
    value = value.replace(r"\_", "_").replace(r"\%", "%").replace(r"\$", "$")
    return value.strip()


groups = dict(
    zip(
        [
            "BROWN",
            "LIGHT_BLUE",
            "PINK",
            "ORANGE",
            "RED",
            "YELLOW",
            "GREEN",
            "DARK_BLUE",
        ],
        ["BR", "LB", "PK", "OR", "RD", "YL", "GR", "DB"],
    )
)
cats = {
    "engine_default": "Engine default",
    "received_content_tool_conflict": "Received conflict",
    "consistent_end_with_stated_reserve": "Stated hold",
}


def expected_row(i, r):
    if i == 1:
        return [
            r[k] for k in ("game", "seed", "rotation", "winner", "winner_seat", "turns")
        ] + [r["treatment_fingerprint"][:8]]
    if i == 2:
        return [
            r["configuration"],
            r["proposals"],
            f"{r['proposing_turns']}/{r['eligible_turns']}",
            f"{100 * float(r['own_turn_propensity']):.2f}",
            f"{r['proposals']}/{r['proposing_turns']} = {float(r['proposals_per_proposing_turn']):.2f}",
            r["eligible_decisions"],
            f"{100 * float(r['eligible_decision_rate']):.2f}",
            f"{float(r['eligible_decisions_per_turn']):.2f}",
            r["zero_proposal_games"],
        ]
    if i == 3:
        return [
            r[k]
            for k in (
                "configuration",
                "trade_groups",
                "first_management_built",
                "entry_eligible",
                "entry_eligible_built",
                "eligible_during_window",
                "without_access",
            )
        ]
    if i == 4:
        return [
            {"0": "Neither side", "1": "One side", "2": "Both sides"}[
                r["newly_completed_sides"]
            ],
            r["trades"],
        ]
    if i == 5:
        return (
            [
                r["game"],
                r["player"] + " " + r["configuration"],
                groups[r["group"]],
                "Y" if r["winner"] == "True" else "N",
            ]
            + [
                r[k]
                for k in (
                    "spend",
                    "sale_proceeds",
                    "paid_developed_rent_after_first_own_spend",
                    "paid_developed_rent_whole_game",
                )
            ]
            + [
                "Y" if r["inherited_deed_at_first_own_spend"] == "True" else "N",
                r["creditor_eliminations_on_group"],
                r["first_own_spend_event"],
            ]
        )
    if i == 6:
        return (
            [
                r["game"],
                "d" + str(int(r["decision"].split("-")[-1])),
                r["player"] + " " + r["model"],
                "Auto" if r["elimination"] == "automatic" else "Decl.",
            ]
            + [
                r[k]
                for k in (
                    "owed",
                    "cash",
                    "menu_mortgage_only",
                    "accessible",
                    "full",
                    "bank_houses",
                )
            ]
            + ["Yes" if r["avoidable"] == "True" else "No"]
        )
    if i == 7:
        return [
            r[k]
            for k in (
                "configuration",
                "uneven_rejection_decisions",
                "some_legal_build_same_decision",
                "same_purchase_multiset",
                "changed_purchase_multiset",
                "ended_in_default",
            )
        ]
    if i == 8:
        return [
            r[k]
            for k in (
                "game",
                "event_seq",
                "turn",
                "player",
                "configuration",
                "cash",
                "reason",
            )
        ]
    if i == 9:
        return [
            r["game"],
            r["model"],
            groups[r["group"]],
            "d" + str(int(r["decision_id"].split("-")[-1])),
            r["turn"],
            cats[r["category"]],
            r["selected_content_name"] or "Absent",
            r["selected_attempt_index"]
            if r["selected_attempt_index"] != ""
            else "Absent",
            r["line"],
        ]
    raise ValueError(i)


tables = []
for i, p in enumerate(sorted((BASE / "astra/exhibits").glob("t*.csv")), 1):
    with p.open(newline="") as f:
        rows = list(csv.DictReader(f))
    tex = (PACKAGE / "tables" / p.with_suffix(".tex").name).read_text()
    body = tex.split(r"\endlastfoot", 1)[1].split(r"\end{longtable}", 1)[0].strip()
    actual = [
        [clean(c) for c in line.split(" & ")]
        for line in re.split(r"\\\\\s*\n?", body)
        if line.strip()
    ]
    expected = [[str(c) for c in expected_row(i, r)] for r in rows]
    mismatch = [
        {"row": n + 1, "expected": e, "actual": a}
        for n, (e, a) in enumerate(zip(expected, actual))
        if e != a
    ]
    tables.append(
        {
            "table": p.stem,
            "source_rows": len(rows),
            "native_rows": len(actual),
            "row_count_equal": len(rows) == len(actual),
            "ordered_cell_mismatches": mismatch,
            "csv_sidecar_identical": sha(p) == sha(PACKAGE / "data" / p.name),
            "json_sidecar_identical": sha(p.with_suffix(".json"))
            == sha(PACKAGE / "data" / p.with_suffix(".json").name),
        }
    )

baseline = json.loads((HERE / "source_snapshots/sol_source_baseline.json").read_text())
source_hashes = {
    name: {
        "baseline": digest,
        "now": sha(BASE / name),
        "unchanged": digest == sha(BASE / name),
    }
    for name, digest in baseline["source_sha256"].items()
}
figures = [
    {"figure": p.name, "asset_identical": sha(p) == sha(PACKAGE / "assets" / p.name)}
    for p in sorted((BASE / "astra/exhibits").glob("f*.pdf"))
]
labels, refs = [], []
for p in PACKAGE.rglob("*.tex"):
    text = p.read_text()
    labels += re.findall(r"\\label\{([^}]+)\}", text)
    refs += re.findall(r"\\(?:ref|pageref|autoref|cref)\{([^}]+)\}", text)
links = []
for p in PACKAGE.rglob("*.tex"):
    for target in re.findall(r"\\href\{run:([^}]+)\}", p.read_text()):
        links.append(
            {
                "file": str(p.relative_to(PACKAGE)),
                "target": target,
                "exists_from_delivered_pdf_dir": (PACKAGE / target).exists(),
            }
        )
report = {
    "scope": "Every displayed native cell in original row order; linked raw metadata retained in identical sidecars.",
    "tables": tables,
    "total_native_rows": sum(t["native_rows"] for t in tables),
    "figures": figures,
    "source_preservation": source_hashes,
    "duplicate_labels": sorted({x for x in labels if labels.count(x) > 1}),
    "unresolved_source_refs": sorted(set(refs) - set(labels)),
    "local_links": links,
    "package_sha256": {
        str(p.relative_to(PACKAGE)): sha(p)
        for p in PACKAGE.rglob("*")
        if p.is_file() and p.suffix in {".tex", ".py", ".json", ".md", ".sh"}
    },
}
(HERE / "verification_table_fidelity.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
print(
    json.dumps(
        {
            "tables": [
                {
                    k: t[k]
                    for k in ("table", "source_rows", "native_rows", "row_count_equal")
                }
                | {"cell_mismatches": len(t["ordered_cell_mismatches"])}
                for t in tables
            ],
            "total_native_rows": report["total_native_rows"],
            "changed_sources": [
                k for k, v in source_hashes.items() if not v["unchanged"]
            ],
            "broken_local_links": [
                x for x in links if not x["exists_from_delivered_pdf_dir"]
            ],
        },
        indent=2,
    )
)

assert report["total_native_rows"] == 837
assert all(
    t["row_count_equal"]
    and not t["ordered_cell_mismatches"]
    and t["csv_sidecar_identical"]
    and t["json_sidecar_identical"]
    for t in tables
)
assert all(v["unchanged"] for v in source_hashes.values())
assert all(f["asset_identical"] for f in figures)
