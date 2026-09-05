from genesis_medical.application.conflict_resolver import ConflictResolver
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.rule_version import RulePriority, RuleVersion
from genesis_medical.domain.value_objects.risk_level import RiskLevel


def make_finding(
    finding_id: str,
    probability: float = 0.5,
) -> ClinicalFinding:
    return ClinicalFinding(
        id=finding_id,
        title=finding_id,
        probability=probability,
        risk=RiskLevel.HIGH,
    )


def make_rule(
    rule_id: str,
    *,
    priority: RulePriority = RulePriority.MEDIUM,
    conflicts_with=None,
    condition_ids=None,
) -> RuleVersion:
    conditions = [
        {"id": condition_id}
        for condition_id in (condition_ids or [])
    ]

    return RuleVersion(
        rule_id=rule_id,
        name=rule_id,
        conditions=conditions,
        actions=[],
        created_at=__import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
        created_by="test",
        priority=priority,
        conflicts_with=conflicts_with or [],
        supports=[],
        is_active=True,
    )


def test_empty_findings_return_empty():
    resolver = ConflictResolver()

    assert resolver.resolve([], {}) == []


def test_non_conflicting_findings_are_preserved():
    resolver = ConflictResolver()

    findings = [
        make_finding("rule_a"),
        make_finding("rule_b"),
    ]

    rules = {
        "rule_a": make_rule("rule_a"),
        "rule_b": make_rule("rule_b"),
    }

    result = resolver.resolve(
        findings,
        rules,
        {
            "condition_high": "rule_a",
            "other": "rule_b",
        },
    )

    assert {finding.id for finding in result} == {
        "rule_a",
        "rule_b",
    }


def test_higher_priority_rule_wins_conflict():
    resolver = ConflictResolver()

    findings = [
        make_finding("low"),
        make_finding("high"),
    ]

    rules = {
        "low": make_rule(
            "low",
            priority=RulePriority.LOW,
            conflicts_with=["high"],
        ),
        "high": make_rule(
            "high",
            priority=RulePriority.HIGH,
            conflicts_with=["low"],
        ),
    }

    result = resolver.resolve(
        findings,
        rules,
        {
            "condition_high": "rule_a",
            "other": "rule_b",
        },
    )

    assert [finding.id for finding in result] == [
        "high",
    ]


def test_conflict_is_symmetric():
    resolver = ConflictResolver()

    findings = [
        make_finding("a"),
        make_finding("b"),
    ]

    rules = {
        "a": make_rule(
            "a",
            priority=RulePriority.MEDIUM,
            conflicts_with=["b"],
        ),
        "b": make_rule(
            "b",
            priority=RulePriority.LOW,
            conflicts_with=[],
        ),
    }

    result = resolver.resolve(
        findings,
        rules,
        {
            "condition_high": "rule_a",
            "other": "rule_b",
        },
    )

    assert [finding.id for finding in result] == [
        "a",
    ]


def test_condition_finding_is_mapped_back_to_rule():
    resolver = ConflictResolver()

    findings = [
        make_finding("condition_high"),
        make_finding("other"),
    ]

    rules = {
        "rule_a": make_rule(
            "rule_a",
            priority=RulePriority.HIGH,
            conflicts_with=["rule_b"],
            condition_ids=["condition_high"],
        ),
        "rule_b": make_rule(
            "rule_b",
            priority=RulePriority.LOW,
            conflicts_with=[],
            condition_ids=["other"],
        ),
    }

    result = resolver.resolve(
        findings,
        rules,
        {
            "condition_high": "rule_a",
            "other": "rule_b",
        },
    )

    assert [finding.id for finding in result] == [
        "condition_high",
    ]


def test_duplicate_finding_ids_are_removed():
    resolver = ConflictResolver()

    findings = [
        make_finding("same"),
        make_finding("same"),
        make_finding("other"),
    ]

    rules = {
        "same": make_rule("same"),
        "other": make_rule("other"),
    }

    result = resolver.resolve(
        findings,
        rules,
        {
            "condition_high": "rule_a",
            "other": "rule_b",
        },
    )

    assert [finding.id for finding in result] == [
        "same",
        "other",
    ]


def test_unknown_finding_uses_own_id_as_rule_id():
    resolver = ConflictResolver()

    finding = make_finding("unknown")

    result = resolver.resolve(
        [finding],
        {},
    )

    assert result == [finding]


def test_multiple_conflicts_keep_highest_priority():
    resolver = ConflictResolver()

    findings = [
        make_finding("low"),
        make_finding("medium"),
        make_finding("high"),
    ]

    rules = {
        "low": make_rule(
            "low",
            priority=RulePriority.LOW,
            conflicts_with=["medium", "high"],
        ),
        "medium": make_rule(
            "medium",
            priority=RulePriority.MEDIUM,
            conflicts_with=["low", "high"],
        ),
        "high": make_rule(
            "high",
            priority=RulePriority.HIGH,
            conflicts_with=["low", "medium"],
        ),
    }

    result = resolver.resolve(
        findings,
        rules,
        {
            "condition_high": "rule_a",
            "other": "rule_b",
        },
    )

    assert [finding.id for finding in result] == [
        "high",
    ]


def test_explicit_finding_rule_mapping_is_used():
    resolver = ConflictResolver()

    findings = [
        make_finding("finding_a"),
        make_finding("finding_b"),
    ]

    rules = {
        "rule_a": make_rule(
            "rule_a",
            priority=RulePriority.HIGH,
            conflicts_with=["rule_b"],
        ),
        "rule_b": make_rule(
            "rule_b",
            priority=RulePriority.LOW,
        ),
    }

    result = resolver.resolve(
        findings,
        rules,
        {
            "finding_a": "rule_a",
            "finding_b": "rule_b",
        },
    )

    assert [finding.id for finding in result] == [
        "finding_a",
    ]    
