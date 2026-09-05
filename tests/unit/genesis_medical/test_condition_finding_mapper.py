from datetime import UTC, datetime

from genesis_medical.adapters.condition_finding_mapper import (
    ConditionFindingMapper,
)
from genesis_medical.domain.rule_version import RulePriority, RuleVersion
from genesis_medical.domain.value_objects.risk_level import RiskLevel


def make_rule() -> RuleVersion:
    return RuleVersion(
        rule_id="glucose_rule",
        name="High glucose",
        conditions=[],
        actions=[],
        created_at=datetime.now(UTC),
        created_by="test",
        version_id=1,
        priority=RulePriority.HIGH,
        comment="Glucose rule",
    )


def test_condition_is_converted_to_clinical_finding():
    rule = make_rule()

    condition = {
        "id": "high_glucose",
        "label": "High glucose",
        "scoring": 8,
        "risk": "HIGH",
        "recommendations": [
            "Repeat glucose test",
        ],
        "description": "Glucose above reference range",
    }

    finding = ConditionFindingMapper.to_finding(
        condition,
        rule,
    )

    assert finding.id == "high_glucose"
    assert finding.title == "High glucose"
    assert finding.probability == 0.8
    assert finding.risk == RiskLevel.HIGH
    assert finding.evidence == [
        "Repeat glucose test",
    ]
    assert finding.description == (
        "Glucose above reference range"
    )


def test_probability_is_limited_to_one():
    rule = make_rule()

    condition = {
        "scoring": 15,
    }

    finding = ConditionFindingMapper.to_finding(
        condition,
        rule,
    )

    assert finding.probability == 1.0


def test_default_scoring_and_risk_are_preserved():
    rule = make_rule()

    condition = {}

    finding = ConditionFindingMapper.to_finding(
        condition,
        rule,
    )

    assert finding.id == "glucose_rule"
    assert finding.title == "High glucose"
    assert finding.probability == 0.5
    assert finding.risk == RiskLevel.NORMAL
    assert finding.evidence == []
    assert finding.description == "Glucose rule"


def test_explicit_medium_risk_overrides_probability():
    rule = make_rule()

    condition = {
        "scoring": 8,
        "risk": "MEDIUM",
    }

    finding = ConditionFindingMapper.to_finding(
        condition,
        rule,
    )

    assert finding.probability == 0.8
    assert finding.risk == RiskLevel.MEDIUM


def test_explicit_critical_risk_is_supported():
    rule = make_rule()

    condition = {
        "scoring": 3,
        "risk": "CRITICAL",
    }

    finding = ConditionFindingMapper.to_finding(
        condition,
        rule,
    )

    assert finding.probability == 0.3
    assert finding.risk == RiskLevel.CRITICAL
