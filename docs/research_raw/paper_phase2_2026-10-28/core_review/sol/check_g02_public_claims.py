"""Original event checks for G02-C008 and G02-C011 after semantic reading."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def main():
    first = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_packets/game-02-part-001.jsonl"
    packet = json.loads(first.read_text().splitlines()[0])
    event_file = ROOT / packet["source_run"] / "events.jsonl"
    events = [json.loads(line) for line in event_file.read_text().splitlines()]
    light_blue = [event for event in events if event["type"] == "RENT_PAID" and event["payload"]["space_index"] in [6, 8, 9]]
    opus_receipts = [event for event in light_blue if event["payload"]["to_player_id"] == "p4"]
    after_first_build = [event for event in opus_receipts if event["seq"] > 943]
    assert not after_first_build
    assert [event["payload"]["amount"] for event in opus_receipts] == [6, 12, 16]
    moves = [event for event in events if event["type"] == "PLAYER_MOVED" and event["actor"].get("player_id") == "p4" and 978 < event["seq"] < 1465]
    assert [event["payload"]["to"] for event in moves] == [12, 19, 25, 28, 37]
    finance = [event for event in events if 1348 <= event["seq"] <= 1376 and event["type"] in ["CASH_CHANGED", "PROPERTY_MORTGAGED", "PROPERTY_UNMORTGAGED"]]
    assert 435 - 100 - 26 == 309
    assert 309 + 120 - 143 - 143 == 143
    result = {
        "source": str(event_file.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(event_file.read_bytes()).hexdigest(),
        "all_light_blue_paid_rents": light_blue,
        "opus_light_blue_rent_before_development": sum(event["payload"]["amount"] for event in opus_receipts),
        "opus_developed_light_blue_paid_rent": 0,
        "moves_between_end_of_eight_house_build_and_bankruptcy": moves,
        "yellow_finance_events": finance,
        "yellow_cash_after_trade_and_fee": 309,
        "yellow_cash_after_illinois_mortgage_and_both_redemptions": 143,
        "limits": "Paid-rent accounting and original move chronology only. No optimal-strategy or winner counterfactual; terminal estate value remains separate.",
    }
    (HERE / "g02_public_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["opus_light_blue_rent_before_development", "opus_developed_light_blue_paid_rent", "yellow_cash_after_trade_and_fee", "yellow_cash_after_illinois_mortgage_and_both_redemptions"]}, indent=2))


if __name__ == "__main__":
    main()
