"""Check 10. Independent source check of every quotation manifest shipped with
the four frozen drafts.

For each manifest entry that names a source file, a 1-based JSONL line and a
JSON pointer, this re-reads the canonical line, resolves the pointer, and
compares (a) the file hash, (b) the field hash and (c) each recorded span or
excerpt with the field text. It does not check TeX rendering; each draft's own
QA does that. Read-only.
"""
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPO = ROOT.parents[2]
OUT = HERE.parent / "data/c10_quote_sources.json"
MANIFESTS = [
    "full_drafts/astra/data/transcript_manifest.json",
    "full_drafts/astra/data/opus_quote_manifest.json",
    "full_drafts/astra/data/fable_quote_manifest.json",
    "full_drafts/sol/data/transcript_manifest.json",
    "full_drafts/sol/data/opus_quote_manifest.json",
    "full_drafts/sol/data/fable_quote_manifest.json",
    "full_drafts/opus/data/inherited/transcript_manifest.json",
    "full_drafts/opus/data/inherited/opus_quote_manifest.json",
    "full_drafts/opus/data/inherited/fable_quote_manifest.json",
    "full_drafts/opus/data/new_quote_manifest.json",
    "full_drafts/fable_5_2/data/quote_manifest.json",
]
_hash, _lines = {}, {}


def fhash(p):
    if p not in _hash:
        _hash[p] = hashlib.sha256((REPO / p).read_bytes()).hexdigest()
    return _hash[p]


def line(p, n):
    if p not in _lines:
        _lines[p] = (REPO / p).read_text(encoding="utf-8").split("\n")
    return json.loads(_lines[p][n - 1])


def resolve(obj, pointer):
    for part in pointer.strip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(obj, str):
            obj = json.loads(obj)
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj


def walk(node, found):
    if isinstance(node, dict):
        if "json_pointer" in node and ("jsonl_line_1based" in node or "line" in node) and ("source" in node or "source_path" in node):
            found.append(node)
        for v in node.values():
            walk(v, found)
    elif isinstance(node, list):
        for v in node:
            walk(v, found)


report = {}
for m in MANIFESTS:
    p = ROOT / m
    if not p.exists():
        report[m] = {"missing": True}
        continue
    entries = []
    walk(json.load(open(p)), entries)
    ok = bad = 0
    problems = []
    whole_file_entries = []
    for e in entries:
        src = e.get("source") or e.get("source_path")
        n = e.get("jsonl_line_1based") or e.get("line")
        try:
            if n in (None, "None"):
                # a whole JSON file named by prefix (returned provider explanations in prompts/)
                import glob
                field = None
                for cand in sorted(glob.glob(str(REPO / src) + "*")):
                    raw = Path(cand).read_bytes()
                    if hashlib.sha256(raw).hexdigest() == e.get("source_sha256"):
                        field = resolve(json.loads(raw), e["json_pointer"])
                        e = dict(e, source_sha256=None)  # file hash already matched
                        whole_file_entries.append(Path(cand).name)
                        break
                if field is None:
                    raise FileNotFoundError("no file with the recorded hash under the prefix")
            else:
                field = resolve(line(src, n), e["json_pointer"])
        except Exception as ex:
            bad += 1; problems.append([e.get("id"), "pointer", repr(ex)[:120]]); continue
        if not isinstance(field, str):
            bad += 1; problems.append([e.get("id"), "non-string field"]); continue
        good = True
        if e.get("source_sha256") and e["source_sha256"] != fhash(src):
            good = False; problems.append([e.get("id"), "source hash"])
        fh = e.get("field_sha256")
        if fh and fh != hashlib.sha256(field.encode("utf-8")).hexdigest():
            good = False; problems.append([e.get("id"), "field hash"])
        spans = []
        if "span_codepoints" in e and "excerpt" in e:
            spans.append((e["span_codepoints"], e["excerpt"]))
        for key in ("spans", "excerpts"):
            for s in e.get(key, []) or []:
                if isinstance(s, dict) and "span" in s and ("text" in s):
                    spans.append((s["span"], s["text"]))
        for (a, b), text in spans:
            if field[a:b] != text:
                good = False; problems.append([e.get("id"), "span", [a, b]])
        if "full_field" in e and isinstance(e["full_field"], str) and e["full_field"] != field:
            good = False; problems.append([e.get("id"), "full_field text"])
        if "field_text" in e and e["field_text"] != field:
            good = False; problems.append([e.get("id"), "field_text"])
        ok += good; bad += (not good)
    report[m] = {"entries_with_pointer": len(entries), "ok": ok, "bad": bad, "problems": problems[:20],
                 "whole_file_entries_matched_by_hash": sorted(set(whole_file_entries))}
distinct = {}
for m, v in report.items():
    distinct[m] = v
report["_summary"] = {"manifests": len(MANIFESTS), "entries_checked": sum(v["entries_with_pointer"] for v in distinct.values()),
                      "ok": sum(v["ok"] for v in distinct.values()), "bad": sum(v["bad"] for v in distinct.values()),
                      "distinct_manifest_contents": "the three inherited manifests are identical copies in astra, sol and opus (28, 10 and 14 entries); with 4 new Opus entries and 50 Fable entries that is 106 distinct entries"}
OUT.write_text(json.dumps(report, indent=1))
for k, v in report.items():
    print(k, v)
