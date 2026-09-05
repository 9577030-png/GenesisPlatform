import pytest

from genesis_core import Condition, Rule, RuleSet


def make_rule(rule_id: str) -> Rule:
    return Rule(
        id=rule_id,
        conditions=(
            Condition(
                fact="value",
                operator="==",
                value=10,
            ),
        ),
        result=rule_id,
    )


def test_rule_set_preserves_rule_order():
    rules = RuleSet(
        (
            make_rule("first"),
            make_rule("second"),
            make_rule("third"),
        )
    )

    assert [rule.id for rule in rules] == [
        "first",
        "second",
        "third",
    ]


def test_rule_set_has_length():
    rules = RuleSet(
        (
            make_rule("first"),
            make_rule("second"),
        )
    )

    assert len(rules) == 2


def test_rule_set_get_returns_rule():
    rules = RuleSet(
        (
            make_rule("first"),
            make_rule("second"),
        )
    )

    assert rules.get("second").id == "second"


def test_rule_set_get_returns_none_for_unknown_rule():
    rules = RuleSet(
        (
            make_rule("first"),
        )
    )

    assert rules.get("missing") is None


def test_rule_set_require_returns_rule():
    rules = RuleSet(
        (
            make_rule("first"),
        )
    )

    assert rules.require("first").id == "first"


def test_rule_set_require_raises_for_unknown_rule():
    rules = RuleSet(
        (
            make_rule("first"),
        )
    )

    with pytest.raises(
        KeyError,
        match="Rule not found",
    ):
        rules.require("missing")


def test_rule_set_rejects_duplicate_rule_ids():
    with pytest.raises(
        ValueError,
        match="RuleSet rule ids must be unique",
    ):
        RuleSet(
            (
                make_rule("same"),
                make_rule("same"),
            )
        )


def test_rule_set_rejects_non_tuple_rules():
    with pytest.raises(
        TypeError,
        match="RuleSet rules must be a tuple",
    ):
        RuleSet([])


def test_rule_set_rejects_invalid_rule_members():
    with pytest.raises(
        TypeError,
        match="RuleSet rules must contain only Rule",
    ):
        RuleSet(
            (
                make_rule("valid"),
                "invalid",
            )
        )


def test_rule_set_is_immutable():
    rules = RuleSet(
        (
            make_rule("first"),
        )
    )

    with pytest.raises(AttributeError):
        rules.rules = (make_rule("second"),)