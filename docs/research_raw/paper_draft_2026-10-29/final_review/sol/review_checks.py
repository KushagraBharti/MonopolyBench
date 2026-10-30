"""Bounded read-only source checks; all outputs stay in this review directory."""
from hashlib import sha256
import json
from pathlib import Path
import runpy

import fitz

HERE = Path(__file__).resolve().parent
DRAFT = HERE.parents[1]
ROOT = DRAFT.parents[2]


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    pdf = DRAFT / "manuscript.pdf"
    doc = fitz.open(pdf)
    text = "\n\n".join(f"=== PDF page {i + 1} ===\n{p.get_text()}" for i, p in enumerate(doc))
    (HERE / "manuscript_extracted.txt").write_text(text)
    inventory = []
    for i, page in enumerate(doc):
        txt = page.get_text()
        inventory.append({"page": i + 1, "start": txt[:140].replace("\n", " "),
                          "figure_lines": [s for s in txt.splitlines() if s.startswith("Figure") or s.startswith("Table")]})
    report = {"pdf_sha256": sha256(pdf.read_bytes()).hexdigest(), "pages": len(doc), "page_inventory": inventory}
    report["reviewed_source_hashes"] = {str(p.relative_to(DRAFT)): sha256(p.read_bytes()).hexdigest()
                                        for p in [*sorted((DRAFT / "sections").glob("*.tex")), DRAFT / "tools/build_exhibits.py"]}

    units = read(DRAFT / "data/t05_spending_units.json")
    groups = read(DRAFT / "data/t03_trade_groups.json")
    debt = read(DRAFT / "data/t06_eliminations.json")
    prior = read(DRAFT / "coauthors/sol/verification.json")
    report["integrated_frozen_counts"] = {
        "spending_units": len(units),
        "spend": sum(r["spend"] for r in units),
        "post_receipts": sum(r["paid_developed_rent_after_first_own_spend"] for r in units),
        "zero_receipts": sum(r["paid_developed_rent_after_first_own_spend"] == 0 for r in units),
        "trade_groups": {k: sum(r[k] for r in groups) for k in ["trade_groups", "entry_eligible", "entry_eligible_built", "first_management_built", "eligible_during_window"]},
        "eliminations": {"total": len(debt), "nominal_insufficient": sum(r["full"] < r["owed"] for r in debt),
                         "accessible_covers": sum(r["accessible"] >= r["owed"] for r in debt),
                         "stock_locks": sum(r["accessible"] != r["full"] for r in debt)},
    }
    assert report["integrated_frozen_counts"]["spend"] == prior["spending_sums"]["spend"]
    assert report["integrated_frozen_counts"]["post_receipts"] == prior["spending_sums"]["post"]
    report["focused_original_events"] = {}
    reducer = runpy.run_path(str(ROOT / "docs/research_raw/paper_phase1_2026-10-28/sol/economics.py"))
    board = read(ROOT / "contracts/data/board.json")
    for game in (15, 19):
        rel, expected = next((p, h) for p, h in prior["original_event_hashes"].items() if f"game-{game}-" in p)
        source = ROOT / rel
        assert sha256(source.read_bytes()).hexdigest() == expected
        events = rows(source)
        config = read(source.parent / "run_config.json")
        reduced = reducer["reconstruct"](events, [p["player_id"] for p in config["players"]], board["spaces"])
        if game == 15:
            keep = [e for e in events if e["seq"] in {711, 718, 1159, 1422, 1423, 1424, 1491, 1564, 1641, 1870, 1985, 1995}]
        else:
            keep = [e for e in events if e["type"] in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD", "RENT_PAID"}
                    and e["payload"].get("space_index") in {37, 39}]
        report["focused_original_events"][str(game)] = {"source": rel, "sha256": expected, "events": keep}
        report["focused_original_events"][str(game)]["original_reducer_winner_groups"] = [r for r in reduced["group_episodes"] if r["player_id"] == "p1"]
        if game == 15:
            episodes = report["focused_original_events"][str(game)]["original_reducer_winner_groups"]
            assert episodes[0]["group"] == "ORANGE" and episodes[0]["acquisition_seq"] == 711
            assert next(r for r in episodes if r["group"] == "GREEN")["acquisition_seq"] == 1995
            assert not any("p1" in [r["thread_initiator"], r["thread_recipient"]] for r in reduced["trades"])
            rent = [e for e in events if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == "p1"
                    and e["payload"]["space_index"] in (16, 18, 19) and e["seq"] >= 718]
            assert sum(e["payload"]["amount"] for e in rent) == 3250
            report["focused_original_events"][str(game)]["orange_paid_rent_sum_after_build"] = 3250
        else:
            totals = {p: {"construction": 0, "sales": 0, "rent": 0} for p in ("p1", "p3")}
            levels = {37: 0, 39: 0}
            for e in keep:
                payload = e["payload"]
                if e["type"] == "RENT_PAID":
                    p = payload["to_player_id"]
                    if p in totals and levels[payload["space_index"]] > 0:
                        totals[p]["rent"] += payload["amount"]
                else:
                    i = payload["space_index"]
                    levels[i] = (5 if e["type"] == "HOTEL_BUILT" else 4 if e["type"] == "HOTEL_SOLD"
                                 else levels[i] + (payload["count"] if e["type"] == "HOUSE_BUILT" else -payload["count"]))
                    if payload["player_id"] in totals:
                        totals[payload["player_id"]]["construction" if e["type"].endswith("BUILT") else "sales"] += payload["count"] * (200 if e["type"].endswith("BUILT") else 100)
            assert totals == {"p1": {"construction": 2000, "sales": 0, "rent": 1400}, "p3": {"construction": 1200, "sales": 600, "rent": 175}}
            report["focused_original_events"][str(game)]["dark_blue_totals"] = totals
    (HERE / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
    for page_number in (1, 7, 8, 9, 10, 11, 12, 13, 18, 30, 31, 32, 33):
        doc[page_number - 1].get_pixmap(dpi=110).save(HERE / f"page-{page_number:02}.png")
    for item in inventory:
        print(item)
    print(json.dumps(report["integrated_frozen_counts"], indent=2))


if __name__ == "__main__":
    main()
