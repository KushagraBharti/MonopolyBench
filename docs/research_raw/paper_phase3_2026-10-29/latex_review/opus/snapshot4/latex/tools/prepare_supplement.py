"""Reformat coauthor exhibits, with derived rows and source provenance explicit."""

import csv
import json
import shutil
from prepare_sources import BASE, HERE, MANIFEST, table, tex, track, write


def sidecar(relative, stem):
    p = track(BASE / relative)
    if p.suffix == ".csv":
        with p.open(newline="") as f:
            rows = list(csv.DictReader(f))
    else:
        rows = json.loads(p.read_text())
    shutil.copy2(p, HERE / "data" / p.name)
    (HERE / "data" / f"{stem}.json").write_text(json.dumps(rows, indent=2) + "\n")
    return rows


def main():
    sections = [
        r"\renewcommand{\thefigure}{S\arabic{figure}}\renewcommand{\theHfigure}{supp.\arabic{figure}}\setcounter{figure}{0}"
        + "\n",
        r"\renewcommand{\thetable}{S\arabic{table}}\renewcommand{\theHtable}{supp.\arabic{table}}\setcounter{table}{0}"
        + "\n",
    ]
    peers = [
        (
            "sol/exhibits/s1_seed_rotation.png",
            "Alternative seed/rotation grid",
            "Sol's alternative rendering of the same 20 outcomes, not an independent dataset. Seats are one-based. Raster export retained to avoid SVG font-substitution artifacts.",
            False,
        ),
        (
            "sol/exhibits/s2_spending_windows.png",
            "Whole-game and post-own-spending receipts",
            "Sol's two-window comparison for all 103 spending units. Whole-game paid developed rent is 93000 game dollars; post-own-expenditure receipts are 92550. No ROI or causal return is identified. Raster export.",
            True,
        ),
        (
            "sol/exhibits/s3_g19_dark_blue.png",
            "G19 dark blue across successive owners",
            "Sol's event-linked ownership, spending and receipts chronology. The same group has different owners and expenditure histories; whole-game receipts cannot be assigned automatically to an owner's own construction. Raster export.",
            False,
        ),
        (
            "fable/exhibits/house_stock_grid.png",
            "House stock through all 20 games",
            "Fable's event-only reconstruction matches the delivered bank state at all 6989 decision requests. Nine games reach zero houses. Hotel conversions return houses; zero inventory is not a count of denied building demand. The dotted level marks the four houses required for a hotel downgrade. Raster export.",
            False,
        ),
    ]
    for relative, title, caption, wide in peers:
        src = track(BASE / relative)
        shutil.copy2(src, HERE / "assets" / src.name)
        sections.append(
            "\\clearpage\n"
            + ("\\begin{landscape}\n" if wide else "")
            + "\\begin{figure}[p]\n\\centering\n"
            + r"\includegraphics[width=\linewidth,height="
            + ("4.4in" if wide else "0.73\\textheight")
            + r",keepaspectratio]{"
            + src.name
            + "}\n"
            + r"\caption["
            + tex(title)
            + "]{"
            + tex(caption)
            + "}\n\\label{fig:peer-"
            + src.stem
            + "}\n\\end{figure}\n\\clearpage\n"
            + ("\\end{landscape}\n" if wide else "")
        )
    sections.append(
        "\\subsection*{Indexed alternative, not a retained result panel}\nOpus's alternative grid is indexed in the source snapshot and source manifest rather than reproduced: its footer contains reference null-model p-values excluded by the shared outline. Its CSV uses rotations 0--3 and the name Argon; its SVG labels seats 1--4 but rotations 0--3. It represents the same twenty outcomes as F2. The original SVG uses CSS variables that can render black in PDF converters.\n"
    )
    for ext in ("svg", "csv"):
        p = track(BASE / "opus/exhibits" / ("outcome_grid." + ext))
        shutil.copy2(p, HERE / "source_snapshots" / ("opus_outcome_grid." + ext))

    causes = sidecar(
        "fable/exhibits/first_management_causes.json", "s01_management_windows"
    )["rows"]
    rows = []
    short = {
        "built": "Built",
        "never_legal_in_window": "Never legal",
        "default_after_refusal": "Default after refusal",
        "default_other": "Other default",
        "received_conflict": "Received conflict",
        "valid_end": "Valid END",
    }
    for r in causes:
        rows.append(
            [
                r["game"],
                r["player"] + " " + r["model"],
                r["group"].replace("_", " "),
                r["first_mgmt_turn"],
                r["first_mgmt_decision"],
                int(r["entry_legal"]),
                int(r["legal_any_menu_that_turn"]),
                int(r["built_first_mgmt_turn"]),
                short[r["cause"]],
            ]
        )
    table(
        "s01_management_windows",
        "All 63 first-management windows, including access and resolution",
        [
            "Game",
            "Seat / agent",
            "Group",
            "Turn",
            "First decision",
            "Entry legal",
            "Legal during",
            "Built",
            "Resolution",
        ],
        "r l l r l r r r L{1.45in}",
        rows,
        "Fable reconstruction. Boolean1=yes,0=no. The whole-window population has43 builds,9 never-legal windows,4 defaults,4 received conflicts and3 valid ENDs. The entry-buildable subset in F4/T9 has34 builds plus3 defaults,3 conflicts and2 stated holds. Valid END does not itself establish a deliberate hold. Different denominator, not conflicting counts.",
        True,
        code_columns=(4,),
    )
    stock = sidecar("fable/exhibits/house_stock_report.json", "s02_house_stock")[
        "games"
    ]
    table(
        "s02_house_stock",
        "Per-game stock minima and decision-time zero-stock exposure",
        [
            "Game",
            "Minimum houses",
            "Minimum hotels",
            "First zero turn",
            "First zero event",
            "Decisions checked",
            "Zero-stock decisions",
            "Mismatches",
        ],
        "r r r r r r r r",
        [
            [
                r["game"],
                r["min_houses"],
                r["min_hotels"],
                r["first_zero_turn"] if r["first_zero_turn"] is not None else "None",
                r["first_zero_seq"] if r["first_zero_seq"] is not None else "None",
                r["decisions_checked"],
                r["decisions_with_zero_houses"],
                r["decision_mismatches"],
            ]
            for r in stock
        ],
        "None means stock never reached zero. Exposure counts are not demand or blocked-build counts. 6989 delivered bank states checked with zero mismatches. Source reconstruction belongs to Fable; this table is a reformatting.",
        True,
    )
    cost = sidecar("opus/exhibits/cost_usage.csv", "s03_provider_cost")
    table(
        "s03_provider_cost",
        "Provider cost and usage, in real USD rather than game currency",
        [
            "Agent",
            "Decisions",
            "Attempts",
            "Missing-cost attempts",
            "Known USD",
            "USD / decision",
            "Completion tokens / decision",
            "Reasoning tokens / decision",
            "Latency seconds / decision",
        ],
        "l r r r r r r r r",
        [
            [
                (
                    "Gemini (Argon)"
                    if r["configured_agent"] == "Argon"
                    else r["configured_agent"]
                ),
                r["decisions"],
                r["own_model_attempts"],
                r["attempts_missing_cost"],
                r["known_cost_usd"],
                r["known_cost_per_decision_usd"],
                r["completion_tokens_per_decision"],
                r["reasoning_tokens_per_decision"],
                r["latency_s_per_decision"],
            ]
            for r in cost
        ],
        "Known cost is incomplete where attempts lack accounting, including1600 Opus refused attempts and3 Grok attempts. Provider token definitions differ; medium effort labels do not equalize compute. Latency is wall-clock observation, not the simulated game horizon. Full request model IDs, token totals and source notes remain in the sidecar.",
        True,
    )
    norms = sidecar("opus/exhibits/normative_contracts.csv", "s04_normative_contracts")
    table(
        "s04_normative_contracts",
        "Conduct contracts and the source for each comparison",
        [
            "Behavior",
            "MonopolyBench status / source",
            "AgentMonopoly status / source",
            "Arena study status / source",
        ],
        "L{1.45in} L{2.35in} L{2.35in} L{2.35in}",
        [
            [
                r["behavior"],
                r["monopolybench_status"] + " Source: " + r["monopolybench_source"],
                r["agentmonopoly_status"] + " Source: " + r["agentmonopoly_source"],
                r["vb_arena_paper_status"] + " Source: " + r["vb_arena_paper_source"],
            ]
            for r in norms
        ],
        "Historical source comparison by Opus. The 56.9% and31.5% promise-enactment values refer to the cited Arena paper, not this MonopolyBench cohort. Instruction permission, externally coded conduct and observed follow-through are distinct. All source columns have been retained in the cells. Descriptions of retry policy are qualified by the actual Opus condition in the main text.",
        True,
    )
    for stem in (
        "s01_management_windows",
        "s02_house_stock",
        "s03_provider_cost",
        "s04_normative_contracts",
    ):
        sections.append(
            "\\clearpage\n\\begin{landscape}\n\\input{tables/"
            + stem
            + "}\n\\clearpage\n\\end{landscape}\n"
        )
    # Preserve the author's full three-layer exhibit, not a new abridgement.
    p = track(BASE / "latex_review/opus/proposed/opus_exhibits.tex")
    shutil.copy2(p, HERE / "tables/opus_exhibits.tex")
    sections.append("\\clearpage\n\\input{tables/opus_exhibits}\n")
    p = track(BASE / "opus/exhibits/affordance_ledger.md")
    shutil.copy2(p, HERE / "source_snapshots" / p.name)
    corrections = {
        "93000": "93,000",
        "92550": "92,550",
        "6989": "6,989",
        "Boolean1=yes,0=no": "Boolean 1 = yes, 0 = no",
        "has43": "has 43",
        "builds,9": "builds, 9",
        "windows,4": "windows, 4",
        "defaults,4": "defaults, 4",
        "and3": "and 3",
        "has34": "has 34",
        "plus3": "plus 3",
        "defaults,3": "defaults, 3",
        "and2": "and 2",
        "including1600": "including 1,600",
        "and31.5": "and 31.5",
    }
    for p in [
        HERE / "tables" / f"s0{i}_{n}.tex"
        for i, n in [
            (1, "management_windows"),
            (2, "house_stock"),
            (3, "provider_cost"),
            (4, "normative_contracts"),
        ]
    ]:
        text = p.read_text()
        for old, new in corrections.items():
            text = text.replace(old, new)
        p.write_text(text)
    text = "".join(sections)
    for old, new in corrections.items():
        text = text.replace(old, new)
    write(HERE / "peer_inputs.tex", text, True)
    (HERE / "supplement_manifest.json").write_text(
        json.dumps(
            {
                "source_sha256": MANIFEST,
                "scope": "Reformatting of coauthor figures and tables; no new analysis. Opus grid indexed rather than rendered because its footer is superseded.",
            },
            indent=2,
        )
        + "\n"
    )
    print("Prepared four peer figures and four supplementary native data tables.")


if __name__ == "__main__":
    main()
