import pytest

from genesis_core import Evidence, RuleEvaluation


def test_evidence_stores_complete_result():
    evidence = Evidence(
        fact="temperature",
        actual=100,
        operator=">",
        expected=90,
        matched=True,
    )

    assert evidence.fact == "temperature"
    assert evidence.actual == 100
    assert evidence.operator == ">"
    assert evidence.expected == 90
    assert evidence.matched is True


def test_evidence_supports_arbitrary_values():
    evidence = Evidence(
        fact="status",
        actual={"state": "active"},
        operator="==",
        expected={"state": "active"},
        matched=True,
    )

    assert evidence.actual == {"state": "active"}
    assert evidence.expected == {"state": "active"}


def test_rule_evaluation_stores_result():
    evaluation = RuleEvaluation(
        rule_id="test_rule",
        matched=True,
        evidence=(),
        result={"action": "accept"},
    )

    assert evaluation.rule_id == "test_rule"
    assert evaluation.matched is True
    assert evaluation.evidence == ()
    assert evaluation.result == {"action": "accept"}


def test_rule_evaluation_preserves_priority_and_version():
    evaluation = RuleEvaluation(
        rule_id="test_rule",
        matched=True,
        evidence=(),
        result="OK",
        priority=100,
        version="7",
    )

    assert evaluation.priority == 100
    assert evaluation.version == "7"


def test_rule_evaluation_accepts_multiple_evidence_items():
    evidence = (
        Evidence(
            fact="temperature",
            actual=100,
            operator=">",
            expected=90,
            matched=True,
        ),
        Evidence(
            fact="pressure",
            actual=8,
            operator=">",
            expected=10,
            matched=False,
        ),
    )

    evaluation = RuleEvaluation(
        rule_id="danger",
        matched=False,
        evidence=evidence,
        result="DANGER",
    )

    assert len(evaluation.evidence) == 2
    assert evaluation.evidence[0].matched is True
    assert evaluation.evidence[1].matched is False


def test_evidence_is_immutable():
    evidence = Evidence(
        fact="value",
        actual=10,
        operator="==",
        expected=10,
        matched=True,
    )

    with pytest.raises(AttributeError):
        evidence.matched = False


def test_rule_evaluation_is_immutable():
    evaluation = RuleEvaluation(
        rule_id="test_rule",
        matched=True,
        evidence=(),
        result="OK",
    )

    with pytest.raises(AttributeError):
        evaluation.matched = False


def test_empty_evidence_is_valid():
    evaluation = RuleEvaluation(
        rule_id="no_conditions",
        matched=True,
        evidence=(),
        result="OK",
    )

    assert evaluation.evidence == ()