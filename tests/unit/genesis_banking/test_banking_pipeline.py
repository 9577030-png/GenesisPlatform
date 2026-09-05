from genesis_core import Fact, RuleEngine
from genesis_banking import get_domain_descriptor
from genesis_banking.resolvers import BankingRuleResolver


def test_banking_descriptor_loads_rule_set() -> None:
    descriptor = get_domain_descriptor()
    rule_set = descriptor.get_rule_loader().load()

    assert descriptor.name == "banking"
    assert rule_set.rules


def test_banking_rules_run_on_unchanged_core() -> None:
    descriptor = get_domain_descriptor()
    rule_set = descriptor.get_rule_loader().load()

    evaluations = RuleEngine().evaluate_matched(
        rule_set.rules,
        (
            Fact("amount", 15000),
            Fact("currency", "USD"),
        ),
    )

    resolved = BankingRuleResolver().resolve(evaluations)

    assert {item.rule_id for item in resolved} == {
        "high_value_foreign_currency",
        "high_value_review",
        "foreign_currency_review",
    }
