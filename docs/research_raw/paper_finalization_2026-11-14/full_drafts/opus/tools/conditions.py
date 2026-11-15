"""Response-condition counts over all resolved decisions. Read-only.

Counts refused attempts by model and game, recovery attempts, readable
provider reasoning on final attempts, and the requested tool_choice recorded in
saved outgoing request records where present.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import lib


def main() -> None:
    refused = Counter()
    refused_first = Counter()
    first_attempts = Counter()
    refused_by_game_opus = {}
    readable = Counter()
    finals = Counter()
    conditions = Counter()
    for g in range(1, 21):
        rg = [0, 0]
        for idx, z in lib.decisions(g).items():
            rz = z.get("decision_resolved")
            if not rz:
                continue
            m = lib.label(rz["player_name"])
            atts = rz.get("attempts", [])
            finals[m] += 1
            for k, a in enumerate(atts):
                conditions[(m, a.get("response_condition"), a.get("outcome"))] += 1
                if a.get("outcome") == "refused":
                    refused[m] += 1
                    if k == 0:
                        refused_first[m] += 1
            if atts:
                first_attempts[m] += 1
                if m == "Opus":
                    rg[1] += 1
                    rg[0] += atts[0].get("outcome") == "refused"
                msg = lib.message_of(atts[-1]) or {}
                if isinstance(msg.get("reasoning"), str) and msg["reasoning"].strip():
                    readable[m] += 1
        refused_by_game_opus[g] = rg
    # Liquidation payloads: which fields describe the debtor's holdings and menu
    liq_n, liq_keys, liq_value_fields = 0, Counter(), Counter()
    for g in range(1, 21):
        for idx, z in lib.decisions(g).items():
            st = z.get("decision_started")
            if not st or st.get("decision_type") != "LIQUIDATION_DECISION":
                continue
            liq_n += 1
            p = st["prompt_payload"]
            for h in p["game_state"]["you"]["holdings"]["owned"]:
                liq_keys.update(h.keys())
            liq_keys.update("options." + k for k in p["action_state"]["scenario"]["options"])
            blob = json.dumps(p["action_state"]) + json.dumps(p["game_state"]["you"])
            for w in ["mortgage_value", '"price"', "house_cost", "salvage", '"group"', "color_group"]:
                if w in blob:
                    liq_value_fields[w] += 1
    out = {
        "liquidation_payloads": {"n": liq_n, "holding_and_menu_fields": dict(liq_keys), "value_field_hits": dict(liq_value_fields)},
        "refused_attempts": dict(refused),
        "refused_first_attempts": dict(refused_first),
        "opus_first_attempt_refusals_by_game": refused_by_game_opus,
        "readable_provider_reasoning_on_final_attempt": {m: f"{readable[m]}/{finals[m]}" for m in finals},
        "attempt_conditions": {f"{a}|{b}|{c}": n for (a, b, c), n in sorted(conditions.items())},
    }
    lib.write_json("response_conditions.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "attempt_conditions"}, indent=1))


if __name__ == "__main__":
    main()
