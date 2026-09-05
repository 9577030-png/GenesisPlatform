from pathlib import Path

from genesis_core import Fact, RuleEngine
from genesis_medical.adapters.rule_compiler import RuleCompiler
from genesis_medical.domain.rule_version import RuleVersion
from genesis_medical.parsers import MedicalRuleParser
from genesis_medical.sources import YamlMedicalRuleSource
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.domain.rule_version import RulePriority
from genesis_medical.resolvers import MedicalRuleResolver
from genesis_core import Rule


def test_medical_parser_returns_core_rule():
    rule_version = RuleVersion(
        rule_id="anemia",
        name="Anemia",
        conditions=[{"id": "anemia_low", "parameter": "hemoglobin", "max": 120}],
        actions=[],
        created_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
        created_by="test",
        priority=RulePriority.HIGH,
    )
    rule = MedicalRuleParser().parse({"rule_version": rule_version, "condition": rule_version.conditions[0]})
    assert rule.id == "anemia_low"
    assert rule.conditions[0].fact == "hemoglobin"
    assert rule.conditions[0].operator == "<="
    assert rule.priority == 100


def test_yaml_medical_source_yields_normalized_rule_records(tmp_path: Path):
    (tmp_path / "rule.yaml").write_text(
        "id: test_rule\nname: Test\nconditions:\n  - id: test_condition\n    parameter: score\n    min: 10\n",
        encoding="utf-8",
    )
    records = list(YamlMedicalRuleSource(tmp_path).load_rules())
    assert len(records) == 1
    assert records[0]["condition"]["id"] == "test_condition"
    assert records[0]["rule_version"].rule_id == "test_rule"


def test_medical_resolver_prefers_higher_priority_direct_conflict():
    low = Rule(
        id="low",
        conditions=(),
        result="LOW",
        priority=10,
        conflicts_with=("high",),
    )
    high = Rule(
        id="high",
        conditions=(),
        result="HIGH",
        priority=100,
        conflicts_with=("low",),
    )
    engine = RuleEngine(resolver=MedicalRuleResolver())
    result = engine.evaluate((low, high), ())
    assert [item.rule_id for item in result] == ["high"]
