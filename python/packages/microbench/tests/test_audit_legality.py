from copy import deepcopy
import pytest
from monopoly_microbench.catalog import load_scenario
from monopoly_microbench.scorer import score_action


def test_unaffordable_bid_is_invalid_even_with_polished_text():
    scenario = load_scenario("auction-bo-railroad-third-railroad-10")
    action = deepcopy(scenario["reference_policy"]["action"])
    action["args"]["bid_amount"] = 1_000_620
    action["private_thought"] = "value monopoly cash reserve optimal safe bid"
    action["public_message"] = "This is a great deal."
    result = score_action(scenario, action)
    assert result["label"] == "invalid" and result["total"] == 0


def test_words_do_not_change_action_quality_score():
    scenario = load_scenario("buy-or-auction-boardwalk-fame-bias-low-cash-15")
    action = deepcopy(scenario["reference_policy"]["action"])
    baseline = score_action(scenario, action)
    action["private_thought"] = "nonsense"
    action["public_message"] = ""
    assert score_action(scenario, action)["total"] == baseline["total"]


@pytest.mark.parametrize("bid", [620.25, "620"])
def test_schema_invalid_bid_cannot_score_as_an_economic_action(bid):
    scenario = load_scenario("auction-bo-railroad-third-railroad-10")
    action = deepcopy(scenario["reference_policy"]["action"])
    action["args"]["bid_amount"] = bid
    result = score_action(scenario, action)
    assert result["label"] == "invalid" and result["total"] == 0
