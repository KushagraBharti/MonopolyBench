import zipfile

import pytest

from monopoly_telemetry.execution_cost import call_cost
from monopoly_telemetry.export import package_zip, unpack_verified
from monopoly_telemetry.inventory import write_inventory, verify_inventory, tree_hash
from monopoly_telemetry.writer_jsonl import read_jsonl_strict


def test_byok_cost_keeps_missing_unknown_and_zero_distinct():
    assert call_cost({"is_byok": True, "cost": 0, "cost_details": {"upstream_inference_cost": 2}})["total_cost"] == 2
    assert call_cost({"cost": 0})["cost_status"] == "known"
    assert call_cost({"is_byok": True, "cost": 0})["total_cost"] is None
    assert call_cost({})["cost_status"] == "missing"
    assert call_cost({}, unknown=True)["cost_status"] == "unknown"
    # Usage v2 rule: a zero gateway charge adds the upstream bill even without a BYOK flag,
    # while a credit charge already includes it.
    assert call_cost({"cost": 0, "cost_details": {"upstream_inference_cost": 1.25}})["total_cost"] == 1.25
    assert call_cost({"cost": 0.5, "cost_details": {"upstream_inference_cost": 0.4}})["total_cost"] == 0.5
    assert call_cost({"cost": 0.1, "is_byok": True, "cost_details": {"upstream_inference_cost": 1}})["total_cost"] == 1.1


@pytest.mark.parametrize("usage", [{"cost": "unavailable"}, {"cost": True}, {"cost": float("nan")}, {"cost": 0, "is_byok": True, "cost_details": []}])
def test_malformed_cost_is_missing_without_breaking_the_decision(usage):
    cost = call_cost(usage)
    assert cost["cost_status"] == "missing" and cost["total_cost"] is None


def test_package_round_trip_and_tamper_detection(tmp_path):
    source = tmp_path / "source"
    (source / "run").mkdir(parents=True)
    (source / "run" / "events.jsonl").write_text('{"x":1}\n')
    manifest = write_inventory(source)
    archive = tmp_path / "game.zip"
    package_zip(source, archive)
    restored = tmp_path / "restored"
    unpack_verified(archive, restored)
    assert verify_inventory(restored) == manifest
    assert tree_hash(list(reversed(manifest["files"]))) == manifest["tree_sha256"]
    (restored / "run" / "events.jsonl").write_text('{"x":2}\n')
    with pytest.raises(ValueError, match="mismatch"):
        verify_inventory(restored)


@pytest.mark.parametrize("name", ["../escape", "/absolute", "C:/escape", "a\\b"])
def test_export_rejects_unsafe_paths(tmp_path, name):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr(name, b"bad")
    with pytest.raises(ValueError):
        unpack_verified(archive, tmp_path / "result")


def test_strict_jsonl_reports_damage(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text('{"ok":1}\n{"partial":')
    with pytest.raises(ValueError, match="trailing"):
        read_jsonl_strict(path)
    path.write_text('{"ok":1}\nbad\n')
    with pytest.raises(ValueError, match=":2:"):
        read_jsonl_strict(path)


def test_live_readers_may_skip_only_an_unterminated_tail(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_bytes(b'{"seq":1}\n{"seq":2,"partial')
    with pytest.raises(ValueError, match="incomplete trailing record"):
        read_jsonl_strict(path)
    assert read_jsonl_strict(path, allow_partial_tail=True) == [{"seq": 1}]
    path.write_bytes(b'{"seq":1}\n{broken}\n')
    with pytest.raises(ValueError, match="malformed JSON"):
        read_jsonl_strict(path, allow_partial_tail=True)
