"""References for a delivered false premise accepted with explicit correction."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units

HERE = Path(__file__).resolve().parent


def main():
    game = units(6)
    sources = []
    for suffix in [19, 20, 21]:
        unit, source = game[suffix]
        sources.append({"suffix": suffix, **source, "applied": unit["applied_action_record"], "prompt": unit["initial_prompt"], "events": unit["canonical_event_segment"]})
    proposer, recipient = game[19][0], game[20][0]
    message = proposer["attempts"][0]["raw_response"]["choices"][0]["message"]
    content = json.loads(message["content"])
    assert content["name"] == "end_turn"
    assert message["tool_calls"][0]["function"]["name"] == "propose_trade"
    actual = proposer["applied_action_record"]["action"]
    assert actual["args"]["offer"]["cash"] == 400
    assert actual["args"]["request"]["properties"] == ["VERMONT_AVENUE"]
    note = recipient["applied_action_record"]["action"]["private_thought"]
    assert "opponent's claim about oranges is incorrect" in note
    memory = recipient["initial_prompt"]["payload"]["game_state"]["memory"]["public_timeline_last_20"]
    assert any(entry.get("message") == actual["public_message"] for entry in memory)
    events = recipient["canonical_event_segment"]
    assert any(event["type"] == "CASH_CHANGED" and event["payload"].get("player_id") == "p1" and event["payload"].get("delta") == 400 for event in events)
    assert len([event for event in events if event["type"] == "PROPERTY_TRANSFERRED"]) == 3
    report = {"sources": sources,
              "readable_proposer_channels": {"content": message["content"], "reasoning": message["reasoning"], "tool_calls": message["tool_calls"]},
              "claims": ["Grok falsely calls scattered p1holdings an orange monopoly and requests lightblueVermont tobreakit.",
                         "Receivedcontent and provider summaryfavorEND; appliedtoolproposes400plus2deeds, so notaconfirmedcoherentintentionaloverpaystrategy.",
                         "Recipient is actuallyexposed, explicitlyrejectsorangepremiseinprivate, andacceptsfavorabletrade. Settlementaloneisnotfalse-premisereliance.",
                         "Followingd021appliedprivatecorrectstheclassificationandcallsthetradebadoverpay; itsfullproviderbundlehasnotbeenreadhere."],
              "limits": "Complete originald019/d020semanticchannelsread; encryptedunavailable. d021appliedchronologyonly. No winnercounterfactual orknowledge/intentattribution.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g06_negative_case_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"source_refs": [{k: source[k] for k in ["suffix", "packet", "line", "sha256"]} for source in sources], "claims": report["claims"], "limits": report["limits"]}))


if __name__ == "__main__":
    main()
