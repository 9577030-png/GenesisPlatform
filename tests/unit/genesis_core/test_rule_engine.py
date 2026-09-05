import pytest

from genesis_core import (
    Condition,
    Fact,
    Rule,
    RuleEngine,
)


def test_rule_engine_evaluates_multiple_rules():
    rules = (
        Rule(
            id="temperature_high",
            conditions=(
                Condition(
                    fact="temperature",
                    operator=">",
                    value=90,
                ),
            ),
            result="HIGH",
        ),
        Rule(
            id="pressure_high",
            conditions=(
                Condition(
                    fact="pressure",
                    operator=">",
                    value=10,
                ),
            ),
            result="PRESSURE_HIGH",
        ),
    )

    facts = (
        Fact("temperature", 100, "C"),
        Fact("pressure", 12, "bar"),
    )

    evaluations = RuleEngine().evaluate(
        rules,
        facts,
    )

    assert len(evaluations) == 2
    assert evaluations[0].rule_id == "temperature_high"
    assert evaluations[1].rule_id == "pressure_high"
    assert evaluations[0].matched is True
    assert evaluations[1].matched is True


def test_rule_engine_returns_only_matched_rules():
    rules = (
        Rule(
            id="temperature_high",
            conditions=(
                Condition(
                    fact="temperature",
                    operator=">",
                    value=90,
                ),
            ),
            result="HIGH",
        ),
        Rule(
            id="pressure_high",
            conditions=(
                Condition(
                    fact="pressure",
                    operator=">",
                    value=10,
                ),
            ),
            result="PRESSURE_HIGH",
        ),
    )

    facts = (
        Fact("temperature", 100, "C"),
        Fact("pressure", 8, "bar"),
    )

    evaluations = RuleEngine().evaluate_matched(
        rules,
        facts,
    )

    assert len(evaluations) == 1
    assert evaluations[0].rule_id == "temperature_high"
    assert evaluations[0].matched is True


def test_rule_engine_evaluates_empty_rules():
    evaluations = RuleEngine().evaluate(
        (),
        (
            Fact("temperature", 100, "C"),
        ),
    )

    assert evaluations == ()


def test_rule_engine_preserves_rule_order():
    rules = (
        Rule(
            id="first",
            conditions=(
                Condition(
                    fact="value",
                    operator=">",
                    value=0,
                ),
            ),
            result="FIRST",
        ),
        Rule(
            id="second",
            conditions=(
                Condition(
                    fact="value",
                    operator=">",
                    value=0,
                ),
            ),
            result="SECOND",
        ),
    )

    evaluations = RuleEngine().evaluate(
        rules,
        (
            Fact("value", 10),
        ),
    )

    assert [
        evaluation.rule_id
        for evaluation in evaluations
    ] == [
        "first",
        "second",
    ]


def test_rule_engine_supports_arbitrary_result():
    rule = Rule(
        id="bank_transaction",
        conditions=(
            Condition(
                fact="amount",
                operator=">",
                value=1000,
            ),
        ),
        result={
            "action": "REVIEW",
            "reason": "large transaction",
        },
    )

    result = RuleEngine().evaluate(
        (rule,),
        (Fact("amount", 1500),),
    )

    assert result[0].matched is True
    assert result[0].result == {
        "action": "REVIEW",
        "reason": "large transaction",
    }


def test_rule_engine_keeps_multiple_fact_types():
    rule = Rule(
        id="mixed",
        conditions=(
            Condition("status", "==", "active"),
            Condition("score", ">=", 10),
            Condition("country", "in", {"DE", "FR"}),
        ),
        result="MATCH",
    )

    result = RuleEngine().evaluate(
        (rule,),
        (
            Fact("status", "active"),
            Fact("score", 12),
            Fact("country", "DE"),
        ),
    )

    assert result[0].matched is True


def test_rule_engine_returns_evidence_for_every_condition():
    rule = Rule(
        id="two_conditions",
        conditions=(
            Condition("temperature", ">", 90),
            Condition("pressure", ">=", 10),
        ),
        result="DANGER",
    )

    result = RuleEngine().evaluate(
        (rule,),
        (
            Fact("temperature", 100, "C"),
            Fact("pressure", 8, "bar"),
        ),
    )

    evaluation = result[0]

    assert evaluation.matched is False
    assert len(evaluation.evidence) == 2
    assert evaluation.evidence[0].matched is True
    assert evaluation.evidence[1].matched is False


def test_rule_engine_preserves_priority_and_version():
    rule = Rule(
        id="important",
        conditions=(
            Condition(
                fact="value",
                operator="==",
                value=1,
            ),
        ),
        result="OK",
        version="3",
        priority=100,
    )

    result = RuleEngine().evaluate(
        (rule,),
        (Fact("value", 1),),
    )

    assert result[0].priority == 100
    assert result[0].version == "3"


def test_rule_engine_accepts_rule_generator():
    def rules():
        yield Rule(
            id="first",
            conditions=(
                Condition(
                    fact="value",
                    operator=">",
                    value=0,
                ),
            ),
            result="FIRST",
        )
        yield Rule(
            id="second",
            conditions=(
                Condition(
                    fact="value",
                    operator="<",
                    value=20,
                ),
            ),
            result="SECOND",
        )

    evaluations = RuleEngine().evaluate(
        rules(),
        (Fact("value", 10),),
    )

    assert len(evaluations) == 2
    assert evaluations[0].rule_id == "first"
    assert evaluations[1].rule_id == "second"


def test_rule_engine_accepts_fact_generator():
    rule = Rule(
        id="generated_facts",
        conditions=(
            Condition(
                fact="value",
                operator="==",
                value=10,
            ),
        ),
        result="MATCH",
    )

    def facts():
        yield Fact("value", 10)

    evaluations = RuleEngine().evaluate(
        (rule,),
        facts(),
    )

    assert evaluations[0].matched is True


def test_rule_rejects_empty_id():
    with pytest.raises(
        ValueError,
        match="Rule id cannot be empty",
    ):
        Rule(
            id="",
            conditions=(),
        )


def test_rule_rejects_non_string_id():
    with pytest.raises(
        TypeError,
        match="Rule id must be a string",
    ):
        Rule(
            id=123,
            conditions=(),
        )


def test_rule_rejects_non_tuple_conditions():
    with pytest.raises(
        TypeError,
        match="Rule conditions must be a tuple",
    ):
        Rule(
            id="invalid",
            conditions=[],
        )


def test_rule_rejects_invalid_condition_members():
    with pytest.raises(
        TypeError,
        match="Rule conditions must contain only Condition",
    ):
        Rule(
            id="invalid",
            conditions=(Condition("value", "==", 1), "invalid"),
        )


def test_rule_condition_count():
    rule = Rule(
        id="count",
        conditions=(
            Condition("a", "==", 1),
            Condition("b", "==", 2),
        ),
    )

    assert rule.condition_count == 2