"""Verify trade directions against G03-C001/C003 source-entry errors."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def main():
    sources = [("game-03-part-002.jsonl", 8), ("game-03-part-002.jsonl", 9), ("game-03-part-010.jsonl", 5)]
    extracted = []
    for name, number in sources:
        path = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_packets" / name
        line = path.read_text().splitlines()[number - 1]
        row = json.loads(line)
        extracted.append({"decision_id": row["decision_id"], "source": str(path.relative_to(ROOT)), "line": number,
                          "line_sha256": hashlib.sha256(line.encode()).hexdigest(), "applied": row["applied_action_record"],
                          "events": row["canonical_event_segment"]})
    offer = extracted[0]["applied"]["action"]["args"]
    assert offer["offer"]["cash"] == 250
    assert offer["offer"]["properties"] == ["BOARDWALK"]
    assert offer["request"]["properties"] == ["TENNESSEE_AVENUE"]
    raw = json.loads((ROOT / extracted[0]["source"]).read_text().splitlines()[7])
    event_path = ROOT / raw["source_run"] / "events.jsonl"
    events = [json.loads(line) for line in event_path.read_text().splitlines()]
    park = [e for e in events if e["type"] in ["PROPERTY_PURCHASED", "PROPERTY_TRANSFERRED"] and e["payload"].get("space_index") == 37]
    assert len(park) == 2
    assert park[0]["payload"]["player_id"] == "p4"
    assert park[1]["payload"]["from_player_id"] == "p4" and park[1]["payload"]["to_player_id"] == "p1"
    sale = [e for e in extracted[2]["events"] if e["type"] == "PROPERTY_TRANSFERRED"]
    assert any(e["payload"]["space_index"] == 26 and e["payload"]["from_player_id"] == "p4" and e["payload"]["to_player_id"] == "p3" for e in sale)
    result = {"sources": extracted, "park_acquisition_or_transfer_events": park,
              "event_source": str(event_path.relative_to(ROOT)), "event_sha256": hashlib.sha256(event_path.read_bytes()).hexdigest(),
              "corrections": ["Grok GIVES Boardwalk AND250 to Argon, receives Tennessee. It does not sell the deed for cash or acquire liquidity.",
                              "Grok never acquires Park Place in game3; Sol buys it and transfers it to Argon.",
                              "Opus RECEIVES Atlantic in d072, not gives it away as C003 follow-up says."],
              "limits": "Applied-flow reference checks only; full channel cause and future economic counterfactuals unresolved."}
    (HERE / "g03_public_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["corrections"], indent=2))


if __name__ == "__main__":
    main()
