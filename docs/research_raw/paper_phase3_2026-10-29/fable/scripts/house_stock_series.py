"""Bank house/hotel stock time series for the 20 research games.

Reconstructs bank building inventory from canonical events only
(HOUSE_BUILT, HOUSE_SOLD, HOTEL_BUILT, HOTEL_SOLD, bank bankruptcy), validates
the reconstruction against the bank inventory delivered in every decision
prompt (prompt_payload.game_state.bank at the LLM_DECISION_REQUESTED seq), and
compares per-game minima with two independent phase-2 audits.

Read-only. Writes CSV/JSON/PNG under fable/exhibits/. No engine import.
Run: python/.venv/bin/python -I <this file> <repo_root>
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

HOUSE_LIMIT = 4
START_HOUSES = 32
START_HOTELS = 12

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(__file__).resolve().parent.parent / "exhibits"
OUT.mkdir(parents=True, exist_ok=True)
COLLECTIONS = [
    ROOT / "saved_games/railway-research-12-games-2026-10-25",
    ROOT / "saved_games/railway-research-8-games-2026-10-26",
]
ASTRA = ROOT / "docs/research_raw/paper_phase2_2026-10-28/core_review/astra/development_aggregation_check.json"
SOL = ROOT / "docs/research_raw/paper_phase2_2026-10-28/core_review/sol/corpus_economics_audit.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_games() -> list[dict]:
    games = []
    for coll in COLLECTIONS:
        with (coll / "game-index.csv").open() as fh:
            for row in csv.DictReader(fh):
                games.append({
                    "game": int(row["collection_game"]),
                    "run_dir": coll / row["package"] / "run",
                    "seed": row.get("seed"),
                    "tree_sha256": row["tree_sha256"],
                })
    games.sort(key=lambda g: g["game"])
    assert [g["game"] for g in games] == list(range(1, 21))
    return games


def reconstruct(run_dir: Path) -> dict:
    events = [json.loads(line) for line in (run_dir / "events.jsonl").open()]
    seqs = [e["seq"] for e in events]
    assert seqs == list(range(seqs[0], seqs[0] + len(seqs))), "non-contiguous seq"
    # delivered bank state per decision id (requested record carries prompt_payload)
    delivered = {}
    seed = None
    for line in (run_dir / "decisions.jsonl").open():
        r = json.loads(line)
        if "prompt_payload" in r and r["prompt_payload"]:
            bank = r["prompt_payload"]["game_state"]["bank"]
            delivered.setdefault(r["decision_id"], (bank["houses_remaining"], bank["hotels_remaining"]))
    summary = json.load((run_dir / "summary.json").open())
    seed = summary.get("run_config", {}).get("seed", seed)
    houses, hotels = START_HOUSES, START_HOTELS
    per_space = {}  # space_index -> (houses, hotel) for bank-bankruptcy returns
    owner = {}
    series = [(0, 0, houses, hotels)]
    checks = 0
    mismatches = []
    first_zero = None
    decisions_at_zero = 0
    for e in events:
        t = e["type"]
        p = e.get("payload") or {}
        if t == "HOUSE_BUILT":
            houses -= p["count"]
            h, ht = per_space.get(p["space_index"], (0, False))
            per_space[p["space_index"]] = (h + p["count"], ht)
        elif t == "HOUSE_SOLD":
            houses += p["count"]
            h, ht = per_space.get(p["space_index"], (0, False))
            per_space[p["space_index"]] = (h - p["count"], ht)
        elif t == "HOTEL_BUILT":
            hotels -= p["count"]
            houses += HOUSE_LIMIT * p["count"]
            per_space[p["space_index"]] = (0, True)
        elif t == "HOTEL_SOLD":
            hotels += p["count"]
            houses -= HOUSE_LIMIT * p["count"]
            per_space[p["space_index"]] = (HOUSE_LIMIT, False)
        elif t == "PROPERTY_PURCHASED":
            owner[p["space_index"]] = p["player_id"]
        elif t == "PROPERTY_TRANSFERRED":
            if "space_index" in p and "to_player_id" in p:
                owner[p["space_index"]] = p["to_player_id"]
        elif t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK":
            # engine.py ~3010-3014: buildings on the bankrupt player's deeds return to the bank
            pid = p.get("player_id")
            for si, who in list(owner.items()):
                if who == pid and si in per_space:
                    h, ht = per_space[si]
                    houses += h
                    hotels += 1 if ht else 0
                    per_space[si] = (0, False)
                    owner[si] = None
        elif t == "LLM_DECISION_REQUESTED":
            did = p["decision_id"]
            if did in delivered:
                checks += 1
                if delivered[did] != (houses, hotels):
                    mismatches.append({"decision_id": did, "seq": e["seq"], "reconstructed": [houses, hotels], "delivered": list(delivered[did])})
                if houses == 0:
                    decisions_at_zero += 1
        if t in ("HOUSE_BUILT", "HOUSE_SOLD", "HOTEL_BUILT", "HOTEL_SOLD") or (t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK"):
            assert 0 <= houses <= START_HOUSES and 0 <= hotels <= START_HOTELS, (e["seq"], houses, hotels)
            series.append((e["seq"], e["turn_index"], houses, hotels))
            if houses == 0 and first_zero is None:
                first_zero = (e["seq"], e["turn_index"])
    last = events[-1]
    series.append((last["seq"], last["turn_index"], houses, hotels))
    return {
        "seed": seed,
        "series": series,
        "min_houses": min(s[2] for s in series),
        "min_hotels": min(s[3] for s in series),
        "first_zero_seq": first_zero[0] if first_zero else None,
        "first_zero_turn": first_zero[1] if first_zero else None,
        "decisions_checked": checks,
        "decisions_with_zero_houses": decisions_at_zero,
        "mismatches": mismatches,
        "final_turn": last["turn_index"],
        "events_sha256": sha256(run_dir / "events.jsonl"),
        "decisions_sha256": sha256(run_dir / "decisions.jsonl"),
        "summary_sha256": sha256(run_dir / "summary.json"),
    }


def g7_lock_seq(run_dir: Path) -> int | None:
    for line in (run_dir / "events.jsonl").open():
        e = json.loads(line)
        if e["type"] == "LLM_DECISION_REQUESTED" and e["payload"]["decision_id"].endswith("dec-000339"):
            return e["seq"]
    return None


def main() -> None:
    games = load_games()
    astra = json.load(open(ASTRA))
    astra_min = {g["game"]: g for g in astra["games"]}
    sol = json.load(open(SOL))
    sol_zero = set(sol["totals"]["zero_house_stock_games"])
    report = {"unit": "bank houses/hotels remaining after each building event; seq = canonical event sequence", "games": []}
    rows = []
    for g in games:
        rec = reconstruct(g["run_dir"])
        a = astra_min.get(g["game"], {})
        entry = {
            "game": g["game"],
            "seed": rec["seed"],
            "tree_sha256": g["tree_sha256"],
            "events_sha256": rec["events_sha256"],
            "decisions_sha256": rec["decisions_sha256"],
            "final_turn": rec["final_turn"],
            "min_houses": rec["min_houses"],
            "min_hotels": rec["min_hotels"],
            "first_zero_seq": rec["first_zero_seq"],
            "first_zero_turn": rec["first_zero_turn"],
            "decisions_checked": rec["decisions_checked"],
            "decision_mismatches": len(rec["mismatches"]),
            "decisions_with_zero_houses": rec["decisions_with_zero_houses"],
            "astra_event_minimum_bank_houses": a.get("event_minimum_bank_houses"),
            "astra_initial_prompt_minimum_bank_houses": a.get("initial_prompt_minimum_bank_houses"),
            "sol_zero_stock_game": g["game"] in sol_zero,
            "agrees_with_astra": a.get("event_minimum_bank_houses") == rec["min_houses"],
            "agrees_with_sol": (rec["min_houses"] == 0) == (g["game"] in sol_zero),
        }
        if rec["mismatches"]:
            entry["mismatch_examples"] = rec["mismatches"][:5]
        report["games"].append(entry)
        for seq, turn, h, ht in rec["series"]:
            rows.append({"game": g["game"], "seed": rec["seed"], "seq": seq, "turn_index": turn, "houses_remaining": h, "hotels_remaining": ht})
        g["rec"] = rec
    report["zero_stock_games"] = [e["game"] for e in report["games"] if e["min_houses"] == 0]
    report["total_decisions_checked"] = sum(e["decisions_checked"] for e in report["games"])
    report["total_decision_mismatches"] = sum(e["decision_mismatches"] for e in report["games"])
    report["all_agree_with_astra"] = all(e["agrees_with_astra"] for e in report["games"])
    report["all_agree_with_sol"] = all(e["agrees_with_sol"] for e in report["games"])
    report["sol_zero_stock_games"] = sorted(sol_zero)
    report["sources"] = {"astra_audit_sha256": sha256(ASTRA), "sol_audit_sha256": sha256(SOL), "script_sha256": sha256(Path(__file__))}
    g7 = next(g for g in games if g["game"] == 7)
    report["g7_d339_seq"] = g7_lock_seq(g7["run_dir"])
    with (OUT / "house_stock_series.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    json.dump(report, (OUT / "house_stock_report.json").open("w"), indent=1)

    # figure: 5 seed blocks x 4 rotations, houses remaining vs turn
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    seeds = []
    for g in games:
        if g["rec"]["seed"] not in seeds:
            seeds.append(g["rec"]["seed"])
    fig, axes = plt.subplots(5, 4, figsize=(11, 10), sharey=True)
    for g in games:
        r = seeds.index(g["rec"]["seed"])
        c = (g["game"] - 1) % 4
        ax = axes[r][c]
        turns = [s[1] for s in g["rec"]["series"]]
        houses = [s[2] for s in g["rec"]["series"]]
        zero = g["rec"]["min_houses"] == 0
        ax.step(turns, houses, where="post", color="#b2182b" if zero else "#4d4d4d", lw=1.4)
        ax.set_ylim(-1, 33)
        ax.set_title(f"G{g['game']}  seed {g['rec']['seed']}  min {g['rec']['min_houses']}", fontsize=8)
        ax.axhline(4, color="#999999", lw=0.6, ls=":")
        if g["game"] == 7 and report["g7_d339_seq"]:
            lock_turn = next(s[1] for s in g["rec"]["series"] if s[0] >= report["g7_d339_seq"]) if any(s[0] >= report["g7_d339_seq"] for s in g["rec"]["series"]) else g["rec"]["final_turn"]
            ax.axvline(lock_turn, color="#2166ac", lw=0.9, ls="--")
            ax.text(lock_turn, 30, " d339 lock", fontsize=7, color="#2166ac")
        ax.tick_params(labelsize=7)
    for ax in axes[-1]:
        ax.set_xlabel("global turn index", fontsize=8)
    for row in axes:
        row[0].set_ylabel("bank houses", fontsize=8)
    fig.suptitle("Bank house stock by game (rows: seed blocks; columns: rotations). Red = reached zero; dotted = 4 houses needed to sell a hotel", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUT / "house_stock_grid.png", dpi=160)
    print(json.dumps({k: v for k, v in report.items() if k != "games"}, indent=1))
    for e in report["games"]:
        print(e["game"], "min", e["min_houses"], "first_zero_turn", e["first_zero_turn"], "checked", e["decisions_checked"], "mismatch", e["decision_mismatches"], "astra", e["astra_event_minimum_bank_houses"], "sol_zero", e["sol_zero_stock_game"], "zero-decisions", e["decisions_with_zero_houses"])


if __name__ == "__main__":
    main()
