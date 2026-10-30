import json

from prepare_game_reading import normalize, restore
from prepare_reading_chunks import decode, encode


def test_nested_json_strings_and_duplicate_observations_are_lossless():
    action = {"name": "accept_trade", "arguments": json.dumps({"public_message": "No", "cash": 100})}
    value = {"payload": {"x": [1, 2]}, "messages": [{"content": '{ "x" : [1, 2] }'}],
             "tool_call": action, "content": json.dumps(action, indent=2), "invalid_content": '{"name":'}
    normalized, originals = normalize(value)
    assert restore(decode(encode(normalized, minimum=10)), originals) == value
    assert normalized["invalid_content"] == '{"name":'


def test_provider_text_and_repeated_text_are_preserved():
    text = "I reject the offer. " * 20
    value = {"reasoning": text, "details": [{"summary": text}], "private": "Accept.",
             "encrypted": {"opaque": True, "sha256": "abc"}}
    normalized, originals = normalize(value)
    assert restore(decode(encode(normalized)), originals) == value
