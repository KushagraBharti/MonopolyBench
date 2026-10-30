"""Provider visibility units and response disagreement are independently specified."""
from reproduce import name_mismatch, reasoning_inventory, private_note_origin


def response(message, usage=None):
    return {"choices": [{"message": message}], "usage": usage or {}}


def test_token_counts_and_tool_private_notes_are_not_provider_reasoning_text():
    raw = response({"tool_calls": [{"function": {"arguments": '{"private_thought":"Think"}'}}]},
                   {"completion_tokens_details": {"reasoning_tokens": 1000}})
    assert reasoning_inventory(raw) == {"text_fields_chars": {}, "opaque_fields": [],
                                        "has_text": False, "has_opaque": False}


def test_text_summary_and_encrypted_data_are_kept_distinct_with_overlap():
    raw = response({"reasoning": "hello", "reasoning_details": [
        {"type": "reasoning.summary", "summary": "brief"},
        {"type": "reasoning.encrypted", "data": "cipher", "text": "cipher"}]})
    result = reasoning_inventory(raw)
    assert result["has_text"] and result["has_opaque"]
    assert sorted(result["text_fields_chars"].values()) == [5, 5]
    assert result["opaque_fields"][0]["type"] == "reasoning.encrypted"


def test_mismatch_is_name_difference_and_argument_identity_not_motive():
    a = {"assistant_content": '{"name":"reject_trade","parameters":{"public_message":"No"}}',
         "parsed_tool_call": {"name": "accept_trade", "arguments": '{"public_message":"No"}'}}
    result = name_mismatch(a)
    assert result["content_name"] == "reject_trade" and result["tool_name"] == "accept_trade"
    assert result["identical_arguments"] is True
    a["assistant_content"] = "No"
    assert name_mismatch(a) is None


def test_public_message_equality_does_not_imply_argument_equality():
    a = {"assistant_content": '{"name":"declare_bankruptcy","arguments":{"public_message":"No","private_thought":"Cash short"}}',
         "parsed_tool_call": {"name": "mortgage_property", "arguments":
             '{"public_message":"No","private_thought":"Cash short","space_key":"A"}'}}
    result = name_mismatch(a)
    assert result["same_public_message_stripped"] and result["same_private_thought_stripped"]
    assert result["identical_arguments"] is False


def test_malformed_content_name_match_keeps_parse_status_and_unknown_arguments():
    a = {"assistant_content": '{"name":"declare_bankruptcy","public_message":"No", broken',
         "parsed_tool_call": {"name": "mortgage_property", "arguments": '{"public_message":"No"}'}}
    result = name_mismatch(a)
    assert result["content_format"] == "malformed_json_name_match"
    assert result["identical_arguments"] is None
    assert result["same_public_message_stripped"] is True


def test_fallback_note_is_not_model_authored_private_analysis():
    assert private_note_origin({"private_thought": "fallback"}, True) == "deterministic_fallback"
    assert private_note_origin({"private_thought": "fallback"}, False) == "nonfallback_final_action"
    assert private_note_origin({}, False) == "absent_or_empty"
