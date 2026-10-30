"""Independent trade orientation and delivered-memory exposure accounting."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def bundle(value):
    parts = []
    if value.get("cash"):
        parts.append(f"${value['cash']}")
    if value.get("properties"):
        parts.append(", ".join(value["properties"]))
    cards = value.get("get_out_of_jail_cards", 0)
    if cards:
        parts.append(f"{cards} Get Out of Jail Free {'card' if cards == 1 else 'cards'}")
    return " + ".join(parts) if parts else "nothing"


def rendered(event):
    p = event["payload"]
    offer, request = bundle(p["offer"]), bundle(p["request"])
    initiator, other = p["initiator_player_id"], p["counterparty_player_id"]
    if event["type"] == "TRADE_ACCEPTED":
        return f"accepted trade with {initiator}: {initiator} gives {offer}; {other} gives {request}"
    if event["type"] == "TRADE_REJECTED":
        return f"rejected trade with {initiator}: {initiator} offered {offer} for {request}"
    return f"countered trade with {other}: offer {offer}; request {request}"


def memory_key(row):
    return row["event_type"], row["turn_index"], row["player_id"], row["action"], row.get("message")


def main():
    counts = Counter()
    bad_events = []
    affected = []
    exposure_counts = Counter()
    total = 0
    for game in range(1, 21):
        source = units(game)
        run = ROOT / next(iter(source.values()))[0]["source_run"]
        events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
        last_offer_by = None
        public = None
        lookup = defaultdict(list)
        for event in events:
            kind, p = event["type"], event["payload"]
            if kind == "LLM_DECISION_REQUESTED":
                public = None
            elif kind == "LLM_PUBLIC_MESSAGE":
                public = p["message"]
            elif kind == "TRADE_PROPOSED":
                last_offer_by = event["actor"]["player_id"]
                counts[kind] += 1
            elif kind in {"TRADE_COUNTERED", "TRADE_ACCEPTED", "TRADE_REJECTED"}:
                actor = event["actor"]["player_id"]
                counts[kind] += 1
                if kind == "TRADE_COUNTERED":
                    last_offer_by = actor
                    defect = "counter_self_partner" if actor == p["counterparty_player_id"] else None
                else:
                    assert last_offer_by in {p["initiator_player_id"], p["counterparty_player_id"]}
                    defect = ("accepted_reversed" if kind == "TRADE_ACCEPTED" else "rejected_offer_misattributed") if last_offer_by == p["counterparty_player_id"] else None
                if defect:
                    row = {"event_type": kind, "turn_index": event["turn_index"], "player_id": actor,
                           "action": rendered(event), "message": public}
                    record = {"game": game, "seq": event["seq"], "event_id": event["event_id"],
                              "defect": defect, "latest_offer_from": last_offer_by,
                              "canonical_actor": actor, "payload": p, "expected_delivered_row": row,
                              "events_sha256": hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()}
                    bad_events.append(record)
                    lookup[memory_key(row)].append(record)
                if kind in {"TRADE_ACCEPTED", "TRADE_REJECTED"}:
                    last_offer_by = None
            elif kind == "TRADE_EXPIRED":
                last_offer_by = None
        exposed_events = set()
        for unit, ref in source.values():
            total += 1
            rows = unit["initial_prompt"]["payload"]["game_state"]["memory"]["public_timeline_last_20"]
            matches = []
            for row in rows:
                for event in lookup.get(memory_key(row), []):
                    # A repeated identical row can match several events. Keep
                    # this ambiguity, and count the prompt union only once.
                    matches.append({"seq": event["seq"], "defect": event["defect"]})
                    exposed_events.add(event["seq"])
            if matches:
                types = sorted({m["defect"] for m in matches})
                exposure_counts.update(types)
                affected.append({"game": game, "decision_id": unit["decision_id"], "source": ref,
                                 "defects": types, "matching_events": matches})
        # Every bad event need not remain in a future last20 memory, but the
        # report keeps that event separately from observed initial exposure.
        for row in bad_events:
            if row["game"] == game:
                row["matched_in_at_least_one_initial_prompt"] = row["seq"] in exposed_events
    summary = {"canonical_event_denominators": dict(counts),
               "bad_event_counts": dict(Counter(r["defect"] for r in bad_events)),
               "initial_prompt_exposure_by_manifestation": dict(exposure_counts),
               "initial_prompt_union_exposed": len(affected), "all_initial_prompts": total,
               "event_sha256_scope": "Canonical events in each matched game",
               "semantic_unit": "Formatter manifestations and initial delivered prompt exposure, not induced model beliefs"}
    assert total == 6989
    report = {"summary": summary, "bad_events": bad_events, "affected_initial_prompts": affected,
              "mechanism": "The formatter always assigns offer to original initiator. A counterparty counter reverses offer orientation while initiator/counterparty fields retain thread roles. Counter text always names the fixed counterparty, which is the actor itself on that side's turns. Canonical transfers and current holdings remain distinct from these text rows.",
              "source_code": "python/packages/arena/src/monopoly_arena/prompting.py:_trade_action_text and _summarize_action_event",
              "source_code_sha256": hashlib.sha256((ROOT / "python/packages/arena/src/monopoly_arena/prompting.py").read_bytes()).hexdigest(),
              "provenance": "Peer target counts known before independently written orientation/exposure pass. All original common and catalog initial judgments already preserved. This is a code/event audit, not new independent semantic annotation.",
              "limits": "Initial prompts only, no retry multiplier. Repeated identical rows can make exact event attribution ambiguous; prompt-level membership in a defect category is still observable. Delivered exposure does not identify reliance or explain all subsequent channel conflicts. Counts for manifestations overlap in prompts and cannot be added.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "trade_timeline_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
