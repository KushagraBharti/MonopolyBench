"""Preserve complete-source semantic audits nominated by Astra after initial labels."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units

HERE = Path(__file__).resolve().parent


def main():
    game = units(12)
    first, first_source = game[61]
    second, second_source = game[239]
    action61 = first["applied_action_record"]["action"]
    action239 = second["applied_action_record"]["action"]
    assert "Without Illinois you still can't build on Tennessee" in action61["public_message"]
    assert action61["args"]["request"]["properties"] == ["ILLINOIS_AVENUE"]
    own = second["initial_prompt"]["payload"]["game_state"]["you"]
    levels = {s["space_key"]: s["houses"] for s in own["holdings"]["owned"]
              if s["space_key"] in {"ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"}}
    assert list(levels.values()) == [2, 2, 3]
    assert own["cash"] == 43 and "pinks 2-2-3" in action239["private_thought"]
    sale = game[238][0]["applied_action_record"]["action"]
    assert sale["args"]["sell_plan"] == [
        {"count": 1, "kind": "HOUSE", "space_key": "ST_CHARLES_PLACE"},
        {"count": 1, "kind": "HOUSE", "space_key": "STATES_AVENUE"},
    ]
    report = {
        "sources": {"61": first_source, "238": game[238][1], "239": second_source},
        "action61": action61, "action239": action239, "post_sale_levels239": levels,
        "semantic_adjudication61": "The sentence does not establish that Illinois belongs to orange or is required to build Tennessee. It can accurately say giving up Illinois still leaves the recipient unable to develop its lone Tennessee. The extractor's causal-dependency interpretation is unestablished. Returned retry reasoning has a confusing offer-direction phrase but no asserted orange-membership premise. This corroborates Sol's initial qualified judgment, now after complete original reading.",
        "semantic_adjudication239": "The current public hold is forward-looking. Applied private explicitly gives2/2/3, and returned provider explicitly recognizes the StCharles/States sales and100payment. Stale-state claim is contradicted, corroborating Sol's initial contradicted label. The separate applied next-roll1claim is impossible on ordinary two dice and is not excused by rejecting the stale-state label.",
        "reading_scope": "Complete original061both attempts and239all returned channels, full actual memories, menus and events read after Astra's semantic nomination.238applied action/menu/events checked, not its complete returned provider text. Opaque text remains unavailable.",
        "provenance": "Initial source-entry labels predate these peer-informed full-original checks. Agreement is not additional independent annotation or evidence of a causal mechanism.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g12_semantic_context_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"61_dependency_falsity": "unestablished", "239_stale_state": "contradicted", "239_levels": levels}))


if __name__ == "__main__":
    main()
