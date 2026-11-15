"""Independent spot-check of argument-bearing quotations against canonical decisions.jsonl.
Reads each manifest pointer from the original file (by line and JSON pointer), checks file hash,
field hash and that every displayed span is the exact substring at its offsets.
Run from repo root: python3 -I docs/research_raw/paper_revision_2026-11-11/reviews/opus/tools/verify_quotes.py"""
import hashlib, json, pathlib
ROOT = pathlib.Path.cwd(); REV = ROOT / "docs/research_raw/paper_revision_2026-11-11"
man = json.loads((REV / "full_drafts/fable_5_2/data/quote_manifest.json").read_text())["quotes"]
WANT = {"g1-d306-offer","g1-d307-counter","g1-d309-accept-note","in-g1-d308-weapon","in-g1-d313-distress","g2-d118-liquidity-pitch",
        "g2-d124-price","g2-d124-note","g2-d128-note","g2-d197-reverse","g7-d39-liquid","g7-d42-final","g7-d42-ceiling",
        "g7-d141-timed-bid","g7-d142-ask-note","in-g7-d43-reinvest","g15-d166-appeal","g15-d169-refusal-note","g15-d174-sweetener",
        "g15-d175-final-refusal","g15-d176-wait-note","g18-d420-note","g18-d431-assurance","g18-d441-invocation","g18-d442-withdrawal",
        "g18-d442-explanation","in-g18-d443-rebuild","g17-d234-public","g13-d250-insurance","g13-d252-floor","g13-d252-omission",
        "g13-d253-accept","g12-d249-content","g12-d249-note","g12-d249-public","g20-d96-appeal","g20-d97-recognition",
        "g20-d100-sale","g20-d101-refusal","in-g20-d95-cashstarved","in-g20-d129-houses","g19-d135-public","g19-d135-note","g19-d136-public"}
def ptr(obj, p):
    for part in p.strip("/").split("/"):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj
res = []; cache = {}
for q in man:
    if q["id"] not in WANT: continue
    src = ROOT / q["source"]
    if src not in cache:
        b = src.read_bytes(); cache[src] = (hashlib.sha256(b).hexdigest(), b.decode().splitlines())
    fh, lines = cache[src]
    rec = json.loads(lines[q["jsonl_line_1based"] - 1])
    val = ptr(rec, q["json_pointer"])
    if not isinstance(val, str): val = json.dumps(val, ensure_ascii=False)
    ok_spans = all(val[s["span"][0]:s["span"][1]] == s["text"] for s in q["spans"])
    did = int(rec["decision_id"].rsplit("-", 1)[1])
    res.append({"id": q["id"], "file_hash_ok": fh == q["source_sha256"],
                "field_hash_ok": hashlib.sha256(val.encode()).hexdigest() == q["field_sha256"],
                "spans_exact": ok_spans, "decision_matches": did == q["decision"], "game": q["game"],
                "pointer": q["json_pointer"], "player": rec.get("player_name"), "delivery_checked": q.get("delivery_checked")})
found = {r["id"] for r in res}
out = {"checked": len(res), "missing_from_manifest": sorted(WANT - found),
       "all_ok": all(r["file_hash_ok"] and r["field_hash_ok"] and r["spans_exact"] and r["decision_matches"] for r in res), "rows": res}
p = REV / "reviews/opus/data/quote_spotcheck.json"; p.write_text(json.dumps(out, indent=1))
print(out["checked"], out["all_ok"], out["missing_from_manifest"])
for r in res:
    if not (r["file_hash_ok"] and r["field_hash_ok"] and r["spans_exact"] and r["decision_matches"]): print("FAIL", r)
