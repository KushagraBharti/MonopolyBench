"""Cohort table, initiation counts and sensitivity cuts for the bargaining claims.

Sensitivity cuts (fresh arithmetic on rebuilt offers):
  * drop every thread whose opening proposal is a Grok received call that
    conflicts with its content (inherited conflict list, 139 selected
    conflicts; joined by decision id);
  * drop offers authored or received by Opus;
  * restrict to games 5-20 (Opus refusal share 1.0) and to games 1-4.
The cohort table is read from the raw cache and compared with the retained
t01_cohort.json.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"
RES = corpus.REPO / "docs/research_raw/paper_rewrite_2026-11-10/data/resolution_conditions.json"
T01 = corpus.REPO / "docs/research_raw/paper_rewrite_2026-11-10/integrated/data/t01_cohort.json"


def contrast(rows):
    a = [r for r in rows if r["accept_legal"] and r["opening"] and r["cell"] == "Author only"]
    n = [r for r in rows if r["accept_legal"] and r["opening"] and r["cell"] == "Neither"]
    ra = sum(r["response"] == "reject_trade" for r in a)
    rn = sum(r["response"] == "reject_trade" for r in n)
    return {"author_only": [ra, len(a)], "neither": [rn, len(n)],
            "diff_pp": round(100 * ra / len(a) - 100 * rn / len(n), 1) if a and n else None}


def main():
    D = corpus.build_cache()
    rows = json.loads((OUT / "offers_rebuilt.json").read_text())
    res = {}
    # cohort
    cohort = []
    for g, game in D["games"].items():
        w = game["winner"]
        cohort.append({"game": g, "block": (g - 1) // 4 + 1, "seed": game["seed"], "turns": game["turns"],
                       "winner": game["pmodel"][w], "winner_seat": game["seats"][w] + 1,
                       "seat_models": [game["pmodel"][p] for p in sorted(game["seats"], key=lambda p: game["seats"][p])],
                       "fingerprint": game["fingerprint"][:8]})
    t01 = json.loads(T01.read_text())
    res["cohort_matches_retained"] = all(c["winner"] == t["winner"] and c["winner_seat"] == t["winner_seat"] and c["turns"] == t["turns"] and c["seed"] == t["seed"]
                                         for c, t in zip(cohort, t01))
    res["cohort"] = cohort
    res["wins_by_model"] = Counter(c["winner"] for c in cohort)
    res["wins_by_seat"] = Counter(c["winner_seat"] for c in cohort)
    # thread initiation and authorship
    threads = {}
    for r in rows:
        if r["stage"] == 0:
            threads[r["thread"]] = D["games"][r["game"]]["pmodel"][r["initiator"]]
    res["threads_by_initiator"] = Counter(threads.values())
    res["offers_by_author"] = Counter(r["author_model"] for r in rows)
    res["settlements"] = sum(r["response"] == "accept_trade" for r in rows)
    res["settlements_by_cell"] = Counter(r["cell"] for r in rows if r["response"] == "accept_trade")
    # Grok conflict threads
    rc = json.loads(RES.read_text())
    conflict_ids = {c["decision_id"] for c in rc["selected_grok_conflicts"]}
    conflict_threads = set()
    for g, game in D["games"].items():
        for idx, d in game["decisions"].items():
            pass
    # map proposing decision -> thread: the offer of an opening row is emitted by the decision preceding the response
    # use events: TRADE_PROPOSED emitted within a conflicting decision's event range
    for g, game in D["games"].items():
        ranges = []
        for idx, d in game["decisions"].items():
            did = game["run"]  # placeholder
        runid = None
    by_game_seq = defaultdict(dict)
    for g, game in D["games"].items():
        run_prefix = None
        for idx, d in game["decisions"].items():
            res_ = d["res"]
            # decision ids in the conflict list are full ids; rebuild
        evs = game["events"]
        prop_seq_to_thread = {}
        n = 0
        for e in evs:
            if e["type"] == "TRADE_PROPOSED":
                n += 1
                prop_seq_to_thread[e["seq"]] = f"G{g:02d}-T{n:03d}"
        run_id = evs[0]["run_id"]
        for idx, d in game["decisions"].items():
            full = f"{run_id}-dec-{idx:06d}"
            if full in conflict_ids:
                for s in range(d["res"]["seq_start"], d["res"]["seq_end"] + 1):
                    if s in prop_seq_to_thread:
                        conflict_threads.add(prop_seq_to_thread[s])
    res["grok_conflict_opened_threads"] = len(conflict_threads)
    res["grok_conflict_opened_threads_settled"] = sum(1 for r in rows if r["thread"] in conflict_threads and r["response"] == "accept_trade")
    cuts = {
        "all": rows,
        "without_grok_conflict_threads": [r for r in rows if r["thread"] not in conflict_threads],
        "without_opus_as_author_or_recipient": [r for r in rows if r["author_model"] != "Opus" and r["recipient_model"] != "Opus"],
        "games_1_4": [r for r in rows if r["game"] <= 4],
        "games_5_20": [r for r in rows if r["game"] >= 5],
    }
    res["open_reject_sensitivity"] = {k: contrast(v) for k, v in cuts.items()}
    # concession sensitivity without Opus recipients
    B = json.loads((OUT / "bargaining.json").read_text())
    conc = B["concession_rows"]
    def cacc(xs, cell):
        ys = [x for x in xs if x["cell"] == cell]
        return [sum(x["response"] == "accept_trade" for x in ys), len(ys)]
    res["concession_sensitivity"] = {
        "all": {"author_only": cacc(conc, "Author only"), "neither": cacc(conc, "Neither")},
        "without_opus_recipient": {"author_only": cacc([x for x in conc if x["recipient_model"] != "Opus"], "Author only"),
                                   "neither": cacc([x for x in conc if x["recipient_model"] != "Opus"], "Neither")},
        "without_grok_conflict_threads": {"author_only": cacc([x for x in conc if x["thread"] not in conflict_threads], "Author only"),
                                          "neither": cacc([x for x in conc if x["thread"] not in conflict_threads], "Neither")},
    }
    res["resolution_conditions_sha256"] = corpus.sha256(RES)
    (OUT / "sensitivity.json").write_text(json.dumps(res, indent=1, default=dict))
    return res


if __name__ == "__main__":
    r = main()
    for k, v in r.items():
        if k != "cohort":
            print(k, json.dumps(v, default=dict))
