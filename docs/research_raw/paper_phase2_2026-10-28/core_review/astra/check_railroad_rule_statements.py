"""Source-link selected rule propositions; this is not a prevalence estimator."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import ROOT, rows

HERE = Path(__file__).resolve().parent
RAILS = {"READING_RAILROAD", "PENNSYLVANIA_RAILROAD", "B_O_RAILROAD", "SHORT_LINE"}
CASES = {
    (1, 304): (
        "Mortgaging them doesn't remove them from the count for rent purposes",
        "Correct counting statement in a successful refusal-recovered mortgage action; no general stable-knowledge inference.",
    ),
    (4, 307): (
        "mortgaged railroads still count toward the owned total for rent calculations",
        "Correct ownership-count statement, but the accompanying no-increase-in-rent claim overlooks making the redeemed landing collectible.",
    ),
    (12, 275): (
        "Mortgaged properties still count toward monopolies since Pennsylvania already charges $200",
        "Correct counting statement alongside an overbroad no-rent-benefit conclusion. Redemption affects collectibility at that deed, not the other rails' multiplier.",
    ),
    (17, 269): (
        "Mortgaged railroads still count toward the rent multiplier for unmortgaged ones",
        "Correct explicit proposition within an otherwise error-prone returned summary. This is not a claim that the whole explanation is correct.",
    ),
    (17, 271): (
        "Mortgaged railroads do not count toward rent multipliers",
        "Incorrect proposition two global decisions after a correct statement, within the same auction and unchanged owned railroads.",
    ),
    (17, 301): (
        "Mortgaged railroads still count toward the railroad monopoly for rent calculations",
        "Correct explicit proposition again within the same auction; other sentences in this explanation need separate adjudication.",
    ),
    (17, 307): (
        "Mortgaged railroads do not count toward rent multipliers",
        "Incorrect proposition again within that auction; the applied bid still follows its mortgage-value strategy.",
    ),
    (17, 389): (
        "I suspect the engine counts mortgaged railroads toward rent",
        "Tentative correct statement explicitly linked to the observed50 Short Line charge, not proof of durable learning.",
    ),
}


def main():
    ledger = rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
    reports = []
    selected = {}
    for u in ledger:
        key = (u["game"], int(u["decision_id"][-6:]))
        if key not in CASES:
            continue
        p = ROOT / u["packet"]
        x = rows(p)[u["packet_line"] - 1]
        selected[key] = x
        phrase, interpretation = CASES[key]
        matching = []
        for index, attempt in enumerate(x["attempts"]):
            for choice in attempt.get("raw_response", {}).get("choices", []):
                message = choice.get("message", {})
                text = message.get("reasoning") or ""
                if phrase in text:
                    start = text.index(phrase)
                    matching.append({
                        "attempt_ordinal_in_packet": index,
                        "message_field": "reasoning",
                        "exact_phrase": phrase,
                        "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                        "character_start": start,
                        "character_end": start + len(phrase),
                        "returned_explanation": text,
                        "reasoning_detail_types": [d.get("type") for d in message.get("reasoning_details", []) or []],
                    })
        assert len(matching) == 1, (key, len(matching))
        you = x["initial_prompt"]["payload"]["game_state"]["you"]
        reports.append({
            "game": key[0], "decision_suffix": key[1], "decision_id": x["decision_id"],
            "model": x["model"], "turn": x["turn_index"],
            "source_unit": u, "packet_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "applied": x["applied_action_record"],
            "cash": you["cash"],
            "owned_railroads": [s for s in you["holdings"]["owned"] if s["space_key"] in RAILS],
            "proposition_evidence": matching, "interpretation": interpretation,
            "review_scope": "Targeted proposition, relevant action/state and surrounding explanatory passages; not whole-decision semantic coverage.",
        })
    assert len(reports) == len(CASES)
    auction_rows = [r for r in reports if r["game"] == 17 and r["decision_suffix"] in {269, 271, 301, 307}]
    assert {r["turn"] for r in auction_rows} == {92}
    assert len({json.dumps(r["owned_railroads"], sort_keys=True) for r in auction_rows}) == 1
    assert all(r["applied"]["action"]["action"] == "bid_auction" for r in auction_rows)
    assert all(len(r["owned_railroads"]) == 2 and all(s["mortgaged"] for s in r["owned_railroads"]) for r in auction_rows)
    x = selected[17, 389]
    events_path = ROOT / x["source_run"] / "events.jsonl"
    events = rows(events_path)
    first_seq = min(e["seq"] for e in x["canonical_event_segment"])
    rents = [e for e in events if e["type"] == "RENT_PAID" and e["seq"] < first_seq
             and e["payload"]["space_index"] == 35]
    assert rents[-1]["payload"]["amount"] == 50
    engine_path = ROOT / "python/packages/engine/src/monopoly_engine/engine.py"
    report = {
        "scope": "Selected source-grounded counterexamples and within-auction inconsistency, not an exhaustive proposition coding or model-comparable prevalence estimate.",
        "interpretive_limit": "Returned explanations are recorded channels, not privileged access to beliefs. Correct counting does not validate other propositions, stable knowledge, action optimality or learning.",
        "cases": reports, "prior_short_line_rent": rents[-1],
        "prior_rent_source": str(events_path.relative_to(ROOT)),
        "prior_rent_source_sha256": hashlib.sha256(events_path.read_bytes()).hexdigest(),
        "engine_rule": "The landed mortgaged deed collects no rent; _count_owned counts all owned railroads for the multiplier on collectible deeds.",
        "engine_source_sha256": hashlib.sha256(engine_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "railroad_rule_statements.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Verified8 targeted source propositions; G17 four auction decisions share turn92 and the same two mortgaged rails; prior Short Line charge50.")


if __name__ == "__main__":
    main()
