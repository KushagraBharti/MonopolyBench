"""Check Opus's ten new spans and all six public messages in original records.

This reads preserved source fields and recipient requests. It does not query a
model, replay a game, or execute an alternative action.
"""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[2]
MANIFEST = BASE / "full_drafts/opus/data/opus_quote_manifest.json"
offers = json.loads((BASE / "data/agenda_offers.json").read_text())
by_decision = {r["decision_id"]: r for r in offers}
cache = {}
checked = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strings(value, path=""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, f"{path}/{index}")
    elif isinstance(value, str):
        yield path, value


for quote in json.loads(MANIFEST.read_text())["quotes"]:
    source = REPO / quote["source"]
    if source not in cache:
        cache[source] = [json.loads(line) for line in source.read_text().splitlines()]
    assert sha(source.read_bytes()) == quote["source_sha256"]
    row = cache[source][quote["jsonl_line_1based"] - 1]
    assert row["decision_id"] == quote["decision_id"]
    field = row
    for key in quote["json_pointer"].strip("/").split("/"):
        field = field[key]
    assert sha(field.encode()) == quote["field_sha256"]
    start, end = quote["span_codepoints"]
    assert field[start:end] == quote["excerpt"]
    check = {"id": quote["id"], "exact_source_span": True}
    if quote["json_pointer"].endswith("public_message"):
        old_offer = by_decision[quote["decision_id"]]
        recipient = old_offer["author"]
        after = cache[source][quote["jsonl_line_1based"]:]
        request = next(r for r in after if r["phase"] == "decision_started" and r["player_id"] == recipient)
        paths = [path for path, text in strings(request["prompt_payload"], "/prompt_payload") if field in text]
        assert paths, quote["id"]
        check.update({"recipient": recipient, "next_request": request["decision_id"],
                      "full_public_message_present": True, "field_paths": paths})
    checked.append(check)

report = {
    "scope": "Peer-informed original-field and recipient-request check, not belief, reliance, or tactic efficacy.",
    "manifest_sha256": sha(MANIFEST.read_bytes()),
    "script_sha256": sha(Path(__file__).read_bytes()),
    "source_files": {str(p.relative_to(REPO)): sha(p.read_bytes()) for p in cache},
    "quotes_checked": len(checked),
    "public_messages_checked": sum("next_request" in r for r in checked),
    "checks": checked,
    "interpretive_correction": "G2 d124's private note says $520 is enough for nine yellow houses. Nine at $150 each cost $1,350. $520 alone buys three, so the note's immediate cash-based building claim is false. This does not determine all collateral-accessible financing or the optimal trade price.",
}
assert report["quotes_checked"] == 10
assert report["public_messages_checked"] == 6
(HERE / "new_quote_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "checks"}, indent=2))
