"""Apply the disclosed, idempotent integration fixes from all three reviews."""

import hashlib
import json
import re
from pathlib import Path

from prepare_sources import BASE, HERE, MANIFEST, prose, tex, track


def main():
    # Safe document navigation: PDF Launch actions are deliberately never emitted.
    labels = {p.stem: "fig:" + p.stem for p in (HERE / "figures").glob("f*.tex")}
    labels.update({p.stem: "tab:" + p.stem for p in (HERE / "tables").glob("t0*.tex")})
    labels.update(
        {
            s: "fig:peer-" + s
            for s in (
                "s1_seed_rotation",
                "s2_spending_windows",
                "s3_g19_dark_blue",
                "house_stock_grid",
            )
        }
    )
    labels["first_management_causes"] = "tab:s01_management_windows"
    local = re.compile(r"\\href\{run:\.\./([^}]+)\}\{([^}]+)\}")
    for name in ("outline_body.tex", "exhibit_index.tex", "selection_notes.tex"):
        p = HERE / name

        def safe(m):
            path, title = m.groups()
            label = labels.get(Path(path).stem)
            if name != "outline_body.tex" and label:
                return r"\hyperref[" + label + "]{" + title + "}"
            return r"\artifactref{" + path + "}{" + title + "}"

        p.write_text(local.sub(safe, p.read_text()))

    preface = (BASE / "astra/exhibit_captions.md").read_text().split("## F1")[0]
    preface = preface.replace(
        "(build_exhibits.py)", "(astra/build_exhibits.py)"
    ).replace("(exhibits/manifest.json)", "(astra/exhibits/manifest.json)")
    (HERE / "caption_preface.tex").write_text(prose(preface))
    table_map = {
        2: ["t01_cohort"],
        3: ["t02_negotiation"],
        4: [
            "t03_trade_groups",
            "t04_bilateral_completion",
            "t09_entry_nonbuild_records",
        ],
        5: ["t05_spending_units"],
        6: ["t06_eliminations"],
        7: ["t07_build_recovery"],
        9: ["t08_cash_trajectories"],
    }
    for n, stems in table_map.items():
        p = next((HERE / "figures").glob(f"f{n:02d}_*.tex"))
        text = p.read_text().split("% Native data cross-reference")[0].rstrip() + "\n"
        text = re.sub(r"\s*Underlying data: Table~.*?\.(?=\}\n\\label\{fig:)", "", text)
        pointer = (
            " Underlying data: "
            + ", ".join(r"Table~\ref{tab:" + s + "}" for s in stems)
            + "."
        )
        text = text.replace("}\n\\label{fig:", pointer + "}\n\\label{fig:")
        p.write_text(text)

    # Exact response-condition cells, adjacent to the same four T2 rows.
    p = HERE / "tables/t02_negotiation.tex"
    text = (
        p.read_text().split("% Complete response-condition column")[0].rstrip() + "\n"
    )
    text += (
        "% Complete response-condition column\n"
        + r"\begingroup\small\begin{tabularx}{\linewidth}{l Y}\toprule Agent & Recorded response condition\\\midrule"
        + "\n"
    )
    for row in json.loads((HERE / "data/t02_negotiation.json").read_text()):
        text += (
            tex(row["configuration"])
            + " & "
            + tex(row["response_condition"])
            + r" \\"
            + "\n"
        )
    text += r"\bottomrule\end{tabularx}\endgroup" + "\n"
    p.write_text(text)

    # The same source rows, exposing fields omitted from the compact main tables.
    companions = []
    for source, number in [
        ("t06_liquidation_routes", "T6a"),
        ("t09_provenance", "T9a"),
    ]:
        src = BASE / "latex_review/fable/proposed/snippets" / f"{source}.tex"
        text = track(src).read_text()
        (HERE / "source_snapshots" / src.name).write_text(text)
        text = re.sub(
            r"\\caption\{([^\n]+?)\}\\label\{[^}]+\}",
            lambda m: r"\caption*{\textbf{"
            + number
            + ".} "
            + m[1]
            + "}"
            + r"\addcontentsline{lot}{table}{"
            + number
            + r"\quad "
            + m[1]
            + "}",
            text,
        )
        text = text.replace(
            r"\tablename\ \thetable\ (continued)", number + " (continued)"
        )
        dest = HERE / "tables" / f"{source}.tex"
        dest.write_text(
            "% Integrated from Fable; independently checked by Sol.\n" + text
        )
        companions.append(
            "\\clearpage\n\\begin{landscape}\n\\input{tables/"
            + source
            + "}\n\\clearpage\n\\end{landscape}\n"
        )
    (HERE / "companion_inputs.tex").write_text("".join(companions))

    # Keep original canonical reason identifiers unbroken at these measured widths.
    for name in ("t08_cash_trajectories", "t09_entry_nonbuild_records"):
        p = HERE / "tables" / f"{name}.tex"
        p.write_text(
            re.sub(
                r"\\path\{([A-Z_0-9]+|end_turn|build_houses_or_hotel|mortgage_property|Absent)\}",
                r"\\tok{\1}",
                p.read_text(),
            )
        )
    p = HERE / "tables/s02_house_stock.tex"
    p.write_text(
        p.read_text().replace(
            r"\textbf{Zero-stock}\\\textbf{decisions}",
            r"\textbf{Decisions at}\\\textbf{zero houses}",
        )
    )
    p = HERE / "tables/s04_normative_contracts.tex"
    text = p.read_text().split("% Normative comparison caption")[0].rstrip() + "\n"
    text += (
        "% Normative comparison caption\n"
        + r"\tablenote{The same act has a different normative status across environments, so rates and labels do not transfer between them.}"
        + "\n"
    )
    p.write_text(text)
    for stem in ("t06_eliminations", "s01_management_windows"):
        p = HERE / "tables" / (stem + ".tex")
        p.write_text(
            p.read_text().replace(r"\arraystretch}{1.12}", r"\arraystretch}{1.05}")
        )
    p = HERE / "table_inputs.tex"
    text = p.read_text()
    if text.startswith("\\clearpage\n"):
        p.write_text(text[len("\\clearpage\n") :])
    p = HERE / "peer_inputs.tex"
    text = p.read_text().replace(
        "\\clearpage\n\\begin{figure}[p]", "\\begin{figure}[htp]", 1
    )
    p.write_text(text)
    p = HERE / "tables/opus_exhibits.tex"
    text = p.read_text()
    start = text.find(r"\subsection*{Opus peer exhibits}")
    first_landscape = text.find(r"\begin{landscape}")
    if 0 <= start < first_landscape:
        introduction = text[start:first_landscape]
        text = text[:start] + text[first_landscape:]
        text = text.replace(
            r"\begin{landscape}", r"\begin{landscape}" + "\n" + introduction, 1
        )
    if not text.startswith("\\begingroup\\small\n"):
        text = "\\begingroup\\small\n" + text + "\\endgroup\n"
    p.write_text(text)
    for stem, note in [
        (
            "s03_provider_cost",
            "Compact CSV view of OC-3 below; the same cost records, not a separate measurement.",
        ),
        (
            "s04_normative_contracts",
            "Source-annotated CSV view of OC-1 below. This version retains every per-cell source column; the author exhibit retains the full explanatory prose.",
        ),
    ]:
        p = HERE / "tables" / (stem + ".tex")
        text = (
            p.read_text().split("% Relationship to author exhibit")[0].rstrip() + "\n"
        )
        p.write_text(
            text + "% Relationship to author exhibit\n" + r"\tablenote{" + note + "}\n"
        )
    # Original source hash in each reusable snippet, alongside exact package data.
    for p in sorted((HERE / "tables").glob("t0*.tex")):
        source = BASE / "astra/exhibits" / f"{p.stem}.json"
        if source.exists():
            body = re.sub(r"^% Canonical source:.*\n", "", p.read_text())
            p.write_text(
                "% Canonical source: astra/exhibits/"
                + source.name
                + " sha256 "
                + hashlib.sha256(source.read_bytes()).hexdigest()
                + "\n"
                + body
            )
    assert not any("run:" in p.read_text() for p in HERE.rglob("*.tex"))
    (HERE / "integration_manifest.json").write_text(
        json.dumps(
            {
                "source_sha256": MANIFEST,
                "scope": "Peer companion transcriptions, copied into this package; no reviewer-folder dependency for LaTeX compilation.",
            },
            indent=2,
        )
        + "\n"
    )
    print(
        "Integrated safe links, full captions, response conditions and two provenance companions."
    )


if __name__ == "__main__":
    main()
