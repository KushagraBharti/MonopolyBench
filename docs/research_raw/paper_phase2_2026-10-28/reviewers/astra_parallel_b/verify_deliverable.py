"""Verify saved review coverage against originals; this does not establish reading."""
import hashlib
import json
import re
from pathlib import Path

out = Path(__file__).resolve().parent
repo = next(p for p in out.parents if (p / "contracts").is_dir())
cache = {}
report = {
    "scope": "games 7 through 13",
    "method": "Structural provenance audit after manually recorded complete reading. Parsing and hash checks do not establish semantic reading.",
    "excluded": "No semantic_review values are accessed or reported.",
    "games": [],
}
for game in range(7, 14):
    directory = out / f"game-{game:02d}"
    progress = json.loads((directory / "progress.json").read_text())
    manifest = json.loads((out.parent.parent / "full_review" / f"game-{game:02d}" / "manifest.json").read_text())
    rows = [json.loads(line) for line in (directory / "coverage.jsonl").read_text().splitlines()]
    assert progress["complete"] and progress["last_page_read"] == len(manifest["pages"])
    assert len(rows) == progress["decisions_total"] == len(manifest["sources"])
    assert len({row["decision_id"] for row in rows}) == len(rows)
    attempts = 0
    for row, source in zip(rows, manifest["sources"]):
        assert row["status"] == "read_all_available_channels"
        assert row["source"] == source
        path = repo / source["packet"]
        if path not in cache:
            cache[path] = path.read_bytes().splitlines(keepends=True)
        raw = cache[path][source["packet_line"] - 1]
        assert source["source_line_sha256"] in {
            hashlib.sha256(raw).hexdigest(), hashlib.sha256(raw.rstrip(b"\r\n")).hexdigest()
        }
        packet = json.loads(raw)
        assert row["decision_id"] == packet["decision_id"] == source["decision_id"]
        assert row["applied_action"] == packet["applied_action_record"]["action"]
        assert row["turn"] == packet["turn_index"] and row["player"] == packet["player_id"]
        events = packet["canonical_event_segment"]
        assert row["event_range"] == [events[0]["seq"], events[-1]["seq"]]
        assert len(row["attempts"]) == len(packet["attempts"])
        for recorded, original in zip(row["attempts"], packet["attempts"]):
            assert recorded["index"] == original["attempt_index_zero_based"]
            assert recorded["outcome"] == original["outcome"]
            assert recorded["condition"] == original["response_condition"]
            assert recorded["validation_errors"] == original["validation_errors"]
        attempts += len(row["attempts"])
    assert attempts == progress["attempts_read"]
    links = 0
    candidates = (directory / "candidates.md").read_text()
    for document in (directory / "notes.md", directory / "candidates.md"):
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
            if "://" not in target:
                assert (document.parent / target.split("#")[0]).resolve().exists(), (document, target)
                links += 1
    report["games"].append({
        "game": game, "complete": True, "pages_read": progress["last_page_read"],
        "decisions": len(rows), "attempts": attempts, "all_source_hashes_match": True,
        "all_applied_actions_match": True, "all_event_ranges_match": True,
        "all_attempt_indexes_outcomes_conditions_validation_errors_match": True,
        "ranked_findings": len(re.findall(r"^\d+\. ", candidates, re.M)),
        "local_document_links_checked": links,
        "final_event": rows[-1]["event_range"][-1],
    })
report["totals"] = {
    key: sum(game[key] for game in report["games"])
    for key in ("pages_read", "decisions", "attempts", "ranked_findings", "local_document_links_checked")
}
assert report["totals"]["decisions"] == 2074
assert report["totals"]["attempts"] == 2696
assert report["totals"]["pages_read"] == 823
(out / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(report, ensure_ascii=False, indent=2))
