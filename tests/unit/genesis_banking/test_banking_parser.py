from genesis_banking import BankingRuleParser
from genesis_core import Rule


def test_banking_parser_returns_core_rule() -> None:
    rule = BankingRuleParser().parse(
        {
            "id": "review_large",
            "conditions": [
                {"fact": "amount", "operator": ">", "value": 1000},
            ],
            "result": {"action": "review"},
        }
    )

    assert isinstance(rule, Rule)
    assert rule.id == "review_large"
