"""Render retained provenance and per-game populations without model inference."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read(name):
    return json.loads((DATA / f"{name}.json").read_text())


conditions = read("resolution_conditions")
windows = read("first_management_windows")["rows"]
certificates = read("certificate_results")
names = ("Sol", "Gemini", "Opus", "Grok")
assert len(windows) == 63
assert sum(r["built_first_mgmt_turn"] for r in windows) == 43
assert sum(r["entry_legal"] for r in windows) == 42
assert sum(r["entry_legal"] and r["built_first_mgmt_turn"] for r in windows) == 34
rows = []
for name in names:
    c = conditions["counts"][name]
    values = [c.get(k, 0) for k in ("construction_tool_listed", "applied_end", "engine_default",
                                   "received_name_conflict", "no_detected_name_conflict")]
    assert values[1] == sum(values[2:])
    rows.append(name + " & " + " & ".join(map(str, values)) + r" \\")
assert sum(c["applied_end"] for c in conditions["counts"].values()) == 663
(ROOT / "sections/end_provenance_table.tex").write_text(r"""\begin{table}[t]
\centering\small
\begin{tabular}{lrrrrr}\toprule
Configuration & Tool-listed & END & Default & Name conflict & No detected conflict\\\midrule
""" + "\n".join(rows) + r"""
\midrule Total & 1,225 & 663 & 66 & 24 & 573\\\bottomrule
\end{tabular}
\caption{Every applied END on a management menu listing construction. Categories partition ENDs, not all listed menus. A default is engine-authored; a conflict is disagreement between selected content and received call names. The remainder includes empty or unparseable content and matching names, not verified reserve choices. Sol and Gemini's selected content fields are all empty; 42 of 43 nondefault Opus ENDs use action-only recovery. Grok uses required tool selection. These observation conditions prevent comparing the last two columns as error or intention rates.}
\label{tab:end-provenance}
\end{table}
""")

ledger, display = [], []
for game in range(1, 21):
    group_rows = [r for r in windows if r["game"] == game]
    cases = [r for r in certificates["results"] if r["game"] == game]
    defaults = sum(r["kind"] == "default" for r in cases)
    kinds = Counter(r["certificate"] for r in cases if r["kind"] == "elimination")
    assert sum(kinds.values()) == 3
    for model in names:
        subset = [r for r in group_rows if r["model"] == model]
        ledger.append({"game": game, "seed_block": (game - 1) // 4 + 1,
                       "model": model, "groups": len(subset),
                       "built_in_window": sum(r["built_first_mgmt_turn"] for r in subset),
                       "entry_eligible": sum(r["entry_legal"] for r in subset),
                       "entry_built": sum(r["entry_legal"] and r["built_first_mgmt_turn"] for r in subset),
                       "resolution": dict(Counter(r["cause"] for r in subset))})
    built = sum(r["built_first_mgmt_turn"] for r in group_rows)
    entry = sum(r["entry_legal"] for r in group_rows)
    entry_built = sum(r["entry_legal"] and r["built_first_mgmt_turn"] for r in group_rows)
    cells = [game, (game - 1) // 4 + 1, f"{built}/{len(group_rows)}", f"{entry_built}/{entry}",
             defaults, kinds["upper_bound_impossibility"], kinds["legal_payment_witness"],
             kinds["exhaustive_financing_impossibility"]]
    display.append(" & ".join(map(str, cells)) + r" \\")
(ROOT / "sections/per_game_audit_table.tex").write_text(r"""\begin{table}[htbp]
\centering\small
\begin{tabular}{rrrrrrrr}\toprule
Game & Block & Built/window & Built/entry & Defaults & Bound & Payable & Lock\\\midrule
""" + "\n".join(display) + r"""
\midrule Total & & 43/63 & 34/42 & 66 & 56 & 3 & 1\\\bottomrule
\end{tabular}
\caption{Per-game populations. Window and entry columns count trade-completed groups; defaults count decisions across all groups. Bound, payable and lock partition each game's three eliminations. A 0/0 cell denotes no eligible group, not a zero rate. Block denotes shared seed, not independent replication. All 80 game/configuration cells, including zeros, are retained in \texttt{data/opportunity\_ledger.json}.}
\label{tab:per-game-audit}
\end{table}
""")
(DATA / "opportunity_ledger.json").write_text(json.dumps({"rows": ledger,
    "source_sha256": {name: hashlib.sha256((DATA / name).read_bytes()).hexdigest()
                      for name in ("resolution_conditions.json", "first_management_windows.json", "certificate_results.json")},
    "scope": "Reaggregation of retained source-qualified audits, not a new canonical-event reduction."}, indent=2) + "\n")
print(json.dumps({"end_rows": 4, "game_rows": 20, "game_configuration_cells": 80}))
