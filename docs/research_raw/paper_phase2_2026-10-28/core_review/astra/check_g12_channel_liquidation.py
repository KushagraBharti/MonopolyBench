"""Peer-nominated G12 elimination, checked against original response and engine.

The local branches stop when the existing debt is paid. They do not reconstruct
an intended action or establish which interface component produced a mismatch.
"""

import hashlib
import json
from pathlib import Path

from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    unit = next(u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
                if u["game"] == 12 and u["decision_id"].endswith("000249"))
    path = ROOT / unit["packet"]
    packet = rows(path)[unit["packet_line"] - 1]
    run = ROOT / packet["source_run"]
    message = packet["attempts"][0]["raw_response"]["choices"][0]["message"]
    content = json.loads(message["content"])
    actual = packet["applied_action_record"]["action"]
    assert content["name"] == "sell_houses_or_hotel"
    assert actual["action"] == "declare_bankruptcy"
    assert "bankruptcy is wrong" in actual["private_thought"]
    assert "yields $393 total" in message["reasoning"]

    # Even the content's two-house sale is legal at this exact prefix.
    engine, decision = restore(run, packet["decision_id"])
    initial = engine.get_snapshot()
    decision, initial_sale = apply(engine, decision, content["name"],
                                  {"sell_plan": content["parameters"]["sell_plan"]})
    actor = next(p for p in engine.state.players if p.player_id == actual.get("player_id", "p1"))
    assert actor.cash == 143 and not actor.bankrupt
    assert [engine.state.board[i].houses for i in (11, 13, 14)] == [2, 2, 1]
    steps = [initial_sale]
    for key in ("ST_CHARLES_PLACE", "STATES_AVENUE", "ST_CHARLES_PLACE"):
        decision, result = apply(engine, decision, "sell_houses_or_hotel",
                                 {"sell_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}]})
        steps.append(result)
    assert actor.cash == 43 and not actor.bankrupt
    assert [engine.state.board[i].houses for i in (11, 13, 14)] == [0, 1, 1]
    paid = [e for s in steps for e in s["events"] if e["type"] == "RENT_PAID"]
    assert len(paid) == 1 and paid[0]["payload"]["amount"] == 250
    assert not any(e["type"] == "PROPERTY_MORTGAGED" for s in steps for e in s["events"])
    report = {
        "source": unit, "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "peer_provenance": "Sol nominated the mechanism and the one-house sequence before this independent implementation.",
        "original_action": actual, "original_content": content,
        "returned_reasoning": message["reasoning"],
        "initial": initial, "legal_content_sale_and_continuation": steps,
        "finding": "Applied avoidable bankruptcy contradicts both the content action and the final recommendation inside its own applied note. Selling five houses suffices without any mortgage.",
        "qualifications": "The note contains intermediate errors, including an incorrect remaining-house count. Its final warning does not establish a complete or privileged internal belief. Attribution to model, provider or gateway remains unidentified. No later outcome simulated.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g12_channel_liquidation_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"original": actual["action"], "content_sale_legal": True,
                      "cash_after_payment": actor.cash, "remaining_houses": [0, 1, 1]}))


if __name__ == "__main__":
    main()
