"""Build the outcome-grid exhibit (CSV + faceted SVG + provenance) from outcome_dependence.json.

Usage: python3 -I build_outcome_grid.py <outcome_dependence.json> <out_dir>

Form: one small-multiple panel per configured agent (alphabetical, no ranking
order). Rows = seed blocks, columns = cyclic rotation within the block. Every
cell shows that agent's turn order in that game; a filled cell means that agent
won. One hue only (four categorical hues fail all-pairs separation in a grid),
so identity comes from the panel title, not colour. Native <title> tooltips give
per-cell details.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

MODELS = ["Argon", "Grok", "Opus", "Sol"]
LABEL = {"Argon": "Gemini 4 Argon", "Grok": "Grok 4.7 (tool_choice=required)",
         "Opus": "Claude Opus 5.5 (action-only after refusal)", "Sol": "GPT-6.1 Sol"}


def main():
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    d = json.loads(src.read_text())
    grid = d["grid"]
    # semantic checks
    assert len(grid) == 20
    blocks = []
    for r in grid:
        if r["seed"] not in blocks:
            blocks.append(r["seed"])
    assert len(blocks) == 5
    wins = {m: sum(r["winner_model"] == m for r in grid) for m in MODELS}
    assert wins == {"Argon": 7, "Grok": 2, "Opus": 3, "Sol": 8}, wins
    seat_wins = {t: sum(r["winner_turn_order"] == t for r in grid) for t in range(4)}
    assert seat_wins == {0: 7, 1: 7, 2: 3, 3: 3}, seat_wins
    for b in blocks:
        rows = [r for r in grid if r["seed"] == b]
        assert len(rows) == 4
        for m in MODELS:  # each model occupies each turn order once per block
            assert sorted(r["turn_order_models"].index(m) for r in rows) == [0, 1, 2, 3]

    # CSV (table view)
    with open(out / "outcome_grid.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["game", "seed_block", "rotation_in_block", "turns", "winner_model", "winner_turn_order",
                    "turn_order_0", "turn_order_1", "turn_order_2", "turn_order_3"])
        for r in grid:
            rows = [x for x in grid if x["seed"] == r["seed"]]
            rot = [x["game"] for x in rows].index(r["game"])
            w.writerow([r["game"], r["seed"], rot, r["turns"], r["winner_model"], r["winner_turn_order"], *r["turn_order_models"]])

    # SVG: 2 x 2 facet layout
    cell, gap = 44, 4
    panel_w = 4 * cell + 3 * gap
    panel_h = 5 * cell + 4 * gap
    left, top = 150, 104
    col_gap, row_gap = 40, 96
    W = left + 2 * panel_w + col_gap + 24
    bottom = top + 34 + 2 * panel_h + row_gap
    H = bottom + 128
    SUB = {"Argon": "Gemini 4 Argon", "Grok": "Grok 4.7 · tool_choice=required",
           "Opus": "Claude Opus 5.5 · action-only after refusal", "Sol": "GPT-6.1 Sol"}
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, Helvetica, Arial, sans-serif" role="img" aria-labelledby="t d">')
    # Seats are one-based (seat k = player p_k = turn order k-1), matching Astra's exhibits.
    s.append('<title id="t">Winner of each game by seed block and rotation, one panel per configured agent</title>')
    s.append('<desc id="d">Filled cells mark games won by the panel\'s agent. Every cell shows that agent\'s seat (1-4) in that game. Twenty games, five shared-dice seed blocks, four cyclic rotations.</desc>')
    s.append('<style>.viz{--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#6f6e69;--grid:#d9d8d3;--win:#2a78d6;--onwin:#ffffff}'
             '@media (prefers-color-scheme: dark){.viz{--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#a3a29b;--grid:#3a3a37;--win:#3987e5;--onwin:#0b0b0b}}'
             '.bg{fill:var(--surface)}.t1{fill:var(--ink);font-size:16px;font-weight:600}.t2{fill:var(--ink2);font-size:12.5px}'
             '.t3{fill:var(--muted);font-size:11.5px}.empty{fill:var(--surface);stroke:var(--grid);stroke-width:1}'
             '.won{fill:var(--win)}.lw{fill:var(--onwin);font-size:12px;font-weight:600}.le{fill:var(--ink2);font-size:12px}'
             'g.c:hover rect{stroke:var(--ink);stroke-width:2}</style>')
    s.append('<g class="viz">')
    s.append(f'<rect class="bg" x="0" y="0" width="{W}" height="{H}"/>')
    s.append('<text class="t1" x="20" y="30">Who won each game: five seed blocks × four cyclic rotations</text>')
    s.append('<text class="t2" x="20" y="50">Filled cell = that agent won. Label = that agent\'s seat in the game (seat 1 moves first).</text>')
    s.append('<text class="t2" x="20" y="67">Rows share raw dice streams; opportunities still diverge after the first differing decision.</text>')
    for pi, m in enumerate(MODELS):
        pc, pr = pi % 2, pi // 2
        x0 = left + pc * (panel_w + col_gap)
        y0 = top + pr * (panel_h + row_gap) + 34
        s.append(f'<text class="t1" x="{x0}" y="{y0 - 22}">{m} · {wins[m]} wins</text>')
        s.append(f'<text class="t3" x="{x0}" y="{y0 - 7}">{SUB[m]}</text>')
        for bi, b in enumerate(blocks):
            rows = [r for r in grid if r["seed"] == b]
            y = y0 + bi * (cell + gap)
            if pc == 0:
                s.append(f'<text class="t2" x="20" y="{y + cell / 2 - 2}">Games {rows[0]["game"]}–{rows[-1]["game"]}</text>')
                s.append(f'<text class="t3" x="20" y="{y + cell / 2 + 13}">seed {b}</text>')
            for ci, r in enumerate(rows):
                x = x0 + ci * (cell + gap)
                t = r["turn_order_models"].index(m)
                won = r["winner_model"] == m
                tip = (f'Game {r["game"]} (seed {b}, rotation {ci}), {r["turns"]} turns. {m} in seat {t + 1}. '
                       f'Winner: {r["winner_model"]} from seat {r["winner_turn_order"] + 1}.')
                s.append(f'<g class="c"><title>{tip}</title>')
                s.append(f'<rect class="{"won" if won else "empty"}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4"/>')
                s.append(f'<text class="{"lw" if won else "le"}" x="{x + cell / 2}" y="{y + cell / 2 + 4}" text-anchor="middle">S{t + 1}</text></g>')
        for ci in range(4):
            s.append(f'<text class="t3" x="{x0 + ci * (cell + gap) + cell / 2}" y="{y0 + panel_h + 14}" text-anchor="middle">r{ci}</text>')
    yb = bottom + 50
    sw = ", ".join(f"seat {t + 1}: {seat_wins[t]}" for t in range(4))
    s.append(f'<text class="t2" x="20" y="{yb}">Wins by winner\'s seat: {sw}. Columns r0–r3 = rotations within a block.</text>')
    s.append(f'<text class="t3" x="20" y="{yb + 19}">Reference i.i.d. uniform nulls (ignore block dependence): P(prespecified agent ≥ 8/20) = 0.10;</text>')
    s.append(f'<text class="t3" x="20" y="{yb + 35}">P(any agent ≥ 8/20) = 0.40; P(seat 1 or 2 wins ≥ 14/20) = 0.058. No ranking or seat effect is established.</text>')
    s.append(f'<text class="t3" x="20" y="{yb + 51}">Source: phase3/opus/outcome_dependence.json (run/summary.json, seat_assignment.json, run_config.json).</text>')
    s.append('</g></svg>')
    (out / "outcome_grid.svg").write_text("\n".join(s))

    prov = {
        "exhibit": ["outcome_grid.svg", "outcome_grid.csv"],
        "inputs": {str(src): hashlib.sha256(src.read_bytes()).hexdigest()},
        "upstream": "outcome_dependence.json records per-game summary.json and seat_assignment.json sha256",
        "script": {"path": "scripts/build_outcome_grid.py", "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "checks_passed": ["20 games", "5 blocks x 4 rotations", "wins Argon 7 Grok 2 Opus 3 Sol 8",
                          "turn-order wins 7/7/3/3", "each agent occupies each turn order once per block"],
        "form_note": "Faceted single-hue grid: four categorical hues fail all-pairs separation (validator), so identity is carried by panel titles.",
        "date": "2026-10-29",
    }
    (out / "outcome_grid.provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
