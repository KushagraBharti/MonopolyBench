"""Audit accepted-trade timeline directions against applied offers and transfers.

Downstream analysis only. Does not change prompts or repair recorded games.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from monopoly_arena.prompting import _trade_action_text
from monopoly_engine.board import SPACE_INDEX_BY_KEY

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHASE1 = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra"


def rows(path):
    with path.open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def bundle_text(bundle):
    parts = []
    if bundle.get("cash"):
        parts.append(f"${bundle['cash']:,}")
    if bundle.get("properties"):
        parts.append(", ".join(bundle["properties"]))
    cards = bundle.get("get_out_of_jail_cards", 0)
    if cards:
        parts.append(f"{cards} Get Out of Jail Free card" + ("s" if cards != 1 else ""))
    return " + ".join(parts) or "nothing"


def correct_summary(author, acceptor, offer, request):
    return (f"accepted trade with {author}: {author} gives {bundle_text(offer)}; "
            f"{acceptor} gives {bundle_text(request)}")


def settlement(author, acceptor, offer, request):
    cash = {author: request.get("cash", 0) - offer.get("cash", 0),
            acceptor: offer.get("cash", 0) - request.get("cash", 0)}
    deeds = [(author, acceptor, SPACE_INDEX_BY_KEY[key]) for key in offer.get("properties", [])]
    deeds += [(acceptor, author, SPACE_INDEX_BY_KEY[key]) for key in request.get("properties", [])]
    return cash, sorted(deeds)


def identity(item):
    return tuple(item.get(key) for key in ("turn_index", "player_id", "event_type", "action", "message"))


def main():
    manifest = json.loads((PHASE1 / "visibility_manifest.json").read_text())
    results, sources = [], []
    prompt_count = 0
    for game in manifest["games"]:
        run = ROOT / game["package"] / "run"
        events = list(rows(run / "events.jsonl"))
        actions = {r["decision_id"]: r["action"] for r in rows(run / "actions.jsonl")}
        current, decision_id, message = None, None, None
        game_results = []
        for index, event in enumerate(events):
            payload = event["payload"]
            if event["type"] == "LLM_DECISION_RESPONSE":
                decision_id = payload["decision_id"]
                message = None
            elif event["type"] == "LLM_PUBLIC_MESSAGE":
                assert payload["decision_id"] == decision_id
                message = payload.get("message") or None
            elif event["type"] in {"TRADE_PROPOSED", "TRADE_COUNTERED"}:
                action = actions[decision_id]
                assert action["action"] in {"propose_trade", "counter_trade"}
                assert action["args"]["offer"] == payload["offer"]
                assert action["args"]["request"] == payload["request"]
                current = {"author": event["actor"]["player_id"], "event": event,
                           "decision_id": decision_id}
            elif event["type"] == "TRADE_ACCEPTED":
                assert current is not None
                author, acceptor = current["author"], event["actor"]["player_id"]
                assert author != acceptor
                assert actions[decision_id]["action"] == "accept_trade"
                assert {author, acceptor} == {payload["initiator_player_id"], payload["counterparty_player_id"]}
                assert current["event"]["payload"]["offer"] == payload["offer"]
                assert current["event"]["payload"]["request"] == payload["request"]
                cash, deeds = settlement(author, acceptor, payload["offer"], payload["request"])
                following = []
                for later in events[index + 1:]:
                    if later["type"] == "LLM_DECISION_REQUESTED":
                        break
                    following.append(later)
                observed_cash = defaultdict(int)
                for later in following:
                    if later["type"] == "CASH_CHANGED" and later["payload"]["reason"] == "TRADE_CASH":
                        observed_cash[later["payload"]["player_id"]] += later["payload"]["delta"]
                assert {pid: observed_cash[pid] for pid in cash} == cash
                observed_deeds = sorted((e["payload"]["from_player_id"], e["payload"]["to_player_id"],
                                         e["payload"]["space_index"])
                                        for e in following if e["type"] == "PROPERTY_TRANSFERRED")
                assert observed_deeds == deeds
                rendered = _trade_action_text("accepted", payload)
                expected = correct_summary(author, acceptor, payload["offer"], payload["request"])
                item = {"turn_index": event["turn_index"], "player_id": acceptor,
                        "event_type": "TRADE_ACCEPTED", "action": rendered, "message": message}
                result = {"game": game["game"], "decision_id": decision_id,
                          "accepted_event": event, "final_offer_source": current,
                          "acceptor": acceptor, "final_author": author,
                          "thread_initiator": payload["initiator_player_id"],
                          "expected_trade_cash_excluding_mortgage_interest": cash,
                          "observed_deed_transfers": deeds,
                          "summary_from_current_implementation": item,
                          "summary_with_actual_offer_author": expected,
                          "direction_reversed": author != payload["initiator_player_id"],
                          "summary_differs": rendered != expected,
                          "recorded_initial_prompt_exposures": []}
                assert result["summary_differs"] == result["direction_reversed"]
                game_results.append(result)
                current = None
        by_identity = {identity(r["summary_from_current_implementation"]): r for r in game_results}
        assert len(by_identity) == len(game_results), "Ambiguous repeated timeline item needs occurrence tracking"
        for record in rows(run / "decisions.jsonl"):
            if record.get("phase") != "decision_started":
                continue
            prompt_count += 1
            timeline = record["prompt_payload"]["game_state"]["memory"]["public_timeline_last_20"]
            for item in timeline:
                if item.get("event_type") != "TRADE_ACCEPTED":
                    continue
                matched = by_identity[identity(item)]
                matched["recorded_initial_prompt_exposures"].append({
                    "decision_id": record["decision_id"], "player_id": record["player_id"],
                    "turn_index": record["turn_index"]})
        results.extend(game_results)
        for name in ("events.jsonl", "actions.jsonl", "decisions.jsonl"):
            path = run / name
            sources.append({"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    reversed_cases = [r for r in results if r["direction_reversed"]]
    affected_prompts = {e["decision_id"] for r in reversed_cases for e in r["recorded_initial_prompt_exposures"]}
    assert len(results) == 113 and prompt_count == 6989
    counts = {"accepted_trades": len(results), "initial_prompts_checked": prompt_count,
              "reversed_trade_summaries": len(reversed_cases),
              "reversed_summaries_present_in_recorded_prompts": sum(bool(r["recorded_initial_prompt_exposures"]) for r in reversed_cases),
              "affected_distinct_initial_prompts": len(affected_prompts),
              "affected_games": len({r["game"] for r in reversed_cases}),
              "reversed_by_game": dict(sorted(Counter(r["game"] for r in reversed_cases).items()))}
    code = ROOT / "python/packages/arena/src/monopoly_arena/prompting.py"
    output = {"version": "accepted_trade_memory_audit_v1", "counts": counts,
              "scope": "All accepted trades and all recorded initial public timeline prompts. Applied actions, public messages and game paths unchanged. No inferred reliance, performance effect, or model intent.",
              "finding": "The formatter assigns the final offer bundle to the thread initiator. When the accepted final terms were authored by the other party, the displayed giver and receiver are reversed. Actual settlement uses the current offer author correctly.",
              "cases": results, "sources": sources,
              "formatter_source": str(code.relative_to(ROOT)),
              "formatter_sha256": hashlib.sha256(code.read_bytes()).hexdigest()}
    (HERE / "trade_memory_audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
