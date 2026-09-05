from datetime import UTC, datetime

import pytest

from genesis_medical.adapters.rule_compiler import RuleCompiler
from genesis_core import Rule
from genesis_medical.domain.rule_version import RulePriority, RuleVersion
from genesis_medical.adapters.compiled_rule import CompiledRule
from genesis_medical.domain.value_objects.gender import Gender


def make_rule_version() -> RuleVersion:
    return RuleVersion(
        rule_id="test_rule",
        name="Test rule",
        conditions=[
            {
                "id": "temperature_high",
                "parameter": "temperature",
                "min": 90,
            },
            {
                "id": "pressure_high",
                "parameter": "pressure",
                "min": 10,
            },
        ],
        actions=[
            {
                "type": "result",
                "code": "DANGER",
            }
        ],
        created_at=datetime.now(UTC),
        created_by="test",
        version_id=1,
        priority=RulePriority.HIGH,
        conflicts_with=["safe_environment"],
        supports=["danger_warning"],
        is_active=True,
    )


def test_rule_version_is_compiled_to_multiple_rules():
    rule_version = make_rule_version()

    compiled_rules = RuleCompiler.compile(rule_version)

    assert isinstance(compiled_rules, tuple)
    assert len(compiled_rules) == 2

    assert all(
        isinstance(item, CompiledRule)
        for item in compiled_rules
    )

    assert compiled_rules[0].rule.id == "temperature_high"
    assert compiled_rules[1].rule.id == "pressure_high"

    assert compiled_rules[0].rule.priority == 100
    assert compiled_rules[1].rule.priority == 100

    assert compiled_rules[0].rule.version == "1"
    assert compiled_rules[1].rule.version == "1"

    assert compiled_rules[0].rule.conflicts_with == (
        "safe_environment",
    )
    assert compiled_rules[1].rule.conflicts_with == (
        "safe_environment",
    )

    assert compiled_rules[0].rule.supports == (
        "danger_warning",
    )
    assert compiled_rules[1].rule.supports == (
        "danger_warning",
    )


def test_each_condition_becomes_independent_rule():
    rule_version = make_rule_version()

    compiled_rules = RuleCompiler.compile(rule_version)

    temperature_rule = compiled_rules[0].rule
    pressure_rule = compiled_rules[1].rule

    assert len(temperature_rule.conditions) == 1
    assert temperature_rule.conditions[0].fact == "temperature"
    assert temperature_rule.conditions[0].operator == ">="
    assert temperature_rule.conditions[0].value == 90

    assert len(pressure_rule.conditions) == 1
    assert pressure_rule.conditions[0].fact == "pressure"
    assert pressure_rule.conditions[0].operator == ">="
    assert pressure_rule.conditions[0].value == 10


def test_min_and_max_stay_inside_one_rule():
    rule_version = RuleVersion(
        rule_id="glucose_rule",
        name="Glucose",
        conditions=[
            {
                "id": "glucose_range",
                "parameter": "glucose",
                "min": 7.0,
                "max": 10.0,
            }
        ],
        actions=[],
        created_at=datetime.now(UTC),
        created_by="test",
    )

    compiled_rules = RuleCompiler.compile(rule_version)

    assert len(compiled_rules) == 1

    compiled = compiled_rules[0]

    assert compiled.rule.id == "glucose_range"
    assert len(compiled.rule.conditions) == 2

def test_generic_condition_is_supported():
    rule_version = RuleVersion(
        rule_id="temperature_rule",
        name="Temperature",
        conditions=[
            {
                "id": "temperature_high",
                "fact": "temperature",
                "operator": ">",
                "value": 90,
            }
        ],
        actions=[],
        created_at=datetime.now(UTC),
        created_by="test",
    )

    compiled_rules = RuleCompiler.compile(rule_version)

    assert len(compiled_rules) == 1

    compiled = compiled_rules[0]

    assert compiled.rule.id == "temperature_high"
    assert len(compiled.rule.conditions) == 1
    assert compiled.rule.conditions[0].fact == "temperature"
    assert compiled.rule.conditions[0].operator == ">"
    assert compiled.rule.conditions[0].value == 90


def test_unsupported_condition_format_is_rejected():
    rule_version = RuleVersion(
        rule_id="invalid_rule",
        name="Invalid rule",
        conditions=[
            {
                "label": "Invalid",
            }
        ],
        actions=[],
        created_at=datetime.now(UTC),
        created_by="test",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported condition format",
    ):
        RuleCompiler.compile(rule_version)


def test_compiled_rule_keeps_source_context():
    rule_version = make_rule_version()

    compiled = RuleCompiler.compile(rule_version)

    assert all(
        isinstance(item, CompiledRule)
        for item in compiled
    )

    assert compiled[0].condition is rule_version.conditions[0]
    assert compiled[0].rule_version is rule_version

    assert compiled[0].rule.id == "temperature_high"
    assert compiled[1].rule.id == "pressure_high"  


def test_gender_specific_condition_is_compiled_for_matching_gender():
    rule_version = RuleVersion(
        rule_id="anemia",
        name="Anemia",
        conditions=[
            {
                "id": "anemia_male",
                "parameter": "hemoglobin",
                "max": 130,
                "gender": "male",
            },
            {
                "id": "anemia_female",
                "parameter": "hemoglobin",
                "max": 120,
                "gender": "female",
            },
        ],
        actions=[],
        created_at=datetime.now(UTC),
        created_by="test",
    )

    compiled = RuleCompiler.compile(
        rule_version,
        patient_gender=Gender.MALE,
    )

    assert len(compiled) == 1
    assert compiled[0].rule.id == "anemia_male"


def test_gender_specific_conditions_can_be_compiled_for_female():
    rule_version = RuleVersion(
        rule_id="anemia",
        name="Anemia",
        conditions=[
            {
                "id": "anemia_male",
                "parameter": "hemoglobin",
                "max": 130,
                "gender": "male",
            },
            {
                "id": "anemia_female",
                "parameter": "hemoglobin",
                "max": 120,
                "gender": "female",
            },
        ],
        actions=[],
        created_at=datetime.now(UTC),
        created_by="test",
    )

    compiled = RuleCompiler.compile(
        rule_version,
        patient_gender=Gender.FEMALE,
    )

    assert len(compiled) == 1
    assert compiled[0].rule.id == "anemia_female"

