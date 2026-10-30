"""Audit explicit content/tool name conflicts without attributing their origin."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def extract(content):
    if not isinstance(content, str):
        return None
    try:
        value = json.loads(content)
    except ValueError:
        names = set(re.findall(r'"name"\s*:\s*"([a-z_]+)"', content))
        if len(names) == 1:
            return {"name": names.pop(), "args": None, "status": "explicit_name_in_malformed_content"}
        return None
    if not isinstance(value, dict) or not isinstance(value.get("name"), str):
        return None
    args = value.get("arguments", value.get("parameters"))
    status = "named_json_call"
    if args is None:
        args = {k: v for k, v in value.items() if k not in {"name", "type"}}
        status = "named_json_flat_arguments"
    if not isinstance(args, dict):
        return None
    return {"name": value["name"], "args": args, "status": status}


def main():
    rows = []
    name_only = []
    denominator = Counter()
    available = Counter()
    for game in range(1, 21):
        for unit, source in units(game).values():
            if unit["model"] != "x-ai/grok-4.7":
                continue
            applied = unit["applied_action_record"]["action"]["action"]
            menu = unit["initial_prompt"]["payload"]["action_state"]
            denominator["all_grok_decisions"] += 1
            if applied == "accept_trade":
                denominator["applied_accepts"] += 1
            if applied == "start_auction" and "buy_property" in menu["available_actions"]:
                denominator["applied_auctions_with_direct_buy_available"] += 1
            if unit["decision_type"] == "JAIL_DECISION":
                denominator["jail_decisions"] += 1
            valid = [(index, a) for index, a in enumerate(unit["attempts"]) if a["outcome"] == "valid"]
            if not valid or unit["resolution"].get("fallback_used"):
                continue
            index, attempt = valid[-1]
            content = extract(attempt.get("assistant_content"))
            if content is None:
                available["no_explicit_parseable_content_call"] += 1
                continue
            available[content["status"]] += 1
            tool = attempt["parsed_tool_call"]
            if content["name"] == tool["name"]:
                continue
            args = tool["arguments"]
            args = json.loads(args) if isinstance(args, str) else args
            row = {"game": game, "decision_id": unit["decision_id"], "source": source,
                   "attempt_index": index, "content_name": content["name"],
                   "received_tool_name": tool["name"], "content_form": content["status"],
                   "all_arguments_equal_exactly": content["args"] == args,
                   "content_arguments": content["args"], "received_arguments": args,
                   "response_condition": attempt.get("response_condition"),
                   "physical_responses": unit["physical_responses"]}
            rows.append(row)
            if content["args"] == args:
                response = attempt["raw_response"]
                message = response["choices"][0]["message"]
                function = message["tool_calls"][0]["function"]
                assert function["name"] == tool["name"] == applied
                assert json.loads(function["arguments"]) == args
                assert message["content"] == attempt["assistant_content"]
                start = re.search(r'"(?:arguments|parameters)"\s*:\s*', message["content"]).end()
                _, length = json.JSONDecoder().raw_decode(message["content"][start:])
                argument_substring = message["content"][start:start + length]
                row["literal_argument_json_substring_equal"] = argument_substring == tool["arguments"]
                row["provider"] = response.get("provider")
                row["saved_object_type"] = response.get("object")
                row["raw_name_matches_parsed_and_applied"] = True
                name_only.append(row)
    summary = {"received_name_conflicts": len(rows),
               "conflict_content_forms": dict(Counter(r["content_form"] for r in rows)),
               "exact_same_argument_name_only_conflicts": len(name_only),
               "literal_argument_json_substrings_equal": sum(r["literal_argument_json_substring_equal"] for r in name_only),
               "name_only_routes": dict(Counter(f"{r['content_name']} -> {r['received_tool_name']}" for r in name_only)),
               "denominators": dict(denominator), "content_availability": dict(available)}
    assert len(rows) == 139 and len(name_only) == 15
    assert (denominator["applied_accepts"], denominator["applied_auctions_with_direct_buy_available"], denominator["jail_decisions"]) == (28, 32, 61)
    client = ROOT / "python/packages/arena/src/monopoly_arena/openrouter_client.py"
    report = {"summary": summary, "name_only_cases": name_only, "all_named_conflicts": rows,
              "source_code_sha256": {str(client.relative_to(ROOT)): hashlib.sha256(client.read_bytes()).hexdigest()},
              "mechanism_boundary": "Saved raw tool name agrees with parsed and applied name in all15name-only cases, so the discrepancy is already present at the saved-response layer. This does not identify base-model emission. Upstream provider/OpenRouter processing is unexcluded. The local stream accumulator keys tool fragments by index and emits object chat.completion after assembly. Stream status and possible fragment association cannot be established from that object type; no HTTP stream flag or raw deltas were verified for these cases.",
              "provenance": "Independent mechanical reconstruction with peer target counts known. First strict nested-argument JSON pass found137conflicts; original inspection added G9d194flat named arguments and G19d224explicit named malformed fragment. This distinguishes parser coverage from behavior correction. All15exact argument cases have structured JSON calls with equal parsed objects, including identical public and private string values. Only5have literally identical serialized argument substrings; spacing and escaping differ in the other10. Use parsed argument equality, not15byte-identicalJSONarguments.",
              "limits": "One malformed fragment is a content-name discrepancy, not a valid alternate action. Content parse availability differs across providers and response conditions, so139is not a latent intent or cross-model prevalence rate. Name-only4reject-to-accept cases are4of28appliedGrokaccepts;7buy-to-auction are7of32voluntaryauctionstartswithbuylegal;4jailnameconflicts are4of61jaildecisions. No strategy, deception or uniquely coherent intention is inferred.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "received_name_conflict_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
