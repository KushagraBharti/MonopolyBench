"""Keep the shared TypeScript campaign contract aligned with the schema and real campaigns."""
import json
from pathlib import Path
import re

import pytest

from monopoly_arena.research_registry import validate_campaign_config


ROOT = Path(__file__).resolve().parents[4]
CAMPAIGNS = sorted((ROOT / "campaigns").glob("*.json"))


def _ts_type_fields(name: str) -> tuple[set[str], str]:
    source = (ROOT / "contracts/ts/research.ts").read_text()
    match = re.search(rf"export type {name} = {{\n(.*?)\n}}\n", source, re.S)
    assert match, f"{name} not found in contracts/ts/research.ts"
    block = match.group(1)
    return {field.group(1) for field in re.finditer(r"^  (\w+)\??:", block, re.M)}, block


def test_campaign_v2_type_covers_every_schema_property_and_policy_version():
    schema = json.loads((ROOT / "contracts/schemas/research_registry.schema.json").read_text())
    definition = schema["$defs"]["campaignConfigV2"]
    fields, block = _ts_type_fields("LongHorizonCampaignConfigV2")
    assert set(definition["properties"]) <= fields
    union = re.search(r"^  execution_policy_version: (.*)$", block, re.M)
    assert union is not None
    assert set(re.findall(r"'(execution_policy_v\d+)'", union.group(1))) == set(
        definition["properties"]["execution_policy_version"]["enum"])


@pytest.mark.parametrize("path", CAMPAIGNS, ids=[path.name for path in CAMPAIGNS])
def test_every_v2_campaign_validates_and_fits_the_shared_type(path):
    config = json.loads(path.read_text())
    if config.get("campaign_config_version") != "long_horizon_campaign_config_v2":
        pytest.skip("Not a v2 campaign configuration")
    validate_campaign_config(config)
    fields, _ = _ts_type_fields("LongHorizonCampaignConfigV2")
    assert set(config) <= fields, f"Undeclared in the TypeScript contract: {sorted(set(config) - fields)}"
