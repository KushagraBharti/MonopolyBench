"""Original-artifact checks for numerical and temporal public-catalog claims."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    packets = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_packets"
    units = {}
    for path in sorted(packets.glob("game-01-part-*.jsonl")):
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            row = json.loads(line)
            units[int(row["decision_id"].rsplit("-", 1)[-1])] = (row, str(path.relative_to(ROOT)), line_number, hashlib.sha256(line.encode()).hexdigest())
    run = ROOT / units[0][0]["source_run"]
    events = rows(run / "events.jsonl")
    rents = [event for event in events if event["type"] == "RENT_PAID" and event["payload"]["from_player_id"] == "p1" and event["payload"]["to_player_id"] == "p3"]
    hotel_rents = [event for event in rents if event["payload"]["space_index"] in [6, 8, 9]]
    assert sum(event["payload"]["amount"] for event in rents) == 1748
    assert sum(event["payload"]["amount"] for event in hotel_rents) == 1700
    speech_order = [{"decision_id": units[n][0]["decision_id"], "action": units[n][0]["applied_action_record"]["action"], "source": list(units[n][1:])} for n in [181, 184, 185, 186]]
    assert [row["action"]["action"] for row in speech_order] == ["bid_auction", "bid_auction", "bid_auction", "drop_out"]
    assert "only worth $25" in speech_order[2]["action"]["public_message"]
    build_turns = {str(n): units[n][0]["turn_index"] for n in [118, 128, 129]}
    assert build_turns == {"118": 40, "128": 43, "129": 43}
    rejected_offer = units[293][0]["applied_action_record"]["action"]
    rejection = units[294][0]["applied_action_record"]["action"]
    assert rejected_offer["action"] == "propose_trade" and rejection["action"] == "reject_trade"
    assert "PACIFIC_AVENUE" in rejected_offer["args"]["offer"]["properties"]
    public_catalog = rows(HERE.parent / "candidate_catalog.jsonl")
    selected = {row["catalog_id"]: row for row in public_catalog if row["catalog_id"] in ["public-G01-C009", "public-G01-C012", "public-G01-C013", "public-G01-C017"]}
    report = {
        "rent_paid": rents, "total_rent_paid_opus_to_argon": 1748,
        "hotel_rent_paid_opus_to_argon": 1700,
        "unpaid_final_hotel_debt": 550, "terminal_cash_transfer": 118,
        "speech_order": speech_order,
        "set_completion_and_build_global_turns": build_turns,
        "completion_condition_negative": {"offer": rejected_offer, "rejection": rejection,
                                           "pre_offer_others": units[293][0]["initial_prompt"]["payload"]["game_state"]["others"]},
        "source_event_file": str((run / "events.jsonl").relative_to(ROOT)),
        "source_event_sha256": hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest(),
        "catalog_entries": selected,
        "limits": "Reference/arithmetic checks, not complete semantic review of every surrounding bundle. Source entry verdicts preserve broader unchecked claims.",
    }
    (HERE / "g01_public_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"total_rent_paid": 1748, "hotel_rent_paid": 1700,
                      "speech_decisions": [181, 184, 185, 186], "completion_and_build_turns": build_turns,
                      "rejected_completion_offer": rejected_offer, "rejection": rejection}, indent=2))


if __name__ == "__main__":
    main()
