"""Verify shared phase-3 assembly without changing games or peer artifacts.

Checks file/source integrity and numerical joins, not annotation validity,
causal identification or a clean external installation.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

from build_reference_library import entries

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[2]
ASTRA = BASE / "astra"
OUT = ASTRA / "exhibits"


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checked_sources = {}
    checked_outputs = {}
    manifest = read(OUT / "manifest.json")
    residual = read(ASTRA / "deployment_residual_check.json")
    for record in (manifest, residual):
        for name, expected in record["source_sha256"].items():
            assert sha(ROOT / name) == expected, name
            checked_sources[name] = expected
    assert sha(ASTRA / "build_exhibits.py") == manifest["script_sha256"]
    assert sha(ASTRA / "check_deployment_residuals.py") == residual["script_sha256"]
    for name, expected in manifest["artifacts"].items():
        assert sha(OUT / name) == expected, name
        checked_outputs[f"astra/exhibits/{name}"] = expected
    assert len(list(OUT.glob("f*.png"))) == 9
    assert len(list(OUT.glob("f*.pdf"))) == 9
    assert len(list(OUT.glob("f*.svg"))) == 9
    table_counts = {}
    for path in sorted(OUT.glob("t*.json")):
        data = read(path)
        with path.with_suffix(".csv").open(newline="") as f:
            csv_rows = list(csv.DictReader(f))
        assert len(data) == len(csv_rows)
        assert set(data[0]) == set(csv_rows[0])
        table_counts[path.stem] = len(data)
    assert len(table_counts) == 9
    eliminations = read(OUT / "t06_eliminations.json")
    assert Counter(r["elimination"] for r in eliminations) == {
        "declared": 56,
        "automatic": 4,
    }
    assert sum(r["avoidable"] for r in eliminations) == 3
    assert sum(r["accessible"] != r["full"] for r in eliminations) == 1

    # Independent reconstructions agree; this assembly join is not another replay.
    causes = read(BASE / "fable/exhibits/first_management_causes.json")
    rows = causes["rows"]
    assert len(rows) == 63
    assert sum(r["built_first_mgmt_turn"] for r in rows) == 43
    assert sum(r["entry_legal"] for r in rows) == 42
    assert sum(r["legal_any_menu_that_turn"] for r in rows) == 54
    entry_residual = [
        r for r in rows if r["entry_legal"] and not r["built_first_mgmt_turn"]
    ]
    indexed = {(r["game"], r["group"]): r for r in entry_residual}
    category_map = {
        "default_other": "engine_default",
        "default_after_refusal": "engine_default",
        "received_conflict": "received_content_tool_conflict",
        "valid_end": "consistent_end_with_stated_reserve",
    }
    for ours in residual["rows"]:
        peer = indexed[(ours["game"], ours["group"])]
        assert ours["decision_id"].endswith(peer["decisions"][-1]["decision_id"])
        assert ours["category"] == category_map[peer["cause"]]
    assert len(indexed) == len(residual["rows"]) == 8
    stock = read(BASE / "fable/exhibits/house_stock_report.json")
    assert sum(r["decisions_checked"] for r in stock["games"]) == 6989
    assert sum(r["decision_mismatches"] for r in stock["games"]) == 0
    assert [r["game"] for r in stock["games"] if r["min_houses"] == 0] == [
        3,
        4,
        5,
        6,
        7,
        9,
        12,
        14,
        18,
    ]
    economics = read(
        ROOT
        / "docs/research_raw/paper_phase2_2026-10-28/core_review/astra/development_aggregation_check.json"
    )
    event_paths = {
        int(p.split("/game-")[1][:2]): ROOT / p
        for p in economics["event_source_hashes"]
    }
    for r in stock["games"]:
        for name, key in (
            ("events.jsonl", "events_sha256"),
            ("decisions.jsonl", "decisions_sha256"),
        ):
            path = event_paths[r["game"]].parent / name
            assert sha(path) == r[key]
            checked_sources[str(path.relative_to(ROOT))] = r[key]
    sol_manifest = read(BASE / "sol/exhibits/manifest.json")
    for name, expected in sol_manifest["outputs"].items():
        assert sha(BASE / "sol/exhibits" / name) == expected
        checked_outputs[f"sol/exhibits/{name}"] = expected
    for r in sol_manifest["inputs"]:
        assert sha(ROOT / r["path"]) == r["sha256"]
        checked_sources[r["path"]] = r["sha256"]

    registry = read(BASE / "reference_registry.json")
    bibliography = BASE / "references.bib"
    assert sha(bibliography) == registry["bibliography_sha256"]
    bib_records = dict(entries(bibliography.read_text()))
    assert len(bib_records) == len(registry["references"]) == 34
    assert (
        len(
            {r["arxiv_version"] for r in registry["references"] if "arxiv_version" in r}
        )
        == 30
    )
    for r in registry["references"]:
        assert (
            hashlib.sha256(bib_records[r["key"]].encode()).hexdigest()
            == r["selected_entry_sha256"]
        )
    for name, expected in registry["source_sha256"].items():
        assert sha(BASE / name) == expected

    # Portable full gallery; the inline preview uses a small selection separately.
    figures = sorted(OUT.glob("f*.png"))
    cards = []
    for p in figures:
        relative = p.relative_to(BASE).as_posix()
        title = p.stem.replace("_", " ")
        cards.append(
            f'<figure><img src="{relative}" alt="{html.escape(title)}">'
            f"<figcaption>{html.escape(title)} · "
            f'<a href="{relative[:-3]}pdf">PDF</a> · '
            f'<a href="{relative[:-3]}svg">SVG</a></figcaption></figure>'
        )
    gallery = (
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MonopolyBench phase 3 figures</title><style>body{margin:0;font-family:var(--font-sans,system-ui);color:var(--foreground,inherit)}figure{margin:0 0 32px}img{display:block;width:100%;height:auto}figcaption{font-size:14px;margin-top:8px}a{color:var(--primary,inherit)}</style></head><body>'
        + "".join(cards)
        + "</body></html>\n"
    )
    (BASE / "figure_gallery.html").write_text(gallery)
    (BASE / "verification.json").write_text("{}\n")
    markdowns = sorted(BASE.glob("*.md")) + sorted(ASTRA.glob("*.md"))
    link_count = 0
    for p in markdowns:
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", p.read_text()):
            target = match[1].strip("<>")
            if "://" in target or target.startswith("#"):
                continue
            path = p.parent / unquote(target.split("#")[0])
            assert path.exists(), f"Broken link: {p.name} -> {target}"
            link_count += 1
    shared_files = markdowns + [
        bibliography,
        BASE / "reference_registry.json",
        BASE / "figure_gallery.html",
    ]
    for p in shared_files:
        checked_outputs[str(p.relative_to(BASE))] = sha(p)
    report = {
        "status": "pass",
        "scope": "Shared phase-3 assembly: file integrity, numerical joins, original-source hashes and local links. Not a new semantic review or clean-environment release test.",
        "figure_exports": {"png": 9, "pdf": 9, "svg": 9},
        "table_rows": table_counts,
        "reference_count": 34,
        "pinned_papers": 30,
        "local_markdown_links_checked": link_count,
        "numerical_checks": {
            "all_60_eliminations_including_4_automatic": True,
            "eight_entry_residuals_match_independent_records": True,
            "all_63_management_windows_match": True,
            "stock_report_6989_states_zero_mismatches": True,
        },
        "source_sha256": checked_sources,
        "artifact_sha256": checked_outputs,
        "script_sha256": sha(Path(__file__)),
        "visual_review": "Astra inspected all nine figure PNGs during assembly. F4 residuals, F5 facets, F6 transparent annotations and F8 three-case chronology received final visual checks; F3/F7 footer additions checked after regeneration.",
        "provenance": "Peer-informed cross-checks preserve original implementation attribution. No assertion of independent human annotation or causal validation.",
    }
    (BASE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in {"source_sha256", "artifact_sha256"}
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
