"""Check the disclosure's received boundary separately from name conflicts."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
games = json.loads((ROOT / "docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json").read_text())["games"]
run = ROOT / next(g["run"] for g in games if g["game"] == 20)
source = run / "decisions.jsonl"
row = next(r for r in map(json.loads, source.read_text().splitlines())
           if r["phase"] == "decision_resolved" and r["decision_id"].endswith("000001"))
index, attempt = next((i, a) for i, a in enumerate(row["attempts"]) if a["outcome"] == "valid")
path = run.parent / "cloud/calls" / (attempt["call_id"] + ".response.json")
saved = json.loads(path.read_text())
request = json.loads(saved["request_payload_raw"])
response = json.loads(saved["response_text"])
assert request.get("stream") is not True
assert response["choices"] == saved["response_json"]["choices"]
message = response["choices"][0]["message"]
tool = message["tool_calls"][0]["function"]
args = json.loads(tool["arguments"])
assert tool["name"] == row["final_action"]["action"]
assert args["public_message"] == row["final_action"]["public_message"]
assert "private_thought" in args["public_message"]
assert message.get("content") == attempt["assistant_content"]
result = {"decision_id": row["decision_id"], "selected_attempt": index,
          "raw_nonstreamed_body_contains_public_fragment": True,
          "matches_applied_public_message": True,
          "scope": "Excludes local stream assembly for this disclosure; generation/provider/OpenRouter unresolved.",
          "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (source, path)}}
(HERE / "g20_transport_check.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
