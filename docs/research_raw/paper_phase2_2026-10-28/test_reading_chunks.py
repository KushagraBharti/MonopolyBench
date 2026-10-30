import pytest

from prepare_reading_chunks import decode, encode


def test_exact_roundtrip_preserves_distinct_channels_and_arguments():
    note = "Buy then build. " * 20
    source = {"first": {"action": "buy", "note": note},
              "second": {"action": "buy", "note": note},
              "third": {"action": "end_turn", "note": note},
              "raw": '{"x":1}', "other_raw": '{ "x": 1 }'}
    encoded = encode(source)
    assert encoded["second"] == {"$same_as": "/first"}
    assert encoded["third"]["action"] == "end_turn"
    assert decode(encoded) == source


def test_paths_with_slash_and_tilde_and_empty_values():
    source = {"a/b~c": "long" * 50, "list": ["long" * 50, [], {}, None, False, 0]}
    assert encode(source)["list"][0] == {"$same_as": "/a~1b~0c"}
    assert decode(encode(source)) == source


def test_reserved_key_rejected():
    with pytest.raises(ValueError):
        encode({"$same_as": "a source value"})
