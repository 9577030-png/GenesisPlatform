import pytest

from genesis_core import Condition, Evaluator, Fact, Rule


@pytest.fixture
def evaluator() -> Evaluator:
    return Evaluator()


def make_rule(
    condition: Condition,
) -> Rule:
    return Rule(
        id="test_rule",
        conditions=(condition,),
        result="MATCH",
        version="1",
        priority=0,
    )


def test_equal(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="temperature",
            operator="==",
            value=37,
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("temperature", 37, "C"),),
    ).matched


def test_not_equal(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="temperature",
            operator="!=",
            value=37,
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("temperature", 38, "C"),),
    ).matched


def test_greater_than(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="temperature",
            operator=">",
            value=37,
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("temperature", 38, "C"),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("temperature", 37, "C"),),
    ).matched


def test_less_than(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="temperature",
            operator="<",
            value=37,
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("temperature", 36, "C"),),
    ).matched


def test_less_or_equal(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="value",
            operator="<=",
            value=10,
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("value", 10),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("value", 11),),
    ).matched


def test_greater_or_equal(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="value",
            operator=">=",
            value=10,
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("value", 10),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("value", 9),),
    ).matched


def test_between(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="temperature",
            operator="between",
            value=(36, 38),
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("temperature", 37, "C"),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("temperature", 40, "C"),),
    ).matched


def test_in_operator(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="country",
            operator="in",
            value={"DE", "FR", "AT"},
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("country", "DE"),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("country", "US"),),
    ).matched


def test_not_in_operator(evaluator: Evaluator):
    rule = make_rule(
        Condition(
            fact="country",
            operator="not_in",
            value={"DE", "FR", "AT"},
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("country", "US"),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("country", "DE"),),
    ).matched


def test_missing_fact_returns_false(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="temperature",
            operator=">",
            value=37,
        )
    )

    evaluation = evaluator.evaluate(
        rule,
        (),
    )

    assert evaluation.matched is False
    assert evaluation.evidence[0].actual is None
    assert evaluation.evidence[0].matched is False


def test_all_rule_conditions_must_match(
    evaluator: Evaluator,
):
    rule = Rule(
        id="dangerous_environment",
        conditions=(
            Condition(
                fact="temperature",
                operator=">",
                value=90,
            ),
            Condition(
                fact="pressure",
                operator=">",
                value=10,
            ),
        ),
        result="DANGER",
        version="1",
        priority=0,
    )

    facts = (
        Fact("temperature", 97.4, "C"),
        Fact("pressure", 8.2, "bar"),
    )

    evaluation = evaluator.evaluate(
        rule,
        facts,
    )

    assert evaluation.matched is False
    assert len(evaluation.evidence) == 2
    assert evaluation.evidence[0].matched is True
    assert evaluation.evidence[1].matched is False


def test_all_rule_conditions_match(
    evaluator: Evaluator,
):
    rule = Rule(
        id="dangerous_environment",
        conditions=(
            Condition(
                fact="temperature",
                operator=">",
                value=90,
            ),
            Condition(
                fact="pressure",
                operator=">",
                value=10,
            ),
        ),
        result="DANGER",
        version="1",
        priority=0,
    )

    facts = (
        Fact("temperature", 97.4, "C"),
        Fact("pressure", 12.0, "bar"),
    )

    evaluation = evaluator.evaluate(
        rule,
        facts,
    )

    assert evaluation.matched is True


def test_evidence_contains_complete_condition_result(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="temperature",
            operator=">",
            value=90,
        )
    )

    evaluation = evaluator.evaluate(
        rule,
        (Fact("temperature", 100, "C"),),
    )

    evidence = evaluation.evidence[0]

    assert evidence.fact == "temperature"
    assert evidence.actual == 100
    assert evidence.operator == ">"
    assert evidence.expected == 90
    assert evidence.matched is True


def test_rule_metadata_is_preserved(
    evaluator: Evaluator,
):
    rule = Rule(
        id="important_rule",
        conditions=(
            Condition(
                fact="score",
                operator=">=",
                value=10,
            ),
        ),
        result={"decision": "review"},
        version="7",
        priority=42,
        conflicts_with=("other_rule",),
        supports=("supporting_rule",),
    )

    evaluation = evaluator.evaluate(
        rule,
        (Fact("score", 15),),
    )

    assert evaluation.rule_id == "important_rule"
    assert evaluation.result == {
        "decision": "review",
    }
    assert evaluation.version == "7"
    assert evaluation.priority == 42


def test_duplicate_fact_names_are_rejected(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator="==",
            value=10,
        )
    )

    with pytest.raises(
        ValueError,
        match="Duplicate fact name",
    ):
        evaluator.evaluate(
            rule,
            (
                Fact("value", 10),
                Fact("value", 20),
            ),
        ) 

def test_between_rejects_invalid_number_of_bounds(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator="between",
            value=(1, 2, 3),
        )
    )

    with pytest.raises(
        ValueError,
        match="exactly two values",
    ):
        evaluator.evaluate(
            rule,
            (Fact("value", 2),),
        )


def test_between_rejects_non_iterable(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator="between",
            value=10,
        )
    )

    with pytest.raises(
        TypeError,
        match="'between' expects exactly two values",
    ):
        evaluator.evaluate(
            rule,
            (Fact("value", 10),),
        )

def test_in_rejects_non_membership_value(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator="in",
            value=None,
        )
    )

    with pytest.raises(
        TypeError,
    ):
        evaluator.evaluate(
            rule,
            (Fact("value", 10),),
        )


def test_not_in_rejects_non_membership_value(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator="not_in",
            value=None,
        )
    )

    with pytest.raises(
        TypeError,
    ):
        evaluator.evaluate(
            rule,
            (Fact("value", 10),),
        )


def test_numeric_comparison_type_error_is_not_silenced(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator=">",
            value=10,
        )
    )

    with pytest.raises(
        TypeError,
    ):
        evaluator.evaluate(
            rule,
            (Fact("value", "not-a-number"),),
        )

def test_equal_supports_different_python_types(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="status",
            operator="==",
            value="active",
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("status", "active"),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("status", "inactive"),),
    ).matched


def test_in_supports_sequence_values(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator="in",
            value=("A", "B", "C"),
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("value", "B"),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("value", "D"),),
    ).matched


def test_between_is_inclusive(
    evaluator: Evaluator,
):
    rule = make_rule(
        Condition(
            fact="value",
            operator="between",
            value=(10, 20),
        )
    )

    assert evaluator.evaluate(
        rule,
        (Fact("value", 10),),
    ).matched

    assert evaluator.evaluate(
        rule,
        (Fact("value", 20),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("value", 9),),
    ).matched

    assert not evaluator.evaluate(
        rule,
        (Fact("value", 21),),
    ).matched













