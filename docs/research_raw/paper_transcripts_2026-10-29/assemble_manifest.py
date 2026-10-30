"""Freeze selected original fields and exact spans for the transcript exhibits.

This source-dependent preparation is separate from the portable typesetter.
It reads the independently reviewed excerpts, then checks them against canonical
files again before retaining the quoted fields in the manuscript package.
"""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DRAFT = HERE.parent / "paper_draft_2026-10-29"
fields = {}
quotes = []
cache = {}
source_hashes = {}


def pointer_parts(pointer):
    if pointer.startswith("$"):
        return re.findall(r"(?:\.([^.[\]]+)|\[(\d+)\])", pointer[1:])
    return [s.replace("~1", "/").replace("~0", "~") for s in pointer.split("/")[1:]]


def extract(path, line, pointer):
    if path not in cache:
        raw = (REPO / path).read_bytes()
        source_hashes[path] = hashlib.sha256(raw).hexdigest()
        cache[path] = raw.decode()
    raw = cache[path]
    record = json.loads(raw.splitlines()[line - 1]) if line else json.loads(raw)
    parts = pointer_parts(pointer)
    normalized = []
    for key in parts:
        if isinstance(key, tuple):
            key = key[0] or key[1]
        normalized.append(key)
        record = record[int(key)] if isinstance(record, list) else record[key]
    assert isinstance(record, str), (path, pointer)
    return record, "/" + "/".join(s.replace("~", "~0").replace("/", "~1") for s in normalized)


def add_field(path, line, pointer):
    value, pointer = extract(path, line, pointer)
    key = hashlib.sha256(f"{path}:{line}:{pointer}".encode()).hexdigest()[:16]
    fields[key] = {"source": path, "jsonl_line_1based": line, "json_pointer": pointer,
                   "source_sha256": source_hashes[path], "field_sha256": hashlib.sha256(value.encode()).hexdigest(),
                   "text": value}
    return key, value


CHANNELS = {"public_message": "public message", "logged_private_thought": "applied private note",
            "selected_response_reasoning": "returned provider explanation",
            "provider_returned_explanation": "returned provider explanation",
            "applied_private_thought": "applied private note", "private_thought": "applied private note",
            "assistant_content_not_applied": "assistant content (not applied)",
            "assistant_content": "assistant content (not applied)"}


def short_model(name):
    return "Grok" if "grok" in name else "Gemini" if "gemini" in name else "Opus" if "opus" in name else "Sol"


def read_a():
    source = json.loads((HERE / "source_a/excerpts.json").read_text())
    for q in source["quotes"]:
        ref = q["source_ref"]
        key, value = add_field(ref["source"], ref["jsonl_line_1based"], ref["json_pointer"])
        span = q["span_unicode_codepoints_zero_based_half_open"]
        assert value[span[0]:span[1]] == q["text"]
        meta = f'{short_model(q["model"])} · {CHANNELS[q["channel"]]} · G{q["game"]} d{q["decision_index"]} · attempt {q["attempt_index_zero_based"]} · excerpt'
        quotes.append({"id": q["id"], "metadata": meta, "decision_id": q["decision_id"],
                       "response_condition": "standard", "applied_action": next(d["applied_action"] for c in source["incidents"] for d in c["decisions"] if d["decision_id"] == q["decision_id"]),
                       "excerpts": [{"field_id": key, "span": span, "text": q["text"]}]})


def read_b():
    source = json.loads((HERE / "source_b/excerpts.json").read_text())
    for q in source["excerpts"]:
        ref = q["sources"][0]
        assert "JSON.parse" not in ref["field_path"]
        key, value = add_field(ref["path"], ref.get("jsonl_line_1based"), ref["field_path"])
        assert source_hashes[ref["path"]] == ref["sha256"]
        span = [q["span"]["start_inclusive"], q["span"]["end_exclusive"]]
        assert value[span[0]:span[1]] == q["text"]
        b = source["decision_bundles"][q["decision_bundle"]]
        channel = CHANNELS.get(q["channel"], q["channel"].replace("_", " "))
        meta = f'{short_model(b["player_name"])} · {channel} · G{b["game"]} d{b["decision"]} · attempt {b["selected_attempt_index"]} · excerpt'
        quotes.append({"id": q["id"], "metadata": meta, "decision_id": b["decision_id"],
                       "response_condition": b["response_condition"], "applied_action": b["action"],
                       "excerpts": [{"field_id": key, "span": span, "text": q["text"]}]})


def merge(new_id, old_ids):
    selected = [next(q for q in quotes if q["id"] == k) for k in old_ids]
    assert len({q["metadata"] for q in selected}) == 1
    q = dict(selected[0]); q["id"] = new_id
    q["excerpts"] = [s for old in selected for s in old["excerpts"]]
    quotes.append(q)


