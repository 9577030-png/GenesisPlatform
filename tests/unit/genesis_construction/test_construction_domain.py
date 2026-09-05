from genesis_core import DefaultRuleLoader, Fact, RuleEngine
from genesis_construction import (
    ConstructionRuleParser,
    ConstructionRuleResolver,
    YamlConstructionRuleSource,
)


def test_construction_pipeline_uses_core_contracts(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "load.yaml").write_text(
        "id: load\nconditions:\n  - fact: load_kn\n    operator: '<='\n    value: 100\nresult:\n  status: acceptable\n",
        encoding="utf-8",
    )

    source = YamlConstructionRuleSource(rules_dir)
    parser = ConstructionRuleParser()
    loader = DefaultRuleLoader(source, parser)
    engine = RuleEngine(loader, ConstructionRuleResolver())

    result = engine.evaluate((Fact("load_kn", 80),))

    assert len(result) == 1
    assert result[0].rule_id == "load"
    assert result[0].matched is True
    assert result[0].result == {"status": "acceptable"}
