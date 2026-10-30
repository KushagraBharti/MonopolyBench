"""Exact reference probabilities for the 20-game outcome grid (descriptive aid).

Usage: python3 -I outcome_dependence.py <cohort_overview.json> <out.json>
Computes, from canonical winners and seats, the block x rotation grid and exact
tail probabilities under simple i.i.d. reference nulls. These nulls IGNORE the
shared-dice block dependence and multiplicity, so they are calibration aids for
captions ("not distinguishable from chance even before accounting for
dependence"), not tests supporting a ranking or a seat effect.
"""
import itertools
import json
import sys
from math import comb

SHORT = {"anthropic/claude-opus-5.5": "Opus", "openai/gpt-6.1-sol": "Sol",
         "google/gemini-4-argon": "Argon", "x-ai/grok-4.7": "Grok"}


def binom_tail(n, p, k):
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def p_max_at_least(n, m, k):
    """P(max count over m equiprobable categories >= k) for n i.i.d. draws, exact."""
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def ways_all_below(n_left, cats_left):
        # number of sequences of length n_left over cats_left categories with every count < k
        if cats_left == 0:
            return 1 if n_left == 0 else 0
        total = 0
        for c in range(0, min(k - 1, n_left) + 1):
            total += comb(n_left, c) * ways_all_below(n_left - c, cats_left - 1)
        return total
    return 1 - ways_all_below(n, m) / m**n


def main():
    d = json.load(open(sys.argv[1]))
    grid = []
    for i, g in enumerate(d["games"], 1):
        a = {x["player_id"]: x for x in g["seat_assignment"]["assignments"]}
        w = a[g["winner_player_id"]]
        order = [SHORT[x["openrouter_model_id"]] for x in sorted(g["seat_assignment"]["assignments"], key=lambda x: x["turn_order"])]
        grid.append({"game": i, "seed": g["seed"], "turns": g["turns"], "winner_model": SHORT[w["openrouter_model_id"]],
                     "winner_turn_order": w["turn_order"], "turn_order_models": order,
                     "summary_sha256": g["summary_sha256"], "seat_assignment_sha256": g["seat_assignment_sha256"]})
    wins = {}
    seats = {}
    for r in grid:
        wins[r["winner_model"]] = wins.get(r["winner_model"], 0) + 1
        seats[r["winner_turn_order"]] = seats.get(r["winner_turn_order"], 0) + 1
    blocks = {}
    for r in grid:
        b = blocks.setdefault(str(r["seed"]), {"games": [], "winner_models": [], "winner_seats": []})
        b["games"].append(r["game"]); b["winner_models"].append(r["winner_model"]); b["winner_seats"].append(r["winner_turn_order"])
    for b in blocks.values():
        b["distinct_winner_models"] = len(set(b["winner_models"]))
        b["distinct_winner_seats"] = len(set(b["winner_seats"]))
    n = len(grid)
    ref = {
        "P(a prespecified model wins >= 8 of 20 | uniform iid)": binom_tail(n, 0.25, 8),
        "P(any model wins >= 8 of 20 | uniform iid)": p_max_at_least(n, 4, 8),
        "P(turn orders 0 or 1 win >= 14 of 20 | uniform iid seats)": binom_tail(n, 0.5, 14),
        "P(some seat or model sweeps a 4-game block | uniform iid), per block": 4 * 0.25**4,
    }
    out = {"grid": grid, "wins_by_model": wins, "wins_by_turn_order": seats, "blocks": blocks,
           "reference_probabilities_iid": ref,
           "caveat": "i.i.d. nulls ignore shared-dice blocks, endogenous opportunities and multiplicity; descriptive calibration only"}
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    print(json.dumps({"wins": wins, "seats": seats, "ref": ref,
                      "blocks": {k: (v["winner_models"], v["winner_seats"]) for k, v in blocks.items()}}, indent=1))


if __name__ == "__main__":
    main()
