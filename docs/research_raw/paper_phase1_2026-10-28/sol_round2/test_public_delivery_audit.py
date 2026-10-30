from public_delivery_audit import DeliveryMemory


def event(kind, seq, payload):
    return {"type": kind, "event_id": f"e{seq}", "seq": seq, "turn_index": 4, "payload": payload}


def build(memory, seq, message):
    memory.update(event("LLM_DECISION_RESPONSE", seq, {
        "decision_id": f"d{seq}", "player_id": "p1", "action_name": "build_houses_or_hotel"}))
    memory.update(event("LLM_PUBLIC_MESSAGE", seq + 1, {
        "decision_id": f"d{seq}", "player_id": "p1", "message": message}))
    memory.update(event("HOUSE_BUILT", seq + 2, {"player_id": "p1", "space_index": 1, "count": 1}))


def test_later_build_message_is_not_retained_in_merged_summary():
    memory = DeliveryMemory()
    build(memory, 1, "First assurance")
    build(memory, 4, "Later incompatible assurance")
    assert len(memory._public_timeline) == 1
    assert memory._public_timeline[0]["message"] == "First assurance"
    assert memory.inserted == {"e2"}
    assert memory.suppressed[0]["source_event_id"] == "e5"
    assert memory.suppressed[0]["retained_source_event_id"] == "e2"


def test_first_nonempty_message_is_adopted_on_merge():
    memory = DeliveryMemory()
    build(memory, 1, " ")
    build(memory, 4, "An actual assurance")
    assert memory._public_timeline[0]["message"] == "An actual assurance"
    assert memory.inserted == {"e5"}
    assert not memory.suppressed


def test_opponent_delivery_requires_an_observed_prompt_and_retains_occurrence():
    memory = DeliveryMemory()
    build(memory, 1, "First assurance")
    build(memory, 4, "Later assurance")
    observed = memory.snapshot_for_player("p2")
    memory.observe({"player_id": "p2", "decision_id": "recipient", "turn_index": 5,
                    "prompt_payload": {"game_state": {"memory": observed}}})
    assert memory.deliveries["e2"]["p2"]["decision_id"] == "recipient"
    assert "e5" not in memory.deliveries


def test_bankruptcy_cash_consumes_pending_message_before_summarized_marker():
    memory = DeliveryMemory()
    memory.update(event("LLM_DECISION_RESPONSE", 1, {
        "decision_id": "d1", "player_id": "p1", "action_name": "declare_bankruptcy"}))
    memory.update(event("LLM_PUBLIC_MESSAGE", 2, {
        "decision_id": "d1", "player_id": "p1", "message": "Work together against p3."}))
    memory.update(event("CASH_CHANGED", 3, {
        "player_id": "p1", "delta": -20, "reason": "BANKRUPTCY_CASH"}))
    memory.update(event("CASH_CHANGED", 4, {
        "player_id": "p1", "delta": 0, "reason": "BANKRUPTCY"}))
    assert memory._public_timeline[0]["action"] == "declared bankruptcy"
    assert memory._public_timeline[0]["message"] is None
    assert memory.claimed_without_summary["e2"]["reason"] == "BANKRUPTCY_CASH"
    assert not memory.inserted
