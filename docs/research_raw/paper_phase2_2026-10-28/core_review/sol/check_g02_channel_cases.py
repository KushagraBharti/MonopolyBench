"""Preserve two complete original-bundle adjudications nominated by Astra.

Sol read all distinct available semantic fields and adjacent chronology before
writing these conclusions. Assertions check references and channel distinctions;
they do not substitute for semantic reading. Initial catalog labels stay intact.
"""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units

HERE = Path(__file__).resolve().parent


def main():
    game = units(2)
    sources = []
    for number in [61, 62, 63, 246, 247, 248]:
        unit, source = game[number]
        # Extractor semantic_review is not evidence and is deliberately omitted.
        sources.append({"suffix": number, **source,
                        "original": {k: v for k, v in unit.items() if k != "semantic_review"}})
    recognition = game[62][0]
    attempt = recognition["attempts"][0]
    message = attempt["raw_response"]["choices"][0]["message"]
    assert "trade for Ventnor went through" in attempt["assistant_content"]
    assert "trade actually went through" in message["reasoning"]
    assert "Ventnor trade went through" in recognition["applied_action_record"]["action"]["private_thought"]
    assert recognition["initial_prompt"]["payload"]["game_state"]["you"]["cash"] == 1181
    probe = game[247][0]
    received = probe["attempts"][0]
    assert '"end_turn"' in received["assistant_content"]
    assert "I will end the turn" in received["raw_response"]["choices"][0]["message"]["reasoning"]
    action = probe["applied_action_record"]["action"]
    assert action["action"] == "propose_trade" and "Probe only" in action["private_thought"]
    assert action["args"]["offer"] == action["args"]["request"] == {
        "cash": 0, "get_out_of_jail_cards": 0, "properties": []}
    assert game[248][0]["applied_action_record"]["action"]["action"] == "reject_trade"
    report = {
        "provenance": "Peer-nominated targets after initial catalog judgments; independently re-read complete available bundles at062/247. Adjacent decisions checked for applied chronology, not claimed as complete bundle readings.",
        "sources": sources,
        "conclusions": {
            "062": "Content, returned provider explanation and applied private explicitly recognize executed Ventnor trade. Public arithmetic correction does not deny execution.063 is public acknowledgment, not first documented recognition. Provider's minor30-loss role wording differs from correct applied public seller reference; no privileged uniformly correct channel is inferred.",
            "247": "Applied empty proposal and recipient248 rejection are real. Applied private says Probe only, but content selects END and returned reasoning ends with END. An applied-channel probe rationale does not establish channel-consistent deliberate probing, intended action, or upstream cause. No retry/default creates the proposal in the saved resolution."
        },
        "limits": "No hidden intent, induced belief, provider emission provenance or winner counterfactual. Original062/247 readings are nonsample audits and do not increase the common-sample count.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g02_channel_case_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("062 execution recognition and247 channel-conflicting empty probe checked")


if __name__ == "__main__":
    main()
