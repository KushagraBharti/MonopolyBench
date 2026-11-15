"""Read-only comparisons of existing records. Writes only beside this script."""
import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = next(p for p in HERE.parents if (p / "contracts/data/board.json").exists())
read = lambda p: json.loads(p.read_text())
digest = lambda s: hashlib.sha256(s.encode()).hexdigest() if s else None
entries = read(BASE / "integrated/data/episodes_188.json")
focal = {(r["game"], r["decision"]): r for r in entries
         if r["U0"] < r["debt"] <= r["Ustar"]}
same_fields = []
for name in ["astra", "sol"]:
    path = BASE / "full_drafts" / name / "data"
    if name == "astra":
        rows = read(path / "complete_financing_records.json")["rows"]
    else:
        rows = read(path / "sixteen_channels.json")
    for row in rows:
        key = row["game"], row["decision"]
        if key not in focal:
            continue
        ref = focal[key]
        for label, text, expected in [
            ("note", row["applied_action"].get("private_thought"), ref["applied_action"].get("private_thought")),
            ("provider", row["provider_reasoning"], ref["provider_reasoning"]),
            ("content", row["assistant_content"], ref["assistant_content"]),
        ]:
            assert digest(text) == digest(expected), (name, key, label)
            if text:
                same_fields.append([name, *key, label, digest(text)])
for row in read(BASE / "full_drafts/opus/data/focal_channels.json")["records"]:
    key = row["game"], row["decision"]
    if key not in focal:
        continue
    ref = focal[key]
    last = row["attempts"][-1]
    for label, text, expected in [
        ("note", row["applied_private_note"], ref["applied_action"].get("private_thought")),
        ("provider", last["provider_reasoning"], ref["provider_reasoning"]),
        ("content", last["assistant_content"], ref["assistant_content"]),
    ]:
        assert digest(text) == digest(expected), ("opus", key, label)
        if text:
            same_fields.append(["opus", *key, label, digest(text)])
for row in read(BASE / "full_drafts/fable_5_2/supplement/sixteen_first_texts.json"):
    key = row["game"], row["decision"]
    ref = focal[key]
    for label, channel, expected in [
        ("note", "authored_private_note", ref["applied_action"].get("private_thought")),
        ("provider", "provider_reasoning_field", ref["provider_reasoning"]),
        ("content", "assistant_content_not_applied", ref["assistant_content"]),
    ]:
        text = row["channels"][channel]["text"]
        assert digest(text) == digest(expected), ("fable_5_2", key, label)
        if text:
            same_fields.append(["fable_5_2", *key, label, digest(text)])

offers = read(BASE / "integrated/data/offers.json")
semantic = [r for r in offers if r["accept_available"]
            and r["response"] == "reject_trade" and r["recipient_new_groups"]]
comparison = [r for r in offers if r["accept_available"]
              and r["completion_cell"] in ["author_only", "neither"]]
assert len(semantic) == 74
assert not ({r["decision_id"] for r in semantic} & {r["decision_id"] for r in comparison})
codes = read(BASE / "integrated/data/reason_comparison.json")["categories"]["D"]
assert [codes[k] for k in ["first_pass_positive", "reviewer_positive", "common_positive", "disagreement_rows", "both_negative"]] == [63, 63, 61, 4, 9]
annotation_hashes = []
for item in read(BASE / "integrated/data/annotation_sources.json")["entries"]:
    original = ROOT / item["source"]
    packaged = BASE / "integrated" / item["packaged"]
    assert hashlib.sha256(original.read_bytes()).hexdigest() == item["sha256"]
    assert original.read_bytes() == packaged.read_bytes()
    annotation_hashes.append(item)

result = {
    "focal_episodes": len(focal),
    "repeated_nonempty_fields_compared_by_sha256": len(same_fields),
    "field_hashes": same_fields,
    "entries_with_unlisted_principal": sum(r["Mstar"] > r["M0"] for r in entries),
    "necessary_plus_insufficient_unlisted_subset": len(focal) + sum(r["Ustar"] < r["debt"] and r["Mstar"] > r["M0"] for r in entries),
    "semantic_population": len(semantic),
    "semantic_and_comparison_populations_disjoint": True,
    "historical_D_code_counts": {k: codes[k] for k in ["first_pass_positive", "reviewer_positive", "common_positive", "disagreement_rows", "both_negative"]},
    "annotation_sources_byte_identical": annotation_hashes,
}
(HERE / "reviewer_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k not in ["field_hashes", "annotation_sources_byte_identical"]}, indent=2))
