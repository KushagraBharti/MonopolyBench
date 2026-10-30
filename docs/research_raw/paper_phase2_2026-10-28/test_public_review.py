from prepare_public_review import assert_public, scrub


def test_channel_removal_preserves_public_dialogue_and_money():
    source = {"cash": 1500, "public_message": "I think the offer is too low.",
              "private_thought": "not part of this review", "reasoning": "not part of this review",
              "memory": {"your_private_thoughts_last_10": [{"thought": "excluded"}],
                         "public_timeline_last_20": [{"message": "Will you accept $200?"}]}}
    result = scrub(source)
    assert_public(result)
    assert result == {"cash": 1500, "public_message": "I think the offer is too low.",
                      "memory": {"public_timeline_last_20": [{"message": "Will you accept $200?"}]}}


def test_nested_private_fields_removed():
    result = scrub([{"offer": {"cash": 200, "private_thought": "excluded"}},
                    {"raw_response": {"choices": [1]}, "outcome": "valid"}])
    assert result == [{"offer": {"cash": 200}}, {"outcome": "valid"}]
    assert_public(result)
