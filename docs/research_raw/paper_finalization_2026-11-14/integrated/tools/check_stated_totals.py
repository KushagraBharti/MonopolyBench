"""Reproduce a numeric-presence description from saved first responses.

This checks written numerals, not correctness of an entire response or reasoning.
No engine, policy, search, replay or model is invoked.
"""
import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in HERE.parents if (p / "contracts/data/board.json").exists())
source = HERE / "data/episodes_188.json"
entries = json.loads(source.read_text())
pattern = re.compile(r"(?<![\w.])\$?\s?(\d{1,3}(?:,\d{3})+|\d+)(?![\w]|\.\d)")
rows = []
source_hashes = {}
for entry in entries:
    if entry["Ustar"] >= entry["debt"]:
        continue
    options = entry["options"]
    forced = not (options["mortgageable_space_keys"] or options["sellable_building_space_keys"])
    texts = {"note": entry["applied_action"].get("private_thought"),
             "provider": entry["provider_reasoning"], "content": entry["assistant_content"]}
    c, d, u = entry["cash"], entry["debt"], entry["Ustar"]
    candidates = {u, u - c, d - u} - {0, c, d, d - c}
    hits = []
    for channel, text in texts.items():
        if not text:
            continue
        for match in pattern.finditer(text):
            number = int(match.group(1).replace(",", ""))
            if number in candidates:
                hits.append(dict(channel=channel, number=number, span=list(match.span()),
                                 context=text[max(0, match.start()-100):match.end()+100],
                                 field_sha256=hashlib.sha256(text.encode()).hexdigest()))
    source_path = entry["source"]
    if source_path not in source_hashes:
        source_hashes[source_path] = hashlib.sha256((ROOT/source_path).read_bytes()).hexdigest()
    rows.append(dict(game=entry["game"], decision=entry["decision"], model=entry["model"],
                     cash=c, debt=d, full_bound=u, listed_total=entry["U0"],
                     forced_menu=forced, has_match=bool(hits), matches=hits,
                     first_matching_channel=hits[0]["channel"] if hits else None,
                     source=source_path, source_sha256=source_hashes[source_path]))
choices = [r for r in rows if not r["forced_menu"]]
assert len(rows) == 56 and len(choices) == 48
assert sum(r["has_match"] for r in choices) == 43
channels = collections.Counter(r["first_matching_channel"] for r in choices if r["has_match"])
assert channels == {"note": 30, "provider": 13}
counts = collections.defaultdict(lambda: [0, 0])
for row in choices:
    counts[row["model"]][0] += 1
    counts[row["model"]][1] += row["has_match"]
output = dict(
    definition="Presence of a numeral equal to the full bound, total asset proceeds, or final deficit; excludes cash, debt, initial shortfall and zero.",
    channel_order=["note", "provider", "content"], rows=rows,
    population_with_financing_option=48, matches=43, first_matching_channels=dict(channels),
    per_configuration=dict(counts), input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    limitation="Numeric presence only. Does not validate other arithmetic, imply a complete budget, or identify how a figure was obtained."
)
(HERE / "data/stated_totals_check.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({k:output[k] for k in ["population_with_financing_option", "matches", "first_matching_channels", "per_configuration"]}, indent=2))