def main():
    read_a(); read_b()
    merge("g19-abort", ["g19_d135_abort", "g19_d135_abort_instruction"])
    merge("g12-sale", ["g12_d249_content_sale", "g12_d249_content_sale_plan"])
    # The final selection is explicit; a quote's omission from print is not an
    # absence finding. Full review files preserve alternative/context excerpts.
    cases = [
        {"id": "omission", "game": 13, "title": "An insurance pitch that omits available collateral", "location": "main", "quote_ids": ["g13-opening-insurance", "g13-seller-counter", "g13-seller-floor", "g13-omission-explanation", "g13-acceptance"]},
        {"id": "withdrawal", "game": 18, "title": "A standing offer withdrawn when its recipient is nearly broke", "location": "main", "quote_ids": ["g18-assurance", "g18-invocation", "g18-withdrawal", "g18-withdrawal-explanation"]},
        {"id": "boycott", "game": 20, "title": "An appeal to withhold a rival's building cash", "location": "main", "quote_ids": ["g20-coordination-appeal", "g20-recognition-note", "g20-sale-response", "g20-concrete-refusal"]},
        {"id": "stock", "game": 3, "title": "A building obstacle contradicted by the speaker's own note", "location": "main", "quote_ids": []},
        {"id": "final", "game": 7, "title": "A public final offer below the private limit", "location": "main", "quote_ids": ["g7_d42_public", "g7_d42_private", "g7_d43_public"]},
        {"id": "abort", "game": 19, "title": "A false proposal sent with an instruction to abort it", "location": "appendix", "quote_ids": ["g19_d135_content_end", "g19-abort", "g19_d135_false_public", "g19_d136_correction_accept"]},
        {"id": "bankruptcy", "game": 12, "title": "Bankruptcy executed while the response argues for selling", "location": "appendix", "quote_ids": ["g12-sale", "g12_d249_private_final", "g12_d249_public_bankruptcy"]},
        {"id": "disclosure", "game": 20, "title": "A private note delivered as public chat", "location": "appendix", "quote_ids": ["g20-received-and-applied-public", "g20-recipient-recognition"]},
    ]
    # Additional source-C spans are incorporated only after the bounded review
    # finishes; a missing file is a hard failure, never a fabricated quote.
    c_source = json.loads((HERE / "source_c/excerpts.json").read_text())
    c_case = next(c for c in c_source["cases"] if c["game"] == 3)
    extra = [q for q in c_case["excerpts"] if q["exhibit_id"] in ["G3-2", "G3-3", "G3-5"]]
    for q in extra:
        key, value = add_field(q["source_path"], q["jsonl_line"], q["full_field_path"])
        span = [q["span_start_zero_based"], q["span_end_exclusive"]]
        assert value[span[0]:span[1]] == q["exact_quote"]
        assert source_hashes[q["source_path"]] == q["source_sha256"]
        d = next(r for r in c_case["reading_scope"] if r["decision_id"] == q["decision_id"])
        meta = f'{short_model(d["model"])} · {CHANNELS[q["channel"]]} · G3 d{d["decision_suffix"]} · attempt 0 · excerpt'
        quotes.append({"id": q["exhibit_id"], "metadata": meta, "decision_id": q["decision_id"],
                       "response_condition": "standard", "applied_action": "end_turn",
                       "excerpts": [{"field_id": key, "span": span, "text": q["exact_quote"]}]})
    cases[3]["quote_ids"] = [q["exhibit_id"] for q in extra]
    ids = [qid for c in cases for qid in c["quote_ids"]]
    assert len(ids) == len(set(ids))
    selected = [next(q for q in quotes if q["id"] == qid) for qid in ids]
    used_fields = {e["field_id"] for q in selected for e in q["excerpts"]}
    manifest = {"schema_version": "transcript-exhibits-v1", "selection": "Five concerning-conduct chronologies prioritized by recorded explanatory contrast, financial stakes and recipient response; three execution/disclosure controls retained in the appendix. Purposive selection, not a severity score, deception rate, or model comparison.",
                "quote_convention": "Verbatim contiguous spans; bracketed ellipses separate noncontiguous spans. All cards are excerpts. Metadata and surrounding paragraphs are editorial. Private notes and returned provider explanations are distinct, fallible channels. Indices and offsets are zero-based, JSONL lines one-based.",
                "cases": cases, "quotes": selected, "fields": {k: v for k, v in fields.items() if k in used_fields},
                "source_reviews": {str((HERE / folder / name).relative_to(REPO)): hashlib.sha256((HERE / folder / name).read_bytes()).hexdigest() for folder in ["source_a", "source_b", "source_c"] for name in ["excerpts.json", "review.md"]}}
    (DRAFT / "data/transcript_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cases": len(cases), "cards": len(selected), "fields": len(used_fields)}))


if __name__ == "__main__":
    main()
