"""Extract every available text channel for the focal first decisions.

Focal set: the sixteen necessary-collateral entries, the six above-bound
financing starts, and the third payable declaration (G12 d249). For every
attempt it records the applied tool call, the applied private note and public
message (tool-call arguments), assistant content, and the provider-returned
reasoning field with its detail types. Each field is hashed. Carried notes in
the delivered request are recorded with their count. Read-only.
"""
from __future__ import annotations

import json

import lib

FINANCE = json.loads((lib.DRAFT / "data/finance_census.json").read_text())
ROWS = {(r["game"], r["decision"]): r for r in FINANCE["rows"]}
SIXTEEN = sorted(k for k, r in ROWS.items() if r["region"] == "C_release_necessary")
SIX = sorted(k for k, r in ROWS.items() if r["category"] == "above_bound" and r["first_action"] != "declare_bankruptcy")
EXTRA = [(12, 249)]


def attempt_record(game: int, idx: int, k: int, a: dict) -> dict:
    m = lib.message_of(a) or {}
    calls = []
    for tc in m.get("tool_calls") or []:
        fn = tc.get("function", {})
        calls.append({"name": fn.get("name"), "arguments": fn.get("arguments")})
    details = m.get("reasoning_details") or []
    reasoning = m.get("reasoning")
    content = m.get("content")
    return {
        "attempt_index": k,
        "response_condition": a.get("response_condition"),
        "outcome": a.get("outcome"),
        "validation_errors": a.get("validation_errors"),
        "assistant_content": content,
        "assistant_content_sha256": lib.sha256_text(content) if isinstance(content, str) else None,
        "provider_reasoning": reasoning,
        "provider_reasoning_sha256": lib.sha256_text(reasoning) if isinstance(reasoning, str) else None,
        "provider_reasoning_detail_types": sorted({d.get("type") for d in details if isinstance(d, dict)}),
        "refusal": m.get("refusal"),
        "tool_calls": calls,
        "json_pointer": f"/attempts/{k}/raw_response/choices/0/message",
    }


def extract(game: int, idx: int, group: str) -> dict:
    z = lib.decision(game, idx)
    s, r = z["decision_started"], z["decision_resolved"]
    fa = r["final_action"]
    notes = s["prompt_payload"]["game_state"].get("memory", {}).get("your_private_thoughts_last_10") or []
    fin = ROWS[(game, idx)]
    rec = {
        "group": group,
        "game": game,
        "decision": idx,
        "turn": s["turn_index"],
        "model": lib.label(s["player_name"]),
        "source_file": lib.rel(lib.decisions_path(game)),
        "decision_id": r["decision_id"],
        "C": fin["C"], "D": fin["D"], "U0": fin["U0"], "Ustar": fin["Ustar"], "M0": fin["M0"], "S": fin["S"],
        "outcome": fin["outcome"],
        "cash_after_payment": fin["cash_after_payment"],
        "applied_action": fa.get("action"),
        "applied_args": fa.get("args"),
        "applied_private_note": fa.get("private_thought"),
        "applied_private_note_sha256": lib.sha256_text(fa.get("private_thought")),
        "applied_public_message": fa.get("public_message"),
        "retry_used": r.get("retry_used"),
        "fallback_used": r.get("fallback_used"),
        "attempts": [attempt_record(game, idx, k, a) for k, a in enumerate(r.get("attempts", []))],
        "carried_notes_count": len(notes),
        "carried_notes": notes,
        "episode_actions": fin["actions"],
        "released_mortgages_used": fin["released_mortgages_used"],
    }
    return rec


def main() -> None:
    out = [extract(g, i, "necessary_collateral") for g, i in SIXTEEN]
    out += [extract(g, i, "above_bound_financing_start") for g, i in SIX]
    out += [extract(g, i, "payable_declaration_channel_conflict") for g, i in EXTRA]
    meta = {
        "description": "All available text channels at the first liquidation decision of each focal episode.",
        "channel_definitions": {
            "applied_private_note": "The private_thought argument of the applied tool call; carried into later requests as the player's own memory.",
            "applied_public_message": "The public_message argument of the applied tool call; delivered to other players.",
            "assistant_content": "Free text returned in the assistant message alongside the tool call.",
            "provider_reasoning": "The gateway's separate readable reasoning field (reasoning.summary for Sol/Grok, reasoning.text for Gemini/Opus); not a tool argument, not delivered to other players, not carried as memory; completeness not established.",
        },
        "selection": {"sixteen": SIXTEEN, "six": SIX, "extra": EXTRA},
        "inputs": {lib.rel(lib.decisions_path(g)): lib.sha256_file(lib.decisions_path(g)) for g in sorted({g for g, _ in SIXTEEN + SIX + EXTRA})},
        "method": "Read-only extraction from saved decision records.",
    }
    lib.write_json("focal_channels.json", {"meta": meta, "records": out})
    for o in out:
        last = o["attempts"][-1]
        lens = [(a["attempt_index"], a["response_condition"], a["outcome"], len(a["provider_reasoning"] or ""), len(a["assistant_content"] or "")) for a in o["attempts"]]
        print(f"G{o['game']} d{o['decision']} {o['model']} {o['group'][:12]} act={o['applied_action']} note_len={len(o['applied_private_note'] or '')} notes_carried={o['carried_notes_count']} attempts={lens} types={last['provider_reasoning_detail_types']}")


if __name__ == "__main__":
    main()
