"""Check integrated finance selections and three quotations against saved records."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in HERE.parents if (p / "contracts/data/board.json").exists())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
games = json.loads((HERE / "data/game_map.json").read_text())
entries = json.loads((HERE / "data/episodes_188.json").read_text())
episodes = json.loads((HERE / "data/liquidation_episodes.json").read_text())
episodes = {(r["game"], r["first_decision"]): r for r in episodes}
cache = {}


def decisions(game):
    if game not in cache:
        path = ROOT / games[str(game)] / "decisions.jsonl"
        cache[game] = (path, [json.loads(s) for s in path.read_text().splitlines()])
    return cache[game]


rows = []
for entry in entries:
    if entry["cash"] + entry["M0"] < entry["debt"] or entry["S"] <= 0:
        continue
    episode = episodes[entry["game"], entry["decision"]]
    path, records = decisions(entry["game"])
    resolved = {r["decision_id"]: r for r in records if r["phase"] == "decision_resolved"}
    actions = [resolved[d]["final_action"]["action"] for d in episode["decisions"]]
    assert actions == episode["actions"] == entry["actions"]
    assert entry["outcome"] == "paid"
    rows.append(dict(game=entry["game"], decision=entry["decision"],
                     cash=entry["cash"], debt=entry["debt"],
                     initially_available_mortgages=entry["M0"],
                     building_salvage=entry["S"], actions=actions,
                     sold_buildings="sell_houses_or_hotel" in actions,
                     source=str(path.relative_to(ROOT)), source_sha256=sha(path)))
assert len(rows) == 30 and sum(not r["sold_buildings"] for r in rows) == 28
assert {(r["game"], r["decision"]) for r in rows if r["sold_buildings"]} == {(12, 282), (18, 372)}
(HERE / "data/development_preservation.json").write_text(json.dumps({
    "population": "All financing entries with buildings and cash plus initially listed mortgages at least the debt.",
    "rows": rows, "no_sale": 28, "total": 30,
    "scope": "Observed action choices, not a cost-optimality claim or policy evaluation."
}, indent=2) + "\n")

registry = json.loads((HERE / "data/finalization_quote_registry.json").read_text())
quotes, latex = [], []
for q in registry:
    path, records = decisions(q["game"])
    matches = [(i, r) for i, r in enumerate(records, 1)
               if r["phase"] == "decision_resolved" and r["decision_id"].endswith(f'-{q["decision"]:06d}')]
    assert len(matches) == 1
    line, record = matches[0]
    field = record["final_action"][q["field"]]
    start = field.index(q["text"])
    assert field.count(q["text"]) == 1
    if q["field"] == "public_message":
        following = next(r for r in records if r["phase"] == "decision_started"
                         and r["decision_id"].endswith(f'-{q["decision"] + 1:06d}'))
        assert q["text"] in json.dumps(following["prompt_payload"], ensure_ascii=False)
    quotes.append(dict(id=q["id"], source=str(path.relative_to(ROOT)),
                       source_sha256=sha(path), jsonl_line_1based=line,
                       json_pointer="/final_action/" + q["field"],
                       field_sha256=hashlib.sha256(field.encode()).hexdigest(),
                       spans=[dict(span=[start, start + len(q["text"])], text=q["text"]) ]))
    escaped = q["text"].replace("$", r"\$").replace("%", r"\%").replace("&", r"\&")
    latex.append(r"\DeclareTranscriptQuote{%s}{%s}{%s}" % (q["id"], q["label"], escaped))
(HERE / "data/finalization_quote_manifest.json").write_text(json.dumps({"quotes": quotes}, indent=2) + "\n")
(HERE / "sections/finalization_quotes.tex").write_text("\n".join(latex) + "\n")
print("Source-checked 30 financing selections (28 without sales) and 3 G7 quotations.")
